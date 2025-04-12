import os
import logging
import time
from plexapi.audio import Track
from typing import List
import spotipy  # Required for handling Spotify exceptions

# Filters a list of Plex items to find tracks that match a specific song title and artist name
# - plexItems: List of Plex items to filter
# - song: The title of the song to match
# - artist: The name of the artist to match
# Returns: A list of matching Plex Track objects
def filterPlexArray(plexItems=[], song="", artist="") -> List[Track]:
    plexItems = [
        item for item in plexItems
        if isinstance(item, Track) and
        item.title.lower() == song.lower() and
        item.artist().title.lower() == artist.lower()
    ]
    return plexItems

# Creates a folder for a playlist if it doesn't already exist
# - playlistName: The name of the playlist (used as the folder name)
# Logs whether the folder was created or already exists
def createFolder(playlistName):
    if not os.path.exists(os.environ.get('SPOTIPY_PATH') + '/' + playlistName):
        os.makedirs(os.environ.get('SPOTIPY_PATH') + '/' + playlistName)
        logging.debug('Created folder %s' % playlistName)
    else:
        logging.debug('Folder %s already exists' % playlistName)

# Retries a function with exponential backoff in case of failures
# - func: The function to retry
# - *args, **kwargs: Arguments and keyword arguments to pass to the function
# Handles Spotify API rate-limiting errors (HTTP 429) and other transient errors
# Raises an exception if the maximum number of retries is exceeded
def retry_with_backoff(func, *args, **kwargs):
    max_retries = 5  # Maximum number of retries
    backoff = 1  # Initial backoff time in seconds

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)  # Attempt to execute the function
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:  # Handle rate-limiting
                retry_after = int(e.headers.get("Retry-After", backoff))
                time.sleep(retry_after)  # Wait for the specified retry duration
                backoff *= 2  # Exponential backoff
            else:
                raise e  # Raise other Spotify exceptions
        except Exception as e:
            time.sleep(backoff)  # Wait before retrying
            backoff *= 2  # Exponential backoff
    raise Exception("Max retries exceeded")  # Raise an exception if retries are exhausted