from flask import request
import json
import os
import time
from utils.user import User
from utils.newsletter import Newsletter
from utils.admin import create_account, delete_account
from utils.atproto_user import AtprotoUser
from utils.firebase import FirebaseClient
from utils.create_cloud_task import create_cloud_task
from utils.endpoints import SUBSTACK_NEWSLETTER_URL, PDS_USERNAME_EXTENSION

def create_dormant_newsletter_route():
    """
    Handles building a newsletter by fetching new posts since last build and creating posts on Bluesky.
    Expects JSON payload: {
        "url": "string"
    }
    """
    firebase = FirebaseClient()
    subdomain = None
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        # Extract required parameters
        url = data.get('url')
        parent_newsletter_subdomain = data.get('parent_newsletter_subdomain')
        
        # Validate required parameter
        if not all([url, parent_newsletter_subdomain]):
            return {"error": "Missing required parameters: url/parent_newsletter_subdomain"}, 400

        # 2. getNewsletterAdmin
        user = User(url)
        admin = user.getNewsletterAdmin()
    
        # 3. getPublication
        newsletter = Newsletter(url)
        publication = newsletter.getPublication(admin['admin_handle'])
        
        # 4. create_account
        subdomain = publication['subdomain']
        newsletter_handle = publication['subdomain'] + PDS_USERNAME_EXTENSION

        if firebase.checkIfNewsletterExists(subdomain):
            return {
                "status": "success",
                "message": f"Newsletter already built."
            }, 200

        account_response = create_account(subdomain)

         # 5. updateProfileDetails
        at_user = AtprotoUser(subdomain, url)
        at_user.updateProfileDetails(
            publication['name'], publication['hero_text'], publication['logo_url']
        )

        # 7. getPosts
        posts_info = newsletter.getPosts(limit=20)
        posts = posts_info.get('postsArray', [])
        posts_added = 0
        for post in posts:
            try:
                post_response = at_user.createEmbededLinkPost(
                    post['title'],
                    post['subtitle'],
                    post['link'],
                    post['thumbnail_url'],
                    post['post_date'],
                    post['labels']
                )
                print(post_response)
                posts_added += 1
            except Exception as e:
                print(f"Skipping post {post['link']} due to error: {e}")

        if posts_added == 0:
            raise Exception("No posts were added.")
        
        # 10. createNewsletter in Firebase
        isDormant = True
        oldest_post_date = posts[-1]['post_date'] if posts else None
        firebase.createNewsletter(
            publication['publication_id'],
            publication['name'],
            publication['subdomain'],
            publication['custom_domain'],
            publication['hero_text'],
            publication['logo_url'],
            posts_info.get('lastBuildDate'),
            posts_info.get('postFrequency'),
            posts_added,
            oldest_post_date,
            isDormant
        )

        # 11. create_cloud_task for /addNewsletterUserGraph
        cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")
        if not cloud_run_endpoint:
            return {
                "status": "warning",
                "message": f"Newsletter built, but couldn't import Newsletter User Graph to Skystack."
            }, 200
        
        endpoint = cloud_run_endpoint.rstrip('/') + '/addNewsletterUserGraph'
        task_payload = {
            "subdomain": publication['subdomain'],
            "publication_id": publication['publication_id'],
            "is_dormant": True
        }
        create_cloud_task(
            endpoint, 
            task_payload,
            os.environ.get('CLOUD_TASKS_REC_NEWSLETTER_PROCESSING_QUEUE', 'default'),
            f"dormant_newsletter_user_graph_{subdomain}_{int(time.time())}"
        )

        return {
            "status": "success",
            "message": f"Newsletter built successfully."
        }, 200
        
    except Exception as e:
        if subdomain:
            delete_account(subdomain)
            firebase.deleteNewsletter(subdomain)
        
        data = request.get_json()
        data['deleted_subdomain'] = subdomain
        
        payload = json.dumps(data)
        firebase.log_failed_task(payload, "/createDormantNewsletter", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500 


def parentNewsletterFollowsRecommendedNewsletters(parent_newsletter_subdomain, newsletter_handle):
    parent_newsletter_url = SUBSTACK_NEWSLETTER_URL.format(subdomain=parent_newsletter_subdomain)
    
    parent_newsletter_at_user = AtprotoUser(parent_newsletter_subdomain, parent_newsletter_url)
    parent_newsletter_at_user.followUser(newsletter_handle)