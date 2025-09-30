from atproto import Client, models
from atproto_client.models.utils import get_response_model

import os
import requests
from io import BytesIO
from PIL import Image

from utils.endpoints import PDS_ENDPOINT, PDS_USERNAME_EXTENSION, OG_CARD_ENDPOINT

class AtprotoUser:
    """A class to manage a user's AT Protocol (Bluesky) account."""
    def __init__(self, username, url):
        """
        Initializes the Atproto client and logs in the user.

        Args:
            username (str): The user's handle without the PDS extension.
        """
        self.username = username
        self.url = url
        self.user_login_pass = os.environ.get("USER_LOGIN_PASS")
        if not self.user_login_pass:
            raise ValueError("USER_LOGIN_PASS environment variables must be set.")
        self.client = Client(PDS_ENDPOINT)
        self.client.login(
            self.username + PDS_USERNAME_EXTENSION,
            self.username + self.user_login_pass
        )

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

        profile_record = models.AppBskyActorProfile.Record(
            display_name=display_name,
            description=description + " \n\n\n" + "This is an automated Substack Account of " + self.url + "\n" + "Discover more/Create at: @skystack.xyz",
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

        # Create post record with custom date  
        post_record = models.AppBskyFeedPost.Record(  
            text=title if not subtitle else title + ' • ' + subtitle,
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
            follow_response = self.client.follow(follow_user)
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
