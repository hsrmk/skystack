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
                yield f"data: {json.dumps({"type": "error", "message": "Missing 'url' in request body"})}\n\n"
                return
            url = data['url']
            yield f"data: {json.dumps({"type": "processing", "message": "Creating account..."})}\n\n"

            # 2. getNewsletterAdmin
            user = User(url)
            admin = user.getNewsletterAdmin()
            if not admin:
                yield f"data: {json.dumps({"type": "error", "message": "Could not fetch newsletter admin"})}\n\n"
                return
            # yield json.dumps({"type": "admin_fetched", **admin}) + '\n'
            
            # 3. getPublication
            newsletter = Newsletter(url)
            publication = newsletter.getPublication(admin['admin_handle'])
            if not publication:
                yield f"data: {json.dumps({"type": "error", "message": "Could not fetch publication details"})}\n\n"
                return
            yield f"data: {json.dumps({"type": "publication_fetched", **publication})}\n\n"
            
            # 4. create_account
            subdomain = publication['subdomain']
            yield f"data: {json.dumps({"type": "duplicate_newsletter_check"})}\n\n"
            
            if firebase.checkIfNewsletterExists(subdomain):
                yield f"data: {json.dumps({
                    "type": "duplicate_newsletter", 
                    "message": "Newsletter already exists",
                    "account": subdomain,
                    "name": publication['name'],
                    "description": publication['hero_text'],
                    "logo_url": publication['logo_url']    
                })}\n\n"
                return
            
            yield f"data: {json.dumps({"type": "duplicate_newsletter_check"})}\n\n"

            account_response = create_account(subdomain)
            if not account_response:
                yield f"data: {json.dumps({"type": "error", "message": "Account creation failed"})}\n\n"
                return

            # 5. updateProfileDetails
            at_user = AtprotoUser(subdomain, url)
            at_user.updateProfileDetails(
                publication['name'], publication['hero_text'], publication['logo_url']
            )
            yield f"data: {json.dumps({
                "type": "account_created",
                "account": subdomain,
                "name": publication['name'],
                "description": publication['hero_text'],
                "logo_url": publication['logo_url']
            })}\n\n"

            # 6. creatingPosts event
            yield f"data: {json.dumps({"type": "creating_posts", "message": "Importing posts..."})}\n\n"

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
                    yield f"data: {json.dumps({"type": "post_added", "added_count": posts_added, "total_count": len(posts), "link": post['link']})}\n\n"
                except Exception as e:
                    print(f"Skipping post {post['link']} due to error: {e}")

            if posts_added == 0:
                raise Exception("No posts were added.")
            
            yield f"data: {json.dumps({"type": "posts_added", "message": "Imported posts..."})}\n\n"

            # 9. finalizing
            yield f"data: {json.dumps({"type": "finalizing", "message": "Finalizing setup..."})}\n\n"

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
                yield f"data: {json.dumps({"type": "partial_error", "message": "Account created and posts imported, but couldn't complete mirroring."})}\n\n"
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
            
            yield f"data: {json.dumps({"type": "cloud_task", "message": f"User Graph {str(add_graph_response)}"})}\n\n"

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
            yield f"data: {json.dumps({"type": "cloud_task", "message": f"Old Posts added {str(old_posts_response)}"})}\n\n"

            # 12. completed
            yield f"data: {json.dumps({"type": "completed", "message": "Substack account bridged!"})}\n\n"
        except Exception as e:
            if subdomain:
                delete_account(subdomain)
                firebase.deleteNewsletter(subdomain)
            
            # Avoid re-reading the request JSON (can raise inside generator)
            try:
                payload = json.dumps(data)
            except Exception:
                payload = '{}'
            firebase.log_failed_task(payload, "/createNewsletter", str(e))
            yield f"data: {json.dumps({"type": "error", "message": f"Internal server error: {str(e)}"})}\n\n"
    # Add anti-buffering headers to keep streaming responsive behind proxies
    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
