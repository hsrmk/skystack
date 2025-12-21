import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import admin
from utils.atproto_user import AtprotoUser

def test_admin_and_atproto_user():
    # Ensure required environment variables are set for the test
    # assert os.environ.get("USER_LOGIN_PASS"), "USER_LOGIN_PASS must be set in environment for this test."
    # assert os.environ.get("ADMIN_PASS"), "ADMIN_PASS must be set in environment for this test."

    username = "runningtests"
    # Create account
    # create_response = admin.create_account(username)
    # assert hasattr(create_response, "handle"), "create_account response should have a 'handle' attribute."
    # assert create_response.handle == "runningtests.skystack.xyz", f"Expected handle to be 'runningtests.skystack.xyz', got {getattr(create_response, 'handle', None)}"

    # Use AtprotoUser to test profile and post features
    user = AtprotoUser(username, "https://hasir.substack.com/")

    # Test updateProfileDetails
    profile_response = user.updateProfileDetails(
        display_name="Test User",
        description="Test description",
        profile_pic_url="https://placehold.co/200x200.png"
    )
    # assert profile_response is not None, "updateProfileDetails should return a response."

    # Test createEmbededLinkPost
    # post_response = user.createEmbededLinkPost(
    #     title="Test Post",
    #     subtitle="Test Subtitle",
    #     link="https://example.com",
    #     thumbnail_url="https://placehold.co/200x200.png",
    #     post_date="2024-06-01T12:00:00Z",
    #     labels=['reaction_count:149', 'comment_count:109', 'child_comment_count:33']
    # )
    # assert post_response is not None, "createEmbededLinkPost should return a response."

    # Delete account
    # delete_response = admin.delete_account(username)
    # assert delete_response is True, "delete_account should return True." 


test_admin_and_atproto_user()