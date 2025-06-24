from atproto import Client, models
import base64
import os
from .endpoints import PDS_ENDPOINT, PDS_USERNAME_EXTENSION

def create_invite_code(client, use_count: int = 1, for_account: str = None):
    data = models.ComAtprotoServerCreateInviteCode.Data(
        use_count=use_count,
        for_account=for_account
    )

    headers = get_admin_headers()
    response = client.com.atproto.server.create_invite_code(data, headers=headers)
    return response.code

def create_account(username: str):
    client = Client(PDS_ENDPOINT)
    invite_code = create_invite_code(client)
    
    user_login_pass = os.environ.get("USER_LOGIN_PASS")
    if not user_login_pass:
        raise ValueError("USER_LOGIN_PASS environment variables must be set.")

    data = models.ComAtprotoServerCreateAccount.Data(
        handle=username + PDS_USERNAME_EXTENSION,
        email='skystack17+' + username + '@gmail.com',
        password=username + user_login_pass,
        invite_code=invite_code
    )
    response = client.com.atproto.server.create_account(data)
    return response


def delete_account(username: str):
    client = Client(PDS_ENDPOINT)
    
    # Resolve handle to DID
    user_data = client.resolve_handle(username + PDS_USERNAME_EXTENSION)  
    delete_account_data = models.ComAtprotoAdminDeleteAccount.Data(did=user_data.did)

    # Delete account as administrator
    headers = get_admin_headers()
    response = client.com.atproto.admin.delete_account(delete_account_data, headers=headers)
    return response       

def get_admin_headers():
    # Get admin credentials from environment variables
    admin_pass = os.environ.get("ADMIN_PASS")
    if not admin_pass:
        raise ValueError("ADMIN_PASS environment variables must be set.")
    
    admin_auth = base64.b64encode(f"admin:{admin_pass}".encode()).decode()
    headers = {
        "Authorization": f"Basic {admin_auth}",
        "Content-Type": "application/json"
    }

    return headers