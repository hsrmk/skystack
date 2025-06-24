import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.admin import create_account, delete_account

def test_create_account():
    # Dummy data for testing
    username = 'testuser'

    try:
        response = create_account(username)
        print('Account creation response:', response)
    except Exception as e:
        print('Error during account creation:', e)

if __name__ == '__main__':
    test_create_account() 