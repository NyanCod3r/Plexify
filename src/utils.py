"""
utils.py - Core synchronization logic for Plexify

This module contains the main functions that drive the synchronization process
between Spotify and Plex. It orchestrates the fetching of playlists by user URI,
and then creates or updates the corresponding playlists in Plex.
It also triggers the discovery playlist generation.

Key functions:
- runSync: Main entry point to start the synchronization.
- dumpSpotifyPlaylists: Fetches and saves Spotify playlists to a JSON file.
- dumpPlexPlaylists: Fetches and saves Plex playlists to a JSON file.
- diffAndSyncPlaylists: Compares Spotify and Plex playlists and syncs them.
"""

import os
import json
import logging
from plexapi.server import PlexServer
import spotipy
from spotify_utils import getSpotifyUserPlaylists, getSpotifyPlaylist
from plex_utils import getPlexPlaylists, createPlaylist

# Main function to run the synchronization process
# - plex: The Plex server instance
# - sp: The Spotify client instance
# - spotify_uris: A list of parsed Spotify URIs
def runSync(plex: PlexServer, sp: spotipy.client, spotify_uris: []):
    logging.info("Starting synchronization process...")
    spotifyPlaylists = dumpSpotifyPlaylists(sp, spotify_uris)
    plexPlaylists = dumpPlexPlaylists(plex)
    diffAndSyncPlaylists(plex, sp, spotifyPlaylists, plexPlaylists)

    logging.info("Synchronization process finished.")

# Dumps all relevant Spotify playlists to a JSON file
# - sp: The Spotify client instance
# - spotify_uris: A list of parsed Spotify URIs
# Returns: A list of Spotify playlists
def dumpSpotifyPlaylists(sp: spotipy.client, spotify_uris: []) -> []:
    logging.info("Dumping Spotify playlists...")
    spotifyPlaylists = []
    for uri in spotify_uris:
        if 'user' in uri:
            spotifyPlaylists.extend(getSpotifyUserPlaylists(sp, uri['user']))
        elif 'playlist' in uri:
            # Use a dummy user, Spotify API does not require user for public playlists
            spotifyPlaylists.append(getSpotifyPlaylist(sp, '', uri['playlist']))
        else:
            logging.warning(f"Unknown URI type: {uri}")
    if spotifyPlaylists:
        with open('spotify_playlists.json', 'w') as f:
            json.dump(spotifyPlaylists, f, indent=4)
        logging.info(f"Successfully dumped {len(spotifyPlaylists)} Spotify playlists.")
    else:
        logging.warning("No Spotify playlists found to dump.")
    return spotifyPlaylists

# Dumps all Plex playlists to a JSON file
# - plex: The Plex server instance
# Returns: A list of Plex playlists
def dumpPlexPlaylists(plex: PlexServer) -> []:
    logging.info("Dumping Plex playlists...")
    plexPlaylists = getPlexPlaylists(plex)
    logging.info(f"Successfully dumped {len(plexPlaylists)} Plex playlists.")
    return plexPlaylists

# Diffs the Spotify and Plex playlists and syncs them
# - plex: The Plex server instance
# - sp: The Spotify client instance
# - spotifyPlaylists: A list of Spotify playlists
# - plexPlaylists: A list of Plex playlists
def diffAndSyncPlaylists(plex: PlexServer, sp: spotipy.client, spotifyPlaylists: [], plexPlaylists: []):
    logging.info("Starting playlist diff and sync...")
    if not spotifyPlaylists:
        logging.info("No Spotify playlists to sync.")
        return
    for playlist in spotifyPlaylists:
        logging.debug(f"Processing Spotify playlist: {playlist['name']}")
        createPlaylist(plex, sp, playlist)
    logging.info("Playlist diff and sync finished.")