import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.atproto_user import AtprotoUser

def test_update_profile():
    # Dummy data for testing
    username = 'testuser'
    display_name = 'Test User'
    description = 'You just keep on trying till you run out of cake'
    profile_pic_url = 'https://substackcdn.com/image/fetch/$s_!E3kF!,w_256,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fhasir.substack.com%2Fimg%2Fsubstack.png'

    # updateProfileDetails(display_name, username, description, profile_pic_url)

def test_posting():
    # Dummy data for testing
    atproto_user = AtprotoUser('testuser')

    title = 'Why I don’t think AGI is right around the corner"'
    subtitle = 'Continual learning is a huge bottleneck'
    link = 'https://www.dwarkesh.com/p/timelines-june-2025'
    thumbnail_url = 'https://substackcdn.com/image/fetch/$s_!cAOq!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2a0dc7f9-1224-47b3-9508-d56bfd9fe14f_1029x562.jpeg'
    post_date = '2025-06-02T17:31:46.502Z'

    try:
        response = atproto_user.createPost(title, subtitle, link, thumbnail_url, post_date)
        print('Account creation response:', response)
    except Exception as e:
        print('Error during account creation:', e)

if __name__ == '__main__':
    test_posting() 