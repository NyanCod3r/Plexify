"""
main.py - Entry point for Plexify

This script initializes logging, loads configuration from environment variables,
connects to Plex and Spotify, and runs the main sync loop. It can sync playlists
based on user URIs.

Key functions/classes:
- Loads and parses SPOTIFY_URIS
- Connects to Plex and Spotify using Client Credentials
- Calls runSync from utils.py in a loop
"""

import logging
import os
import time
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from spotify_utils import parseSpotifyURI
from utils import runSync

# Configure logging based on LOG_LEVEL environment variable
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=log_level
)

logging.info("Starting Plexify...")
if log_level == 'DEBUG':
    logging.debug("Debug mode is enabled. Detailed logs will be shown.")

# Entry point of the application
if __name__ == '__main__':
    # Retrieve Plex server URL and token from environment variables
    baseurl = os.environ.get('PLEX_URL')
    token = os.environ.get('PLEX_TOKEN')

    # Validate Plex server URL and token
    if not baseurl or not token:
        logging.error("PLEX_URL or PLEX_TOKEN is not set. Please configure these environment variables.")
        exit(1)

    # Connect to the Plex server using the provided URL and token
    try:
        plex = PlexServer(baseurl, token)
        logging.info("Successfully connected to Plex server.")
    except Exception as e:
        logging.error(f"Failed to connect to Plex server: {e}")
        exit(1)

    # Set up Spotify client credentials for API access
    try:
        client_credentials_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        logging.info("Successfully authenticated with Spotify.")
    except Exception as e:
        logging.error(f"Failed to authenticate with Spotify: {e}")
        exit(1)

    # Retrieve and parse Spotify URIs from environment variables
    spotify_uris_str = os.environ.get('SPOTIFY_URIS', '')
    spotify_uris = []
    if spotify_uris_str:
        for spotifyUri in spotify_uris_str.split(','):
            spotifyUriParts = parseSpotifyURI(spotifyUri)
            if spotifyUriParts:
                spotify_uris.append(spotifyUriParts)

    if not spotify_uris:
        logging.error("SPOTIFY_URIS is not set. Exiting.")
        exit(1)

    # Retrieve the interval to wait between sync operations (default: 3600 seconds)
    secondsToWait = int(os.environ.get('SECONDS_TO_WAIT', 3600))

    # Main loop: continuously sync Spotify playlists with Plex
    while True:
        try:
            # Run the sync operation
            runSync(plex, sp, spotify_uris)
        except Exception as e:
            logging.error(f"An error occurred during the sync operation: {e}")

        # Wait for the specified interval before the next sync
        logging.info(f"Waiting {secondsToWait} seconds before the next sync...")
        time.sleep(secondsToWait)