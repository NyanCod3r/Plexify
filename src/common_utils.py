"""
common_utils.py - Shared utilities for Plexify

This module provides shared helpers for retry logic and folder creation.

Key functions:
- createFolder: Ensure playlist folder exists
- retry_with_backoff: Retry logic for API calls
"""

import os
import logging
import time
import spotipy

# Creates a folder for a playlist if it doesn't already exist
# - playlistName: The name of the playlist (used as the folder name)
def createFolder(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
        logging.debug(f'Ensured folder exists: {folder_path}')
    except Exception as e:
        logging.error(f'Failed to create folder {folder_path}: {e}')

# Retries a function with exponential backoff in case of failures
# - func: The function to retry
# - *args, **kwargs: Arguments and keyword arguments to pass to the function
# Handles Spotify API rate-limiting errors (HTTP 429) and other transient errors
def retry_with_backoff(func, *args, **kwargs):
    max_retries = 5
    backoff = 1

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", backoff))
                time.sleep(retry_after)
                backoff *= 2
            else:
                raise e
        except Exception as e:
            time.sleep(backoff)
            backoff *= 2
    raise Exception("Max retries exceeded")