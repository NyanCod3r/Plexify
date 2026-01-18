from typing import List, Dict
from common_utils import createFolder
from spotify_utils import getSpotifyTracks
from plexapi.server import PlexServer

import warnings
warnings.filterwarnings('ignore', module='eyed3.id3.frames')

import logging
import os
import subprocess
import time

# Rate limiting: max 20 requests/second = 1 request per 0.05 seconds
DOWNLOAD_DELAY = float(os.environ.get('DOWNLOAD_DELAY', '0.05'))

def ensureLocalFiles(sp, playlist: dict):
    """
    Ensures that all tracks in a Spotify playlist are downloaded locally.
    
    File structure: MUSIC_PATH/<Playlist>/<Artist>/<Album>/<Track>.mp3
    """
    musicPath = os.environ.get('MUSIC_PATH')
    if not musicPath:
        logging.error("MUSIC_PATH environment variable not set.")
        return
    
    playlistName = playlist.get('name', 'Unknown Playlist')
    logging.info(f"Ensuring local files for playlist: {playlistName}")
    
    tracks = getSpotifyTracks(sp, playlist)
    
    download_queue = []
    
    safePlaylistName = sanitizeFilename(playlistName)
    playlistFolder = os.path.join(musicPath, safePlaylistName)
    
    for item in tracks:
        track = item.get('track')
        if not track:
            continue
            
        trackName = track.get('name', 'Unknown Track')
        artistName = track['artists'][0]['name'] if track.get('artists') else 'Unknown Artist'
        albumName = track.get('album', {}).get('name', 'Unknown Album')
        
        safeArtist = sanitizeFilename(artistName)
        safeAlbum = sanitizeFilename(albumName)
        safeTrack = sanitizeFilename(trackName)
        
        artistFolder = os.path.join(playlistFolder, safeArtist)
        albumFolder = os.path.join(artistFolder, safeAlbum)
        createFolder(albumFolder)
        
        trackPath = os.path.join(albumFolder, f"{safeTrack}.mp3")
        
        if os.path.exists(trackPath):
            logging.debug(f"Track already exists: {trackPath}")
            continue
        
        # Use search query instead of Spotify URL to reduce API calls
        search_query = f"{artistName} - {trackName}"
        download_queue.append((search_query, albumFolder, trackName, artistName))
    
    if download_queue:
        logging.info(f"Downloading {len(download_queue)} missing tracks...")
        logging.info(f"Rate limiting enabled: {DOWNLOAD_DELAY}s delay between downloads")
        
        for idx, (search_query, output_folder, track_name, artist_name) in enumerate(download_queue, 1):
            downloadSpotifyTrack(search_query, output_folder, track_name, artist_name)
            
            # Rate limiting: wait between downloads
            if idx < len(download_queue):
                time.sleep(DOWNLOAD_DELAY)
                
        logging.info(f"Completed downloading {len(download_queue)} tracks")
    else:
        logging.info(f"All tracks already present for playlist: {playlistName}")

def downloadSpotifyTrack(search_query: str, output_folder: str, track_name: str, artist_name: str):
    """
    Downloads a single track using spotdl with search query instead of URL.
    This reduces Spotify API calls from spotdl.
    """
    spotdl_log_level = os.environ.get('SPOTDL_LOG_LEVEL', os.environ.get('LOG_LEVEL', 'INFO'))
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    
    try:
        cmd = [
            'spotdl',
            search_query,
            '--output', output_folder,
            '--format', 'mp3',
            '--log-level', spotdl_log_level
        ]
        
        # Pass Spotify credentials to spotdl
        if client_id and client_secret:
            cmd.extend(['--client-id', client_id])
            cmd.extend(['--client-secret', client_secret])
            logging.debug(f"Passing credentials to spotdl: client_id={client_id[:8]}...")
        else:
            logging.warning("SPOTIPY_CLIENT_ID or SPOTIPY_CLIENT_SECRET not set - spotdl will use default credentials")
        
        # Log the full command for debugging
        logging.debug(f"spotdl command: {' '.join(cmd)}")
        
        logging.info(f"Downloading: {artist_name} - {track_name}")
        
        result = subprocess.run(cmd, timeout=300)
        
        if result.returncode != 0:
            logging.error(f"Failed to download: {track_name}")
        else:
            logging.info(f"Downloaded: {track_name}")
            
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout downloading: {track_name}")
    except Exception as e:
        logging.error(f"Error downloading {track_name}: {e}")

def sanitizeFilename(name: str) -> str:
    """
    Removes or replaces characters that are invalid in filenames.
    """
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()

def get_one_star_tracks(plex: PlexServer, playlist_name: str) -> List[Dict]:
    """
    Retrieves all tracks from Plex that have a 1-star rating.
    Searches in the Plex library section matching the playlist name.
    """
    logging.info(f"Fetching 1-star rated tracks from Plex library: {playlist_name}...")
    one_star_tracks = []
    
    try:
        music_library = plex.library.section(playlist_name)
        all_tracks = music_library.searchTracks()
        
        for track in all_tracks:
            if hasattr(track, 'userRating') and track.userRating == 2.0:
                one_star_tracks.append({
                    'plex_track': track,
                    'title': track.title,
                    'artist': track.artist().title if track.artist() else 'Unknown'
                })
                
        logging.info(f"Found {len(one_star_tracks)} tracks with 1-star rating in {playlist_name}.")
    except Exception as e:
        logging.error(f"Error fetching 1-star tracks from library '{playlist_name}': {e}")
    
    return one_star_tracks

def delete_plex_track(track):
    """
    Deletes a track from Plex library and the filesystem.
    """
    try:
        file_path = track.media[0].parts[0].file if track.media else None
        track_title = track.title
        
        track.delete()
        logging.info(f"Deleted from Plex library: {track_title}")
        
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")
        else:
            logging.warning(f"File not found for deletion: {file_path}")
            
    except Exception as e:
        logging.error(f"Error deleting track {track.title}: {e}")