import os
import logging
import subprocess
import eyed3
from plexapi.server import PlexServer
from plexapi.audio import Track
from typing import List
from plexapi.exceptions import BadRequest, NotFound
from common_utils import filterPlexArray, createFolder  # Import the necessary functions
from spotify_utils import getSpotifyTracks
import spotipy  # Import spotipy

# Retrieves tracks from Plex that match the tracks in a Spotify playlist
# - plex: The Plex server instance
# - spotifyTracks: List of tracks from the Spotify playlist
# - playlistName: The name of the playlist
# Returns: A list of matching Plex Track objects
def getPlexTracks(plex: PlexServer, spotifyTracks: [], playlistName) -> List[Track]:
    plexTracks = []
    for spotifyTrack in spotifyTracks:
        track = spotifyTrack['track']
        track_name = track['name'].title()
        artist_name = track['artists'][0]['name'].title()
        logging.debug("Searching Plex for: %s by %s" % (track_name, artist_name))
        try:
            # Search for tracks in Plex that match the track name
            musicTracks = plex.search(track_name, mediatype='track')
            # Find the exact track that matches both the track name and artist name
            exact_track = next((t for t in musicTracks if t.title == track_name and t.grandparentTitle == artist_name), None)
        except Exception as e:
            logging.debug(f"Issue making plex request: {str(e)}")
            continue
        if exact_track is not None:
            # Filter the tracks and add the exact match to the plexTracks list
            plexMusic = filterPlexArray(musicTracks, track['name'], track['artists'][0]['name'])
            if len(plexMusic) > 0:
                logging.debug("Found Plex Song: %s by %s" % (track['name'], track['artists'][0]['name']))
                plexTracks.append(plexMusic[0])
        else:
            # Download the track from Spotify if no exact match is found
            logging.debug("Could not find song in Plex Library: %s by %s , downloading" % (track['name'], track['artists'][0]['name']))
            sp_uri = track['external_urls']['spotify']
            createFolder(playlistName)
            try:
                # Use spotdl to download the track
                command = [
                    'spotdl', '--output',
                    os.path.join(os.environ.get('SPOTIPY_PATH'), playlistName, '{artist} - {title}.{output-ext}'),
                    '--download', sp_uri
                ]
                subprocess.run(command, check=True)
                track_name = track['name'].title()
                artist_name = track['artists'][0]['name'].title()
                downloaded_file = os.environ.get('SPOTIPY_PATH') + '/' + playlistName + '/' + artist_name + ' - ' + track_name + '.mp3'
                # Handle special characters in the file name
                if "?" in downloaded_file or ":" in downloaded_file:
                    downloaded_file = downloaded_file.replace("?", "")
                    downloaded_file = downloaded_file.replace(":", "-")
                    downloaded_file = downloaded_file.replace("\\", "")
                    base, ext = os.path.splitext(downloaded_file)
                    base = base.rstrip()
                    new_file_name = f'"{base + ext}"'
                    os.rename(downloaded_file, new_file_name)
                    downloaded_file = new_file_name
                # Add metadata to the downloaded file
                audiofile = eyed3.load(downloaded_file)
                if audiofile.tag is None:
                    audiofile.initTag()
                audiofile.tag.album_artist = artist_name
                audiofile.tag.artist = artist_name
                audiofile.tag.title = track_name
                audiofile.tag.save()
            except Exception as e:
                logging.debug(f"Issue downloading song or no song found. Error: {str(e)}")
                continue
    return plexTracks

# Creates or updates a Plex playlist with tracks from a Spotify playlist
# - plex: The Plex server instance
# - sp: The Spotify client instance
# - playlist: The Spotify playlist to sync
def createPlaylist(plex: PlexServer, sp: spotipy.Spotify, playlist: []):
    playlistName = playlist['name']
    logging.info('Starting playlist %s' % playlistName)
    # Retrieve matching tracks from Plex
    plexTracks = getPlexTracks(plex, getSpotifyTracks(sp, playlist), playlistName)
    if len(plexTracks) > 0:
        try:
            # Check if the playlist already exists in Plex
            playlistNames = [playlist.title for playlist in plex.playlists()]
            if (playlistName in playlistNames):
                # Update the existing playlist
                plexPlaylist = plex.playlist(playlistName)
                logging.info('Updating playlist %s' % playlistName)
                plexPlaylist.addItems(plexTracks)
            else:
                # Create a new playlist in Plex
                logging.info("Creating playlist %s" % playlistName)
                plex.createPlaylist(title=playlistName, items=plexTracks)
        except (NotFound, BadRequest):
            logging.info("Something wrong for playlist %s" % playlistName)
    else:
        logging.info("No tracks found for playlist %s" % playlistName)

# Deletes tracks from a Plex playlist that are not in the corresponding Spotify playlist
# - plex: The Plex server instance
# - spotifyTracks: List of tracks from the Spotify playlist
# - playlistName: The name of the Plex playlist
def delete_unmatched_files(plex: PlexServer, spotifyTracks: [], playlistName: str) -> List[Track]:
    try:
        # Retrieve the Plex playlist
        plexPlaylist = plex.playlist(playlistName)
        plexTracks = plexPlaylist.items()
        # Get the list of track titles from Spotify
        spotify_tracks = [track['track']['name'] for track in spotifyTracks]
        # Identify tracks in Plex that are not in Spotify
        tracks_to_delete = set(track.title for track in plexTracks) - set(spotify_tracks)
        plex_playlist = plex.playlist(playlistName)
        for track_title in tracks_to_delete:
            # Remove unmatched tracks from the Plex playlist
            track = next((item for item in plexTracks if item.title == track_title), None)
            if track is not None:
                print('Deleting track:', track_title)
                plex_playlist.removeItems(track)
                track.delete()
    except Exception as e:
        logging.debug(f"Issue deleting tracks from playlist: {str(e)}")