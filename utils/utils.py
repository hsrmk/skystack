import requests
import feedparser
import html
from datetime import datetime, timezone

from .endpoints import RSS_ENDPOINT

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
    1. [[title, subtitle, link, thumbnail_url, post_date], ...] for entries newer than lastBuildDate
    2. [published, ...] for those entries
    """
    feed_url = url + RSS_ENDPOINT
    feed = feedparser.parse(feed_url)
    lastBuildDate = datetime.fromisoformat(lastBuildDate.replace("Z", "+00:00"))

    items = []
    post_dates_list = []

    for entry in feed.entries:
        # entry.published_parsed is a time.struct_time
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            entry_time = datetime(*entry.published_parsed[:6])
            # Make entry_time timezone-aware if naive
            if entry_time.tzinfo is None or entry_time.tzinfo.utcoffset(entry_time) is None:
                entry_time = entry_time.replace(tzinfo=timezone.utc)
            if lastBuildDate.tzinfo is None or lastBuildDate.tzinfo.utcoffset(lastBuildDate) is None:
                lastBuildDate = lastBuildDate.replace(tzinfo=timezone.utc)
            
            if entry_time > lastBuildDate:
                post_date = entry_time.isoformat().replace('+00:00', 'Z')

                item = {
                    "title": html.unescape(entry.title),
                    "subtitle": html.unescape(entry.summary),
                    "link": entry.link,
                    "post_date": post_date
                }
                
                # Set thumbnail_url to None by default
                thumbnail_url = None
                # Add thumbnail URL if enclosure exists in links
                if hasattr(entry, 'links') and entry.links:
                    for link in entry.links:
                        if link.get('rel') == 'enclosure' and link.get('type', '').startswith('image/'):
                            thumbnail_url = link['href']
                            break
                        
                item["thumbnail_url"] = thumbnail_url
                items.append(item)
                post_dates_list.append(post_date)
            else:
                break

    return items, post_dates_list

def getPostFreqDetails(numberOfPosts, postFrequency, post_dates_list):
    """
    Calculate post frequency details by combining existing data with new published list.
    
    Args:
        numberOfPosts (int): Current number of posts
        postFrequency (float): Current average post frequency
        publishedList (list): List of published times (oldest to latest). eg: ['Fri, 20 Jun 2020 10:04:16 GMT']
    
    Returns:
        dict: Updated post frequency details
    """
    # Update number of posts
    numberOfPosts += len(post_dates_list)
    
    # Update last post time (use the latest from publishedList)
    if post_dates_list:
        lastBuildDate = post_dates_list[0]
    
    # Calculate new post frequency
    if len(post_dates_list) > 1:
        # Convert published times to datetime objects
        post_dates = [datetime.fromisoformat(pub.replace('Z', '+00:00')) for pub in post_dates_list]
        
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
        'lastBuildDate': lastBuildDate,
        'postFrequency': new_postFrequency
    }