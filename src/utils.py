import time
import logging
import json
import os
from typing import List
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

# Dump Spotify playlists to a JSON file
def dumpSpotifyPlaylists(sp: spotipy.Spotify, spotifyURIs: [], dumpFile: str):
    playlists = []
    for spotifyUriParts in spotifyURIs:
        if 'user' in spotifyUriParts.keys() and 'playlist' not in spotifyUriParts.keys():
            playlists.extend(getSpotifyUserPlaylists(sp, spotifyUriParts['user']))
        elif 'user' in spotifyUriParts.keys() and 'playlist' in spotifyUriParts.keys():
            playlists.append(getSpotifyPlaylist(sp, spotifyUriParts['user'], spotifyUriParts['playlist']))
    
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
def runSync(plex: PlexServer, sp: spotipy.Spotify, spotifyURIs: []):
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
def getSpotifyUserPlaylists(sp: spotipy.client, userId: str) -> []:
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
def getSpotifyPlaylist(sp: spotipy.client, userId: str, playlistId: str) -> []:
    playlist = retry_with_backoff(sp.user_playlist, userId, playlistId)
    return playlist

# Retrieve all tracks from a Spotify playlist
def getSpotifyTracks(sp: spotipy.client, playlist: []) -> []:
    spotifyTracks = []
    tracks = playlist['tracks']
    spotifyTracks.extend(tracks['items'])
    while tracks['next']:
        tracks = retry_with_backoff(sp.next, tracks)
        spotifyTracks.extend(tracks['items'])
    return spotifyTracks