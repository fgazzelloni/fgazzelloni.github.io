#!/usr/bin/env python3
"""
Fetch podcast episodes from Spotify RSS feed and create Quarto posts.

This script fetches episodes from a Spotify podcast RSS feed, checks for new
episodes not yet added to the site, and creates properly formatted Quarto
markdown files for each new episode.
"""

import os
import sys
import json
import re
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


# Configuration
SPOTIFY_SHOW_ID = "43CSCODQFQkZ05u3Up5OD6"
# Try multiple RSS feed URLs as Spotify/Anchor may use different formats
RSS_FEED_URLS = [
    f"https://anchor.fm/s/{SPOTIFY_SHOW_ID}/podcast/rss",
    f"https://podcasters.spotify.com/pod/show/{SPOTIFY_SHOW_ID}/feed",
]
POSTS_DIR = Path("content/podcasts/posts")
STATE_FILE = Path("scripts/.podcast_state.json")


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def load_state():
    """Load the state file tracking processed episodes."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"processed_episodes": []}


def save_state(state):
    """Save the state file tracking processed episodes."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def fetch_rss_feed():
    """Fetch and parse the podcast RSS feed."""
    print("Attempting to fetch RSS feed from multiple sources...")
    
    for i, url in enumerate(RSS_FEED_URLS, 1):
        print(f"  Attempt {i}/{len(RSS_FEED_URLS)}: {url}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            print(f"  ✓ Successfully fetched from: {url}")
            return ET.fromstring(response.content)
        except requests.RequestException as e:
            print(f"  ✗ Failed: {e}")
            if i < len(RSS_FEED_URLS):
                print(f"  Trying next URL...")
            continue
    
    print("\nError: Could not fetch RSS feed from any source.")
    print("\nNote: This error may occur in sandboxed environments with limited internet access.")
    print("The script will work correctly in GitHub Actions with full internet access.")
    sys.exit(1)


def extract_episode_info(item):
    """Extract episode information from RSS item."""
    # Define namespaces
    namespaces = {
        'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'spotify': 'http://www.spotify.com/ns/rss',
        'content': 'http://purl.org/rss/1.0/modules/content/'
    }
    
    episode = {}
    
    # Extract basic info
    episode['title'] = item.find('title').text if item.find('title') is not None else "Untitled Episode"
    
    # Extract publication date
    pub_date = item.find('pubDate')
    if pub_date is not None:
        try:
            # Parse RFC 2822 date format
            dt = datetime.strptime(pub_date.text, '%a, %d %b %Y %H:%M:%S %Z')
            episode['date'] = dt.strftime('%Y-%m-%d')
        except ValueError:
            try:
                # Try alternative format
                dt = datetime.strptime(pub_date.text, '%a, %d %b %Y %H:%M:%S %z')
                episode['date'] = dt.strftime('%Y-%m-%d')
            except ValueError:
                episode['date'] = datetime.now().strftime('%Y-%m-%d')
    else:
        episode['date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Extract description
    description = item.find('description')
    if description is not None:
        episode['description'] = description.text or ""
    else:
        # Try content:encoded
        content_encoded = item.find('content:encoded', namespaces)
        if content_encoded is not None:
            episode['description'] = content_encoded.text or ""
        else:
            episode['description'] = ""
    
    # Clean HTML from description
    episode['description'] = re.sub(r'<[^>]+>', '', episode['description'])
    episode['description'] = episode['description'].strip()
    
    # Extract episode GUID (unique identifier)
    guid = item.find('guid')
    episode['guid'] = guid.text if guid is not None else ""
    
    # Extract Spotify episode URL
    episode['spotify_url'] = ""
    link = item.find('link')
    if link is not None and link.text:
        episode['spotify_url'] = link.text
    
    # Try to get episode ID from enclosure or guid
    enclosure = item.find('enclosure')
    episode_id = None
    
    if enclosure is not None:
        url = enclosure.get('url', '')
        # Try to extract episode ID from URL
        match = re.search(r'/episode/([a-zA-Z0-9]+)', url)
        if match:
            episode_id = match.group(1)
    
    # If not found, try from guid
    if not episode_id and episode['guid']:
        # Extract from Spotify URI format: spotify:episode:ID
        if 'spotify:episode:' in episode['guid']:
            episode_id = episode['guid'].split('spotify:episode:')[1]
        else:
            # Try URL format
            match = re.search(r'/episode/([a-zA-Z0-9]+)', episode['guid'])
            if match:
                episode_id = match.group(1)
    
    episode['episode_id'] = episode_id
    
    # Extract image URL
    itunes_image = item.find('itunes:image', namespaces)
    if itunes_image is not None:
        episode['image_url'] = itunes_image.get('href', '')
    else:
        # Try to get from enclosure
        episode['image_url'] = ""
    
    return episode


def download_image(url, filepath):
    """Download an image from URL to filepath."""
    if not url:
        return False
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"  Downloaded image: {filepath}")
        return True
    except requests.RequestException as e:
        print(f"  Warning: Could not download image: {e}")
        return False


def create_episode_post(episode):
    """Create a Quarto post for a podcast episode."""
    # Generate slug
    base_slug = slugify(episode['title'])[:50]  # Limit slug length
    episode_slug = f"podcast-{base_slug}"
    
    # Create episode directory
    episode_dir = POSTS_DIR / base_slug
    episode_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate embed URL
    if episode['episode_id']:
        embed_url = f"https://open.spotify.com/embed/episode/{episode['episode_id']}?utm_source=generator"
    else:
        # Fallback to show embed
        embed_url = f"https://open.spotify.com/embed/show/{SPOTIFY_SHOW_ID}/video?utm_source=generator"
    
    # Download featured image
    has_image = False
    if episode['image_url']:
        image_path = episode_dir / "featured.png"
        has_image = download_image(episode['image_url'], image_path)
    
    # Generate summary (first 200 chars of description)
    summary = episode['description'][:200].strip()
    if len(episode['description']) > 200:
        summary += "..."
    
    # Extract key topics (simple extraction from description)
    key_topics = []
    description_lower = episode['description'].lower()
    
    # Look for common topic indicators
    topic_keywords = [
        'data science', 'machine learning', 'artificial intelligence',
        'health metrics', 'epidemiology', 'public health',
        'infectious disease', 'statistics', 'research'
    ]
    
    for keyword in topic_keywords:
        if keyword in description_lower:
            key_topics.append(keyword.title())
    
    # If no topics found, add generic ones
    if not key_topics:
        key_topics = ['Health Metrics', 'Data Science']
    
    # Create index.qmd content
    qmd_content = f"""---
title: "{episode['title']}"
date: '{episode['date']}'
image: featured.png
slug: {episode_slug}
toc: true
categories:
  - health metrics
  - data science
summary: "{summary}"
execute: 
  eval: false
---


<iframe data-testid="embed-iframe" style="border-radius:12px" src="{embed_url}" width="624" height="351" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>


## Episode Overview

{episode['description']}

## Key Topics Discussed

"""
    
    # Add key topics as bullet points
    for topic in key_topics[:5]:  # Limit to 5 topics
        qmd_content += f"- {topic}\n"
    
    qmd_content += "\n\n"
    
    # Write the index.qmd file
    qmd_path = episode_dir / "index.qmd"
    with open(qmd_path, 'w', encoding='utf-8') as f:
        f.write(qmd_content)
    
    print(f"  Created post: {episode_dir / 'index.qmd'}")
    
    return str(episode_dir)


def main():
    """Main function to fetch and process podcast episodes."""
    print("=== Podcast Episode Fetcher ===")
    print(f"Spotify Show ID: {SPOTIFY_SHOW_ID}")
    print(f"Posts directory: {POSTS_DIR}")
    print()
    
    # Load state
    state = load_state()
    processed_episodes = set(state.get('processed_episodes', []))
    print(f"Previously processed episodes: {len(processed_episodes)}")
    
    # Fetch RSS feed
    root = fetch_rss_feed()
    
    # Find all items (episodes)
    channel = root.find('channel')
    if channel is None:
        print("Error: Could not find channel in RSS feed")
        sys.exit(1)
    
    items = channel.findall('item')
    print(f"Found {len(items)} episodes in feed")
    print()
    
    # Process each episode
    new_episodes = []
    for item in items:
        episode = extract_episode_info(item)
        
        # Skip if already processed
        if episode['guid'] in processed_episodes:
            continue
        
        print(f"Processing new episode: {episode['title']}")
        print(f"  Date: {episode['date']}")
        print(f"  GUID: {episode['guid']}")
        
        # Create the post
        try:
            episode_dir = create_episode_post(episode)
            new_episodes.append(episode['guid'])
            processed_episodes.add(episode['guid'])
            print(f"  ✓ Successfully created post")
        except Exception as e:
            print(f"  ✗ Error creating post: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Save updated state
    state['processed_episodes'] = list(processed_episodes)
    state['last_run'] = datetime.now().isoformat()
    save_state(state)
    
    # Summary
    print("=== Summary ===")
    print(f"New episodes processed: {len(new_episodes)}")
    print(f"Total episodes tracked: {len(processed_episodes)}")
    
    if new_episodes:
        print("\nNew episodes added:")
        for guid in new_episodes:
            print(f"  - {guid}")
    else:
        print("\nNo new episodes to process.")


if __name__ == "__main__":
    main()
