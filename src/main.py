import logging
import os
import time
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from spotify_utils import parseSpotifyURI
from utils import runSync

# Entry point of the application
if __name__ == '__main__':
    # Configure logging to display timestamps and messages
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    # Retrieve Spotify URIs from environment variables
    spotifyUris = os.environ.get('SPOTIFY_URIS')

    # If no Spotify URIs are provided, log an error and exit
    if spotifyUris is None:
        logging.error("No spotify uris! We need at least one to work with")

    # Retrieve the interval to wait between sync operations (default: 3600 seconds)
    secondsToWait = int(os.environ.get('SECONDS_TO_WAIT', 3600))

    # Retrieve Plex server URL and token from environment variables
    baseurl = os.environ.get('PLEX_URL')
    token = os.environ.get('PLEX_TOKEN')

    # Connect to the Plex server using the provided URL and token
    plex = PlexServer(baseurl, token)

    # Set up Spotify client credentials for API access
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Split the Spotify URIs into a list
    spotifyUris = spotifyUris.split(",")

    # Parse each Spotify URI into its components and store them in a list
    spotifyMainUris = []
    for spotifyUri in spotifyUris:
        spotifyUriParts = parseSpotifyURI(spotifyUri)
        spotifyMainUris.append(spotifyUriParts)

    # Main loop: continuously sync Spotify playlists with Plex
    while True:
        # Run the sync operation
        runSync(plex, sp, spotifyMainUris)

        # Wait for the specified interval before the next sync
        time.sleep(secondsToWait)