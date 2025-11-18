import os
import datetime
from typing import List

from atproto import Client, models

from utils.utils import fetch_json
from utils.endpoints import SUBSTACK_BESTSELLERS_ENDPOINT, PDS_USERNAME_EXTENSION

class Categories:
    """Utility methods for working with Substack categories."""

    def __init__(self, handle: str | None = None, app_password: str | None = None) -> None:
        # Allow overriding the default admin credentials; fall back to env vars if not provided.
        if handle is None:
            handle = os.environ.get("ADMIN_BSKY_USERNAME")
        if app_password is None:
            app_password = os.environ.get("ADMIN_BSKY_APP_PASSWORD")

        if not handle or not app_password:
            raise ValueError("Both handle and app password are required to authenticate the Bluesky client.")

        self.client = Client()
        self.client.login(handle, app_password)

    def getBestsellers(self, id: str, count: int = 100) -> List[str]:
        """
        Fetches the paid leaderboard for a category and returns up to `count`
        subdomains of the publications listed.

        :param id: str - Category identifier used in the endpoint path.
        :param count: int - Maximum number of subdomains to return.
        :return: list[str] - Subdomains extracted from the leaderboard items.
        """
        subdomains: List[str] = []
        page = 0
        while len(subdomains) < count:
            url = SUBSTACK_BESTSELLERS_ENDPOINT.format(id=id, page=page)
            data = fetch_json(url)

            items = data.get("items") if isinstance(data, dict) else None
            if not isinstance(items, list) or not items:
                break

            for item in items:
                if len(subdomains) >= count:
                    break

                publication = item.get("publication") if isinstance(item, dict) else None
                if not isinstance(publication, dict):
                    continue

                subdomain = publication.get("subdomain")
                if isinstance(subdomain, str) and subdomain:
                    subdomains.append(subdomain + PDS_USERNAME_EXTENSION)

            more = data.get("more") if isinstance(data, dict) else False
            if not more:
                break

            page += 1

        return subdomains

    def getListMembers(self, list_uri: str, page_limit: int = 100) -> List[str]:
        """
        Retrieves the usernames of accounts contained within a Bluesky list.

        :param list_uri: The URI identifying the list to query.
        :param page_limit: Maximum number of items to request per API call.
        :return: list[str] - Handles of list members.
        """
        usernames: List[str] = []
        cursor: str | None = None

        while True:
            params = models.AppBskyGraphGetList.Params(list=list_uri, limit=page_limit, cursor=cursor)
            response = self.client.app.bsky.graph.get_list(params)

            for item in getattr(response, "items", []) or []:
                subject = getattr(item, "subject", None)
                handle = getattr(subject, "handle", None)
                if isinstance(handle, str) and handle:
                    usernames.append(handle)

            cursor = getattr(response, "cursor", None)
            if not cursor:
                break

        return usernames

    def addUsersToList(self, usernames: List[str], list_uri: str) -> tuple[int, int, List[str]]:
        """
        Adds multiple usernames (handles) to an atproto list.

        :param usernames: List of Bluesky handles (e.g., ["alice.bsky.social", "bob.bsky.social"]).
        :param list_uri: The URI of the list to add users to.
        :return: Tuple of (successful_count, failed_count, failed_usernames) - number of successfully added users, number of failed attempts, and list of failed usernames.
        """
        successful = 0
        failed = 0
        failed_usernames: List[str] = []

        for username in usernames:
            if not isinstance(username, str) or not username:
                failed += 1
                failed_usernames.append(username if username else "<empty>")
                continue

            # Resolve handle to DID if it's not already a DID
            if username.startswith("did:"):
                did = username
            else:
                try:
                    did = self.client.resolve_handle(username).did
                except Exception as e:
                    print(f"Error resolving handle '{username}': {e}")
                    failed += 1
                    failed_usernames.append(username)
                    continue

            # Create list item record
            created_at = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
            record = models.AppBskyGraphListitem.Record(subject=did, list=list_uri, created_at=created_at)
            data = models.ComAtprotoRepoCreateRecord.Data(
                repo=self.client.me.did,
                collection=models.ids.AppBskyGraphListitem,
                record=record,
            )

            try:
                res = self.client.com.atproto.repo.create_record(data)
                successful += 1
            except Exception as e:
                print(f"Error adding user '{username}' (did: '{did}') to list: {e}")
                failed += 1
                failed_usernames.append(username)
                continue

        return (successful, failed, failed_usernames)