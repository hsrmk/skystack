from flask import request
import json
import os
import time
from utils.newsletter import Newsletter
from utils.atproto_user import AtprotoUser
from utils.firebase import FirebaseClient
from utils.create_cloud_task import create_cloud_task
from endpoints.add_newsletter_user_graph import create_dormant_newsletters_for_newsletter

def activate_dormant_newsletter_route():
    """
    Converts a newsletter from dormant to active, by importing all old posts and following all recommended newsletters.
    Expects JSON payload: {
        "subdomain": "string"
    }
    """
    firebase = FirebaseClient()
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        subdomain = data.get('subdomain')
        
        # Validate required parameters
        if not subdomain:
            return {"error": "Missing required parameters: subdomain"}, 400
        
        firebase.setDormantNewsletterActive(subdomain)

        rec_newsletter_subdomains = firebase.getRecommendedNewsletterSubdomains(subdomain)
        oldest_added_post = firebase.getOldestPostDate(subdomain)

        cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")
        add_old_posts_endpoint = cloud_run_endpoint.rstrip('/') + '/addOlderPosts'
        add_older_posts_payload = {
            "oldestDatePostAdded": oldest_added_post,
            "subdomain": subdomain,
            "numberOfIterations": 10
        }

        old_posts_response = create_cloud_task(
            add_old_posts_endpoint, 
            add_older_posts_payload,
            os.environ.get('CLOUD_TASKS_OLD_POSTS_IMPORT_QUEUE', 'default'),
            task_name=f"add_older_posts_{subdomain}_{int(time.time())}"
        )
        print("old_posts_response: ", old_posts_response)

        create_dormant_newsletters_for_newsletter(subdomain, rec_newsletter_subdomains)
        
        return {
            "status": "success",
            "message": f"Newsletter converted from dormant to active."
        }, 200
        
    except Exception as e:
        payload =  json.dumps(request.get_json())
        firebase.log_failed_task(payload, "/activateDormantNewsletter", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500 