import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.utils import getLatestRSSItems

def test_get_latest_rss_items():
    # This will print the entries for manual inspection
    getLatestRSSItems(url='https://thefp.com', lastPostTime=None)

if __name__ == '__main__':
    test_get_latest_rss_items()
