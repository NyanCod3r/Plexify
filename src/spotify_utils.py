"""
spotify_utils.py - Spotify API helpers for Plexify

This module provides functions for interacting with the Spotify API. It handles
parsing URIs, fetching user playlists, finding playlists by name, and retrieving
all tracks from a playlist.

Key functions:
- parseSpotifyURI: Parse Spotify URI into components.
- getSpotifyPlaylist: Fetch a specific playlist by ID.
- getSpotifyUserPlaylists: Fetch all playlists for a given user.
- findPlaylistsByName: Search for and retrieve playlists by their exact names.
- getSpotifyTracks: Fetch all tracks from a playlist object.
"""

import re
import spotipy
import logging
from typing import List
from common_utils import retry_with_backoff

# Parses a Spotify URI into its components (e.g., user, playlist)
# - uriString: The Spotify URI to parse
# Returns: A dictionary containing the parsed components
def parseSpotifyURI(uriString: str) -> {}:
    logging.debug(f"Parsing Spotify URI: {uriString}")
    if not uriString:
        logging.warning("Received an empty Spotify URI string.")
        return {}
    spotifyUriStrings = re.sub(r'^spotify:', '', uriString).split(":")
    if len(spotifyUriStrings) % 2 != 0:
        logging.error(f"Invalid or incomplete Spotify URI provided: '{uriString}'")
        return {}
    spotifyUriParts = {}
    for i, string in enumerate(spotifyUriStrings):
        if i % 2 == 0:
            spotifyUriParts[spotifyUriStrings[i]] = spotifyUriStrings[i+1]
    logging.debug(f"Parsed Spotify URI components: {spotifyUriParts}")
    return spotifyUriParts

# Retrieves a specific Spotify playlist
# - sp: The Spotify client instance
# - userId: The ID of the Spotify user
# - playlistId: The ID of the Spotify playlist
# Returns: The Spotify playlist object
def getSpotifyPlaylist(sp: spotipy.client, userId: str, playlistId: str) -> []:
    logging.info(f"Retrieving Spotify playlist for user: {userId}, playlist ID: {playlistId}")
    playlist = retry_with_backoff(sp.user_playlist, userId, playlistId)
    logging.debug(f"Retrieved playlist: {playlist}")
    return playlist

# Retrieves all playlists for a specific Spotify user
# - sp: The Spotify client instance
# - userId: The ID of the Spotify user
# Returns: A list of Spotify playlists
def getSpotifyUserPlaylists(sp: spotipy.client, userId: str) -> []:
    logging.info(f"Retrieving all playlists for Spotify user: {userId}")
    playlists = retry_with_backoff(sp.user_playlists, userId)
    spotifyPlaylists = []
    while playlists:
        playlistItems = playlists['items']
        logging.debug(f"Processing {len(playlistItems)} playlists for user: {userId}")
        for i, playlist in enumerate(playlistItems):
            if playlist['owner']['id'] == userId:
                logging.debug(f"Adding playlist: {playlist['name']} (ID: {playlist['id']})")
                spotifyPlaylists.append(getSpotifyPlaylist(sp, userId, playlist['id']))
        if playlists['next']:
            playlists = retry_with_backoff(sp.next, playlists)
        else:
            playlists = None
    logging.info(f"Retrieved {len(spotifyPlaylists)} playlists for user: {userId}")
    return spotifyPlaylists

# Finds and retrieves playlists by their exact names from the current user's library
# - sp: The Spotify client instance
# - playlist_names: A list of playlist names to search for
# Returns: A list of found Spotify playlist objects
def findPlaylistsByName(sp: spotipy.client, playlist_names: List[str]) -> List:
    found_playlists = []
    user_playlists = retry_with_backoff(sp.current_user_playlists)
    while user_playlists:
        for playlist in user_playlists['items']:
            if playlist['name'] in playlist_names:
                logging.info(f"Found playlist by name: {playlist['name']}")
                full_playlist = getSpotifyPlaylist(sp, playlist['owner']['id'], playlist['id'])
                found_playlists.append(full_playlist)
        if user_playlists['next']:
            user_playlists = retry_with_backoff(sp.next, user_playlists)
        else:
            user_playlists = None
    return found_playlists

# Retrieves all tracks from a Spotify playlist
# - sp: The Spotify client instance
# - playlist: The Spotify playlist object
# Returns: A list of tracks in the playlist
def getSpotifyTracks(sp: spotipy.client, playlist: []) -> []:
    logging.info(f"Retrieving tracks for playlist: {playlist['name']}")
    spotifyTracks = []
    tracks = playlist['tracks']
    spotifyTracks.extend(tracks['items'])
    logging.debug(f"Retrieved {len(tracks['items'])} initial tracks for playlist: {playlist['name']}")
    while tracks['next']:
        tracks = retry_with_backoff(sp.next, tracks)
        spotifyTracks.extend(tracks['items'])
        logging.debug(f"Retrieved additional {len(tracks['items'])} tracks for playlist: {playlist['name']}")
    logging.info(f"Retrieved total {len(spotifyTracks)} tracks for playlist: {playlist['name']}")
    return spotifyTracks