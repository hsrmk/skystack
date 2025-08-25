from flask import request
import json
import os
from utils.user import User
from utils.newsletter import Newsletter
from utils.admin import create_account, delete_account
from utils.atproto_user import AtprotoUser
from utils.firebase import FirebaseClient
from utils.create_cloud_task import create_cloud_task
from utils.endpoints import SUBSTACK_NEWSLETTER_URL, PDS_USERNAME_EXTENSION

def follow_users_route():
    """
    Handles following other skystack users for a particular user.
    Expects JSON payload: {
        "user": "string"
        "recommended_newsletters_subdomains: ["string"]
    }
    """
    firebase = FirebaseClient()
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        user = data.get('user')
        recommended_newsletters_subdomains = data.get('recommended_newsletters_subdomains')
        
        # Validate required parameters
        if not all([user, recommended_newsletters_subdomains]):
            return {"error": "Missing required parameters: user, recommended_newsletters_subdomains"}, 400
        
        url = SUBSTACK_NEWSLETTER_URL.format(subdomain=user)

         # 5. updateProfileDetails
        at_user = AtprotoUser(user, url)

        for newsletter_subdomain in recommended_newsletters_subdomains:
            newsletter_handle = newsletter_subdomain + PDS_USERNAME_EXTENSION
            at_user.followUser(newsletter_handle)
        
    except Exception as e:
        payload =  json.dumps(request.get_json())
        firebase.log_failed_task(payload, "/followUsers", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500 