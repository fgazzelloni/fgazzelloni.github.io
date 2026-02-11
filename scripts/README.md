# Automated Spotify Podcast Fetching

This directory contains the automation system that fetches new podcast episodes from Spotify and creates properly formatted Quarto posts.

## Overview

The system consists of:
- **GitHub Actions Workflow** (`.github/workflows/fetch-podcasts.yml`) - Runs daily to check for new episodes
- **R Script** (`scripts/fetch-podcasts.R`) - Fetches episodes from Spotify API and creates post files

## Setup Instructions

### 1. Get Spotify API Credentials

To use the Spotify API, you need to create a Spotify application and get your credentials:

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the app details:
   - **App Name**: "Podcast Episode Fetcher" (or any name you prefer)
   - **App Description**: "Automated fetching of podcast episodes"
   - **Redirect URI**: `http://localhost:8888/callback` (required but not used)
   - Accept the terms and conditions
5. Click "Create"
6. On your app's dashboard, you'll see:
   - **Client ID** - Copy this value
   - **Client Secret** - Click "Show Client Secret" and copy this value

### 2. Configure GitHub Secrets

Add your Spotify credentials as GitHub repository secrets:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click "New repository secret"
4. Add the following secrets:
   - **Name**: `SPOTIFY_CLIENT_ID`  
     **Value**: [Your Client ID from Spotify]
   - **Name**: `SPOTIFY_CLIENT_SECRET`  
     **Value**: [Your Client Secret from Spotify]

### 3. Required R Packages

The script uses the following R packages (automatically installed by the workflow):

- `httr` - HTTP requests
- `jsonlite` - JSON parsing
- `spotifyr` - Spotify API wrapper
- `stringr` - String manipulation
- `glue` - String templating
- `fs` - File system operations

### 4. Configuration

The podcast show ID is configured in the R script. The default is:
```r
SHOW_ID <- "43CSCODQFQkZ05u3Up5OD6"
```

To change this to a different show:
1. Open `scripts/fetch-podcasts.R`
2. Update the `SHOW_ID` variable with your show's Spotify ID
3. To find a show ID, go to the show on Spotify web, the URL will be:
   `https://open.spotify.com/show/[SHOW_ID]`

## How It Works

### Automated Daily Runs

The GitHub Actions workflow runs automatically every day at midnight UTC. It:

1. Checks out the repository
2. Sets up R environment
3. Installs required packages
4. Runs the fetch script with Spotify credentials
5. Commits and pushes any new episodes found

### Manual Triggering

You can also manually trigger the workflow:

1. Go to **Actions** tab in your GitHub repository
2. Select "Fetch Spotify Podcasts" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

### Episode Processing

For each new episode, the script:

1. Fetches episode metadata from Spotify API
2. Generates a URL-friendly slug from the episode title
3. Checks if the episode already exists (by slug)
4. If new, creates a folder: `content/podcasts/posts/[slug]/`
5. Generates an `index.qmd` file with:
   - YAML frontmatter (title, date, categories, summary, etc.)
   - Spotify embed iframe
   - Episode overview section
   - Key topics section
6. Downloads the episode cover image as `featured.png`
7. Commits the new files to the repository

### Duplicate Prevention

The script checks existing episode folders and skips any that already exist, preventing duplicates.

## File Structure

After running, new episodes will be organized as:

```
content/podcasts/
├── index.qmd (listing page - automatically updates)
└── posts/
    ├── hmsidr/
    │   ├── index.qmd
    │   └── featured.png
    ├── [new-episode-1]/
    │   ├── index.qmd
    │   └── featured.png
    └── [new-episode-2]/
        ├── index.qmd
        └── featured.png
```

## Post Format

Each `index.qmd` file follows this format:

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
summary: "Episode description from Spotify"
execute: 
  eval: false
---

[Spotify embed iframe]

## Episode Overview

[Episode description]

## Key Topics Discussed

- [Automatically extracted topics]
```

## Troubleshooting

### Workflow Fails

1. **Check GitHub Actions logs**: Go to Actions tab and view the workflow run
2. **Verify secrets are set**: Ensure `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are configured
3. **Test API credentials**: Try authenticating manually with your credentials

### No New Episodes Added

This is normal if there are no new episodes since the last run. The script will output:
```
⊙ No new episodes to add.
```

### Authentication Errors

If you see authentication errors:
1. Verify your Spotify API credentials are correct
2. Make sure the app is not in "Development Mode" (which has user limits)
3. Check that the credentials in GitHub Secrets match your Spotify app

### Image Download Failures

If images fail to download but episodes are still created:
- This is not critical - the posts will be created without the `featured.png`
- Check the workflow logs for specific image URL errors
- Images can be added manually later if needed

## Testing Locally

To test the script locally before running in GitHub Actions:

1. Install R and required packages:
   ```r
   install.packages(c("httr", "jsonlite", "spotifyr", "stringr", "glue", "fs"))
   ```

2. Set environment variables:
   ```bash
   export SPOTIFY_CLIENT_ID="your_client_id"
   export SPOTIFY_CLIENT_SECRET="your_client_secret"
   ```

3. Run the script:
   ```bash
   Rscript scripts/fetch-podcasts.R
   ```

## Customization

### Categories

The script automatically extracts categories from episode descriptions. To customize:
- Edit the `extract_categories()` function in `scripts/fetch-podcasts.R`
- Add/modify the keywords list
- Change default categories

### Episode Limit

By default, the script fetches up to 50 episodes. To change this:
- Edit the `limit` parameter in the `get_show_episodes()` call
- Maximum is 50 per request (use pagination for more)

### Embed Style

To customize the Spotify embed iframe:
- Edit the iframe template in the `create_episode_post()` function
- Modify dimensions, style, or other attributes

## Support

For issues or questions:
1. Check the GitHub Actions workflow logs
2. Review the Spotify API documentation: https://developer.spotify.com/documentation/web-api
3. Check the spotifyr package documentation: https://github.com/charlie86/spotifyr
