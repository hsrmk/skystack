from flask import request
import json
from utils.firebase import FirebaseClient
from utils.create_cloud_task import create_cloud_task
import os

def newsletter_build_check_route():
    """
    Checks for newsletters that need to be built and creates cloud tasks for each one.
    Expects JSON payload: {} (no parameters required)
    """
    # Initialize Firebase client
    firebase = FirebaseClient()
    try:
        # Get newsletters that need to be built
        newsletters_to_build = firebase.getNewslettersToBeBuilt()
        
        if not newsletters_to_build:
            return {
                "status": "success",
                "message": "No newsletters need to be built at this time",
                "newsletters_checked": 0,
                "tasks_created": 0
            }, 200
        
        # Get cloud run endpoint for build_newsletter
        cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")
        if not cloud_run_endpoint:
            return {
                "error": "CLOUD_RUN_ENDPOINT environment variable not set"
            }, 500
        
        build_endpoint = cloud_run_endpoint.rstrip('/') + '/buildNewsletter'
        
        # Create cloud tasks for each newsletter that needs to be built
        tasks_created = 0
        failed_tasks = []
        
        for newsletter in newsletters_to_build:
            try:
                # Prepare payload for build_newsletter endpoint
                task_payload = {
                    "lastBuildDate": newsletter['lastBuildDate'],
                    "noOfPosts": newsletter['numberOfPostsAdded'],
                    "postFrequency": newsletter['postFrequency'],
                    "subdomain": newsletter['sub_domain']
                }
                
                # Create cloud task
                task_result = create_cloud_task(build_endpoint, task_payload)
                
                if task_result["status"] == "success":
                    tasks_created += 1
                    print(f"Created cloud task for newsletter: {newsletter['sub_domain']}")
                else:
                    failed_tasks.append({
                        "subdomain": newsletter['sub_domain'],
                        "error": task_result["message"]
                    })
                    print(f"Failed to create cloud task for newsletter: {newsletter['sub_domain']} - {task_result['message']}")
                    
            except Exception as e:
                failed_tasks.append({
                    "subdomain": newsletter['sub_domain'],
                    "error": str(e)
                })
                print(f"Exception creating cloud task for newsletter: {newsletter['sub_domain']} - {str(e)}")
        
        return {
            "status": "success",
            "message": f"Newsletter build check completed. {tasks_created} tasks created.",
            "newsletters_checked": len(newsletters_to_build),
            "tasks_created": tasks_created,
            "failed_tasks": failed_tasks
        }, 200
        
    except Exception as e:
        payload =  json.dumps(request.get_json())
        firebase.log_failed_task(payload, "/newsletterBuildCheck", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500 