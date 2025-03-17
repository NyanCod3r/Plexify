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

def getPlexTracks(plex: PlexServer, spotifyTracks: [], playlistName) -> List[Track]:
    plexTracks = []
    for spotifyTrack in spotifyTracks:
        track = spotifyTrack['track']
        track_name = track['name'].title()
        artist_name = track['artists'][0]['name'].title()
        logging.info("Searching Plex for: %s by %s" % (track_name, artist_name))
        try:
            musicTracks = plex.search(track_name, mediatype='track')
            exact_track = next((t for t in musicTracks if t.title == track_name and t.grandparentTitle == artist_name), None)
        except Exception as e:
            logging.info(f"Issue making plex request: {str(e)}")
            continue
        if exact_track is not None:
            plexMusic = filterPlexArray(musicTracks, track['name'], track['artists'][0]['name'])
            if len(plexMusic) > 0:
                logging.info("Found Plex Song: %s by %s" % (track['name'], track['artists'][0]['name']))
                plexTracks.append(plexMusic[0])
        else:
            logging.info("Could not find song in Plex Library: %s by %s , downloading" % (track['name'], track['artists'][0]['name']))
            sp_uri = track['external_urls']['spotify']
            createFolder(playlistName)
            try:
                command = [
                    'spotdl', '--output',
                    os.path.join(os.environ.get('SPOTIPY_PATH'), playlistName, '{artist} - {title}.{output-ext}'),
                    '--download', sp_uri
                ]
                subprocess.run(command, check=True)
                track_name = track['name'].title()
                artist_name = track['artists'][0]['name'].title()
                downloaded_file = os.environ.get('SPOTIPY_PATH') + '/' + playlistName + '/' + artist_name + ' - ' + track_name + '.mp3'
                if "?" in downloaded_file or ":" in downloaded_file:
                    downloaded_file = downloaded_file.replace("?", "")
                    downloaded_file = downloaded_file.replace(":", "-")
                    base, ext = os.path.splitext(downloaded_file)
                    base = base.rstrip()
                    new_file_name = base + ext
                    os.rename(downloaded_file, new_file_name)
                    downloaded_file = new_file_name
                audiofile = eyed3.load(downloaded_file)
                if audiofile.tag is None:
                    audiofile.initTag()
                audiofile.tag.album_artist = artist_name
                audiofile.tag.artist = artist_name
                audiofile.tag.title = track_name
                audiofile.tag.save()
            except Exception as e:
                logging.info(f"Issue downloading song or no song found. Error: {str(e)}")
                continue
    return plexTracks

def createPlaylist(plex: PlexServer, sp: spotipy.Spotify, playlist: []):
    playlistName = playlist['name']
    logging.info('Starting playlist %s' % playlistName)
    plexTracks = getPlexTracks(plex, getSpotifyTracks(sp, playlist), playlistName)
    if len(plexTracks) > 0:
        try:
            playlistNames = [playlist.title for playlist in plex.playlists()]
            if (playlistName in playlistNames):
                plexPlaylist = plex.playlist(playlistName)
                logging.info('Updating playlist %s' % playlistName)
                plexPlaylist.addItems(plexTracks)
            else:
                logging.info("Creating playlist %s" % playlistName)
                first_track = plexTracks[0]
                library_name = playlistName
                library_section = plex.library.section(library_name)
                items_to_add = library_section.search()
                plex.createPlaylist(title=playlistName, items=plexTracks)
        except (NotFound, BadRequest):
            logging.info("Something wrong for playlist %s" % playlistName)
    else:
        logging.info("No tracks found for playlist %s" % playlistName)

def delete_unmatched_files(plex: PlexServer, spotifyTracks: [], playlistName: str) -> List[Track]:
    try:
        plexPlaylist = plex.playlist(playlistName)
        plexTracks = plexPlaylist.items()
        spotify_tracks = [track['track']['name'] for track in spotifyTracks]
        tracks_to_delete = set(track.title for track in plexTracks) - set(spotify_tracks)
        plex_playlist = plex.playlist(playlistName)
        for track_title in tracks_to_delete:
            track = next((item for item in plexTracks if item.title == track_title), None)
            if track is not None:
                print('Deleting track:', track_title)
                plex_playlist.removeItems(track)
                track.delete()
    except Exception as e:
        logging.info(f"Issue deleting tracks from playlist: {str(e)}")