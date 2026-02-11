#!/usr/bin/env Rscript

# Fetch Podcast Episodes from RSS Feed and Create Quarto Posts
# This script fetches episodes from an RSS feed and creates
# properly formatted Quarto (.qmd) posts for each new episode.

library(httr)
library(xml2)
library(stringr)
library(glue)
library(fs)
library(magick)

# Configuration
RSS_FEED_URL <- "https://anchor.fm/s/10dab65b8/podcast/rss"
SHOW_ID <- "43CSCODQFQkZ05u3Up5OD6"  # For Spotify embeds
POSTS_DIR <- "content/podcasts/posts"

# Function to create URL-friendly slug from title
create_slug <- function(title) {
  slug <- title %>%
    tolower() %>%
    str_replace_all("[^a-z0-9\\s-]", "") %>%  # Remove special characters
    str_replace_all("\\s+", "-") %>%          # Replace spaces with hyphens
    str_replace_all("-+", "-") %>%             # Replace multiple hyphens with single
    str_trim() %>%                             # Trim whitespace
    str_remove("^-+") %>%                      # Remove leading hyphens
    str_remove("-+$")                          # Remove trailing hyphens
  
  # Validate slug has minimum length
  if (nchar(slug) < 3) {
    # Fallback to generic slug with timestamp
    slug <- paste0("episode-", format(Sys.time(), "%Y%m%d%H%M%S"))
  }
  
  return(slug)
}

# Function to get existing episode slugs
get_existing_episodes <- function() {
  if (!dir.exists(POSTS_DIR)) {
    return(character(0))
  }
  existing_dirs <- list.dirs(POSTS_DIR, recursive = FALSE, full.names = FALSE)
  return(existing_dirs)
}

# Function to extract categories from description
extract_categories <- function(description) {
  # Default categories
  categories <- c("health metrics", "data science")
  
  # Try to extract relevant keywords
  keywords <- c("research", "epidemiology", "infectious disease", 
                "public health", "technology", "innovation")
  
  for (keyword in keywords) {
    if (str_detect(tolower(description), keyword)) {
      if (!keyword %in% categories) {
        categories <- c(categories, keyword)
      }
    }
  }
  
  # Limit to 3-4 categories
  return(head(categories, 4))
}

# Function to download image from URL
# Simplified function using magick
download_image <- function(image_url, output_path) {
  tryCatch({
    cat(glue("  → Downloading image from {image_url}\n"))
    
    # Download and convert using magick
    img <- image_read(image_url)
    
    # Convert to PNG format regardless of source format
    image_write(img, path = output_path, format = "png")
    
    cat(glue("✓ Downloaded and converted image to {output_path}\n"))
    return(TRUE)
    
  }, error = function(e) {
    cat(glue("✗ Error downloading image: {e$message}\n"))
    return(FALSE)
  })
}

# Function to create index.qmd file for an episode
create_episode_post <- function(episode_data, episode_dir) {
  # Extract episode information
  title <- episode_data$title
  date <- as.Date(episode_data$pub_date)
  description <- if (!is.null(episode_data$description) && episode_data$description != "") {
    episode_data$description
  } else {
    "Episode description coming soon."
  }
  episode_id <- episode_data$episode_id  # Extracted from episode URL if available
  
  # Create slug for this episode
  episode_slug <- create_slug(title)
  
  # Create categories
  categories <- extract_categories(description)
  categories_yaml <- paste0("  - ", categories, collapse = "\n")
  
  # Spotify embed URL
  # Use episode-specific URL if available, otherwise fall back to show URL
  if (!is.null(episode_id) && episode_id != "") {
    spotify_embed <- glue('https://open.spotify.com/embed/episode/{episode_id}?utm_source=generator')
  } else {
    spotify_embed <- glue('https://open.spotify.com/embed/show/{SHOW_ID}/video?utm_source=generator')
  }
  
  # Generate key topics from description
  # Simple approach: extract sentences that look like topics
  # Split on period followed by space to avoid splitting on abbreviations
  sentences <- str_split(description, "\\.\\s+")[[1]] %>% str_trim()
  key_topics <- head(sentences[nchar(sentences) > 20 & nchar(sentences) < 200], 3)
  if (length(key_topics) == 0) {
    key_topics <- c("Data-driven insights", "Health metrics analysis", "Innovative approaches to public health")
  }
  key_topics_md <- paste0("- ", key_topics, collapse = "\n")
  
  # Create the index.qmd content
  qmd_content <- glue('---
title: "{title}"
date: \'{date}\'
image: featured.png
slug: podcast-{episode_slug}
toc: true
categories:
{categories_yaml}
summary: |
  {description}
execute: 
  eval: false
---


<iframe data-testid="embed-iframe" style="border-radius:12px" src="{spotify_embed}" width="624" height="351" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>


## Episode Overview

{description}

## Key Topics Discussed

{key_topics_md}


')
  
  # Write the qmd file
  qmd_path <- file.path(episode_dir, "index.qmd")
  writeLines(qmd_content, qmd_path)
  cat(glue("✓ Created {qmd_path}\n"))
  
  # Download episode image if available
  if (!is.null(episode_data$image_url) && episode_data$image_url != "") {
    image_path <- file.path(episode_dir, "featured.png")
    download_image(episode_data$image_url, image_path)
  } else {
    cat("✗ No image available for this episode\n")
  }
}

# Function to parse RSS feed and extract episode data
parse_rss_feed <- function(rss_url) {
  cat(glue("→ Fetching RSS feed from {rss_url}...\n"))
  
  tryCatch({
    # Fetch RSS feed
    response <- GET(rss_url, timeout(30))
    if (status_code(response) != 200) {
      stop(glue("HTTP error {status_code(response)}"))
    }
    
    # Parse XML
    rss_xml <- read_xml(content(response, "text", encoding = "UTF-8"))
    
    # Extract channel info for debugging
    channel_title <- xml_text(xml_find_first(rss_xml, "//channel/title"))
    cat(glue("✓ Successfully fetched feed: {channel_title}\n"))
    
    # Find all episode items
    items <- xml_find_all(rss_xml, "//item")
    cat(glue("✓ Found {length(items)} episodes in feed\n\n"))
    
    # Parse each episode
    episodes <- lapply(items, function(item) {
      # Extract basic info
      title <- xml_text(xml_find_first(item, ".//title"))
      pub_date_str <- xml_text(xml_find_first(item, ".//pubDate"))
      description <- xml_text(xml_find_first(item, ".//description"))
      
      # Parse publication date (RSS 2.0 format: "Tue, 08 Jan 2026 10:00:00 GMT")
      pub_date <- tryCatch({
        # Try to parse RFC 2822 date format
        parsed <- strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S", tz = "GMT")
        if (is.na(parsed)) {
          # If parsing fails, return current date
          Sys.Date()
        } else {
          as.Date(parsed)
        }
      }, error = function(e) {
        # Fallback to current date if parsing fails
        Sys.Date()
      })
      
      # Extract enclosure (audio file URL)
      enclosure <- xml_find_first(item, ".//enclosure")
      audio_url <- if (!is.na(enclosure)) {
        xml_attr(enclosure, "url")
      } else {
        ""
      }
      
      # Extract iTunes image if available
      image_url <- tryCatch({
        # Try itunes:image first (using local-name to avoid namespace issues)
        itunes_image <- xml_find_first(item, ".//*[local-name()='image' and namespace-uri()='http://www.itunes.com/dtds/podcast-1.0.dtd']")
        if (!is.na(itunes_image)) {
          xml_attr(itunes_image, "href")
        } else {
          # Try media:thumbnail (using local-name)
          media_thumb <- xml_find_first(item, ".//*[local-name()='thumbnail']")
          if (!is.na(media_thumb)) {
            xml_attr(media_thumb, "url")
          } else {
            ""
          }
        }
      }, error = function(e) {
        ""
      })
      
      # Try to extract Spotify episode ID from link or guid
      episode_id <- tryCatch({
        link <- xml_text(xml_find_first(item, ".//link"))
        if (grepl("spotify.com/episode/", link)) {
          # Extract episode ID from Spotify URL
          match_result <- str_match(link, "episode/([a-zA-Z0-9]+)")
          if (!is.na(match_result[1, 1])) {
            match_result[1, 2]
          } else {
            ""
          }
        } else {
          ""
        }
      }, error = function(e) {
        ""
      })
      
      # Return episode data
      list(
        title = title,
        pub_date = pub_date,
        description = description,
        audio_url = audio_url,
        image_url = image_url,
        episode_id = episode_id
      )
    })
    
    return(episodes)
    
  }, error = function(e) {
    stop(glue("ERROR: Failed to fetch or parse RSS feed: {e$message}"))
  })
}

# Main execution
main <- function() {
  cat("=== RSS Podcast Fetcher ===\n\n")
  
  # Fetch and parse RSS feed
  episodes <- parse_rss_feed(RSS_FEED_URL)
  
  # Get existing episodes
  existing_episodes <- get_existing_episodes()
  cat(glue("→ Found {length(existing_episodes)} existing episode(s)\n\n"))
  
  # Process each episode
  new_episodes_count <- 0
  
  for (i in seq_along(episodes)) {
    episode_data <- episodes[[i]]
    slug <- create_slug(episode_data$title)
    
    # Check if episode already exists
    if (slug %in% existing_episodes) {
      cat(glue("⊙ Skipping existing episode: {episode_data$title}\n"))
      next
    }
    
    cat(glue("→ Processing new episode: {episode_data$title}\n"))
    
    # Create episode directory
    episode_dir <- file.path(POSTS_DIR, slug)
    dir_create(episode_dir)
    cat(glue("  ✓ Created directory: {episode_dir}\n"))
    
    # Create episode post
    create_episode_post(episode_data, episode_dir)
    
    new_episodes_count <- new_episodes_count + 1
    cat("\n")
  }
  
  # Summary
  cat("=== Summary ===\n")
  cat(glue("Total episodes fetched: {length(episodes)}\n"))
  cat(glue("New episodes added: {new_episodes_count}\n"))
  cat(glue("Existing episodes: {length(existing_episodes)}\n"))
  
  if (new_episodes_count > 0) {
    cat("\n✓ Successfully added new episodes!\n")
  } else {
    cat("\n⊙ No new episodes to add.\n")
  }
}

# Run the script
main()
