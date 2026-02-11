#!/usr/bin/env Rscript

# Fetch Spotify Podcast Episodes and Create Quarto Posts
# This script fetches episodes from a Spotify podcast show and creates
# properly formatted Quarto (.qmd) posts for each new episode.

library(httr)
library(jsonlite)
library(spotifyr)
library(stringr)
library(glue)
library(fs)

# Configuration
SHOW_ID <- "43CSCODQFQkZ05u3Up5OD6"
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
download_image <- function(image_url, output_path) {
  tryCatch({
    response <- GET(image_url, timeout(30))
    if (status_code(response) == 200) {
      writeBin(content(response, "raw"), output_path)
      cat(glue("✓ Downloaded image to {output_path}\n"))
      return(TRUE)
    } else {
      cat(glue("✗ Failed to download image: HTTP {status_code(response)}\n"))
      return(FALSE)
    }
  }, error = function(e) {
    cat(glue("✗ Error downloading image: {e$message}\n"))
    return(FALSE)
  })
}

# Function to create index.qmd file for an episode
create_episode_post <- function(episode, episode_dir) {
  # Extract episode information
  title <- episode$name
  date <- as.Date(episode$release_date)
  description <- if (!is.null(episode$description) && episode$description != "") {
    episode$description
  } else {
    "Episode description coming soon."
  }
  episode_id <- episode$id
  
  # Create slug for this episode
  episode_slug <- create_slug(title)
  
  # Create categories
  categories <- extract_categories(description)
  categories_yaml <- paste0("  - ", categories, collapse = "\n")
  
  # Spotify embed URL (using episode-specific URL)
  spotify_embed <- glue('https://open.spotify.com/embed/episode/{episode_id}?utm_source=generator')
  
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
summary: "{description}"
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
  if (!is.null(episode$images) && length(episode$images) > 0) {
    # Get the largest image (first in the list)
    image_url <- episode$images[[1]]$url
    image_path <- file.path(episode_dir, "featured.png")
    download_image(image_url, image_path)
  } else {
    cat("✗ No image available for this episode\n")
  }
}

# Main execution
main <- function() {
  cat("=== Spotify Podcast Fetcher ===\n\n")
  
  # Check for required environment variables
  client_id <- Sys.getenv("SPOTIFY_CLIENT_ID")
  client_secret <- Sys.getenv("SPOTIFY_CLIENT_SECRET")
  
  if (client_id == "" || client_secret == "") {
    stop("ERROR: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables must be set")
  }
  
  cat("✓ Found Spotify credentials\n")
  
  # Authenticate with Spotify
  cat("→ Authenticating with Spotify API...\n")
  tryCatch({
    access_token <- get_spotify_access_token(
      client_id = client_id,
      client_secret = client_secret
    )
    cat("✓ Successfully authenticated\n\n")
  }, error = function(e) {
    stop(glue("ERROR: Failed to authenticate with Spotify: {e$message}"))
  })
  
  # Fetch show episodes
  cat(glue("→ Fetching episodes for show ID: {SHOW_ID}...\n"))
  tryCatch({
    episodes <- get_show_episodes(
      id = SHOW_ID,
      limit = 50,
      authorization = access_token
    )
    cat(glue("✓ Found {nrow(episodes)} episodes\n\n"))
  }, error = function(e) {
    stop(glue("ERROR: Failed to fetch episodes: {e$message}"))
  })
  
  # Get existing episodes
  existing_episodes <- get_existing_episodes()
  cat(glue("→ Found {length(existing_episodes)} existing episode(s)\n\n"))
  
  # Process each episode
  new_episodes_count <- 0
  
  for (i in seq_len(nrow(episodes))) {
    episode <- episodes[i, ]
    slug <- create_slug(episode$name)
    
    # Check if episode already exists
    if (slug %in% existing_episodes) {
      cat(glue("⊙ Skipping existing episode: {episode$name}\n"))
      next
    }
    
    cat(glue("→ Processing new episode: {episode$name}\n"))
    
    # Create episode directory
    episode_dir <- file.path(POSTS_DIR, slug)
    dir_create(episode_dir)
    cat(glue("  ✓ Created directory: {episode_dir}\n"))
    
    # Create episode post
    create_episode_post(episode, episode_dir)
    
    new_episodes_count <- new_episodes_count + 1
    cat("\n")
  }
  
  # Summary
  cat("=== Summary ===\n")
  cat(glue("Total episodes fetched: {nrow(episodes)}\n"))
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
