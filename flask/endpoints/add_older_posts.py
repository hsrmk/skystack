from flask import request
import json
from utils.newsletter import Newsletter
from utils.atproto_user import AtprotoUser
from utils.firebase import FirebaseClient
from utils.endpoints import SUBSTACK_NEWSLETTER_URL

def add_older_posts_route():
    """
    Adds posts before the oldestDatePostAdded to Bluesky Account.
    Expects JSON payload: {
        "oldestDatePostAdded": "string",  (ISO with Z)
        "subdomain": "string"
    }
    """
    firebase = FirebaseClient()
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        oldestDatePostAdded = data.get('oldestDatePostAdded')
        subdomain = data.get('subdomain')
        
        # Validate required parameters
        if not all([oldestDatePostAdded, subdomain]):
            return {"error": "Missing required parameters: oldestDatePostAdded, subdomain"}, 400
        
        url = SUBSTACK_NEWSLETTER_URL.format(subdomain=subdomain)

        # Initialize newsletter and fetch new data
        newsletter = Newsletter(url)
        newsletter_data = newsletter.getOlderPosts(oldestDatePostAdded)
        
        # Initialize AtprotoUser for creating posts
        at_user = AtprotoUser(subdomain, url)
        
        # Create embedded link posts for each new post item
        posts_added = 0
        for post_item in newsletter_data:
            try:
                at_user.createEmbededLinkPost(
                    post_item['title'],
                    post_item['subtitle'],
                    post_item['link'],
                    post_item['thumbnail_url'],
                    post_item['post_date'],
                    post_item['labels']
                )
                print(f"Created post: {post_item['title']}")
                posts_added += 1
            except Exception as e:
                print(f"Skipping post {post_item.get('link', 'unknown')} due to error: {e}")
        
        # Update last build details in Firebase
        firebase.updateNumPosts(subdomain, posts_added)
        
        return {
            "status": "success",
            "message": f"Old Posts added successfully. {posts_added} old posts added." if posts_added > 0 else "No old posts added."
        }, 200
        
    except Exception as e:
        payload =  json.dumps(request.get_json())
        firebase.log_failed_task(payload, "/addOlderPosts", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500 