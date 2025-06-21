from atproto import Client, models
import requests
from io import BytesIO
import os

from endpoints import PDS_ENDPOINT

def updateProfileDetails(display_name, username, description, profile_pic_url):
    user_login_pass = os.environ.get("USER_LOGIN_PASS")
    if not user_login_pass:
        raise ValueError("USER_LOGIN_PASS environment variables must be set.")
    
    # Initialize client and login
    client = Client(PDS_ENDPOINT)
    client.login(username + '.skystack.xyz', username + user_login_pass)
    print('Welcome,', client.app.bsky.actor.profile.get(client.me.did, 'self'))

    # Download image from URL and upload as blob
    response = requests.get(profile_pic_url)
    response.raise_for_status()
    image_data = BytesIO(response.content).read()
    blob_response = client.com.atproto.repo.upload_blob(image_data)

    profile_record = models.AppBskyActorProfile.Record(
        display_name=display_name,
        description=description,
        avatar=blob_response.blob,
    )
    # Update the profile using the profile record namespace  
    client.app.bsky.actor.profile.create(  
        repo=client.me.did,  
        record=profile_record
    )

updateProfileDetails()