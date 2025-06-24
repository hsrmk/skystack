import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.newsletter import Newsletter

# Dummy data for getPublication
DUMMY_PROFILE_DATA = {
    "id": 2067309,
    "name": "Bari Weiss",
    "handle": "bariweiss",
    "publicationUsers": [
        {
            "id": 23750,
            "user_id": 2067309,
            "publication_id": 260347,
            "role": "admin",
            "public": True,
            "is_primary": False,
            "publication": {
                "id": 260347,
                "name": "The Free Press",
                "subdomain": "bariweiss",
                "custom_domain": "www.thefp.com",
                "hero_text": "A new media company built on the ideals that were once the bedrock of American journalism.",
                "logo_url": "https://bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com/public/images/9cb7f208-a15c-46a8-a040-7e7a2150def9_1280x1280.png"
            }
        }
    ]
}

# Dummy data for getRecommendedPublications
DUMMY_RECOMMENDATIONS_DATA = [
    {
        "id": 4841618,
        "recommended_publication_id": 3575926,
        "recommending_publication_id": 35345,
        "recommendedPublication": {
            "id": 3575926,
            "name": "Green Tape",
            "subdomain": "greentapeblog",
            "custom_domain": "www.greentape.pub",
            "author": {
                "id": 75852873,
                "name": "Thomas Hochman",
                "handle": "thomashochman"
            }
        }
    }
]

# Dummy data for getPosts
DUMMY_POSTS_DATA = [
    {
        "id": 41997751,
        "publication_id": 508241,
        "title": "Coming soon",
        "post_date": "2021-09-30T07:47:35.496Z",
        "canonical_url": "https://hasir.substack.com/p/coming-soon",
        "subtitle": None,
        "cover_image": None
    }
]

NEWSLETTER_URL = "https://www.thefp.com/"
TEST_POSTS_URL = "https://hasir.substack.com"

@patch('utils.newsletter.fetch_json', return_value=DUMMY_PROFILE_DATA)
def test_get_publication(mock_fetch):
    newsletter = Newsletter(NEWSLETTER_URL)
    pub = newsletter.getPublication("bariweiss")
    assert pub == {
        'publication_id': 260347,
        'name': 'The Free Press',
        'subdomain': 'bariweiss',
        'custom_domain': 'www.thefp.com',
        'hero_text': 'A new media company built on the ideals that were once the bedrock of American journalism.',
        'logo_url': 'https://bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com/public/images/9cb7f208-a15c-46a8-a040-7e7a2150def9_1280x1280.png'
    }

@patch('utils.newsletter.fetch_json', return_value=DUMMY_RECOMMENDATIONS_DATA)
def test_get_recommended_publications(mock_fetch):
    newsletter = Newsletter(NEWSLETTER_URL)
    rec_newsletters, rec_users = newsletter.getRecommendedPublications(3575926)
    assert rec_newsletters == [
        {
            'publication_id': 3575926,
            'name': 'Green Tape',
            'subdomain': 'greentapeblog',
            'custom_domain': 'www.greentape.pub'
        }
    ]
    assert rec_users == [
        {
            'id': 75852873,
            'name': 'Thomas Hochman',
            'handle': 'thomashochman'
        }
    ]

@patch('utils.newsletter.fetch_json', return_value=DUMMY_POSTS_DATA)
def test_get_posts(mock_fetch):
    newsletter = Newsletter(TEST_POSTS_URL)
    result = newsletter.getPosts(limit=1)
    assert result['postsArray'] == [
        {
            'title': 'Coming soon',
            'subtitle': None,
            'link': 'https://hasir.substack.com/p/coming-soon',
            'id': 41997751,
            "thumbnail_url": None
        }
    ]
    assert result['numberOfPosts'] == 1
    assert result['lastPostTime'] == '2021-09-30T07:47:35.496Z'
    assert result['postFrequency'] is None

if __name__ == '__main__':
    pytest.main([__file__])