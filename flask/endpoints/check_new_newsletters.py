import os
import json
import time
from flask import request

from utils.categories import Categories
from utils.firebase import FirebaseClient
from utils.create_cloud_task import create_cloud_task


def check_new_newsletters_route():
    """
    Identifies newsletters that are not yet in the Bluesky list and schedules
    announcement tasks over a 12-hour window, spacing tasks evenly.
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

        # Required environment configuration
        username = os.environ.get("STATUS_BSKY_USERNAME")
        password = os.environ.get("STATUS_BSKY_APP_PASSWORD")
        all_newsletters_list = os.environ.get("STATUS_BSKY_ALL_NEWSLETTERS_LIST")
        cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")

        if not username or not password:
            return {"error": "STATUS_BSKY_USERNAME or STATUS_BSKY_APP_PASSWORD not set"}, 500
        if not all_newsletters_list:
            return {"error": "STATUS_BSKY_ALL_NEWSLETTERS_LIST not set"}, 500
        if not cloud_run_endpoint:
            return {"error": "CLOUD_RUN_ENDPOINT environment variable not set"}, 500

        # Initialize helpers
        categories = Categories(handle=username, app_password=password)

        # Step 1: Get existing members from the Bluesky list
        existing_members = categories.getListMembers(all_newsletters_list)
        existing_members_set = set(existing_members)

        # Step 2: Fetch all newsletter details
        all_newsletter_details = firebase.getAllNewsletterDetails()
        if not all_newsletter_details:
            return {
                "status": "success",
                "message": "No newsletters found in Firebase",
                "tasks_scheduled": 0,
                "new_newsletters": 0
            }, 200

        newsletter_map = {}
        for detail in all_newsletter_details:
            detail_username = detail.get("username")
            if isinstance(detail_username, str) and detail_username:
                newsletter_map[detail_username] = detail

        remaining_newsletters = [
            detail for username_key, detail in newsletter_map.items()
            if username_key not in existing_members_set
        ]

        total_new = len(remaining_newsletters)
        if total_new == 0:
            return {
                "status": "success",
                "message": "All newsletters are already in the list",
                "tasks_scheduled": 0,
                "new_newsletters": 0
            }, 200

        # Prepare scheduling parameters
        total_window_seconds = 48 * 3600  # 48 hours
        interval_seconds = total_window_seconds / (total_new - 1) if total_new > 1 else 0

        announce_endpoint = cloud_run_endpoint.rstrip('/') + '/announceNewsletter'
        queue_name = os.environ.get('CLOUD_TASKS_CREATE_AND_BUILD_QUEUE', 'default')

        tasks_scheduled = []

        for index, newsletter in enumerate(remaining_newsletters):
            delay_seconds = int(index * interval_seconds)
            payload = {
                "username": newsletter.get("username"),
                "name": newsletter.get("name"),
                "description": newsletter.get("description"),
                "substackUrl": newsletter.get("substackUrl")
            }

            task_username = newsletter.get('username', 'unknown')
            if isinstance(task_username, str) and task_username.endswith('.skystack.xyz'):
                task_username = task_username[:-len('.skystack.xyz')]

            task_response = create_cloud_task(
                announce_endpoint,
                payload,
                queue_name,
                task_name=f"announce_{task_username}_{int(time.time())}",
                delay_seconds=delay_seconds,
                headers={
                    "Authorization": f"Bearer {cloud_function_token}"
                }
            )

            tasks_scheduled.append({
                "username": newsletter.get("username"),
                "delay_seconds": delay_seconds,
                "delay_hours": round(delay_seconds / 3600, 2),
                "task_response": task_response
            })

        return {
            "status": "success",
            "message": f"Scheduled {len(tasks_scheduled)} announcement tasks over 12 hours",
            "new_newsletters": total_new,
            "tasks_scheduled": tasks_scheduled
        }, 200

    except Exception as e:
        payload = json.dumps(request.get_json(silent=True) or {})
        firebase.log_failed_task(payload, "/checkNewNewsletters", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500

