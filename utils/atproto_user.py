from atproto import Client, models
import os
import requests
from io import BytesIO
from PIL import Image

from utils.endpoints import PDS_ENDPOINT, PDS_USERNAME_EXTENSION

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
        blob_response = self.uploadBlob(profile_pic_url)
        profile_record = models.AppBskyActorProfile.Record(
            display_name=display_name,
            description=description + " \n\n\n" + "This is an automated Substack account of " + self.url + "\n" + "Discover more at: @skystack.xyz",
            avatar=blob_response.blob,
        )
        # Update the profile using the profile record namespace
        profile_response = self.client.app.bsky.actor.profile.create(
            repo=self.client.me.did,
            record=profile_record,
            rkey='self'
        )
        return profile_response

    def createEmbededLinkPost(self, title, subtitle, link, thumbnail_url, post_date):
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

        # Create post record with custom date  
        post_record = models.AppBskyFeedPost.Record(  
            text=title + ' • ' + subtitle,  
            created_at=post_date,  # ISO format with Z suffix  
            embed=external_embed
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
        follow_response = self.client.follow(follow_user)
        return follow_response

    def uploadBlob(self, image_url):
        """
        Downloads an image from a URL and uploads it as a blob to the PDS.

        Args:
            image_url (str): The URL of the image to upload.

        Returns:
            The response from the server containing the uploaded blob's reference.
        """
        # Download image from URL and upload as blob
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = BytesIO(response.content).read()

        # Check if image size is greater than 500KB (512000 bytes)
        if len(image_data) > 512000:
            img = Image.open(BytesIO(image_data))
            img_format = img.format if img.format else 'JPEG'
            # Start with quality 85, reduce by 5, but if still too large at quality=20, resize image
            quality = 85
            buffer = BytesIO()
            while True:
                buffer.seek(0)
                buffer.truncate()
                img.save(buffer, format=img_format, quality=quality, optimize=True)
                if buffer.tell() <= 512000:
                    break
                if quality > 20:
                    quality -= 5
                else:
                    # If quality is already low, start resizing
                    width, height = img.size
                    # Reduce size by 10% each iteration
                    new_width = int(width * 0.9)
                    new_height = int(height * 0.9)
                    if new_width < 1 or new_height < 1:
                        # If image is too small, break to avoid errors
                        break
                    img = img.resize((new_width, new_height), Image.LANCZOS)
            image_data = buffer.getvalue()

        blob_response = self.client.com.atproto.repo.upload_blob(image_data)
        return blob_response
