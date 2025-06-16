import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.user import User

# Dummy data as provided
DUMMY_DATA = [
    {
        "id": 2067309,
        "name": "Bari Weiss",
        "bio": "Writer, editor and author of \"How to Fight Anti-Semitism.\"",
        "photo_url": "https://bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com/public/images/dcefd577-0400-48d6-96c8-cde128a32ebe_6000x4000.jpeg",
        "profile_set_up_at": "2021-04-16T16:55:48.489Z",
        "handle": "bariweiss",
        "is_byline_only": False,
        "bestseller_tier": None
    }
]

NEWSLETTER_URL = "https://www.thefp.com/"

@patch('utils.user.fetch_json', return_value=DUMMY_DATA)
def test_get_newsletter_admin(mock_fetch):
    user = User(NEWSLETTER_URL)
    admin = user.getNewsletterAdmin()
    assert admin == {
        'id': 2067309,
        'name': 'Bari Weiss',
        'admin_handle': 'bariweiss'
    }

@patch('utils.user.fetch_json', return_value=DUMMY_DATA)
def test_get_newsletter_users_limit_1(mock_fetch):
    user = User(NEWSLETTER_URL)
    users = user.getNewsletterUsers(limit=1)
    assert users == [
        {
            'id': 2067309,
            'name': 'Bari Weiss',
            'handle': 'bariweiss'
        }
    ]

if __name__ == '__main__':
    pytest.main([__file__]) 