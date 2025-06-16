from .utils import fetch_json
from .endpoints import NEWSLETTER_USERS_RANKED

class User:
    def __init__(self, url):
        self.url = url.rstrip('/')

    def getNewsletterAdmin(self):
        """
        Fetches the admin (first user) of the newsletter.
        Returns a dict with id, name, admin_handle.
        """
        api_url = self.url + NEWSLETTER_USERS_RANKED
        data = fetch_json(api_url)
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        admin = data[0]
        return {
            'id': admin.get('id'),
            'name': admin.get('name'),
            'admin_handle': admin.get('handle')
        }

    def getNewsletterUsers(self, limit=10):
        """
        Fetches up to `limit` users of the newsletter.
        Returns a list of dicts with id, name, handle.
        """
        api_url = self.url + NEWSLETTER_USERS_RANKED
        data = fetch_json(api_url)
        if not data or not isinstance(data, list):
            return []
        users = data[:limit]
        return [
            {
                'id': user.get('id'),
                'name': user.get('name'),
                'handle': user.get('handle')
            }
            for user in users
        ]
