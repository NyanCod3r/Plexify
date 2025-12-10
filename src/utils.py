"""
utils.py - Core synchronization logic for Plexify

This module contains the main functions that drive the synchronization process
between Spotify and Plex. It orchestrates the fetching of playlists by user URI,
and then creates or updates the corresponding playlists in Plex.
It also triggers the discovery playlist generation.

Key functions:
- runSync: Main entry point to start the synchronization.
- dumpSpotifyPlaylists: Fetches and saves Spotify playlists to a JSON file.
- diffAndSyncPlaylists: Compares Spotify and Plex playlists and syncs them.
"""

import os
import json
import logging
import spotipy
from spotify_utils import getSpotifyUserPlaylists, getSpotifyPlaylist
from plex_utils import ensureLocalFiles

# Main function to run the synchronization process
# - plex: The Plex server instance
# - sp: The Spotify client instance
# - spotify_uris: A list of parsed Spotify URIs
def runSync(sp: spotipy.client, spotify_uris: list):
    """
    Main sync function. Fetches Spotify playlists and ensures local files exist.
    """
    logging.info("Starting synchronization process...")
    spotifyPlaylists = dumpSpotifyPlaylists(sp, spotify_uris)
    syncPlaylists(sp, spotifyPlaylists)
    logging.info("Synchronization process finished.")

# Dumps all relevant Spotify playlists to a JSON file
# - sp: The Spotify client instance
# - spotify_uris: A list of parsed Spotify URIs
# Returns: A list of Spotify playlists
def dumpSpotifyPlaylists(sp: spotipy.client, spotify_uris: list) -> list:
    """
    Fetches all Spotify playlists based on provided URIs.
    """
    logging.info("Fetching Spotify playlists...")
    spotifyPlaylists = []
    
    for uri in spotify_uris:
        if 'user' in uri:
            spotifyPlaylists.extend(getSpotifyUserPlaylists(sp, uri['user']))
        elif 'playlist' in uri:
            spotifyPlaylists.append(getSpotifyPlaylist(sp, '', uri['playlist']))
        else:
            logging.warning(f"Unknown URI type: {uri}")
    
    if spotifyPlaylists:
        with open('spotify_playlists.json', 'w') as f:
            json.dump(spotifyPlaylists, f, indent=4)
        logging.info(f"Found {len(spotifyPlaylists)} Spotify playlists.")
    else:
        logging.warning("No Spotify playlists found.")
    
    return spotifyPlaylists

def syncPlaylists(sp: spotipy.client, spotifyPlaylists: list):
    """
    Ensures local files exist for all Spotify playlists.
    """
    if not spotifyPlaylists:
        logging.info("No playlists to sync.")
        return
    
    for playlist in spotifyPlaylists:
        playlist_name = playlist.get('name', 'Unknown')
        logging.info(f"Processing playlist: {playlist_name}")
        ensureLocalFiles(sp, playlist)