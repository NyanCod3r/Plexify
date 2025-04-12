import logging
import os
import time
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from spotify_utils import parseSpotifyURI
from utils import runSync

# Configure logging based on PLEXIFY_DEBUG environment variable
debug_mode = os.environ.get('PLEXIFY_DEBUG', '0') == '1'
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG if debug_mode else logging.INFO
)

logging.info("Starting Plexify...")
if debug_mode:
    logging.debug("Debug mode is enabled. Detailed logs will be shown.")
else:
    logging.info("Debug mode is disabled. Only main actions will be logged.")

# Entry point of the application
if __name__ == '__main__':
    # Retrieve Spotify URIs from environment variables
    spotifyUris = os.environ.get('SPOTIFY_URIS')

    # If no Spotify URIs are provided, log an error and exit
    if spotifyUris is None:
        logging.error("No Spotify URIs provided! We need at least one to work with.")
        exit(1)

    # Retrieve the interval to wait between sync operations (default: 3600 seconds)
    secondsToWait = int(os.environ.get('SECONDS_TO_WAIT', 3600))

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

    # Split the Spotify URIs into a list
    spotifyUris = spotifyUris.split(",")

    # Parse each Spotify URI into its components and store them in a list
    spotifyMainUris = []
    for spotifyUri in spotifyUris:
        spotifyUriParts = parseSpotifyURI(spotifyUri)
        spotifyMainUris.append(spotifyUriParts)

    # Main loop: continuously sync Spotify playlists with Plex
    while True:
        try:
            # Run the sync operation
            runSync(plex, sp, spotifyMainUris)
        except Exception as e:
            logging.error(f"An error occurred during the sync operation: {e}")

        # Wait for the specified interval before the next sync
        logging.info(f"Waiting {secondsToWait} seconds before the next sync...")
        time.sleep(secondsToWait)