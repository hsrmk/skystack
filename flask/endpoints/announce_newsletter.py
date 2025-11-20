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
    Creates announcement posts on Bluesky for newsletters that:
    1. Exist in the all-newsletters static JSON (Firebase.getAllNewsletterUsernames)
    2. Are NOT already present in the all-newsletters Bluesky list
       (Categories.getListMembers for STATUS_BSKY_ALL_NEWSLETTERS_LIST)

    No request body is required; this endpoint derives everything from
    Firebase + Bluesky list state.

    Requires Bearer token authentication (handled upstream).
    """
    firebase = FirebaseClient()
    
    try:
        # Get username and password from environment variables
        username = os.environ.get("STATUS_BSKY_USERNAME")
        password = os.environ.get("STATUS_BSKY_APP_PASSWORD")
        all_newsletters_list = os.environ.get("STATUS_BSKY_ALL_NEWSLETTERS_LIST")
        
        if not username or not password:
            return {"error": "STATUS_BSKY_USERNAME or STATUS_BSKY_APP_PASSWORD not set"}, 500
        if not all_newsletters_list:
            return {"error": "STATUS_BSKY_ALL_NEWSLETTERS_LIST not set"}, 500
        
        # Initialize shared instances
        categories = Categories(handle=username, app_password=password)
        # URL will be updated per-newsletter; initialize with a placeholder
        at_user = AtprotoUser(username, "", password=password, pds_type="bsky")

        # Step 1: Get existing members from the Bluesky list
        existing_members = categories.getListMembers(all_newsletters_list)
        existing_members_set = set(existing_members)

        # Step 2: Get all newsletter details from Firebase-backed static JSON
        all_newsletter_details = firebase.getAllNewsletterDetails()
        if not all_newsletter_details:
            return {
                "status": "completed",
                "message": "No newsletters returned from getAllNewsletterDetails",
                "total_processed": 0,
                "total_successful": 0,
                "total_failed": 0,
                "total_users_added_to_list": 0,
                "total_users_failed_to_list": 0,
            }, 200

        newsletter_map = {}
        for detail in all_newsletter_details:
            username = detail.get("username")
            if isinstance(username, str) and username:
                newsletter_map[username] = detail

        # Step 3: Determine which newsletters are not yet in the list
        remaining_newsletters = [
            detail for username_key, detail in newsletter_map.items()
            if username_key not in existing_members_set
        ]
        
        # Aggregate tracking
        total_processed = 0
        total_successful = 0
        total_failed = 0
        total_users_added = 0
        total_users_failed = 0
        errors = []
        
        # Process each newsletter username that is not already in the list
        for newsletter in remaining_newsletters:
            newsletter_username = newsletter.get("username")
            newsletter_name = newsletter.get("name") or newsletter_username
            description = newsletter.get("description") or newsletter_name
            substack_url = newsletter.get("substackUrl")

            if not newsletter_username:
                total_failed += 1
                errors.append("Missing username for newsletter entry")
                continue

            total_processed += 1

            try:
                # Keep AtprotoUser.url in sync for any image fallback logic
                at_user.url = substack_url

                # Prepare post data
                # We assume newsletter_username is the full handle already; no extension added.
                post_text = f"{newsletter_name} is now available to follow at @{newsletter_username}."
                link = substack_url
                thumbnail_url = substack_url + OG_CARD_ENDPOINT
                post_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                labels = None
                embedTitle = newsletter_name
                embedSubtitle = description

                # Create the post
                at_user.createEmbededLinkPostWithMentions(post_text, link, thumbnail_url, post_date, labels, embedTitle, embedSubtitle)

                # Add to list
                successful, failed, failed_usernames = categories.addUsersToList(
                    [newsletter_username],
                    all_newsletters_list
                )
                
                total_users_added += successful
                total_users_failed += failed
                total_successful += 1
                
            except Exception as e:
                total_failed += 1
                error_msg = f"{newsletter_username}: {str(e)}"
                errors.append(error_msg)
                # Log individual failure but continue processing
                payload = json.dumps({"username": newsletter_username})
                firebase.log_failed_task(payload, f"/announceNewsletter", str(e))
        
        # Build aggregated response
        response = {
            "status": "completed",
            "total_processed": total_processed,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "total_users_added_to_list": total_users_added,
            "total_users_failed_to_list": total_users_failed
        }
        
        # Include errors if any
        if errors:
            response["errors"] = errors
        
        return response, 200
        
    except Exception as e:
        payload = {}
        firebase.log_failed_task(payload, "/announceNewsletter", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500

