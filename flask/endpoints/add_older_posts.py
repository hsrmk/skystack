import os
import json
import time
from flask import request

from utils.newsletter import Newsletter
from utils.atproto_user import AtprotoUser
from utils.firebase import FirebaseClient
from utils.endpoints import SUBSTACK_NEWSLETTER_URL
from utils.create_cloud_task import create_cloud_task

def add_older_posts_route():
    """
    Adds posts before the oldestDatePostAdded to Bluesky Account.
    Expects JSON payload: {
        "oldestDatePostAdded": "string",  (ISO with Z)
        "subdomain": "string",
        "numberOfIterations": "number"  (must be > 0 to execute)
    }
    Due to Bluesky rate limits, we import only 10 old posts per hour. We recursively call the /addOlderPosts API in 
    scheduled in the background and on each call we decrease the numberOfIterations, till either it is 0 or no more posts to add.
    """
    firebase = FirebaseClient()
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        oldestDatePostAdded = data.get('oldestDatePostAdded')
        subdomain = data.get('subdomain')
        numberOfIterations = data.get('numberOfIterations')
        
        # Validate required parameters
        if not all([oldestDatePostAdded, subdomain, numberOfIterations]):
            return {"error": "Missing required parameters: oldestDatePostAdded, subdomain, numberOfIterations"}, 400
        
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
        oldest_post_date = newsletter_data[-1]['post_date'] if newsletter_data else None
        firebase.updateNumPosts(subdomain, posts_added, oldest_post_date)
        
        cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")
        if cloud_run_endpoint and numberOfIterations > 0 and len(newsletter_data) > 0:
            add_old_posts_endpoint = cloud_run_endpoint.rstrip('/') + '/addOlderPosts'
            add_old_posts_payload = {
                "oldestDatePostAdded": oldest_post_date,
                "subdomain": subdomain,
                "numberOfIterations": numberOfIterations - 1
            }

            old_posts_response = create_cloud_task(
                add_old_posts_endpoint,
                add_old_posts_payload,
                os.environ.get('CLOUD_TASKS_OLD_POSTS_IMPORT_QUEUE', 'default'),
                task_name=f"add_older_posts_{subdomain}_{int(time.time())}",
                delay_seconds=3600
            )

        response_data = {
            "status": "success",
            "message": f"Old Posts added successfully. {posts_added} old posts added." if posts_added > 0 else "No old posts added."
        }
        
        if 'old_posts_response' in locals():
            response_data["oldPostsResponse"] = old_posts_response
            response_data["numberOfIterationsPending"] = numberOfIterations - 1
        
        return response_data, 200
        
    except Exception as e:
        payload =  json.dumps(request.get_json())
        firebase.log_failed_task(payload, "/addOlderPosts", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500 