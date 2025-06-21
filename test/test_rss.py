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

    # Mock feedparser.parse to return our entry
    mock_parse.return_value.entries = [entry]

    url = 'https://hasir.substack.com/'
    date_str = 'Fri, 20 Jun 2020 10:04:16 GMT'
    lastBuildDate = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')

    items, published = getLatestRSSItems(url, lastBuildDate)

    assert items == [{
        'title': 'Coming soon',
        'subtitle': 'This is Hasir’s Newsletter, a newsletter about Writing, tech, philosophy and more tech.',
        'link': 'https://hasir.substack.com/p/coming-soon'
    }]
    assert published == ['Thu, 30 Sep 2021 07:47:35 GMT']

if __name__ == '__main__':
    pytest.main([__file__])
