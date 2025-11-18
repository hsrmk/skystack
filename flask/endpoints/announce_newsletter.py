import os
import json
from datetime import datetime, timezone
from flask import request

from utils.atproto_user import AtprotoUser
from utils.endpoints import PDS_USERNAME_EXTENSION, OG_CARD_ENDPOINT
from utils.firebase import FirebaseClient
from utils.categories import Categories

def announce_newsletter_route():
    """
    Creates an announcement post on Bluesky when a newsletter is created.
    Expects JSON payload: {
        "newsletterId": "string",
        "custom_domain": "string" (optional)
    }
    Requires Bearer token authentication.
    """
    firebase = FirebaseClient()
    
    try:
        # Verify Bearer token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "Missing or invalid Authorization header"}, 401
        
        token = auth_header.split(" ")[1]
        cloud_function_token = os.environ.get("CLOUD_FUNCTION_TOKEN")
        
        if not cloud_function_token or token != cloud_function_token:
            return {"error": "Invalid token"}, 401
        
        # Get request data
        data = request.get_json()
        if not data:
            return {"error": "No JSON data provided"}, 400
        
        newsletter_id = data.get("newsletterId")
        custom_domain = data.get("custom_domain")
        
        if not newsletter_id:
            return {"error": "Missing required parameter: newsletterId"}, 400
        
        # Determine URL
        if custom_domain:
            url = f"https://{custom_domain}"
        else:
            url = f"https://{newsletter_id}.substack.com"
        
        # Get username and password from environment variables
        username = os.environ.get("STATUS_BSKY_USERNAME")
        password = os.environ.get("STATUS_BSKY_APP_PASSWORD")
        all_newsletters_list = os.environ.get("STATUS_BSKY_ALL_NEWSLETTERS_LIST")
        
        if not username or not password:
            return {"error": "USERNAME or PASSWORD environment variables not set"}, 500
        
        # Initialize AtprotoUser
        at_user = AtprotoUser(username, url, password=password, pds_type="bsky")
        
        # Prepare post data
        title = f"@{newsletter_id}{PDS_USERNAME_EXTENSION} is now available to follow"
        link = f"https://{newsletter_id}.substack.com"
        thumbnail_url = url + OG_CARD_ENDPOINT
        post_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        labels = None
        
        # Create the post
        at_user.createEmbededLinkPost(
            title,
            "",  # Empty subtitle
            link,
            thumbnail_url,
            post_date,
            labels
        )

        categories = Categories(handle=username, app_password=password)
        successful = 0
        failed = 0
        failed_usernames = []
        successful, failed, failed_usernames = categories.addUsersToList([f"{newsletter_id}{PDS_USERNAME_EXTENSION}"], all_newsletters_list)
        
        response = {
            "status": "success",
            "message": "Announcement post created successfully and added to All Newsletters List.",
            "newsletterId": newsletter_id,
            "users_added_to_list": successful,
            "users_failed_to_list": failed
        }
        # Only include failed usernames if there are failures
        if failed_usernames:
            response["failed_usernames"] = failed_usernames

        return response, 200
        
    except Exception as e:
        payload = json.dumps(request.get_json()) if request.get_json() else "{}"
        firebase.log_failed_task(payload, "/announceNewsletter", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500

