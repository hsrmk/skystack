import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.newsletter import Newsletter


def test_get_publication():
    newsletter = Newsletter("https://hasir.substack.com/")
    pub = newsletter.getPublication('hasir')
    assert pub == {
        'publication_id': 508241,
        'name': "Hasir’s Newsletter",
        'subdomain': "hasir",
        'custom_domain': None,
        'hero_text': "Writing, tech, philosophy and more tech",
        'logo_url': None
    }

def test_get_recommended_publications():
    newsletter = Newsletter("https://hasir.substack.com/")
    rec_newsletters, rec_users = newsletter.getRecommendedPublications(508241)
    assert rec_newsletters == [
        {
            'publication_id': 11029,
            'name': "Remains of the Day",
            'subdomain': "eugenewei",
            'custom_domain': None
        }
    ]
    assert rec_users == [
        {
            'id': 43916,
            'name': "Eugene Wei",
            'handle': "eugenewei"
        }
    ]

def test_get_posts():
    newsletter = Newsletter("https://hasir.substack.com/")
    posts = newsletter.getPosts()

    assert posts['postsArray'] == [
        {
            'title': "Coming Sooner(?)",
            'subtitle': "Maybe",
            'link': "https://hasir.substack.com/p/coming-sooner",
            'id': 167107842,
            'thumbnail_url': None,
            'post_date': "2025-06-29T15:16:29.827Z"
        },
        {
            'title': "Coming soon",
            'subtitle': "",
            'link': "https://hasir.substack.com/p/coming-soon",
            'id': 41997751,
            'thumbnail_url': "https://substackcdn.com/image/fetch/$s_!LMqd!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2a468181-7d79-4f0f-977c-c157ee482072_1000x1000.heic",
            'post_date': "2021-09-30T07:47:35.496Z"
        }
    ]
    assert posts['numberOfPosts'] == 2
    assert posts['lastBuildDate'] == "2025-06-29T15:16:29.827Z"
    assert posts['postFrequency'] == 1368.3117399421296

def test_get_newsletter_data_since_last_build():
    newsletter = Newsletter("https://hasir.substack.com/")
    result = newsletter.getNewsletterDataSinceLastBuild("2021-10-30T07:47:35.496Z", 1, 1)
    
    assert result == {
        'post_items': [
            {
                'title': 'Coming Sooner(?)',
                'subtitle': 'Maybe',
                'link': 'https://hasir.substack.com/p/coming-sooner',
                'post_date': '2025-06-29T15:16:29Z',
                'thumbnail_url': None
            }
        ],
        'number_of_posts': 2,
        'last_build_date': '2025-06-29T15:16:29Z',
        'post_frequency': 1
    }