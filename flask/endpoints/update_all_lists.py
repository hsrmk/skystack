import os
import json
import time
from flask import request

from utils.firebase import FirebaseClient
from utils.create_cloud_task import create_cloud_task

def update_all_lists_route():
    """
    Schedules update tasks for all categories, spacing them out over 6 days.
    For each category, creates a cloud task to call /updateList endpoint.
    """
    firebase = FirebaseClient()
    try:
        # Get all categories
        categories = firebase.getCategories()
        
        if not categories:
            return {
                "status": "success",
                "message": "No categories found",
                "tasks_scheduled": 0
            }, 200
        
        # Calculate spacing: spread over total_days days
        total_categories = len(categories)
        total_days = 1
        total_seconds = total_days * 24 * 3600  # total_days days in seconds
        
        # Calculate delay interval between tasks
        if total_categories > 1:
            interval_seconds = total_seconds / (total_categories - 1)
        else:
            interval_seconds = 0
        
        cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")
        if not cloud_run_endpoint:
            return {
                "status": "error",
                "message": "CLOUD_RUN_ENDPOINT environment variable not set"
            }, 500
        
        update_list_endpoint = cloud_run_endpoint.rstrip('/') + '/updateList'
        tasks_scheduled = []
        
        # Schedule a task for each category
        for index, category in enumerate(categories):
            delay_seconds = int(index * interval_seconds)
            
            payload = {
                "id": category.get("id"),
                "name": category.get("name"),
                "list_url": category.get("list_url")
            }
            
            task_response = create_cloud_task(
                update_list_endpoint,
                payload,
                os.environ.get('CLOUD_TASKS_CREATE_AND_BUILD_QUEUE', 'default'),
                task_name=f"update_list_{category.get('id', 'unknown')}_{int(time.time())}",
                delay_seconds=delay_seconds
            )
            
            tasks_scheduled.append({
                "category_id": category.get("id"),
                "category_name": category.get("name"),
                "delay_seconds": delay_seconds,
                "delay_days": round(delay_seconds / (24 * 3600), 2),
                "task_response": task_response
            })
        
        return {
            "status": "success",
            "message": f"Scheduled {len(tasks_scheduled)} update tasks over {total_days} days",
            "total_categories": total_categories,
            "tasks_scheduled": tasks_scheduled
        }, 200
        
    except Exception as e:
        payload = json.dumps(request.get_json()) if request.is_json else "{}"
        firebase.log_failed_task(payload, "/updateAllLists", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500