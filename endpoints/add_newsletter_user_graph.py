from utils.newsletter import Newsletter
from utils.user import User
from utils.firebase import FirebaseClient

def add_newsletter_user_graph(url, subdomain, publication_id):
    """
    Adds newsletter user graph data by fetching recommended publications, newsletter users,
    and updating the Firebase database.
    
    Args:
        url (str): The newsletter URL
        subdomain (str): The newsletter subdomain
        publication_id (str): The publication ID
    
    Returns:
        dict: Status message indicating success or failure
    """
    try:
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
        
        return {"status": "success", "message": "Newsletter user graph updated successfully"}
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to update newsletter user graph: {str(e)}"}
