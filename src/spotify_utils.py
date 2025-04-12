import re
import spotipy
from typing import List
from common_utils import retry_with_backoff

# Parses a Spotify URI into its components (e.g., user, playlist)
# - uriString: The Spotify URI to parse
# Returns: A dictionary containing the parsed components
def parseSpotifyURI(uriString: str) -> {}:
    spotifyUriStrings = re.sub(r'^spotify:', '', uriString).split(":")
    spotifyUriParts = {}
    for i, string in enumerate(spotifyUriStrings):
        if i % 2 == 0:
            spotifyUriParts[spotifyUriStrings[i]] = spotifyUriStrings[i+1]
    return spotifyUriParts

# Retrieves a specific Spotify playlist
# - sp: The Spotify client instance
# - userId: The ID of the Spotify user
# - playlistId: The ID of the Spotify playlist
# Returns: The Spotify playlist object
def getSpotifyPlaylist(sp: spotipy.client, userId: str, playlistId: str) -> []:
    playlist = retry_with_backoff(sp.user_playlist, userId, playlistId)
    return playlist

# Retrieves all playlists for a specific Spotify user
# - sp: The Spotify client instance
# - userId: The ID of the Spotify user
# Returns: A list of Spotify playlists
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

# Retrieves all tracks from a Spotify playlist
# - sp: The Spotify client instance
# - playlist: The Spotify playlist object
# Returns: A list of tracks in the playlist
def getSpotifyTracks(sp: spotipy.client, playlist: []) -> []:
    spotifyTracks = []
    tracks = playlist['tracks']
    spotifyTracks.extend(tracks['items'])
    while tracks['next']:
        tracks = retry_with_backoff(sp.next, tracks)
        spotifyTracks.extend(tracks['items'])
    return spotifyTracks