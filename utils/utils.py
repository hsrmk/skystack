import requests
import feedparser
import html
import datetime

def fetch_json(url):
    """
    General fetch function to get JSON data from a URL.
    Raises an exception if the request fails or the response is not JSON.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def getLatestRSSItems(url, lastBuildDate):
    """
    Fetches RSS feed and returns two arrays:
    1. [[title, subtitle, link], ...] for entries newer than lastBuildDate
    2. [published, ...] for those entries
    """
    feed_url = f"{url.rstrip('/')}/feed"
    feed = feedparser.parse(feed_url)

    items = []
    published_list = []

    for entry in feed.entries:
        # entry.published_parsed is a time.struct_time
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            entry_time = datetime.datetime(*entry.published_parsed[:6])
            if entry_time > lastBuildDate:
                items.append({
                    "title": entry.title,
                    "subtitle": html.unescape(entry.summary),
                    "link": entry.link
                })
                published_list.append(entry.published)
            else:
                break
        else:
            continue
    return items, published_list

def getPostFreqDetails(numberOfPosts, lastPostTime, postFrequency, publishedList):
    """
    Calculate post frequency details by combining existing data with new published list.
    
    Args:
        numberOfPosts (int): Current number of posts
        lastPostTime (str): Last post time in string format. eg: 'Fri, 20 Jun 2020 10:04:16 GMT'
        postFrequency (float): Current average post frequency
        publishedList (list): List of published times (oldest to latest). eg: ['Fri, 20 Jun 2020 10:04:16 GMT']
    
    Returns:
        dict: Updated post frequency details
    """
    # Update number of posts
    numberOfPosts += len(publishedList)
    
    # Update last post time (use the latest from publishedList)
    if publishedList:
        lastPostTime = publishedList[0]
    
    # Calculate new post frequency
    if len(publishedList) > 1:
        # Convert published times to datetime objects
        post_dates = [datetime.datetime.strptime(pub, '%a, %d %b %Y %H:%M:%S %Z') for pub in publishedList]
        
        # Calculate time differences in days
        time_diffs = [
            (post_dates[i] - post_dates[i+1]).total_seconds() / 86400.0
            for i in range(len(post_dates)-1)
        ]
        
        # Calculate new average frequency
        new_postFrequency = sum(time_diffs) / len(time_diffs)
        
        # If previous postFrequency exists, take a weighted average
        if postFrequency is not None:
            new_postFrequency = (postFrequency + new_postFrequency) / 2
    else:
        new_postFrequency = postFrequency
    
    return {
        'numberOfPosts': numberOfPosts,
        'lastPostTime': lastPostTime,
        'postFrequency': new_postFrequency
    }
