from flask import request
import json
from utils.atproto_user import AtprotoUser
from utils.firebase import FirebaseClient
from utils.endpoints import SUBSTACK_NEWSLETTER_URL, PDS_USERNAME_EXTENSION

def follow_user_route():
    """
    Handles following a single skystack user for a particular user.
    Expects JSON payload: {
        "user": "string",
        "to_follow_subdomain": "string"
    }
    """
    firebase = FirebaseClient()
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        user = data.get('user')
        to_follow_subdomain = data.get('to_follow_subdomain')
        
        # Validate required parameters
        if not all([user, to_follow_subdomain]):
            return {"error": "Missing required parameters: user, to_follow_subdomain"}, 400
        
        url = SUBSTACK_NEWSLETTER_URL.format(subdomain=user)
        at_user = AtprotoUser(user, url)
        newsletter_handle = to_follow_subdomain + PDS_USERNAME_EXTENSION
        at_user.followUser(newsletter_handle)
        return {"status": "success", "message": f"{user} now follows {to_follow_subdomain}"}, 200

    except Exception as e:
        payload =  json.dumps(request.get_json())
        firebase.log_failed_task(payload, "/followUser", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500 