import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.admin import create_account

def test_create_account():
    # Dummy data for testing
    handle = 'dummyuser3.skystack.xyz'
    email = 'dummyuser+3@example.com'
    password = 'DummyPassword123!'

    try:
        response = create_account(handle, email, password)
        print('Account creation response:', response)
    except Exception as e:
        print('Error during account creation:', e)

if __name__ == '__main__':
    test_create_account() 