from atproto import Client, models
import base64
import os
from .endpoints import PDS_ENDPOINT

def create_invite_code(client, use_count: int = 1, for_account: str = None):
    data = models.ComAtprotoServerCreateInviteCode.Data(
        use_count=use_count,
        for_account=for_account
    )

    # Get admin credentials from environment variables
    admin_pass = os.environ.get("ADMIN_PASS")
    if not admin_pass:
        raise ValueError("ADMIN_PASS environment variables must be set.")
    
    admin_auth = base64.b64encode(f"admin:{admin_pass}".encode()).decode()
    headers = {
        "Authorization": f"Basic {admin_auth}",
        "Content-Type": "application/json"
    }
    response = client.com.atproto.server.create_invite_code(data, headers=headers)
    return response.code

def create_account(handle: str, email: str, password: str, invite_code: str = None):
    client = Client(PDS_ENDPOINT)
    if not invite_code:
        invite_code = create_invite_code(client)

    data = models.ComAtprotoServerCreateAccount.Data(
        handle=handle,
        email=email,
        password=password,
        invite_code=invite_code
    )
    response = client.com.atproto.server.create_account(data)
    return response