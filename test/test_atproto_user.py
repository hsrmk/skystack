import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.atproto_user import updateProfileDetails, createPost

def test_update_profile():
    # Dummy data for testing
    username = 'testuser'
    display_name = 'Test User'
    description = 'You just keep on trying till you run out of cake'
    profile_pic_url = 'https://substackcdn.com/image/fetch/$s_!E3kF!,w_256,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fhasir.substack.com%2Fimg%2Fsubstack.png'

    updateProfileDetails(display_name, username, description, profile_pic_url)

def test_posting():
    # Dummy data for testing
    username = 'testuser'
    title = 'In The Long Run, We\'re All Dad'
    subtitle = 'twoo'
    link = 'https://www.astralcodexten.com/p/still-alive'

    try:
        response = createPost(username, title, subtitle, link)
        print('Account creation response:', response)
    except Exception as e:
        print('Error during account creation:', e)

if __name__ == '__main__':
    test_posting() 