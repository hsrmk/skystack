import re

from atproto import Client, client_utils, models

import os
import requests
from io import BytesIO
from PIL import Image

from utils.endpoints import PDS_ENDPOINT, PDS_USERNAME_EXTENSION, OG_CARD_ENDPOINT

class AtprotoUser:
    """A class to manage a user's AT Protocol (Bluesky) account."""
    def __init__(self, username, url, password=None, pds_type="custom"):
        """
        Initializes the Atproto client and logs in the user.

        Args:
            username (str): The user's handle. For custom PDS, without the PDS extension.
                           For bsky, the full handle (e.g., 'user.bsky.social').
            url (str): The Substack URL associated with this account.
            password (str, optional): The password for login. If None, falls back to
                                     environment variable USER_LOGIN_PASS.
            pds_type (str, optional): Type of PDS to use. Either "bsky" or "custom".
                                     Defaults to "custom" for backward compatibility.
        """
        self.username = username
        self.url = url
        self.pds_type = pds_type
        
        # Determine password
        if password is None:
            self.user_login_pass = os.environ.get("USER_LOGIN_PASS")
            if not self.user_login_pass:
                raise ValueError("USER_LOGIN_PASS environment variable must be set when password is not provided.")
        else:
            self.user_login_pass = password
        
        # Initialize client based on PDS type
        if pds_type == "bsky":
            # For Bluesky, don't pass PDS_ENDPOINT
            self.client = Client()
            # Login with username as-is and password as-is
            login_username = username
            login_password = self.user_login_pass
        else:
            # For custom PDS, use PDS_ENDPOINT
            self.client = Client(PDS_ENDPOINT)
            # Login with username + extension and username + password
            login_username = self.username + PDS_USERNAME_EXTENSION
            login_password = self.username + self.user_login_pass
        
        self.client.login(login_username, login_password)

    def updateProfileDetails(self, display_name, description, profile_pic_url):
        """
        Updates the user's profile details on Bluesky.

        Args:
            display_name (str): The new display name.
            description (str): The new profile description.
            profile_pic_url (str): The URL of the new profile picture.

        Returns:
            The response from the server after updating the profile.
        """
        if profile_pic_url is not None:
            blob_response = self.uploadBlob(profile_pic_url)
            avatar_blob = blob_response.blob
        else:
            avatar_blob = None

        # Ensure combined string is ≤256 chars. If too long, trim description.
        description_str = (
            description + "\n\n\n" +
            "This is an automated Substack Account of " + self.url + "\n" +
            "Discover more/Create at: @skystack.xyz"
        )
        if len(description_str) > 256:
            base_str = (
                "\n\n\n" +
                "This is an automated Substack Account of " + self.url + "\n" +
                "Discover more/Create at: @skystack.xyz"
            )
            avail_len = 256 - len(base_str) - 3  # 3 for the ellipsis
            trimmed_description = (description[:avail_len] + '...') if avail_len > 0 else '...'
            description_str = trimmed_description + base_str

        profile_record = models.AppBskyActorProfile.Record(
            display_name=display_name,
            description=description_str,
            avatar=avatar_blob,
        )
        # Update the profile using the profile record namespace
        profile_response = self.client.app.bsky.actor.profile.create(
            repo=self.client.me.did,
            record=profile_record,
            rkey='self'
        )
        return profile_response

    def createEmbededLinkPost(self, title, subtitle, link, thumbnail_url, post_date, labels):
        """
        Creates a new post with a link card embed.

        Args:
            title (str): The title of the link card.
            subtitle (str): The description/subtitle of the link card.
            link (str): The URL the link card should point to.
            thumbnail_url (str): The URL of the image for the link card's thumbnail.
            post_date (str): ISO format date string with Z suffix  
        Returns:
            The response from the server after creating the post.
        """
        # Create external embed for link preview
        blob_response = self.uploadBlob(thumbnail_url)
        external_embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                uri=link,
                title=title,
                description=subtitle,
                thumb=blob_response.blob
            )
        )

        # 'labels': ['reaction_count:149', 'comment_count:109', 'child_comment_count:33']
        # https://deepwiki.com/search/i-am-creating-a-embed-post-lik_58bdf979-e9bd-4898-bb81-a3c788c42510
        self_labels = None  
        if labels:  
            label_values = [models.ComAtprotoLabelDefs.SelfLabel(val=label) for label in labels]  
            self_labels = models.ComAtprotoLabelDefs.SelfLabels(values=label_values)

        text_builder = None
        title_handle_match = re.search(rf'@([A-Za-z0-9.-]+){re.escape(PDS_USERNAME_EXTENSION)}', title)

        if title_handle_match:
            resolved_handle = f"{title_handle_match.group(1)}{PDS_USERNAME_EXTENSION}"
            mention_handle = f"@{resolved_handle}"
            try:
                mention_did = self.client.resolve_handle(resolved_handle).did
            except Exception:
                mention_did = None

            if mention_did:
                text_builder = client_utils.TextBuilder()
                text_builder.text(title[:title_handle_match.start()])
                text_builder.mention(handle=mention_handle, did=mention_did)
                text_builder.text(title[title_handle_match.end():])

        # Append subtitle text while keeping facets aligned when using TextBuilder
        if subtitle:
            if text_builder:
                text_builder.text(' • ')
                text_builder.text(subtitle)
            else:
                title = title + ' • ' + subtitle

        record_text = text_builder.build_text() if text_builder else title
        record_facets = text_builder.build_facets() if text_builder else None

        # Create post record with custom date  
        post_record = models.AppBskyFeedPost.Record(  
            text=record_text,
            facets=record_facets,
            created_at=post_date,  # ISO format with Z suffix  
            embed=external_embed,
            labels=self_labels
        )
        
        # Create the post using the record namespace 
        post_response = self.client.app.bsky.feed.post.create(  
            repo=self.client.me.did,
            record=post_record  
        )
        return post_response

    def followUser(self, follow_user):
        """
        Follows another user on the network.

        Args:
            follow_user (str): The handle or DID of the user to follow 
                               (e.g., 'bob.bsky.social').

        Returns:
            The response from the server after following the user.
        """
        try:
            user_data = self.client.resolve_handle(follow_user)
            follow_response = self.client.follow(user_data.did)
            return follow_response
        except Exception as e:
            print(f"Error following user {follow_user}: {e}")

    def uploadBlob(self, image_url):
        """
        Downloads an image from a URL and uploads it as a blob to the PDS.

        Args:
            image_url (str): The URL of the image to upload.

        Returns:
            The response from the server containing the uploaded blob's reference.
        """
        # Download image from URL and upload as blob
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = BytesIO(response.content).read()
        except requests.exceptions.Timeout:
            # If timeout, use fallback image URL
            image_url = self.url + OG_CARD_ENDPOINT
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = BytesIO(response.content).read()

        blob_response = self.client.com.atproto.repo.upload_blob(image_data, headers={"Content-Type": "url/" + image_url})
        return blob_response
