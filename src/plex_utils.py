from typing import List, Dict
from common_utils import createFolder
from spotify_utils import getSpotifyTracks
from plexapi.server import PlexServer
from youtubesearchpython import VideosSearch

import warnings
warnings.filterwarnings('ignore', module='eyed3.id3.frames')

import logging
import os
import subprocess
import time
import mutagen
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Supported audio formats to check for existing files (FLAC first, then MP3)
SUPPORTED_FORMATS = ['.flac', '.mp3']

# In-memory cache for YouTube search results to avoid rate-limiting during a single run
youtube_url_cache = {}
spotify_client_id = os.environ.get('SPOTIPY_CLIENT_ID')
spotify_client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

class SpotifyThrottled:
    """
    A wrapper for the spotipy.Spotify client that throttles API calls.
    """
    def __init__(self, spotify_client):
        self._spotify = spotify_client
        # Default to 0.1s (10 req/s), adjustable via env var
        self.throttle_delay = float(os.environ.get('DOWNLOAD_DELAY', '0.1'))
        self.last_call_time = 0

    def __getattr__(self, name):
        attr = getattr(self._spotify, name)
        if callable(attr):
            def throttled_method(*args, **kwargs):
                current_time = time.time()
                time_since_last_call = current_time - self.last_call_time
                
                if time_since_last_call < self.throttle_delay:
                    sleep_time = self.throttle_delay - time_since_last_call
                    logging.debug(f"Throttling Spotify API call for {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                
                result = attr(*args, **kwargs)
                self.last_call_time = time.time()
                return result
            return throttled_method
        return attr

def ensureLocalFiles(sp, playlist: dict):
    """
    Ensures that all tracks in a Spotify playlist are downloaded locally.
    
    File structure: MUSIC_PATH/<Playlist>/<Artist>/<Album>/<Artist - Track>.mp3
    """
    musicPath = os.environ.get('MUSIC_PATH')
    if not musicPath:
        logging.error("❌ MUSIC_PATH environment variable not set.")
        return
    
    playlistName = playlist.get('name', 'Unknown Playlist')
    logging.info(f"📁 Ensuring local files for playlist: {playlistName}")
    
    # Wrap the Spotify client to throttle API calls
    throttled_sp = SpotifyThrottled(sp)
    tracks = getSpotifyTracks(throttled_sp, playlist)
    
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
        track_uri = track.get('uri')
        
        safeArtist = sanitizeFilename(artistName)
        safeAlbum = sanitizeFilename(albumName)
        safeTrack = sanitizeFilename(trackName)
        
        artistFolder = os.path.join(playlistFolder, safeArtist)
        albumFolder = os.path.join(artistFolder, safeAlbum)
        createFolder(albumFolder)
        
        # Define the standard filename - check for FLAC preference
        prefer_flac = os.environ.get('PREFER_FLAC', 'true').lower() in ['true', '1', 'yes']
        file_extension = 'flac' if prefer_flac else 'mp3'
        expected_filename = f"{safeArtist} - {safeTrack}.{file_extension}"
        expected_filepath = os.path.join(albumFolder, expected_filename)
        
        logging.info(f"🔎 Checking for track '{safeTrack}' in path: '{albumFolder}'")
        
        # Check if a file for this track already exists, even with a different name
        if track_exists_in_directory(albumFolder, safeTrack):
            continue
            
        # If not found by name, check by ID3 tags and rename if a match is found
        if find_and_rename_track_by_tag(albumFolder, artistName, trackName, expected_filepath):
            continue
        
        logging.warning(f"❗ Track not found locally. Queuing for download to '{expected_filepath}'")
        
        download_queue.append((track_uri, albumFolder, trackName, artistName, expected_filepath))
    
    if download_queue:
        logging.info(f"⬇️  Downloading {len(download_queue)} missing tracks...")
        
        for idx, (track_uri, output_folder, track_name, artist_name, expected_filepath) in enumerate(download_queue, 1):
            downloadSpotifyTrack(track_uri, output_folder, track_name, artist_name, expected_filepath)
            
            # Rate limiting: wait 0.1s between downloads (10 requests/sec)
            if idx < len(download_queue):
                time.sleep(0.1)
                
        logging.info(f"✅ Completed downloading {len(download_queue)} tracks")
    else:
        logging.info(f"✨ All tracks already present for playlist: {playlistName}")

def search_youtube_for_track(artist_name: str, track_name: str) -> str:
    """
    Searches YouTube for a track and returns the URL of the most likely official audio.
    Uses an in-memory cache to avoid re-querying for the same track.
    Returns None if no suitable video is found.
    """
    # Validate inputs first
    if not artist_name or not track_name:
        logging.error(f"❌ Invalid input: artist_name='{artist_name}', track_name='{track_name}'")
        return None
        
    # Sanitize the search query to prevent issues with special characters
    safe_artist = str(artist_name).strip()
    safe_track = str(track_name).strip()
    search_query = f"{safe_artist} - {safe_track}"
    
    # Check cache first
    if search_query in youtube_url_cache:
        cached_result = youtube_url_cache[search_query]
        if cached_result:
            logging.info(f"📦 Found YouTube URL in cache for: '{search_query}'")
            return cached_result
        else:
            logging.info(f"📦 Cached negative result for: '{search_query}'")
            return None

    logging.info(f"▶️  Searching YouTube for: '{search_query}'")
    
    try:
        # Use yt-dlp to search but get video IDs instead of direct URLs
        search_cmd = [
            'yt-dlp',
            '--get-id',  # Get video IDs instead of URLs
            '--no-playlist',
            f'ytsearch5:{search_query}'
        ]
        
        search_process = subprocess.run(search_cmd, capture_output=True, text=True, timeout=30)
        
        if search_process.returncode == 0 and search_process.stdout.strip():
            video_ids = search_process.stdout.strip().split('\n')
            if video_ids and video_ids[0]:
                # Construct proper YouTube URL from video ID
                first_video_id = video_ids[0]
                youtube_url = f"https://www.youtube.com/watch?v={first_video_id}"
                logging.info(f"🎯 Found YouTube URL via yt-dlp search: {youtube_url}")
                youtube_url_cache[search_query] = youtube_url
                return youtube_url
        
        # If yt-dlp search fails, try the original method with better error handling
        logging.info(f"🔄 yt-dlp search failed, trying YoutubeSearchPython...")
        videos_search = VideosSearch(safe_artist + " " + safe_track, limit=5)
        
        # Get results with additional validation
        search_result = videos_search.result()
        if not search_result or not isinstance(search_result, dict):
            logging.warning(f"❓ Invalid search result structure for '{search_query}'")
            youtube_url_cache[search_query] = None
            return None
            
        results = search_result.get('result', [])
        
        if not results:
            logging.warning(f"❓ No YouTube results found for '{search_query}'")
            youtube_url_cache[search_query] = None
            return None
            
        # Just take the first valid result to avoid complexity
        for video in results:
            if video and isinstance(video, dict) and video.get('link'):
                video_url = video['link']
                logging.info(f"⚠️  Using first available result: {video_url}")
                youtube_url_cache[search_query] = video_url
                return video_url
        
        logging.warning(f"❓ No valid YouTube results found for '{search_query}'")
        youtube_url_cache[search_query] = None
        return None
        
    except subprocess.TimeoutExpired:
        logging.error(f"⏰ YouTube search timeout for '{search_query}'")
        youtube_url_cache[search_query] = None
        return None
    except TypeError as e:
        logging.error(f"💥 Type error in YouTube library for '{search_query}': {e}")
        logging.error(f"🔍 This is a known issue with YoutubeSearchPython library")
        youtube_url_cache[search_query] = None
        return None
    except Exception as e:
        logging.error(f"💥 General error searching YouTube for '{search_query}': {e}")
        youtube_url_cache[search_query] = None
        return None

def normalize_for_matching(text: str) -> str:
    """
    Normalize text for fuzzy matching by removing special characters and converting to lowercase.
    Handles cases like "AC/DC" -> "acdc", "Ac-Dc" -> "acdc", etc.
    """
    if not text:
        return ""
    
    # Convert to lowercase and remove common separators and punctuation
    normalized = text.lower()
    # Remove these characters: / \ - _ . : ; , ( ) [ ] ' "
    chars_to_remove = '/\\-_.,:;()[]\'\"'
    for char in chars_to_remove:
        normalized = normalized.replace(char, '')
    
    # Remove extra spaces
    normalized = ' '.join(normalized.split())
    
    return normalized

def track_exists_in_directory(folder: str, track_title: str) -> bool:
    """
    Checks if FLAC first, then MP3 exists for the track.
    Uses both filename and metadata matching for better accuracy.
    """
    try:
        normalized_track = normalize_for_matching(track_title)
        
        # Check for FLAC first
        for filename in os.listdir(folder):
            name_lower = filename.lower()
            if name_lower.endswith('.flac'):
                # Check filename match (extract track name from "Artist - Track.flac")
                if ' - ' in filename:
                    filename_track = filename.split(' - ', 1)[1].rsplit('.', 1)[0]
                    if normalize_for_matching(filename_track) == normalized_track:
                        logging.debug(f"✅ Found existing FLAC by filename: '{filename}'")
                        return True
                
                # Also check metadata if filename match fails
                try:
                    filepath = os.path.join(folder, filename)
                    audiofile = mutagen.File(filepath, easy=True)
                    if audiofile:
                        tag_title = audiofile.get('title', [None])[0]
                        if tag_title and normalize_for_matching(tag_title) == normalized_track:
                            logging.debug(f"✅ Found existing FLAC by metadata: '{filename}'")
                            return True
                except:
                    pass  # Skip files with bad metadata
        
        # Then check for MP3
        for filename in os.listdir(folder):
            name_lower = filename.lower()
            if name_lower.endswith('.mp3'):
                # Check filename match
                if ' - ' in filename:
                    filename_track = filename.split(' - ', 1)[1].rsplit('.', 1)[0]
                    if normalize_for_matching(filename_track) == normalized_track:
                        logging.debug(f"✅ Found existing MP3 by filename: '{filename}'")
                        return True
                
                # Also check metadata if filename match fails
                try:
                    filepath = os.path.join(folder, filename)
                    audiofile = mutagen.File(filepath, easy=True)
                    if audiofile:
                        tag_title = audiofile.get('title', [None])[0]
                        if tag_title and normalize_for_matching(tag_title) == normalized_track:
                            logging.debug(f"✅ Found existing MP3 by metadata: '{filename}'")
                            return True
                except:
                    pass  # Skip files with bad metadata
                
    except FileNotFoundError:
        return False
    return False

def find_and_rename_track_by_tag(folder: str, artist_name: str, track_title: str, expected_filepath: str) -> bool:
    """
    Scans audio files in a directory, checks their metadata for a match,
    and renames the file if a match is found. Only supports FLAC and MP3.
    Uses normalized matching to handle artist name variations.
    """
    try:
        normalized_artist = normalize_for_matching(artist_name)
        normalized_track = normalize_for_matching(track_title)
        
        for filename in os.listdir(folder):
            # Only check FLAC and MP3 files
            if not (filename.lower().endswith('.flac') or filename.lower().endswith('.mp3')):
                continue

            current_filepath = os.path.join(folder, filename)
            
            try:
                audiofile = mutagen.File(current_filepath, easy=True)
                if not audiofile:
                    continue
            except Exception as e:
                logging.warning(f"⚠️  Could not read metadata for '{filename}': {e}")
                continue

            tag_artist = audiofile.get('artist', [None])[0]
            tag_title = audiofile.get('title', [None])[0]

            if tag_artist and tag_title:
                # Use normalized matching for both artist and title
                if (normalize_for_matching(tag_artist) == normalized_artist and 
                    normalize_for_matching(tag_title) == normalized_track):
                    
                    logging.info(f"✅ Found track by metadata tag: '{filename}' (Artist: '{tag_artist}' -> '{artist_name}', Title: '{tag_title}' -> '{track_title}')")
                    
                    if current_filepath != expected_filepath:
                        logging.warning(f"🎨 Renaming '{filename}' to '{os.path.basename(expected_filepath)}'")
                        os.rename(current_filepath, expected_filepath)
                    
                    return True
    except FileNotFoundError:
        return False
    except Exception as e:
        logging.error(f"❌ Error processing metadata in '{folder}': {e}")
    
    return False

def downloadSpotifyTrack(track_uri: str, output_folder: str, track_name: str, artist_name: str, expected_filepath: str):
    """
    Downloads a single track using YouTube search + yt-dlp.
    Format determined by PREFER_FLAC environment variable (default: true).
    """
    download_stats['downloads_attempted'] += 1
    spotdl_log_level = os.environ.get('SPOTDL_LOG_LEVEL', os.environ.get('LOG_LEVEL', 'INFO')).upper()
    prefer_flac = os.environ.get('PREFER_FLAC', 'true').lower() in ['true', '1', 'yes']
    formats_tried = []
    
    # Get list of files before download
    files_before = set()
    if os.path.exists(output_folder):
        files_before = set(os.listdir(output_folder))
    
    # Try YouTube search approach
    logging.info(f"🔄 Using YouTube search for '{artist_name} - {track_name}'")
    
    youtube_url = search_youtube_for_track(artist_name, track_name)
    if youtube_url:
        try:
            output_filename = f"{sanitizeFilename(artist_name)} - {sanitizeFilename(track_name)}.%(ext)s"
            output_path = os.path.join(output_folder, output_filename)
            
            if prefer_flac:
                # Try FLAC first, fallback to MP3 if FLAC fails
                formats_tried.append('FLAC')
                cmd = [
                    'yt-dlp',
                    '--format', 'bestaudio[ext=flac]/bestaudio[acodec*=flac]/bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=480]',
                    '--extract-audio',
                    '--audio-format', 'flac',
                    '--audio-quality', '0',  # Best quality
                    '--output', output_path,
                    '--no-playlist',
                    '--embed-metadata',
                    '--ignore-errors',
                    '--no-post-overwrites',
                    '--prefer-free-formats',
                ]
                
                logging.info(f"🎵 Requesting FLAC output for '{artist_name} - {track_name}'")
            else:
                # MP3 only mode
                formats_tried.append('MP3')
                cmd = [
                    'yt-dlp',
                    '--format', 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=480]',
                    '--extract-audio',
                    '--audio-format', 'mp3',
                    '--audio-quality', '0',  # Best quality
                    '--output', output_path,
                    '--no-playlist',
                    '--embed-metadata',
                    '--ignore-errors',
                    '--no-post-overwrites',
                    '--prefer-free-formats',
                ]
                
                logging.info(f"🎵 Requesting MP3 output for '{artist_name} - {track_name}'")
            
            # Try to specify ffmpeg path explicitly if available
            ffmpeg_path = None
            try:
                ffmpeg_result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
                if ffmpeg_result.returncode == 0:
                    ffmpeg_path = ffmpeg_result.stdout.strip()
                    cmd.extend(['--ffmpeg-location', ffmpeg_path])
            except:
                pass
            
            # Add verbosity based on log level
            if spotdl_log_level == 'DEBUG':
                cmd.extend(['--verbose'])
                logging.debug(f"💻 yt-dlp command: {' '.join(cmd + [youtube_url])}")
            elif spotdl_log_level in ['ERROR', 'WARNING']:
                cmd.extend(['--quiet'])
            else:
                cmd.extend(['--no-warnings'])
            
            cmd.append(youtube_url)
            
            logging.info(f"⬇️  Downloading via yt-dlp: {youtube_url}")
            
            # Capture output based on log level
            capture_output = spotdl_log_level != 'DEBUG'
            
            process = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=300)
            
            if process.returncode == 0:
                # Check what files were actually created
                files_after = set()
                if os.path.exists(output_folder):
                    files_after = set(os.listdir(output_folder))
                
                new_files = files_after - files_before
                audio_files = [f for f in new_files if f.lower().endswith('.flac') or f.lower().endswith('.mp3')]
                
                if audio_files:
                    for audio_file in audio_files:
                        if audio_file.lower().endswith('.flac'):
                            logging.info(f"🎵 Successfully downloaded FLAC: {audio_file}")
                            track_download_success()
                        else:
                            logging.info(f"✅ Successfully downloaded MP3: {audio_file}")
                            track_download_success()
                    return True
                else:
                    if prefer_flac:
                        logging.warning(f"⚠️  FLAC download failed, trying MP3 fallback...")
                    else:
                        logging.warning(f"⚠️  MP3 download failed")
                        track_download_failure()
                        return False
            
            # If FLAC failed and we're in FLAC mode, try MP3 fallback
            if prefer_flac:
                formats_tried.append('MP3 (fallback)')
                logging.info(f"🔄 FLAC download failed, trying MP3 fallback for '{artist_name} - {track_name}'")
                
                cmd_mp3 = [
                    'yt-dlp',
                    '--format', 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=480]',
                    '--extract-audio',
                    '--audio-format', 'mp3',
                    '--audio-quality', '0',
                    '--output', output_path,
                    '--no-playlist',
                    '--embed-metadata',
                    '--ignore-errors',
                    '--no-post-overwrites',
                    '--prefer-free-formats',
                ]
                
                if ffmpeg_path:
                    cmd_mp3.extend(['--ffmpeg-location', ffmpeg_path])
                
                if spotdl_log_level == 'DEBUG':
                    cmd_mp3.extend(['--verbose'])
                elif spotdl_log_level in ['ERROR', 'WARNING']:
                    cmd_mp3.extend(['--quiet'])
                else:
                    cmd_mp3.extend(['--no-warnings'])
                
                cmd_mp3.append(youtube_url)
                
                process_mp3 = subprocess.run(cmd_mp3, capture_output=capture_output, text=True, timeout=300)
                
                if process_mp3.returncode == 0:
                    files_after = set()
                    if os.path.exists(output_folder):
                        files_after = set(os.listdir(output_folder))
                    
                    new_files = files_after - files_before
                    audio_files = [f for f in new_files if f.lower().endswith('.flac') or f.lower().endswith('.mp3')]
                    
                    if audio_files:
                        for audio_file in audio_files:
                            logging.info(f"✅ Successfully downloaded MP3 fallback: {audio_file}")
                            track_download_success()
                        return True
                
        except subprocess.TimeoutExpired:
            logging.error(f"⏰ yt-dlp timeout for {artist_name} - {track_name}")
            formats_tried.append('YouTube (timeout)')
        except Exception as e:
            logging.error(f"💥 yt-dlp error: {e}")
            formats_tried.append('YouTube (error)')
    
    # If YouTube approach fails completely, try spotdl as last resort
    formats_tried.append('spotdl')
    logging.warning(f"🔄 YouTube download failed, trying spotdl as last resort for '{artist_name} - {track_name}'")
    
    try:
        output_template = os.path.join(output_folder, "{artists} - {title}.{output-ext}")
        
        cmd = [
            'python', '-m', 'spotdl',
            '--client-id', spotify_client_id,
            '--client-secret', spotify_client_secret,
            'download', track_uri,
            '--output', output_template,
            '--format', 'flac' if prefer_flac else 'mp3',
            '--overwrite', 'skip',
            '--audio', 'youtube',
            '--no-cache',
            '--dont-filter-results',
            '--log-level', spotdl_log_level,
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if process.returncode == 0:
            files_after = set()
            if os.path.exists(output_folder):
                files_after = set(os.listdir(output_folder))
            
            new_files = files_after - files_before
            audio_files = [f for f in new_files if f.lower().endswith('.flac') or f.lower().endswith('.mp3')]
            
            if audio_files:
                format_used = 'flac' if any(f.lower().endswith('.flac') for f in audio_files) else 'mp3'
                logging.info(f"✅ spotdl succeeded: {', '.join(audio_files)}")
                track_download_success()
                return True
        
        logging.error(f"❌ All download methods failed for '{artist_name} - {track_name}'")
        track_download_failure()
        return False
        
    except Exception as e:
        logging.error(f"💥 Final download attempt failed: {e}")
        track_download_failure()
        return False

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
    logging.info(f"🔍 Fetching 1-star rated tracks from Plex library: {playlist_name}...")
    one_star_tracks = []
    
    try:
        music_library = plex.library.section(playlist_name)
        all_tracks = music_library.searchTracks()
        
        for track in all_tracks:
            if hasattr(track, 'userRating') and track.userRating in [1.0, 2.0]:
                one_star_tracks.append({
                    'plex_track': track,
                    'title': track.title,
                    'artist': track.artist().title if track.artist() else 'Unknown'
                })
                
        logging.info(f"📊 Found {len(one_star_tracks)} tracks with 1-star rating in {playlist_name}.")
    except Exception as e:
        logging.error(f"❌ Error fetching 1-star tracks from library '{playlist_name}': {e}")
    
    return one_star_tracks

def delete_plex_track(track, playlist_name: str = "Unknown"):
    """
    Deletes a track from Plex library and the filesystem.
    Tracks success/failure for recap.
    """
    failed_platforms = []
    artist_name = track.artist().title if track.artist() else 'Unknown Artist'
    track_title = track.title
    
    try:
        file_path = track.media[0].parts[0].file if track.media else None
        
        # Try to delete from Plex library
        try:
            track.delete()
            logging.info(f"🗑️  Deleted from Plex library: {track_title}")
        except Exception as e:
            logging.error(f"❌ Failed to delete from Plex library: {track_title} - {e}")
            failed_platforms.append('Plex')
        
        # Track result
        if failed_platforms:
            track_deletion_failure()
        else:
            track_deletion_success()
            
    except Exception as e:
        logging.error(f"❌ Error deleting track {track_title}: {e}")
        track_deletion_failure()

# Global statistics tracking
download_stats = {
    'downloads_attempted': 0,
    'downloads_successful': 0,
    'downloads_failed': 0,
    'tracks_deleted': 0,
    'delete_failures': 0
}

def reset_stats():
    """Reset statistics for a new sync cycle."""
    global download_stats
    download_stats = {
        'downloads_attempted': 0,
        'downloads_successful': 0,
        'downloads_failed': 0,
        'tracks_deleted': 0,
        'delete_failures': 0
    }

def track_download_success():
    """Track a successful download."""
    download_stats['downloads_successful'] += 1

def track_download_failure():
    """Track a failed download."""
    download_stats['downloads_failed'] += 1

def track_deletion_success():
    """Track a successful deletion."""
    download_stats['tracks_deleted'] += 1

def track_deletion_failure():
    """Track a failed deletion."""
    download_stats['delete_failures'] += 1

def print_sync_recap():
    """Print comprehensive sync statistics."""
    print("\n" + "="*60)
    print("🎵 SYNC CYCLE RECAP")
    print("="*60)
    print(f"📊 Downloads Attempted: {download_stats['downloads_attempted']}")
    print(f"✅ Downloads Successful: {download_stats['downloads_successful']}")
    print(f"❌ Downloads Failed: {download_stats['downloads_failed']}")
    print(f"🗑️  Tracks Deleted: {download_stats['tracks_deleted']}")
    print(f"💥 Delete Failures: {download_stats['delete_failures']}")
    
    if download_stats['downloads_attempted'] > 0:
        success_rate = (download_stats['downloads_successful'] / download_stats['downloads_attempted']) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print("="*60 + "\n")