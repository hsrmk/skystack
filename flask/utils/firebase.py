import os
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

class FirebaseClient:
    def __init__(self):
        creds_dict = {
            "type": os.environ.get("FIREBASE_TYPE"),
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
            "auth_uri": os.environ.get("FIREBASE_AUTH_URI"),
            "token_uri": os.environ.get("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.environ.get("FIREBASE_UNIVERSE_DOMAIN")
        }
        cred = credentials.Certificate(creds_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def add_to_collection(self, collection_name, document_id, data):
        """
        Adds or updates a document in the specified Firestore collection.
        :param collection_name: str
        :param document_id: str
        :param data: dict
        """
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc_ref.set(data)

    def createNewsletter(self, publication_id, name, sub_domain, custom_domain, hero_text, logo_url, lastBuildDate, postFrequency, numberOfPostsAdded, oldestPostDate, isDormant = False):
        """
        Creates or updates a newsletter document in the 'newsletters' collection.
        :param publication_id: str
        :param name: str
        :param sub_domain: str (used as document_id)
        :param custom_domain: str
        :param hero_text: str
        :param logo_url: str
        :param lastBuildDate: str
        :param postFrequency: any
        :param numberOfPostsAdded: any
        :param skipPostFrequencyCheck: bool
        """
        data = {
            "publication_id": publication_id,
            "name": name,
            "sub_domain": sub_domain,
            "custom_domain": custom_domain,
            "hero_text": hero_text,
            "logo_url": logo_url,
            "lastBuildDate": lastBuildDate,
            "postFrequency": postFrequency,
            "numberOfPostsAdded": numberOfPostsAdded,
            "skipPostFrequencyCheck": False,
            "oldestPostDate": oldestPostDate,
            "isDormant": isDormant
        }
        self.add_to_collection("newsletters", sub_domain, data)

    def updateNewsletterUserGraph(self, subdomain, newsletter_users, recommendedNewsletters, recommendedUsers):
        """
        Updates newsletter_users, recommendedNewsletters and recommendedUsers for a newsletter by subdomain, keeping other fields unchanged.
        :param newsletter_users: list of dicts [{id, name, handle}]
        :param recommendedNewsletters: list of dicts [{publication_id, name, sub_domain, custom_domain}]
        :param recommendedUsers: list of dicts [{id, name, handle}]
        """
        doc_ref = self.db.collection("newsletters").document(subdomain)
        update_data = {
            "newsletter_users": newsletter_users,
            "recommendedNewsletters": recommendedNewsletters,
            "recommendedUsers": recommendedUsers,
        }
        doc_ref.update(update_data)

    def updateLastBuildDetails(self, subdomain, lastBuildDate, numberOfPostsAdded, postFrequency):
        """
        Updates lastBuildDate, numberOfPostsAdded, and postFrequency for a newsletter by subdomain, keeping other fields unchanged.
        :param subdomain: str
        :param lastBuildDate: str
        :param numberOfPostsAdded: any
        :param postFrequency: any
        """
        doc_ref = self.db.collection("newsletters").document(subdomain)
        update_data = {
            "lastBuildDate": lastBuildDate,
            "numberOfPostsAdded": numberOfPostsAdded,
            "postFrequency": postFrequency
        }
        doc_ref.update(update_data)

    def updateNumPosts(self, subdomain, numberOfPostsAddedNow, oldestPostDate):
        """
        Updates numberOfPostsAdded by adding numberOfPostsAddedNow to the existing count for a newsletter by subdomain.
        Also updates oldestPostDate (required).
        :param subdomain: str
        :param numberOfPostsAddedNow: int - number of posts to add to the existing count
        :param oldestPostDate: str - updates oldestPostDate (required)
        """
        doc_ref = self.db.collection("newsletters").document(subdomain)
        doc = doc_ref.get()
        
        update_fields = {}
        if doc.exists:
            current_data = doc.to_dict()
            current_posts = current_data.get("numberOfPostsAdded", 0)
            
            # Ensure both values are integers for proper addition
            try:
                current_posts = int(current_posts) if current_posts is not None else 0
                new_posts = int(numberOfPostsAddedNow)
                updated_posts = current_posts + new_posts
            except (ValueError, TypeError):
                # If conversion fails, treat as 0
                updated_posts = 0 + int(numberOfPostsAddedNow) if numberOfPostsAddedNow is not None else 0
            
            update_fields["numberOfPostsAdded"] = updated_posts
            update_fields["oldestPostDate"] = oldestPostDate
            doc_ref.update(update_fields)
        else:
            # If document doesn't exist, create it with the new post count and oldestPostDate
            update_fields["numberOfPostsAdded"] = numberOfPostsAddedNow
            update_fields["oldestPostDate"] = oldestPostDate
            doc_ref.set(update_fields)

    def getNewslettersToBeBuilt(self):
        """
        Returns a list of newsletters that are due to be built (lastBuildDate + postFrequency < current time).
        lastBuildDate is in ISO 8601 format, postFrequency is in days.
        :return: list of dicts with sub_domain, custom_domain, lastBuildDate, numberOfPostsAdded, postFrequency
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        newsletters_to_build = []
        newsletters_ref = self.db.collection("newsletters")
        docs = newsletters_ref.stream()
        for doc in docs:
            data = doc.to_dict()
            lastBuildDate_str = data.get("lastBuildDate")
            postFrequency = data.get("postFrequency")

            try:
                if lastBuildDate_str:
                    # Parse ISO 8601 format with 'Z' (e.g., 2024-06-07T12:34:56Z)
                    lastBuildDate = datetime.datetime.fromisoformat(lastBuildDate_str.replace('Z', '+00:00'))
                else:
                    lastBuildDate = None
            except Exception:
                lastBuildDate = None
            try:
                postFrequency = int(postFrequency) if postFrequency is not None else None
            except Exception:
                postFrequency = None

            
            if lastBuildDate and postFrequency is not None:
                next_build_time = lastBuildDate + datetime.timedelta(days=postFrequency)
                skip_check = data.get("skipPostFrequencyCheck", False)
                if next_build_time < now or skip_check:
                    newsletters_to_build.append({
                        "sub_domain": data.get("sub_domain"),
                        "lastBuildDate": lastBuildDate_str,
                        "numberOfPostsAdded": data.get("numberOfPostsAdded"),
                        "postFrequency": postFrequency
                    })
                    
                    # If skipPostFrequencyCheck was True, set it to False after adding
                    if skip_check:
                        doc_ref = self.db.collection("newsletters").document(data.get("sub_domain"))
                        doc_ref.update({"skipPostFrequencyCheck": False})
        
        return newsletters_to_build

    def checkIfNewsletterExists(self, subdomain):
        """
        Checks if a newsletter document exists in the 'newsletters' collection for the given subdomain.
        :param subdomain: str
        :return: bool (True if exists, False otherwise)
        """
        doc_ref = self.db.collection("newsletters").document(subdomain)
        doc = doc_ref.get()
        return doc.exists
    
    def getRecommendedNewsletterSubdomains(self, subdomain):
        """
        Returns a list of subdomains for recommended newsletters by subdomain.
        :param subdomain: str
        :return: list of str (subdomains)
        """
        doc_ref = self.db.collection("newsletters").document(subdomain)
        doc = doc_ref.get()
        if not doc.exists:
            return []
        data = doc.to_dict() or {}
        recommended = data.get("recommendedNewsletters")
        if not isinstance(recommended, list):
            return []
        return [newsletter.get('subdomain') for newsletter in recommended if 'subdomain' in newsletter]

    def getOldestPostDate(self, subdomain):
        """
        Returns the oldestPostDate field for a newsletter by subdomain.
        :param subdomain: str
        :return: str | None
        """
        doc_ref = self.db.collection("newsletters").document(subdomain)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        data = doc.to_dict() or {}
        return data.get("oldestPostDate")

    def setDormantNewsletterActive(self, subdomain):
        """
        Sets the isDormant flag to False for a newsletter by subdomain.
        Per request: makes the isDormant flag to False from True.
        :param subdomain: str
        """
        doc_ref = self.db.collection("newsletters").document(subdomain)
        doc_ref.update({"isDormant": False})

    def deleteNewsletter(self, subdomain):
        """
        Deletes a newsletter document from the 'newsletters' collection by subdomain.
        :param subdomain: str
        """
        doc_ref = self.db.collection("newsletters").document(subdomain)
        doc_ref.delete()
    
    def log_failed_task(self, payload: str, endpoint: str, error: str):
        """
        Logs a failed task to the 'failed_tasks' collection in Firestore.
        Each entry uses a timestamp as the document ID.

        :param payload: str - The payload that was attempted to be sent
        :param endpoint: str - The endpoint the task was targeting
        :param error: str - The error message encountered
        """
        # Hardcoded map of endpoint to priority number, 1 being highest
        endpoint_priority_map = {
            "/createNewsletter": 1,
            "/buildNewsletter": 2,
            "/newsletterBuildCheck": 3,
            "/createDormantNewsletter": 4,
            "/addNewsletterUserGraph": 5,
            "/followUser": 6,
            "/addOlderPosts": 7,
            "/activateDormantNewsletter": 8
        }
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        priority = endpoint_priority_map.get(endpoint, 5)

        data = {
            "payload": payload,
            "endpoint": endpoint,
            "error": error,
            "priority": priority,
            "created_at": timestamp
        }
        self.add_to_collection("endpoint_failures", timestamp, data)
