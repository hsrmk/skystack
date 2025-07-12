from flask import request
from utils.newsletter import Newsletter
from utils.user import User
from utils.firebase import FirebaseClient
from utils.endpoints import SUBSTACK_NEWSLETTER_URL

def add_newsletter_user_graph_route():
    """
    Handles adding newsletter user graph data by fetching recommended publications, newsletter users,
    and updating the Firebase database.
    Expects JSON payload: {
        "subdomain": "string", 
        "publication_id": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        subdomain = data.get('subdomain')
        publication_id = data.get('publication_id')
        
        # Validate required parameters
        if not all([subdomain, publication_id]):
            return {"error": "Missing required parameters: subdomain, publication_id"}, 400
        
        url = SUBSTACK_NEWSLETTER_URL.format(subdomain=subdomain)

        # Initialize the newsletter and user objects
        newsletter = Newsletter(url)
        user = User(url)
        firebase_client = FirebaseClient()
        
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
        
        return {
            "status": "success", 
            "message": "Newsletter user graph updated successfully",
            "newsletter_users_count": len(newsletter_users),
            "recommended_newsletters_count": len(recommended_newsletters),
            "recommended_users_count": len(recommended_users)
        }, 200
        
    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500