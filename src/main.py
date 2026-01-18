"""
main.py - Entry point for Plexify

Downloads tracks from Spotify playlists to local filesystem.
No Plex playlist operations - use Plex Smart Playlists instead.
"""

import os
import logging
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from plexapi.server import PlexServer
from spotify_utils import parseSpotifyURI
from utils import runSync

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=log_level
)

logging.info("Starting Plexify...")

# Entry point of the application
if __name__ == '__main__':
    # Set up Spotify client credentials
    try:
        client_id = os.environ.get('SPOTIPY_CLIENT_ID')
        client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

        if not client_id or not client_secret:
            logging.error("SPOTIPY_CLIENT_ID or SPOTIPY_CLIENT_SECRET not set.")
            exit(1)

        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        logging.info("Successfully authenticated with Spotify.")
    except Exception as e:
        logging.error(f"Failed to authenticate with Spotify: {e}")
        exit(1)

    # Set up Plex server connection
    try:
        plex_url = os.environ.get('PLEX_URL')
        plex_token = os.environ.get('PLEX_TOKEN')
        if not plex_url or not plex_token:
            logging.error("PLEX_URL or PLEX_TOKEN not set.")
            exit(1)
        plex = PlexServer(plex_url, plex_token)
        logging.info("Successfully connected to Plex.")
    except Exception as e:
        logging.error(f"Failed to connect to Plex: {e}")
        exit(1)

    # Parse Spotify URIs
    spotify_uris_str = os.environ.get('SPOTIFY_URIS', '')
    spotify_uris = []

    if spotify_uris_str:
        for uri_str in spotify_uris_str.split(','):
            uri_str = uri_str.strip()
            if uri_str:
                parsed_uri = parseSpotifyURI(uri_str)
                if parsed_uri:
                    spotify_uris.append(parsed_uri)
                    logging.debug(f"Parsed URI: {parsed_uri}")

    if not spotify_uris:
        logging.error("No valid Spotify URIs provided in SPOTIFY_URIS.")
        exit(1)

    # Get sync interval
    secondsToWait = int(os.environ.get('SECONDS_TO_WAIT', 3600))
    first_run = True

    # Main sync loop
    while True:
        try:
            runSync(sp, spotify_uris, force_refresh=first_run)
            first_run = False
        except Exception as e:
            logging.error(f"Sync error: {e}")

        logging.info(f"Waiting {secondsToWait} seconds before next sync...")
        time.sleep(secondsToWait)