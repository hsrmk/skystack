from flask import request, Response, stream_with_context
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
    Handles the creation of a newsletter and bridges it to Bluesky, streaming progress events.
    Expects JSON payload: { "url": "string" }
    """
    firebase = FirebaseClient()
    def event_stream():
        subdomain = None
        try:
            data = request.get_json()
            if not data or 'url' not in data:
                yield json.dumps({"type": "error", "message": "Missing 'url' in request body"}) + '\n'
                return
            url = data['url']
            yield json.dumps({"type": "processing", "message": "Creating account..."}) + '\n'

            # 2. getNewsletterAdmin
            user = User(url)
            admin = user.getNewsletterAdmin()
            if not admin:
                yield json.dumps({"type": "error", "message": "Could not fetch newsletter admin"}) + '\n'
                return
            # yield json.dumps({"type": "admin_fetched", **admin}) + '\n'
            
            # 3. getPublication
            newsletter = Newsletter(url)
            publication = newsletter.getPublication(admin['admin_handle'])
            if not publication:
                yield json.dumps({"type": "error", "message": "Could not fetch publication details"}) + '\n'
                return
            yield json.dumps({"type": "publication_fetched", **publication}) + '\n'
            
            # 4. create_account
            subdomain = publication['subdomain']
            
            if firebase.checkIfNewsletterExists(subdomain):
                yield json.dumps({
                    "type": "duplicate_newsletter", 
                    "message": "Newsletter already exists",
                    "account": subdomain,
                    "name": publication['name'],
                    "description": publication['hero_text'],
                    "logo_url": publication['logo_url']    
                }) + '\n'
                return
            
            yield json.dumps({"type": "duplicate_newsletter_check"}) + '\n'

            account_response = create_account(subdomain)
            if not account_response:
                yield json.dumps({"type": "error", "message": "Account creation failed"}) + '\n'
                return

            # 5. updateProfileDetails
            at_user = AtprotoUser(subdomain, url)
            at_user.updateProfileDetails(
                publication['name'], publication['hero_text'], publication['logo_url']
            )
            yield json.dumps({
                "type": "account_created",
                "account": subdomain,
                "name": publication['name'],
                "description": publication['hero_text'],
                "logo_url": publication['logo_url']
            }) + '\n'

            # 6. creatingPosts event
            yield json.dumps({"type": "creating_posts", "message": "Importing posts..."}) + '\n'

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
            yield json.dumps({"type": "posts_added", "message": "Imported posts..."}) + '\n'

            # 9. finalizing
            yield json.dumps({"type": "finalizing", "message": "Finalizing setup..."}) + '\n'

            # 10. createNewsletter in Firebase
            firebase.createNewsletter(
                publication['publication_id'],
                publication['name'],
                subdomain,
                publication['custom_domain'],
                publication['hero_text'],
                publication['logo_url'],
                posts_info.get('lastBuildDate'),
                posts_info.get('postFrequency'),
                posts_added
            )

            # 11. create_cloud_task for /addNewsletterUserGraph
            cloud_run_endpoint = os.environ.get("CLOUD_RUN_ENDPOINT")
            if not cloud_run_endpoint:
                yield json.dumps({"type": "partial_error", "message": "Account created and posts imported, but couldn't complete mirroring."}) + '\n'
                return
            
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

            yield json.dumps({"type": "cloud_task", "message": f"User Graph {str(add_graph_response)}"}) + '\n'

            oldest_post_date = posts[-1]['post_date'] if posts else None
            add_old_posts_endpoint = endpoint = cloud_run_endpoint.rstrip('/') + '/addOlderPosts'
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
            yield json.dumps({"type": "cloud_task", "message": f"Old Posts added {str(old_posts_response)}"}) + '\n'

            # 12. completed
            yield json.dumps({"type": "completed", "message": "Substack account bridged!"}) + '\n'
        except Exception as e:
            if subdomain:
                delete_account(subdomain)
                firebase.deleteNewsletter(subdomain)
            
            payload =  json.dumps(request.get_json())
            firebase.log_failed_task(payload, "/createNewsletter", str(e))
            yield json.dumps({"type": "error", "message": f"Internal server error: {str(e)}"}) + '\n'

    return Response(stream_with_context(event_stream()), mimetype='application/json')
