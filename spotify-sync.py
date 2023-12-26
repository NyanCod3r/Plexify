import re
import time
import logging
from plexapi.server import PlexServer
from plexapi.audio import Track
import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
import eyed3
from typing import List
from plexapi.exceptions import BadRequest, NotFound
import spotdl
import subprocess
import argparse

try:
    def filterPlexArray(plexItems=[], song="", artist="") -> List[Track]:
        plexItems = [
            item for item in plexItems
            if isinstance(item, Track) and
            item.title.lower() == song.lower() and
            item.artist().title.lower() == artist.lower()
        ]
        return plexItems
    
    
    def getSpotifyPlaylist(sp: spotipy.client, userId: str, playlistId: str) -> []:
        playlist = sp.user_playlist(userId, playlistId)
        return playlist
    
    
    # Returns a list of spotify playlist objects
    def getSpotifyUserPlaylists(sp: spotipy.client, userId: str) -> []:
        playlists = sp.user_playlists(userId)
        spotifyPlaylists = []
        while playlists:
            playlistItems = playlists['items']
            for i, playlist in enumerate(playlistItems):
                if playlist['owner']['id'] == userId:
                    spotifyPlaylists.append(getSpotifyPlaylist(sp, userId, playlist['id']))
            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None
        return spotifyPlaylists
    
    
    def getSpotifyTracks(sp: spotipy.client, playlist: []) -> []:
        spotifyTracks = []
        tracks = playlist['tracks']
        spotifyTracks.extend(tracks['items'])
        while tracks['next']:
            tracks = sp.next(tracks)
            spotifyTracks.extend(tracks['items'])
        return spotifyTracks
    
    
    def getPlexTracks(plex: PlexServer, spotifyTracks: [], playlistName) -> List[Track]:
        plexTracks = []
        for spotifyTrack in spotifyTracks:
            track = spotifyTrack['track']
            logging.info("Searching Plex for: %s by %s" % (track['name'], track['artists'][0]['name']))
            try:
                musicTracks = plex.search(track['name'], mediatype='track')
                exact_track = next((t for t in musicTracks if t.title == track['name'] and t.grandparentTitle == track['artists'][0]['name']), None)
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
                sp_uri=track['external_urls']['spotify']
                createFolder(playlistName)
                try:
                    command = [
                        'spotdl' , '--output',
                        os.path.join(os.environ.get('SPOTIPY_PATH'), playlistName, '{artist} - {title}.{output-ext}'),
                        '--download', sp_uri
                    ]
    
                    subprocess.run(command, check=True)
                    downloaded_file = os.environ.get('SPOTIPY_PATH') + '/' + playlistName + '/' + track['artists'][0]['name'] + ' - ' + track['name'] + '.mp3'
                    # If downloaded_file contains a question mark
                    if "?" in downloaded_file or ":" in downloaded_file:
                        downloaded_file = downloaded_file.replace("?", "")
                        downloaded_file = downloaded_file.replace(":", "-")
                        # Split the filename into the base and extension
                        base, ext = os.path.splitext(downloaded_file)
                        # Remove trailing spaces from the base
                        base = base.rstrip()
                        new_file_name = base + ext
                        os.rename(downloaded_file, new_file_name)
                        downloaded_file = new_file_name
                    audiofile = eyed3.load(downloaded_file)
                    # Check if the file has ID3 tags
                    if audiofile.tag is None:
                        # If not, create a new ID3 tag
                        audiofile.initTag()
                    # Set the artist and title tags
                    audiofile.tag.album_artist = track['artists'][0]['name']
                    audiofile.tag.artist = track['artists'][0]['name']
                    audiofile.tag.title = track['name']
                    # Save the changes
                    audiofile.tag.save()
    
                    #time.sleep(10)
                except Exception as e:
                    logging.info(f"Issue downloading song or no song found. Error: {str(e)}")
                    continue
        return plexTracks
    
    def createFolder(playlistName):
        # if playlistName not present in SPOTIPY_PATH create it
        if not os.path.exists(os.environ.get('SPOTIPY_PATH') + '/' + playlistName):
            os.makedirs(os.environ.get('SPOTIPY_PATH') + '/' + playlistName)
            logging.info('Created folder %s' % playlistName) 
        else:
            logging.info('Folder %s already exists' % playlistName)
    
    def createPlaylist(plex: PlexServer, sp: spotipy.Spotify, playlist: []):
        playlistName = playlist['name']
        logging.info('Starting playlist %s' % playlistName)
        plexTracks = getPlexTracks(plex, getSpotifyTracks(sp, playlist), playlistName)
        if len(plexTracks) > 0:
            try:
                playlistNames = [playlist.title for playlist in plex.playlists()]
                if playlistName in playlistNames:
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
    
    def parseSpotifyURI(uriString: str) -> {}:
        spotifyUriStrings = re.sub(r'^spotify:', '', uriString).split(":")
        spotifyUriParts = {}
        for i, string in enumerate(spotifyUriStrings):
            if i % 2 == 0:
                spotifyUriParts[spotifyUriStrings[i]] = spotifyUriStrings[i+1]
    
        return spotifyUriParts
    
    def delete_unmatched_files(plex: PlexServer, spotifyTracks: [], playlistName: str) -> List[Track]:
        try:
            plexPlaylist = plex.playlist(playlistName)
            plexTracks = plexPlaylist.items()
    
            # Get the list of tracks in the Spotify playlist
            spotify_tracks = [track['track']['name'] for track in spotifyTracks]
    
            # Find the tracks that are in the Plex playlist but not in the Spotify playlist
            tracks_to_delete = set(track.title for track in plexTracks) - set(spotify_tracks)
    
            # Get the Plex playlist
            plex_playlist = plex.playlist(playlistName)
    
            # For each track to delete
            for track_title in tracks_to_delete:
                # Find the track in the Plex playlist
                track = next((item for item in plexTracks if item.title == track_title), None)
    
                # If the track is in the Plex playlist
                if track is not None:
                    print('Deleting track:', track_title)
                    # Remove the track from the Plex playlist
                    plex_playlist.removeItems(track)
                    # Delete the track from the Plex library
                    track.delete()
        except Exception as e:
            logging.info(f"Issue deleting tracks from playlist: {str(e)}")
    
    
    def runSync(plex : PlexServer, sp : spotipy.Spotify, spotifyURIs: []):
        logging.info('Starting a Sync Operation')
        playlists = []
    
        for spotifyUriParts in spotifyURIs:
            if 'user' in spotifyUriParts.keys() and 'playlist' not in spotifyUriParts.keys():
                logging.info('Getting playlists for %s' % spotifyUriParts['user'])
                playlists.extend(getSpotifyUserPlaylists(sp, spotifyUriParts['user']))
            elif 'user' in spotifyUriParts.keys() and 'playlist' in spotifyUriParts.keys():
                logging.info('Getting playlist from user %s playlist id %s' % (spotifyUriParts['user'], spotifyUriParts['playlist']))
                playlists.append(getSpotifyPlaylist(sp, spotifyUriParts['user'], spotifyUriParts['playlist']))
    
        for playlist in playlists:
            createPlaylist(plex, sp, playlist)
            playlistName = playlist['name']
            delete_unmatched_files(plex, getSpotifyTracks(sp, playlist), playlistName)
        logging.info('Finished a Sync Operation')
    
    if __name__ == '__main__':
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
        spotifyUris = os.environ.get('SPOTIFY_URIS')
    
        if spotifyUris is None:
            logging.error("No spotify uris")
    
        secondsToWait = int(os.environ.get('SECONDS_TO_WAIT', 1800))
        baseurl = os.environ.get('PLEX_URL')
        token = os.environ.get('PLEX_TOKEN')
        plex = PlexServer(baseurl, token)
    
        client_credentials_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
        spotifyUris = spotifyUris.split(",")
    
    
        spotifyMainUris = []
    
        for spotifyUri in spotifyUris:
            spotifyUriParts = parseSpotifyURI(spotifyUri)
            spotifyMainUris.append(spotifyUriParts)
    
        while True:
            runSync(plex, sp, spotifyMainUris)
            time.sleep(secondsToWait)
except Exception as e:
    logging.info(f"Are you testing?: {str(e)}")