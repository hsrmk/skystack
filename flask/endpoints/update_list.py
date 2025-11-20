from flask import request
import json
from utils.firebase import FirebaseClient
from utils.categories import Categories

def update_list_route():
    """
    Updates a Bluesky list by adding newsletter usernames that are:
    1. In the bestsellers list for the given category
    2. Not already in the list
    3. Present in the all newsletters collection
    
    Expects JSON payload: {
        "id": "string",           # Category ID for bestsellers
        "name": "string",         # Category name (for logging)
        "list_url": "string"      # URI of the Bluesky list to update
    }
    """
    firebase = FirebaseClient()
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        id = data.get('id')
        name = data.get('name')
        list_url = data.get('list_url')
        
        # Validate required parameters
        if not all([id, list_url]):
            return {"error": "Missing required parameters: id, list_url"}, 400
        
        # Initialize Categories client
        categories = Categories()
        
        # Step 1: Get all newsletter usernames
        all_newsletters = firebase.getAllNewsletterUsernames()
        
        # Step 2: Get bestsellers for the category
        bestsellers = categories.getBestsellers(id)
        
        # Step 3: Get already present usernames in the list
        existing_members = categories.getListMembers(list_url)
        
        # Step 4: Remove already present usernames from all newsletters
        existing_members_set = set(existing_members)
        all_newsletters_set = set(all_newsletters)
        
        remaining_newsletters = all_newsletters_set - existing_members_set
        
        # Step 5: Find intersection of remaining newsletters and bestsellers
        bestsellers_set = set(bestsellers)
        usernames_to_add = remaining_newsletters & bestsellers_set
        
        # Step 6: Add users to list
        successful = 0
        failed = 0
        failed_usernames = []
        
        if usernames_to_add:
            successful, failed, failed_usernames = categories.addUsersToList(list(usernames_to_add), list_url)
        
        # Prepare minimal response
        response = {
            "status": "success",
            "message": f"Updated list '{name}' (ID: {id})",
            "total_newsletters": len(all_newsletters),
            "bestsellers_count": len(bestsellers),
            "existing_members_count": len(existing_members),
            "users_added": successful,
            "users_failed": failed
        }
        
        # Only include failed usernames if there are failures
        if failed_usernames:
            response["failed_usernames"] = failed_usernames
        
        return response, 200

    except Exception as e:
        payload = json.dumps(request.get_json())
        firebase.log_failed_task(payload, "/updateList", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500