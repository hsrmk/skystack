import os
import json
from datetime import datetime, timezone
from flask import request

from utils.atproto_user import AtprotoUser
from utils.endpoints import OG_CARD_ENDPOINT
from utils.firebase import FirebaseClient
from utils.categories import Categories

def announce_newsletter_route():
    """
    Creates an announcement post for a single newsletter provided in the request body.
    Requires Bearer token authentication and the following JSON payload:
    {
        "username": "...",
        "name": "...",
        "description": "...",
        "substackUrl": "..."
    }
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

        if not request.is_json:
            return {"error": "Request body must be JSON"}, 400

        payload = request.get_json(silent=True) or {}
        newsletter_username = payload.get("username")
        newsletter_name = payload.get("name")
        description = payload.get("description")
        substack_url = payload.get("substackUrl")

        if not newsletter_username:
            return {"error": "username is required"}, 400
        if not substack_url:
            return {"error": "substackUrl is required"}, 400

        # Get username and password from environment variables
        username = os.environ.get("STATUS_BSKY_USERNAME")
        password = os.environ.get("STATUS_BSKY_APP_PASSWORD")
        all_newsletters_list = os.environ.get("STATUS_BSKY_ALL_NEWSLETTERS_LIST")
        
        if not username or not password:
            return {"error": "STATUS_BSKY_USERNAME or STATUS_BSKY_APP_PASSWORD not set"}, 500
        if not all_newsletters_list:
            return {"error": "STATUS_BSKY_ALL_NEWSLETTERS_LIST not set"}, 500
        
        newsletter_name = newsletter_name or newsletter_username
        description = description or newsletter_name

        # Initialize shared instances
        categories = Categories(handle=username, app_password=password)
        at_user = AtprotoUser(username, substack_url, password=password, pds_type="bsky")

        # Step 1: Get existing members from the Bluesky list
        existing_members = categories.getListMembers(all_newsletters_list)
        existing_members_set = set(existing_members)

        if newsletter_username in existing_members_set:
            return {
                "status": "skipped",
                "message": f"{newsletter_username} already exists in the list"
            }, 200

        try:
            # Prepare post data
            post_text = f"{newsletter_name} is now available to follow at @{newsletter_username}."
            link = substack_url
            thumbnail_url = substack_url + OG_CARD_ENDPOINT
            post_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            labels = None
            embedTitle = newsletter_name
            embedSubtitle = description

            # Create the post
            at_user.createEmbededLinkPostWithMentions(
                post_text,
                link,
                thumbnail_url,
                post_date,
                labels,
                embedTitle,
                embedSubtitle
            )

            # Add to list
            successful, failed, failed_usernames = categories.addUsersToList(
                [newsletter_username],
                all_newsletters_list
            )

            response = {
                "status": "completed",
                "username": newsletter_username,
                "list_added": successful,
                "list_failed": failed,
                "failed_usernames": failed_usernames
            }

            return response, 200 if failed == 0 else 207

        except Exception as e:
            error_msg = f"{newsletter_username}: {str(e)}"
            firebase.log_failed_task(json.dumps(payload), "/announceNewsletter", error_msg)
            return {"error": error_msg}, 500
        
    except Exception as e:
        firebase.log_failed_task(json.dumps(request.get_json(silent=True) or {}), "/announceNewsletter", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500

