from .utils import fetch_json
from .endpoints import PUBLIC_PROFILE_ENDPOINT, RECOMMENDATIONS_ENDPOINT

class Newsletter:
    def __init__(self, url):
        self.url = url.rstrip('/')

    def getPublication(self, admin_handle):
        """
        Fetches publication details for the given admin_handle.
        Returns a dict with publication_id, name, subdomain, custom_domain, hero_text, logo_url.
        """
        endpoint = PUBLIC_PROFILE_ENDPOINT.format(admin_handle=admin_handle)
        api_url = self.url + endpoint
        data = fetch_json(api_url)
        # Find the admin's publication (role == 'admin')
        pub_user = None
        for pu in data.get('publicationUsers', []):
            if pu.get('role') == 'admin':
                pub_user = pu
                break
        if not pub_user or 'publication' not in pub_user:
            return None
        pub = pub_user['publication']
        return {
            'publication_id': pub.get('id'),
            'name': pub.get('name'),
            'subdomain': pub.get('subdomain'),
            'custom_domain': pub.get('custom_domain'),
            'hero_text': pub.get('hero_text'),
            'logo_url': pub.get('logo_url')
        }

    def getRecommendedPublications(self, publication_id):
        """
        Fetches recommended publications and users for a given publication_id.
        Returns two arrays:
        - rec_newsletters: [publication_id, name, subdomain, custom_domain]
        - rec_users: [id, name, handle]
        """
        endpoint = RECOMMENDATIONS_ENDPOINT.format(publication_id=publication_id)
        api_url = self.url + endpoint
        data = fetch_json(api_url)
        rec_newsletters = []
        rec_users = []
        for rec in data:
            pub = rec.get('recommendedPublication', {})
            if pub:
                rec_newsletters.append({
                    'publication_id': pub.get('id'),
                    'name': pub.get('name'),
                    'subdomain': pub.get('subdomain'),
                    'custom_domain': pub.get('custom_domain')
                })
                author = pub.get('author', {})
                if author:
                    rec_users.append({
                        'id': author.get('id'),
                        'name': author.get('name'),
                        'handle': author.get('handle')
                    })
        return rec_newsletters, rec_users
