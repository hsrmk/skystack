import os
import json
import time
from flask import request, Response, stream_with_context

from utils.user import User
from utils.newsletter import Newsletter
from utils.admin import create_account, delete_account
from utils.atproto_user import AtprotoUser
from utils.firebase import FirebaseClient
from utils.create_cloud_task import create_cloud_task
from utils.endpoints import PDS_USERNAME_EXTENSION

def create_newsletter_route():
    """
    Handles the creation of a newsletter and bridges it to Bluesky.
    Expects JSON payload: { "url": "string" }
    Returns a streaming JSON response.
    """
    def generate():
        firebase = FirebaseClient()
        subdomain = None
        data = None
        try:
            data = request.get_json()
            if not data or 'url' not in data:
                yield f"data: {json.dumps({'state': 'error', 'message': 'Missing url in request body'})}\n\n"
                return
            url = data['url']

            # Step 1: Fetching newsletter admin
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Fetching newsletter data', 'submessage': 'Contacting Substack...'})}\n\n"
            
            user = User(url)
            admin = user.getNewsletterAdmin()
            if not admin:
                raise Exception(f"Could not fetch newsletter admin.")

            # Step 2: Getting publication details
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Analyzing newsletter', 'submessage': 'Fetching publication details...'})}\n\n"
            
            newsletter = Newsletter(url)
            publication = newsletter.getPublication(admin['admin_handle'])
            if not publication:
                raise Exception(f"Could not fetch publication details.")

            # Step 3: Checking if newsletter exists
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Checking availability', 'submessage': 'Verifying newsletter status...'})}\n\n"
            
            subdomain = publication['subdomain']
            if firebase.checkIfNewsletterExists(subdomain):
                yield f"data: {json.dumps({'state': 'finished', 'message': 'Newsletter is already available to follow!', 'profilePicImage': publication['logo_url'], 'name': publication['name'], 'username': subdomain, 'description': publication['hero_text'], 'substackUrl': url, 'skystackUrl': f'https://bsky.app/profile/{subdomain}{PDS_USERNAME_EXTENSION}', 'submessage': 'Newsletter already exists, returning with already available data'})}\n\n"
                return

            # Step 4: Creating Bluesky account
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Creating Bluesky account', 'submessage': 'Setting up Bluesky profile...'})}\n\n"
            
            account_response = create_account(subdomain)
            if not account_response:
                raise Exception(f"Account creation failed.")

            # Step 5: Updating profile details
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Customizing profile', 'submessage': 'Adding newsletter branding...'})}\n\n"
            
            at_user = AtprotoUser(subdomain, url)
            at_user.updateProfileDetails(
                publication['name'], publication['hero_text'], publication['logo_url']
            )

            # Step 6: Fetching and posting content
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Importing content', 'submessage': 'Fetching latest posts...'})}\n\n"
            
            posts_info = newsletter.getPosts(limit=10)
            posts = posts_info.get('postsArray', [])
            posts_added = 0

            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Publishing posts', 'submessage': 'Creating Bluesky posts...'})}\n\n"
            
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

            if posts_added == 0 and len(posts) != 0:
                raise Exception("No posts were added. All errored out.")
            
            # Step 7: Saving to database
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Saving newsletter', 'submessage': 'Updating Skystack status...'})}\n\n"
            
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

            # Step 8: Setting up background tasks
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Finalizing setup', 'submessage': 'Configuring background processes...'})}\n\n"
            
            cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")
            if not cloud_run_endpoint:
                raise Exception(f"Cloud Run Endpoint not found. Finished items: posts_added: {posts_added}.")

            # Step 9: Importing Substack Recommendation Graph
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Importing Substack Recommendation Graph', 'submessage': 'Importing Newsletter Recommendation Graph in the background...'})}\n\n"
            
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

            # Step 9: Importing Old Posts
            yield f"data: {json.dumps({'state': 'step_completed', 'message': 'Older Posts', 'submessage': 'Setting up imports for old posts in the background...'})}\n\n"

            add_old_posts_endpoint = cloud_run_endpoint.rstrip('/') + '/addOlderPosts'
            add_old_posts_payload = {
                "oldestDatePostAdded": oldest_post_date,
                "subdomain": subdomain,
                "numberOfIterations": 10
            }

            old_posts_response = create_cloud_task(
                add_old_posts_endpoint,
                add_old_posts_payload,
                os.environ.get('CLOUD_TASKS_OLD_POSTS_IMPORT_QUEUE', 'default'),
                task_name=f"add_older_posts_{subdomain}_{int(time.time())}"
            )

            # Final success response
            yield f"data: {json.dumps({'state': 'finished', 'message': 'Newsletter is now available to follow!', 'profilePicImage': publication['logo_url'], 'name': publication['name'], 'username': subdomain, 'description': publication['hero_text'], 'substackUrl': url, 'skystackUrl': f'https://bsky.app/profile/{subdomain}{PDS_USERNAME_EXTENSION}', 'submessage': 'Newsletter built from scratch', 'posts_added': posts_added, 'cloud_tasks': {'user_graph': str(add_graph_response), 'older_posts': str(old_posts_response)}})}\n\n"
            
        except Exception as e:
            if subdomain:
                delete_account(subdomain)
                firebase.deleteNewsletter(subdomain)
            try:
                payload = json.dumps(data)
            except Exception:
                payload = '{}'
            firebase.log_failed_task(payload, "/createNewsletter", str(e))
            yield f"data: {json.dumps({'state': 'error', 'message': f'Internal server error: {str(e)}'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )