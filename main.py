import logging
import os
import time
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from spotify_utils import parseSpotifyURI
from utils import runSync

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    spotifyUris = os.environ.get('SPOTIFY_URIS')

    if spotifyUris is None:
        logging.error("No spotify uris! We need at least one to work with")

    secondsToWait = int(os.environ.get('SECONDS_TO_WAIT', 3600))
    baseurl = os.environ.get('PLEX_URL')
    token = os.environ.get('PLEX_TOKEN')
    plex = PlexServer(baseurl, token)
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    spotifyUris = spotifyUris.split(",")

    spotifyMainUris = []

    for spotifyUri in spotifyUris:
        spotifyUriParts = parseSpotifyURI(spotifyUri)
        spotifyMainUris.append(spotifyUriParts)

    while True:
        runSync(plex, sp, spotifyMainUris)
        time.sleep(secondsToWait)