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

def create_account(username: str):
    client = Client(PDS_ENDPOINT)
    if not invite_code:
        invite_code = create_invite_code(client)
    
    user_login_pass = os.environ.get("USER_LOGIN_PASS")
    if not user_login_pass:
        raise ValueError("USER_LOGIN_PASS environment variables must be set.")

    data = models.ComAtprotoServerCreateAccount.Data(
        handle=username + '.skystack.xyz',
        email='skystack17+' + username + '@gmail.com',
        password=username + user_login_pass,
        invite_code=invite_code
    )
    response = client.com.atproto.server.create_account(data)
    return response


def delete_account(username: str):
    # Get admin credentials from environment variables
    admin_pass = os.environ.get("ADMIN_PASS")
    if not admin_pass:
        raise ValueError("ADMIN_PASS environment variables must be set.")

    client = Client(PDS_ENDPOINT)
    client.login('admin', admin_pass)
    
    # Resolve handle to DID  
    response = client.resolve_handle(username + '.skystack.xyz')  

    # Delete account as administrator  
    client.com.atproto.admin.delete_account(
        models.ComAtprotoAdminDeleteAccount.Data(
            did=response.did
        )
    )