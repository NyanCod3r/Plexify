"""
utils.py - Core utilities for Plexify

This module provides core utilities for syncing Spotify playlists to Plex, including:
- retry_with_backoff: Retry logic for API calls
- dumpSpotifyPlaylists: Dump Spotify playlists to JSON
- dumpPlexPlaylists: Dump Plex playlists to JSON
- diffAndSyncPlaylists: Compare and sync Spotify/Plex playlists
- runSync: Main sync operation
- getSpotifyUserPlaylists, getSpotifyPlaylist, getSpotifyTracks: Spotify playlist helpers
- parse_spotify_playlist_id: Extracts playlist ID from URL/URI
- get_special_playlist: Fetches Discover Weekly or Release Radar and saves to correct folder

"""

import time
import logging
import json
import os
from typing import List, Any, Dict
import spotipy
from plexapi.server import PlexServer
from common_utils import filterPlexArray, createFolder
from spotify_utils import getSpotifyUserPlaylists, getSpotifyPlaylist, getSpotifyTracks
from plex_utils import createPlaylist, delete_unmatched_files
from common_utils import retry_with_backoff

# Retry a function with exponential backoff in case of failures
def retry_with_backoff(func, *args, **kwargs):
    max_retries = 5
    backoff = 1  # Initial backoff time in seconds

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:  # Handle rate-limiting
                retry_after = int(e.headers.get("Retry-After", backoff))
                time.sleep(retry_after)
                backoff *= 2  # Exponential backoff
            else:
                raise e
        except Exception as e:
            time.sleep(backoff)
            backoff *= 2  # Exponential backoff
    raise Exception("Max retries exceeded")

def parse_spotify_playlist_id(playlist_url_or_uri: str) -> str:
    """
    Extracts the playlist ID from a Spotify URL or URI.
    Supports URLs like https://open.spotify.com/playlist/ID and URIs like spotify:playlist:ID
    """
    if 'playlist/' in playlist_url_or_uri:
        return playlist_url_or_uri.split('playlist/')[1].split('?')[0]
    elif 'spotify:playlist:' in playlist_url_or_uri:
        return playlist_url_or_uri.split('spotify:playlist:')[1].split('?')[0]
    else:
        return playlist_url_or_uri  # Assume it's already an ID

def get_special_playlist(sp: spotipy.Spotify, playlist_type: str) -> dict:
    """
    Fetches the Discover Weekly or Release Radar playlist for the current user.
    playlist_type: 'discover_weekly' or 'release_radar'
    Returns the playlist object.
    """
    # Official Spotify IDs (may change for some users)
    ids = {
        'discover_weekly': '37i9dQZEVXcJZyENOWUFo7',
        'release_radar': '37i9dQZEVXbLRQDuF5jeBp',
    }
    playlist_id = ids.get(playlist_type)
    if not playlist_id:
        raise ValueError('Unknown playlist type')
    # Use 'spotify' as the user for these algorithmic playlists
    return retry_with_backoff(sp.user_playlist, 'spotify', playlist_id)

# Dump Spotify playlists to a JSON file
def dumpSpotifyPlaylists(sp: spotipy.Spotify, spotifyURIs: list[dict], dumpFile: str):
    """
    Dumps Spotify playlists to a JSON file. Special handling for Discover Weekly and Release Radar.
    """
    playlists = []
    for spotifyUriParts in spotifyURIs:
        # Special handling for Discover Weekly and Release Radar
        if spotifyUriParts.get('special') == 'discover_weekly':
            playlist = get_special_playlist(sp, 'discover_weekly')
            playlist['__folder__'] = 'Discover Weekly'
            playlists.append(playlist)
        elif spotifyUriParts.get('special') == 'release_radar':
            playlist = get_special_playlist(sp, 'release_radar')
            playlist['__folder__'] = 'Release Radar'
            playlists.append(playlist)
        elif 'user' in spotifyUriParts.keys() and 'playlist' not in spotifyUriParts.keys():
            playlists.extend(getSpotifyUserPlaylists(sp, spotifyUriParts['user']))
        elif 'user' in spotifyUriParts.keys() and 'playlist' in spotifyUriParts.keys():
            playlists.append(getSpotifyPlaylist(sp, spotifyUriParts['user'], spotifyUriParts['playlist']))
        elif 'playlist_id' in spotifyUriParts.keys():
            playlists.append(sp.playlist(spotifyUriParts['playlist_id']))
    # Save playlists to a JSON file
    with open(dumpFile, 'w') as f:
        json.dump(playlists, f)
    logging.debug(f"Dumped Spotify playlists to {dumpFile}")

# Dump Plex playlists to a JSON file
def dumpPlexPlaylists(plex: PlexServer, dumpFile: str):
    playlists = plex.playlists()
    plexPlaylists = []
    for playlist in playlists:
        plexPlaylists.append({
            'title': playlist.title,
            'items': [{'title': item.title, 'artist': item.grandparentTitle} for item in playlist.items()]
        })
    
    # Save playlists to a JSON file
    with open(dumpFile, 'w') as f:
        json.dump(plexPlaylists, f)
    logging.debug(f"Dumped Plex playlists to {dumpFile}")

# Compare Spotify and Plex playlists and sync them
def diffAndSyncPlaylists(plex: PlexServer, sp: spotipy.Spotify, spotifyDumpFile: str, plexDumpFile: str):
    # Load Spotify playlists from the dump file
    with open(spotifyDumpFile, 'r') as f:
        spotifyPlaylists = json.load(f)
    
    # Load Plex playlists from the dump file
    with open(plexDumpFile, 'r') as f:
        plexPlaylists = json.load(f)
    
    # Compare and sync each Spotify playlist with Plex
    for spotifyPlaylist in spotifyPlaylists:
        playlistName = spotifyPlaylist['name']
        spotifyTracks = getSpotifyTracks(sp, spotifyPlaylist)
        spotifyTrackNames = {track['track']['name'] for track in spotifyTracks}
        
        # Find the corresponding Plex playlist
        plexPlaylist = next((pl for pl in plexPlaylists if pl['title'] == playlistName), None)
        if plexPlaylist:
            plexTrackNames = {track['title'] for track in plexPlaylist['items']}
            tracksToAdd = spotifyTrackNames - plexTrackNames
            
            # Add missing tracks to Plex
            if tracksToAdd:
                logging.debug(f"Adding tracks to Plex playlist {playlistName}: {tracksToAdd}")
                createPlaylist(plex, sp, spotifyPlaylist)
            
            # Skip track deletion logic
            logging.debug(f"Skipping track deletion for Plex playlist {playlistName}")
        else:
            # Create a new Plex playlist if it doesn't exist
            logging.debug(f"Creating new Plex playlist {playlistName}")
            createPlaylist(plex, sp, spotifyPlaylist)

# Main function to run the sync operation
def runSync(plex: PlexServer, sp: spotipy.Spotify, spotifyURIs: list[dict]):
    logging.info('Starting a Sync Operation')
    spotifyDumpFile = 'spotify_playlists.json'
    plexDumpFile = 'plex_playlists.json'
    
    # Dump Spotify and Plex playlists to JSON files
    dumpSpotifyPlaylists(sp, spotifyURIs, spotifyDumpFile)
    dumpPlexPlaylists(plex, plexDumpFile)
    
    # Compare and sync the playlists
    diffAndSyncPlaylists(plex, sp, spotifyDumpFile, plexDumpFile)
    
    logging.info('Finished a Sync Operation')

# Retrieve all playlists for a Spotify user
def getSpotifyUserPlaylists(sp: spotipy.client, userId: str) -> list[dict]:
    playlists = retry_with_backoff(sp.user_playlists, userId)
    spotifyPlaylists = []
    while playlists:
        playlistItems = playlists['items']
        for i, playlist in enumerate(playlistItems):
            if playlist['owner']['id'] == userId:
                spotifyPlaylists.append(getSpotifyPlaylist(sp, userId, playlist['id']))
        if playlists['next']:
            playlists = retry_with_backoff(sp.next, playlists)
        else:
            playlists = None
    return spotifyPlaylists

# Retrieve a specific Spotify playlist
def getSpotifyPlaylist(sp: spotipy.client, userId: str, playlistId: str) -> dict:
    playlist = retry_with_backoff(sp.user_playlist, userId, playlistId)
    return playlist

# Retrieve all tracks from a Spotify playlist
def getSpotifyTracks(sp: spotipy.client, playlist: dict) -> list[dict]:
    spotifyTracks = []
    tracks = playlist['tracks']
    spotifyTracks.extend(tracks['items'])
    while tracks['next']:
        tracks = retry_with_backoff(sp.next, tracks)
        spotifyTracks.extend(tracks['items'])
    return spotifyTracks