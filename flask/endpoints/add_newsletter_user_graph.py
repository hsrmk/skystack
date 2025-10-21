import os
import json
import time
from flask import request
from utils.newsletter import Newsletter
from utils.user import User
from utils.firebase import FirebaseClient
from utils.endpoints import SUBSTACK_NEWSLETTER_URL
from utils.create_cloud_task import create_cloud_task

def add_newsletter_user_graph_route():
    """
    Handles adding newsletter user graph data by fetching recommended publications, newsletter users,
    and updating the Firebase database.
    Expects JSON payload: {
        "subdomain": "string", 
        "publication_id": "string"
    }
    """
    firebase_client = FirebaseClient()
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        subdomain = data.get('subdomain')
        publication_id = data.get('publication_id')
        is_dormant = data.get('is_dormant')

        # Validate required parameters
        if not (subdomain and publication_id and is_dormant is not None):
            return {"error": "Missing required parameters: subdomain, publication_id, is_dormant"}, 400
        
        url = SUBSTACK_NEWSLETTER_URL.format(subdomain=subdomain)

        # Initialize the newsletter and user objects
        newsletter = Newsletter(url)
        user = User(url)
        
        # 1. Get recommended publications and users
        recommended_newsletters, recommended_users = newsletter.getRecommendedPublications(publication_id)
        
        # 2. Get newsletter users
        newsletter_users = user.getNewsletterUsers()
        
        # 3. Update the newsletter user graph in Firebase
        firebase_client.updateNewsletterUserGraph(
            subdomain=subdomain,
            newsletter_users=newsletter_users,
            recommendedNewsletters=recommended_newsletters,
            recommendedUsers=recommended_users
        )

        cloud_tasks_info = None
        if not is_dormant:
            recommended_newsletters_subdomains = [newsletter['subdomain'] for newsletter in recommended_newsletters]
            cloud_tasks_info = create_dormant_newsletters_for_newsletter(subdomain, recommended_newsletters_subdomains)

        response_body = {
            "status": "success", 
            "message": "Newsletter user graph updated successfully",
            "newsletter_users_count": len(newsletter_users),
            "recommended_newsletters_count": len(recommended_newsletters),
            "recommended_users_count": len(recommended_users)
        }

        if cloud_tasks_info is not None:
            response_body["cloud_tasks"] = cloud_tasks_info

        return response_body, 200
        
    except Exception as e:
        payload =  json.dumps(request.get_json())
        firebase_client.log_failed_task(payload, "/addNewsletterUserGraph", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500
    
# We create dormant newsletters only for non-dormant ones.
def create_dormant_newsletters_for_newsletter(subdomain, recommended_newsletters_subdomains):
    # 4. For each of the recommended newsletters create dormant newsletter accounts.
    cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")
    if not cloud_run_endpoint:
        return {
            "status": "warning",
            "message": "Newsletter user graph only imported to Skystack, not created in Bluesky.",
            "create_dormant_newsletters": []
        }

    create_dormant_newsletter_endpoint = cloud_run_endpoint.rstrip('/') + '/createDormantNewsletter'
    follow_user_endpoint = cloud_run_endpoint.rstrip('/') + '/followUser'

    task_responses = []
    for index, newsletter_subdomain in enumerate(recommended_newsletters_subdomains, start=1):
        recommended_newsletter_url = SUBSTACK_NEWSLETTER_URL.format(subdomain=newsletter_subdomain)
        create_dormant_newsletter_task_payload = {
            "url": recommended_newsletter_url,
            "parent_newsletter_subdomain": subdomain
        }

        create_dormant_newsletter_task_response = create_cloud_task(
            create_dormant_newsletter_endpoint,
            create_dormant_newsletter_task_payload,
            os.environ.get('CLOUD_TASKS_REC_NEWSLETTER_PROCESSING_QUEUE', 'default'),
            f"create_dormant_newsletter_{newsletter_subdomain}_{subdomain}_{int(time.time())}",
            delay_seconds=index * 30
        )

        follow_user_task_payload = {
            "user": subdomain,
            "to_follow_subdomain": newsletter_subdomain
        }
        follow_user_task_response = create_cloud_task(
            follow_user_endpoint,
            follow_user_task_payload,
            os.environ.get('CLOUD_TASKS_OLD_POSTS_IMPORT_QUEUE', 'default'),
            f"follow_user_{subdomain}_follows_{newsletter_subdomain}_{int(time.time())}",
            delay_seconds=index * 1800
        )

        task_responses.append({
            "subdomain": newsletter_subdomain,
            "index": index,
            **(create_dormant_newsletter_task_response or {"status": "error", "message": "Unknown error creatin create_dormant_newsletter task"}),
            **(follow_user_task_response or {"status": "error", "message": "Unknown error creatin follow_user task"}),
        })

    return {
        "status": "success",
        "create_dormant_newsletters": task_responses
    }