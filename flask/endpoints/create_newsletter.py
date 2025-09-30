from flask import request, jsonify
import json
import os
import time
from utils.user import User
from utils.newsletter import Newsletter
from utils.admin import create_account, delete_account
from utils.atproto_user import AtprotoUser
from utils.firebase import FirebaseClient
from utils.create_cloud_task import create_cloud_task

def create_newsletter_route():
    """
    Handles the creation of a newsletter and bridges it to Bluesky.
    Expects JSON payload: { "url": "string" }
    Returns a standard JSON response.
    """
    firebase = FirebaseClient()
    subdomain = None
    data = None
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return {"error": "Missing url in request body"}, 400
        url = data['url']

        # 2. getNewsletterAdmin
        user = User(url)
        admin = user.getNewsletterAdmin()
        if not admin:
            return {"error": "Could not fetch newsletter admin"}, 400

        # 3. getPublication
        newsletter = Newsletter(url)
        publication = newsletter.getPublication(admin['admin_handle'])
        if not publication:
            return {"error": "Could not fetch publication details"}, 400

        # 4. create_account
        subdomain = publication['subdomain']
        if firebase.checkIfNewsletterExists(subdomain):
            return {
                "type": "duplicate_newsletter",
                "message": "Newsletter already exists",
                "account": subdomain,
                "name": publication['name'],
                "description": publication['hero_text'],
                "logo_url": publication['logo_url']
            }, 409

        account_response = create_account(subdomain)
        if not account_response:
            return {"error": "Account creation failed"}, 500

        # 5. updateProfileDetails
        at_user = AtprotoUser(subdomain, url)
        at_user.updateProfileDetails(
            publication['name'], publication['hero_text'], publication['logo_url']
        )

        # 7. getPosts
        posts_info = newsletter.getPosts(limit=10)
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
        oldest_post_date = posts[-1]['post_date'] if posts else None
        firebase.createNewsletter(
            publication['publication_id'],
            publication['name'],
            subdomain,
            publication['custom_domain'],
            publication['hero_text'],
            publication['logo_url'],
            posts_info.get('lastBuildDate'),
            posts_info.get('postFrequency'),
            posts_added,
            oldest_post_date
        )

        # 11. create_cloud_task for /addNewsletterUserGraph
        cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")
        if not cloud_run_endpoint:
            return {
                "type": "partial_error",
                "message": "Account created and posts imported, but could not complete mirroring.",
                "account": subdomain,
                "posts_added": posts_added
            }, 200

        endpoint = cloud_run_endpoint.rstrip('/') + '/addNewsletterUserGraph'
        task_payload = {
            "subdomain": subdomain,
            "publication_id": publication['publication_id'],
            "is_dormant": False
        }
        add_graph_response = create_cloud_task(
            endpoint,
            task_payload,
            task_name=f"add_user_graph_{subdomain}_{int(time.time())}"
        )

        add_old_posts_endpoint = cloud_run_endpoint.rstrip('/') + '/addOlderPosts'
        add_older_posts_payload = {
            "oldestDatePostAdded": oldest_post_date,
            "subdomain": subdomain
        }

        old_posts_response = create_cloud_task(
            add_old_posts_endpoint,
            add_older_posts_payload,
            os.environ.get('CLOUD_TASKS_REC_NEWSLETTER_PROCESSING_QUEUE', 'default'),
            task_name=f"add_older_posts_{subdomain}_{int(time.time())}"
        )

        return {
            "type": "completed",
            "message": "Substack account bridged!",
            "account": subdomain,
            "name": publication['name'],
            "description": publication['hero_text'],
            "logo_url": publication['logo_url'],
            "posts_added": posts_added,
            "cloud_tasks": {
                "user_graph": str(add_graph_response),
                "older_posts": str(old_posts_response)
            }
        }, 200
    except Exception as e:
        if subdomain:
            delete_account(subdomain)
            firebase.deleteNewsletter(subdomain)
        try:
            payload = json.dumps(data)
        except Exception:
            payload = '{}'
        firebase.log_failed_task(payload, "/createNewsletter", str(e))
        return {"error": f"Internal server error: {str(e)}"}, 500
