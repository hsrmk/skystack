import sys
import os
import datetime
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.utils import getLatestRSSItems

@patch('feedparser.parse')
def test_getLatestRSSItems(mock_parse):
    # Prepare mock feed entry
    entry = MagicMock()
    entry.title = 'Coming soon'
    entry.summary = 'This is Hasir’s Newsletter, a newsletter about Writing, tech, philosophy and more tech.'
    entry.link = 'https://hasir.substack.com/p/coming-soon'
    entry.published = 'Thu, 30 Sep 2021 07:47:35 GMT'
    entry.published_parsed = datetime.datetime(2021, 9, 30, 7, 47, 35).timetuple()
    entry.thumbnail_url = 'https://substackcdn.com/image/fetch/$s_!LMqd!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2a468181-7d79-4f0f-977c-c157ee482072_1000x1000.heic'

    # Mock feedparser.parse to return our entry
    mock_parse.return_value.entries = [entry]

    url = 'https://hasir.substack.com/'
    date_str = 'Fri, 20 Jun 2020 10:04:16 GMT'
    lastBuildDate = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')

    items, published = getLatestRSSItems(url, lastBuildDate)
    print(items)
    assert items == [{
        'title': 'Coming soon',
        'subtitle': 'This is Hasir’s Newsletter, a newsletter about Writing, tech, philosophy and more tech.',
        'link': 'https://hasir.substack.com/p/coming-soon',
        'thumbnail_url': 'https://substackcdn.com/image/fetch/$s_!LMqd!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2a468181-7d79-4f0f-977c-c157ee482072_1000x1000.heic'
    }]
    assert published == ['Thu, 30 Sep 2021 07:47:35 GMT']

if __name__ == '__main__':
    pytest.main([__file__])
