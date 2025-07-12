import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.user import User

def test_get_newsletter_admin():
    user = User("https://hasir.substack.com/")
    admin = user.getNewsletterAdmin()
    assert admin == {
        'id': 49600103,
        'name': "Hasir Mushtaq",
        'admin_handle': "hasir"
    }

def test_get_newsletter_users():
    user = User("https://hasir.substack.com/")
    users = user.getNewsletterUsers()
    assert users == [
        {
            'id': 49600103,
            'name': "Hasir Mushtaq",
            'handle': "hasir"
        }
    ] 