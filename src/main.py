"""
main.py - Entry point for Plexify

Downloads tracks from Spotify playlists to local filesystem.
No Plex playlist operations - use Plex Smart Playlists instead.
"""

import os
import logging
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from plexapi.server import PlexServer

from utils import runSync, parseSpotifyURI
from plex_utils import get_one_star_tracks, delete_plex_track
from spotify_utils import removeTrackFromPlaylist

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=log_level
)

logging.info("Starting Plexify...")

# Entry point of the application
def main():
    spotify_client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    spotify_client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    spotify_uris = os.environ.get('SPOTIFY_URIS', '').split(',')

    if not spotify_client_id or not spotify_client_secret:
        logging.error("Spotify credentials not set. Exiting.")
        return

    if not spotify_uris or spotify_uris == ['']:
        logging.error("SPOTIFY_URIS not set. Exiting.")
        return

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        redirect_uri='http://localhost:8888/callback',
        scope='playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'
    ))

    logging.info("Successfully authenticated with Spotify.")

    plex_url = os.environ.get('PLEX_URL')
    plex_token = os.environ.get('PLEX_TOKEN')

    if not plex_url or not plex_token:
        logging.error("Plex credentials not set. Exiting.")
        return

    plex = PlexServer(plex_url, plex_token)
    logging.info("Successfully connected to Plex.")

    parsed_uris = [parseSpotifyURI(uri.strip()) for uri in spotify_uris]
    seconds_to_wait = int(os.environ.get('SECONDS_TO_WAIT', 3600))

    while True:
        try:
            # Sync playlists from Spotify
            synced_playlists = runSync(sp, parsed_uris)
            
            # Process 1-star deletions for each synced playlist
            process_one_star_deletions(plex, sp, synced_playlists)
            
            logging.info(f"Waiting {seconds_to_wait} seconds before next sync...")
            time.sleep(seconds_to_wait)
        except KeyboardInterrupt:
            logging.info("Shutting down Plexify.")
            break
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(60)

def process_one_star_deletions(plex: PlexServer, sp: spotipy.Spotify, playlists: list):
    """
    Check all Plex libraries for 1-star rated tracks and remove them from both Plex and Spotify.
    """
    logging.info("Checking for 1-star rated tracks across all playlists...")
    
    total_deleted = 0
    
    for playlist in playlists:
        playlist_name = playlist.get('name', 'Unknown')
        playlist_id = playlist.get('id')
        
        if not playlist_id:
            logging.warning(f"Skipping playlist '{playlist_name}' - no ID found")
            continue
        
        # Get 1-star tracks from Plex library (library name = playlist name)
        one_star_tracks = get_one_star_tracks(plex, playlist_name)
        
        if not one_star_tracks:
            logging.debug(f"No 1-star tracks found in playlist: {playlist_name}")
            continue
        
        logging.info(f"Found {len(one_star_tracks)} 1-star tracks in '{playlist_name}'")
        
        for track_info in one_star_tracks:
            plex_track = track_info['plex_track']
            track_title = track_info['title']
            track_artist = track_info['artist']
            
            # Find matching Spotify track in the playlist
            spotify_track_id = find_spotify_track_in_playlist(sp, playlist, track_title, track_artist)
            
            if spotify_track_id:
                # Remove from Spotify playlist
                try:
                    removeTrackFromPlaylist(sp, playlist_id, spotify_track_id)
                    logging.info(f"Removed '{track_artist} - {track_title}' from Spotify playlist '{playlist_name}'")
                except Exception as e:
                    logging.error(f"Failed to remove from Spotify: {e}")
                    continue
            else:
                logging.warning(f"Could not find '{track_artist} - {track_title}' in Spotify playlist '{playlist_name}'")
            
            # Delete from Plex library and filesystem
            try:
                delete_plex_track(plex_track)
                total_deleted += 1
            except Exception as e:
                logging.error(f"Failed to delete from Plex: {e}")
    
    if total_deleted > 0:
        logging.info(f"Completed 1-star cleanup: {total_deleted} tracks deleted")
    else:
        logging.info("No 1-star tracks to delete")

def find_spotify_track_in_playlist(sp: spotipy.Spotify, playlist: dict, track_title: str, track_artist: str) -> str:
    """
    Find a Spotify track ID in a playlist by matching title and artist.
    Returns the track ID if found, None otherwise.
    """
    tracks = playlist.get('tracks', {}).get('items', [])
    
    # Normalize strings for comparison
    normalized_title = track_title.lower().strip()
    normalized_artist = track_artist.lower().strip()
    
    for item in tracks:
        track = item.get('track')
        if not track:
            continue
        
        spotify_title = track.get('name', '').lower().strip()
        spotify_artists = track.get('artists', [])
        
        # Check if title matches
        if normalized_title != spotify_title:
            continue
        
        # Check if any artist matches
        for artist in spotify_artists:
            if normalized_artist == artist.get('name', '').lower().strip():
                return track.get('id')
    
    return None

if __name__ == '__main__':
    main()