import requests
import feedparser


def fetch_json(url):
    """
    General fetch function to get JSON data from a URL.
    Raises an exception if the request fails or the response is not JSON.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def getLatestRSSItems(url, lastPostTime=None):
    """
    Fetch and print all entries from the RSS feed at url + '/feed'.
    For now, prints all entries and their details for inspection.
    """
    feed_url = url.rstrip('/') + '/feed'
    feed = feedparser.parse(feed_url)
    print(f"Feed Title: {feed.feed.get('title')}")
    print(f"Feed: {feed.feed}")
    # for entry in feed.entries:
    #     print("--- Entry ---")
    #     for k, v in entry.items():
    #         print(f"{k}: {v}")
    #     print() 