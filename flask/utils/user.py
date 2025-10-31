import re
import urllib.parse

from utils.utils import fetch_json
from utils.endpoints import NEWSLETTER_USERS_RANKED

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
            handle = self.extract_handle_from_url(self.url)
            if handle:
                return {
                    'id': 0,
                    'name': handle,
                    'admin_handle': handle
                }
            return None

        admin = data[0]
        handle = admin.get('handle')
        if not handle:
            handle_from_url = self.extract_handle_from_url(self.url)
            if handle_from_url:
                return {
                    'id': admin.get('id', 0),
                    'name': admin.get('name') or handle_from_url,
                    'admin_handle': handle_from_url
                }
            else:
                return None
        return {
            'id': admin.get('id'),
            'name': admin.get('name'),
            'admin_handle': handle
        }

    def extract_handle_from_url(url):
        parsed_url = urllib.parse.urlparse(url)
        netloc = parsed_url.netloc if parsed_url.netloc else parsed_url.path.split('/')[0]
        match = re.match(r'^([a-zA-Z0-9\-_.]+)\.substack\.com$', netloc)
        if match:
            return match.group(1)
        return None

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
