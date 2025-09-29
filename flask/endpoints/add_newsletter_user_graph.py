import os
import json
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
        if not all([subdomain, publication_id, is_dormant]):
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

        if not is_dormant:
            recommended_newsletters_subdomains = [newsletter['subdomain'] for newsletter in recommended_newsletters]
            create_dormant_newsletters_for_newsletter(subdomain, recommended_newsletters_subdomains)
        
        return {
            "status": "success", 
            "message": "Newsletter user graph updated successfully",
            "newsletter_users_count": len(newsletter_users),
            "recommended_newsletters_count": len(recommended_newsletters),
            "recommended_users_count": len(recommended_users)
        }, 200
        
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
            "message": "Newsletter user graph only imported to Skystack, not create in Bluesky."
        }, 200
    
    endpoint = cloud_run_endpoint.rstrip('/') + '/createDormantNewsletter'

    for newsletter_subdomain in recommended_newsletters_subdomains:
        recommended_newsletter_url = SUBSTACK_NEWSLETTER_URL.format(subdomain=newsletter_subdomain)
        task_payload = {
            "url": recommended_newsletter_url,
            "parent_newsletter_subdomain": subdomain
        }

        create_cloud_task(
            endpoint, 
            task_payload, 
            os.environ.get('CLOUD_TASKS_REC_NEWSLETTER_PROCESSING_QUEUE', 'default'), 
            f"create_dormant_newsletter_{subdomain}"
        )