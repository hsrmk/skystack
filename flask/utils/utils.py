import os
import requests
import feedparser
import html
from datetime import datetime, timezone

from utils.endpoints import RSS_ENDPOINT, SUBSTACK_CDN, OG_CARD_ENDPOINT

def is_localhost():
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
    return ENVIRONMENT == 'local'

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
                            thumbnail_url = normalize_substack_image_url(link['href'], url, isPost=True)
                            break
                        
                item["thumbnail_url"] = thumbnail_url
                items.append(item)
                post_dates_list.append(post_date)
            else:
                break

    return items, post_dates_list

def getPostFreqDetails(numberOfPosts, postFrequency, lastBuildDate, post_dates_list):
    """
    Calculate post frequency details using an incremental running average.
    
    Args:
        numberOfPosts (int): Current number of posts
        postFrequency (float): Current average post frequency (in days)
        lastBuildDate (str): '2025-07-04T14:02:13Z' (ISO String with Z suffix)
        post_dates_list (list): List of published times (latest to oldest). eg: ['2025-07-04T14:02:13Z'] (ISO String with Z suffix)
    
    Returns:
        dict: Updated post frequency details
    """
    # Update number of posts
    newNumberOfPosts = numberOfPosts + len(post_dates_list)
    
    # Update last post time (use the latest from publishedList)
    if post_dates_list:
        lastBuildDate = post_dates_list[0]
    
    # Calculate new post frequency using incremental running average
    if len(post_dates_list) > 0:
        # Convert published times to datetime objects
        post_dates = [datetime.fromisoformat(pub.replace('Z', '+00:00')) for pub in post_dates_list]
        
        # If only one new post, augment with lastBuildDate to calculate frequency
        if len(post_dates_list) == 1:
            old_last_build = datetime.fromisoformat(lastBuildDate.replace('Z', '+00:00'))
            # Insert lastBuildDate at the end to create a time series
            post_dates.append(old_last_build)
        
        # Calculate time differences in days between consecutive posts
        time_diffs = [
            (post_dates[i] - post_dates[i+1]).total_seconds() / 86400.0
            for i in range(len(post_dates)-1)
        ]
        
        # Calculate average frequency from new posts
        new_posts_avg_frequency = sum(time_diffs) / len(time_diffs)
        
        # Calculate incremental running average
        if postFrequency is not None and numberOfPosts > 0:
            # Weighted average: (old_freq * old_count + new_freq * new_count) / total_count
            # For single post case, we use 1 as the weight since we're only adding one new data point
            weight = len(post_dates_list) if len(post_dates_list) > 1 else 1
            new_postFrequency = (postFrequency * numberOfPosts + new_posts_avg_frequency * weight) / newNumberOfPosts
        else:
            # If no previous data, use the new average
            new_postFrequency = new_posts_avg_frequency
    else:
        # If no new posts, keep the previous frequency
        new_postFrequency = postFrequency
    
    return {
        'numberOfPosts': newNumberOfPosts,
        'lastBuildDate': lastBuildDate,
        'postFrequency': new_postFrequency
    }

def normalize_substack_image_url(image_url, url, isPost=False):
    """
    If the image_url is already from substackcdn.com, return as is.
    Otherwise, wrap it with the substackcdn.com image fetch URL.
    """
    if image_url is None and isPost:
        return url + OG_CARD_ENDPOINT
    elif image_url is None:
        return None
    # Accept both https://substackcdn.com and https://www.substackcdn.com
    if image_url.startswith("https://substackcdn.com/") or image_url.startswith("https://www.substackcdn.com/"):
        return image_url
    
    return SUBSTACK_CDN + image_url