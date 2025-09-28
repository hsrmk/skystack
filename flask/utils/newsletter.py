from utils.endpoints import PUBLIC_PROFILE_ENDPOINT, RECOMMENDATIONS_ENDPOINT, ARCHIVE_ENDPOINT
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from utils.utils import fetch_json, getLatestRSSItems, getPostFreqDetails, normalize_substack_image_url
class Newsletter:
    def __init__(self, url: str):
        self.url = url.rstrip('/')

    # Internal helpers
    def _fetch_archive_page(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        endpoint = ARCHIVE_ENDPOINT.format(offset=offset, limit=limit)
        api_url = self.url + endpoint
        data = fetch_json(api_url)
        return data or []

    def _parse_iso_z(self, iso_str: Optional[str]) -> Optional[datetime]:
        if not iso_str:
            return None
        try:
            return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        except Exception:
            return None

    def _labels_from_post(self, post: Dict[str, Any]) -> List[str]:
        return [
            f"{label}:{post.get(label)}"
            for label in ['reaction_count', 'comment_count', 'child_comment_count']
            if post.get(label) not in (None, '', [])
        ]

    def _map_post_item(self, post: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': post.get('title'),
            'subtitle': post.get('subtitle'),
            'link': post.get('canonical_url'),
            'id': post.get('id'),
            'thumbnail_url': normalize_substack_image_url(post.get('cover_image'), self.url, isPost=True),
            'post_date': post.get('post_date'),
            'labels': self._labels_from_post(post)
        }

    def getPublication(self, admin_handle: str) -> Optional[Dict[str, Any]]:
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
            'logo_url': normalize_substack_image_url(pub.get('logo_url'), self.url) if pub.get('logo_url') else normalize_substack_image_url(data.get('photo_url'), self.url)
        }

    def getRecommendedPublications(self, publication_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
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

    def getPosts(self, limit: int = 50) -> Dict[str, Any]:
        """
        Fetches up to `limit` posts, paginating as needed (max 20 per request).
        Returns:
        - postsArray: [title, subtitle, link, id, thumbnail_url]
        - numberOfPosts: number of posts returned
        - lastPostTime: post_date of the latest post (arr[0])
        - postFrequency: average time (in days) between posts
        """
        posts: List[Dict[str, Any]] = []
        offset = 0
        max_per_page = 20
        while len(posts) < limit:
            fetch_limit = min(max_per_page, limit - len(posts))
            data = self._fetch_archive_page(offset=offset, limit=fetch_limit)
            if not data:
                break
            posts.extend(data)
            if len(data) < fetch_limit:
                break  # No more posts available
            offset += fetch_limit

        posts = posts[:limit]
        postsArray = [self._map_post_item(post) for post in posts]
        numberOfPosts = len(postsArray)
        lastBuildDate = posts[0]['post_date'] if posts else None
        
        # Calculate postFrequency (average days between posts)
        if numberOfPosts > 1:
            post_dates = [datetime.fromisoformat(post['post_date'].replace('Z', '+00:00')) for post in posts]
            time_diffs = [
                (post_dates[i] - post_dates[i+1]).total_seconds() / 86400.0
                for i in range(len(post_dates)-1)
            ]
            postFrequency = sum(time_diffs) / len(time_diffs)
        else:
            postFrequency = None

        return {
            'postsArray': postsArray,
            'numberOfPosts': numberOfPosts,
            'lastBuildDate': lastBuildDate,
            'postFrequency': postFrequency
        }

    def getLatestPosts(self, lastBuildDate: Optional[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Fetch posts that are strictly newer than the provided ISO Z timestamp.

        Args:
        - lastBuildDate (str): ISO 8601 string with 'Z' suffix, e.g. '2025-09-06T12:00:27.657Z'.

        Returns:
        - items (list[dict]): post dicts with keys: title, subtitle, link, id, thumbnail_url, post_date
        - post_dates_list (list[str]): ISO Z date strings for each item returned
        """
        if not lastBuildDate:
            return [], []

        cutoff_dt = self._parse_iso_z(lastBuildDate)
        if cutoff_dt is None:
            return [], []

        items = []
        post_dates_list = []

        offset = 0
        max_per_page = 20
        stop_pagination = False
        while True:
            data = self._fetch_archive_page(offset=offset, limit=max_per_page)
            if not data:
                break

            for post in data:
                post_date_str = post.get('post_date')
                if not post_date_str:
                    continue
                post_dt = self._parse_iso_z(post_date_str)
                if post_dt is None:
                    continue

                # Only include posts strictly newer than cutoff
                if post_dt > cutoff_dt:
                    item = self._map_post_item(post)
                    item['post_date'] = post_date_str
                    items.append(item)
                    post_dates_list.append(post_date_str)
                else:
                    # As data is reverse chronological, older or equal means we can stop.
                    stop_pagination = True
                    break

            if stop_pagination:
                break

            if len(data) < max_per_page:
                break  # No more posts available

            offset += max_per_page

        return items, post_dates_list

    def getOlderPosts(self, oldestAddedPostDate: Optional[str]) -> List[Dict[str, Any]]:
        """
        Fetch posts that are strictly older than the provided ISO Z timestamp.

        Args:
        - oldestAddedPostDate (str): ISO 8601 string with 'Z' suffix, e.g. '2025-09-06T12:00:27.657Z'.

        Returns:
        - items (list[dict]): post dicts with keys: title, subtitle, link, id, thumbnail_url, post_date
        """
        MAX_ITEMS = 5000

        if not oldestAddedPostDate:
            return [], []

        oldest_dt = self._parse_iso_z(oldestAddedPostDate)
        if oldest_dt is None:
            return [], []

        items = []

        offset = 0
        max_per_page = 20
        while True:
            if len(items) >= MAX_ITEMS:
                break

            data = self._fetch_archive_page(offset=offset, limit=max_per_page)
            if not data:
                break

            for post in data:
                if len(items) >= MAX_ITEMS:
                    break

                post_date_str = post.get('post_date')
                if not post_date_str:
                    continue
                post_dt = self._parse_iso_z(post_date_str)
                if post_dt is None:
                    continue

                # Only include posts strictly older than oldestAddedPostDate
                if post_dt < oldest_dt:
                    item = self._map_post_item(post)
                    item['post_date'] = post_date_str
                    items.append(item)

            if len(data) < max_per_page or len(items) >= MAX_ITEMS:
                break  # No more posts available or reached max limit

            offset += max_per_page

        # Truncate in case we went over in the last page
        if len(items) > MAX_ITEMS:
            items = items[:MAX_ITEMS]

        return items

    def getNewsletterDataSinceLastBuild(self, lastBuildDate, numberOfPosts, postFrequency):
        """
        Build a newsletter by fetching latest RSS items and calculating post frequency details.
        
        Returns a dictionary containing updated newsletter statistics:
        - 'post_items' (list): New items from the RSS feed.
        - 'number_of_posts' (int): Updated total number of posts.
        - 'last_post_time' (str): Timestamp of the most recent post.
        - 'post_frequency' (float): Updated average post frequency in days.
        """
        
        # Fetch latest RSS items
        # items, post_dates_list = getLatestRSSItems(self.url, lastBuildDate) # Maybe use RSS instead?
        items, post_dates_list = self.getLatestPosts(lastBuildDate)
        
        # Call getPostFreqDetails
        post_freq_details = getPostFreqDetails(
            numberOfPosts=numberOfPosts,
            postFrequency=postFrequency,  # n days
            lastBuildDate=lastBuildDate,
            post_dates_list=post_dates_list
        )
    
        return {
            'post_items': items,
            'number_of_posts': post_freq_details['numberOfPosts'],
            'last_build_date': post_freq_details['lastBuildDate'],
            'post_frequency': post_freq_details['postFrequency']
        }
