from flask import request
import json
from utils.newsletter import Newsletter
from utils.atproto_user import AtprotoUser
from utils.firebase import FirebaseClient
from utils.endpoints import SUBSTACK_NEWSLETTER_URL

def build_newsletter_route():
    """
    Handles building a newsletter by fetching new posts since last build and creating posts on Bluesky.
    Expects JSON payload: {
        "lastBuildDate": "string", 
        "noOfPosts": "int",
        "postFrequency": "float",
        "subdomain": "string"
    }
    """
    firebase = FirebaseClient()
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        lastBuildDate = data.get('lastBuildDate')
        noOfPosts = data.get('noOfPosts')
        postFrequency = data.get('postFrequency')
        subdomain = data.get('subdomain')
        
        # Validate required parameters
        if not all([lastBuildDate, noOfPosts is not None, postFrequency is not None, subdomain]):
            return {"error": "Missing required parameters: lastBuildDate, noOfPosts, postFrequency, subdomain"}, 400
        
        url = SUBSTACK_NEWSLETTER_URL.format(subdomain=subdomain)

        # Initialize newsletter and fetch new data
        newsletter = Newsletter(url)
        newsletter_data = newsletter.getNewsletterDataSinceLastBuild(
            lastBuildDate=lastBuildDate,
            numberOfPosts=noOfPosts,
            postFrequency=postFrequency
        )
        
        # Initialize AtprotoUser for creating posts
        at_user = AtprotoUser(subdomain, url)
        
        # Create embedded link posts for each new post item
        posts_added = 0
        for post_item in newsletter_data['post_items']:
            try:
                at_user.createEmbededLinkPost(
                    post_item['title'],
                    post_item['subtitle'],
                    post_item['link'],
                    post_item['thumbnail_url'],
                    post_item['post_date']
                )
                print(f"Created post: {post_item['title']}")
                posts_added += 1
            except Exception as e:
                print(f"Skipping post {post_item.get('link', 'unknown')} due to error: {e}")
        
        # Update last build details in Firebase
        firebase.updateLastBuildDetails(
            subdomain=subdomain,
            lastBuildDate=newsletter_data['last_build_date'],
            numberOfPostsAdded=newsletter_data['number_of_posts'],
            postFrequency=newsletter_data['post_frequency']
        )
        
        return {
            "status": "success",
            "message": f"Newsletter built successfully. {posts_added} posts added." if posts_added > 0 else "No new posts since last build. Nothing added."
        }, 200
        
    except Exception as e:
        payload =  json.dumps(request.get_json())
        firebase.log_failed_task(payload, "/buildNewsletter", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500 