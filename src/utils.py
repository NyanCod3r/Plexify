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
from typing import List, Dict
from spotify_utils import getSpotifyUserPlaylists, getSpotifyPlaylist
from plex_utils import ensureLocalFiles

CACHE_FILE = 'spotify_playlists.json'

def load_cached_playlists() -> List[Dict]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cached = json.load(f)
                logging.info(f"Loaded {len(cached)} playlists from cache.")
                return cached
        except Exception as e:
            logging.warning(f"Failed to load cache: {e}")
    return None

def has_playlist_changed(sp: spotipy.Spotify, cached_playlist: Dict) -> bool:
    try:
        current = sp.playlist(cached_playlist['id'], fields='snapshot_id')
        changed = current['snapshot_id'] != cached_playlist.get('snapshot_id')
        if changed:
            logging.info(f"Playlist '{cached_playlist['name']}' has changed")
        return changed
    except Exception as e:
        logging.warning(f"Could not check playlist changes: {e}")
        return True

# Main function to run the synchronization process
# - plex: The Plex server instance
# - sp: The Spotify client instance
# - spotify_uris: A list of parsed Spotify URIs
def runSync(sp: spotipy.Spotify, spotify_uris: List[Dict], force_refresh: bool = False):
    """
    Main sync function. Uses cached data when possible to minimize API calls.
    """
    logging.info("Starting synchronization process...")
    
    cached_playlists = None if force_refresh else load_cached_playlists()
    
    if cached_playlists:
        logging.info("Using cached playlist data. Checking for changes...")
        spotifyPlaylists = []
        needs_update = []
        
        for cached in cached_playlists:
            if has_playlist_changed(sp, cached):
                needs_update.append(cached['id'])
            else:
                spotifyPlaylists.append(cached)
        
        if needs_update:
            logging.info(f"{len(needs_update)} playlists need updating.")
            fresh_playlists = dumpSpotifyPlaylists(sp, spotify_uris, only_ids=needs_update)
            
            for fresh in fresh_playlists:
                spotifyPlaylists = [p for p in spotifyPlaylists if p['id'] != fresh['id']]
                spotifyPlaylists.append(fresh)
            
            with open(CACHE_FILE, 'w') as f:
                json.dump(spotifyPlaylists, f, indent=4)
        else:
            logging.info("All playlists are up-to-date. No API calls needed.")
    else:
        logging.info("No cache found or forced refresh. Fetching all playlists...")
        spotifyPlaylists = dumpSpotifyPlaylists(sp, spotify_uris)
    
    syncPlaylists(sp, spotifyPlaylists)
    logging.info("Synchronization process finished.")
    return spotifyPlaylists

# Dumps all relevant Spotify playlists to a JSON file
# - sp: The Spotify client instance
# - spotify_uris: A list of parsed Spotify URIs
# Returns: A list of Spotify playlists
def dumpSpotifyPlaylists(sp: spotipy.Spotify, spotify_uris: List[Dict], only_ids: List[str] = None) -> List[Dict]:
    """
    Fetches Spotify playlists based on provided URIs.
    """
    logging.info("Fetching Spotify playlists...")
    spotifyPlaylists = []
    
    for uri in spotify_uris:
        if 'user' in uri:
            user_playlists = getSpotifyUserPlaylists(sp, uri['user'])
            if only_ids:
                user_playlists = [p for p in user_playlists if p['id'] in only_ids]
            spotifyPlaylists.extend(user_playlists)
        elif 'playlist' in uri:
            if not only_ids or uri['playlist'] in only_ids:
                spotifyPlaylists.append(getSpotifyPlaylist(sp, '', uri['playlist']))
        else:
            logging.warning(f"Unknown URI type: {uri}")
    
    if spotifyPlaylists:
        with open(CACHE_FILE, 'w') as f:
            json.dump(spotifyPlaylists, f, indent=4)
        logging.info(f"Found {len(spotifyPlaylists)} Spotify playlists.")
    else:
        logging.warning("No Spotify playlists found.")
    
    return spotifyPlaylists

def syncPlaylists(sp: spotipy.Spotify, spotifyPlaylists: List[Dict]):
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