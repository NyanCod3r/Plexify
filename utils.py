import time
import logging
import json
import os
from typing import List
import spotipy
from plexapi.server import PlexServer
from common_utils import filterPlexArray, createFolder  # Import the necessary functions
from spotify_utils import getSpotifyUserPlaylists, getSpotifyPlaylist, getSpotifyTracks
from plex_utils import createPlaylist, delete_unmatched_files

def retry_with_backoff(func, *args, **kwargs):
    max_retries = 5
    backoff = 1  # initial backoff time in seconds

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", backoff))
                time.sleep(retry_after)
                backoff *= 2  # Exponential backoff
            else:
                raise e
        except Exception as e:
            time.sleep(backoff)
            backoff *= 2  # Exponential backoff
    raise Exception("Max retries exceeded")

def dumpSpotifyPlaylists(sp: spotipy.Spotify, spotifyURIs: [], dumpFile: str):
    playlists = []
    for spotifyUriParts in spotifyURIs:
        if 'user' in spotifyUriParts.keys() and 'playlist' not in spotifyUriParts.keys():
            playlists.extend(getSpotifyUserPlaylists(sp, spotifyUriParts['user']))
        elif 'user' in spotifyUriParts.keys() and 'playlist' in spotifyUriParts.keys():
            playlists.append(getSpotifyPlaylist(sp, spotifyUriParts['user'], spotifyUriParts['playlist']))
    
    with open(dumpFile, 'w') as f:
        json.dump(playlists, f)
    logging.info(f"Dumped Spotify playlists to {dumpFile}")

def dumpPlexPlaylists(plex: PlexServer, dumpFile: str):
    playlists = plex.playlists()
    plexPlaylists = []
    for playlist in playlists:
        plexPlaylists.append({
            'title': playlist.title,
            'items': [{'title': item.title, 'artist': item.grandparentTitle} for item in playlist.items()]
        })
    
    with open(dumpFile, 'w') as f:
        json.dump(plexPlaylists, f)
    logging.info(f"Dumped Plex playlists to {dumpFile}")

def diffAndSyncPlaylists(plex: PlexServer, sp: spotipy.Spotify, spotifyDumpFile: str, plexDumpFile: str):
    with open(spotifyDumpFile, 'r') as f:
        spotifyPlaylists = json.load(f)
    
    with open(plexDumpFile, 'r') as f:
        plexPlaylists = json.load(f)
    
    for spotifyPlaylist in spotifyPlaylists:
        playlistName = spotifyPlaylist['name']
        spotifyTracks = getSpotifyTracks(sp, spotifyPlaylist)
        spotifyTrackNames = {track['track']['name'] for track in spotifyTracks}
        
        plexPlaylist = next((pl for pl in plexPlaylists if pl['title'] == playlistName), None)
        if plexPlaylist:
            plexTrackNames = {track['title'] for track in plexPlaylist['items']}
            tracksToAdd = spotifyTrackNames - plexTrackNames
            tracksToDelete = plexTrackNames - spotifyTrackNames
            
            if tracksToAdd:
                logging.info(f"Adding tracks to Plex playlist {playlistName}: {tracksToAdd}")
                createPlaylist(plex, sp, spotifyPlaylist)
            
            if tracksToDelete:
                logging.info(f"Deleting tracks from Plex playlist {playlistName}: {tracksToDelete}")
                delete_unmatched_files(plex, spotifyTracks, playlistName)
        else:
            logging.info(f"Creating new Plex playlist {playlistName}")
            createPlaylist(plex, sp, spotifyPlaylist)

def runSync(plex: PlexServer, sp: spotipy.Spotify, spotifyURIs: []):
    logging.info('Starting a Sync Operation')
    spotifyDumpFile = 'spotify_playlists.json'
    plexDumpFile = 'plex_playlists.json'
    
    dumpSpotifyPlaylists(sp, spotifyURIs, spotifyDumpFile)
    dumpPlexPlaylists(plex, plexDumpFile)
    diffAndSyncPlaylists(plex, sp, spotifyDumpFile, plexDumpFile)
    
    logging.info('Finished a Sync Operation')

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

def getSpotifyPlaylist(sp: spotipy.client, userId: str, playlistId: str) -> []:
    playlist = retry_with_backoff(sp.user_playlist, userId, playlistId)
    return playlist

def getSpotifyTracks(sp: spotipy.client, playlist: []) -> []:
    spotifyTracks = []
    tracks = playlist['tracks']
    spotifyTracks.extend(tracks['items'])
    while tracks['next']:
        tracks = retry_with_backoff(sp.next, tracks)
        spotifyTracks.extend(tracks['items'])
    return spotifyTracks