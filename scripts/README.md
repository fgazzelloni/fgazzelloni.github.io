# Automated Podcast Fetching System

This directory contains the automation scripts and workflows for fetching podcast episodes from Spotify and creating properly formatted Quarto posts.

## Overview

The system automatically:
- Fetches podcast episodes from Spotify RSS feed (Show ID: `43CSCODQFQkZ05u3Up5OD6`)
- Checks for new episodes not yet added to the site
- Creates formatted Quarto markdown files for each new episode
- Downloads episode thumbnail images
- Commits and pushes changes to the repository

## Components

### 1. Python Script (`fetch_podcasts.py`)

The main script that handles episode fetching and post generation.

**Features:**
- Fetches episodes from Spotify RSS feed
- Maintains state to track processed episodes (`.podcast_state.json`)
- Generates URL-friendly slugs for episodes
- Creates properly formatted `index.qmd` files with frontmatter
- Downloads episode thumbnails as `featured.png`
- Extracts episode metadata (title, date, description, embed URL)
- Automatically generates key topics from episode descriptions

**Usage:**
```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Run the script
python scripts/fetch_podcasts.py
```

### 2. GitHub Actions Workflow (`../.github/workflows/fetch-podcasts.yml`)

Automated workflow that runs daily to fetch and add new podcast episodes.

**Schedule:**
- Runs daily at midnight UTC
- Can be triggered manually via GitHub Actions UI

**Workflow Steps:**
1. Checks out the repository
2. Sets up Python 3.11
3. Installs dependencies from `requirements.txt`
4. Runs the podcast fetching script
5. Commits and pushes new episode files (if any)

**Permissions:**
- `contents: write` - Required to commit and push changes

## Configuration

### Spotify Show ID

The Spotify Show ID is configured in `fetch_podcasts.py`:
```python
SPOTIFY_SHOW_ID = "43CSCODQFQkZ05u3Up5OD6"
```

### RSS Feed

The script uses the Spotify RSS feed URL:
```
https://anchor.fm/s/{SHOW_ID}/podcast/rss
```

No API credentials are required as the script uses the public RSS feed.

## File Structure

New episodes are created in the following structure:

```
content/podcasts/
└── posts/
    └── [episode-slug]/
        ├── index.qmd          # Episode post with frontmatter
        └── featured.png       # Episode thumbnail (if available)
```

### Example `index.qmd` Format

```yaml
---
title: "Episode Title"
date: '2026-01-08'
image: featured.png
slug: podcast-episode-slug
toc: true
categories:
  - health metrics
  - data science
summary: "Episode summary/description"
execute: 
  eval: false
---

<iframe data-testid="embed-iframe" style="border-radius:12px" 
  src="https://open.spotify.com/embed/episode/..." 
  width="624" height="351" frameBorder="0" 
  allowfullscreen="" 
  allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
  loading="lazy"></iframe>

## Episode Overview

[Episode description]

## Key Topics Discussed

- Topic 1
- Topic 2
- Topic 3
```

## State Management

The script maintains a state file at `scripts/.podcast_state.json` to track processed episodes:

```json
{
  "processed_episodes": [
    "episode-guid-1",
    "episode-guid-2"
  ],
  "last_run": "2026-02-11T12:00:00.000000"
}
```

This prevents duplicate posts and ensures only new episodes are added.

## Error Handling

The script includes error handling for:
- Network failures when fetching RSS feed
- Parsing errors in RSS feed XML
- Image download failures (non-critical, continues processing)
- File system errors when creating posts

Errors are logged to stdout for debugging in GitHub Actions logs.

## Testing Locally

To test the script locally:

```bash
# Navigate to repository root
cd /path/to/fgazzelloni.github.io

# Install dependencies
pip install -r scripts/requirements.txt

# Run the script
python scripts/fetch_podcasts.py

# Check the generated posts
ls -la content/podcasts/posts/

# Preview with Quarto
quarto preview
```

## Manual Triggering

To manually trigger the workflow:

1. Go to the repository on GitHub
2. Click on "Actions" tab
3. Select "Fetch Podcast Episodes" workflow
4. Click "Run workflow" button
5. Click the green "Run workflow" button in the dialog

## Troubleshooting

### No new episodes detected

- Check if episodes are already in `scripts/.podcast_state.json`
- Verify RSS feed is accessible: `https://anchor.fm/s/43CSCODQFQkZ05u3Up5OD6/podcast/rss`
- Check GitHub Actions logs for errors

### Image downloads failing

- This is non-critical; the post will be created without a featured image
- Check if the RSS feed includes image URLs in `<itunes:image>` tags

### Workflow not running

- Verify the workflow file is in `.github/workflows/`
- Check GitHub Actions are enabled for the repository
- Ensure the repository has `contents: write` permission

## Dependencies

- Python 3.11+
- `requests` library for HTTP requests
- Standard library modules: `xml.etree.ElementTree`, `json`, `re`, `datetime`, `pathlib`

## Future Enhancements

Potential improvements:
- Use Spotify Web API for richer metadata
- Add support for episode chapters
- Generate AI-powered summaries using episode transcripts
- Support multiple podcast shows
- Add email notifications for new episodes
- Include episode duration in metadata
