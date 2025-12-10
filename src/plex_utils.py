import os
import logging
import subprocess
import eyed3
import time
import glob
from typing import List
from common_utils import createFolder
from spotify_utils import getSpotifyTracks
import spotipy

# Suppress eyed3 POPM warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='eyed3')

def find_existing_file(music_path: str, artist_name: str, track_name: str, max_depth: int = 2) -> str:
    """
    Search for existing file in music library up to max_depth levels.
    Returns full path if found, None otherwise.
    """
    # Normalize search terms (remove special chars, lowercase)
    artist_norm = artist_name.replace('/', '').replace('_', '').replace(' ', '').replace('-','').lower()
    track_norm = track_name.replace('/', '').replace('_', '').replace(' ', '').replace('-','').lower()
    
    # Search patterns for different depth levels
    patterns = [
        os.path.join(music_path, '*.mp3'),           # Root level
        os.path.join(music_path, '*', '*.mp3'),      # 1 level deep (artist folders)
        os.path.join(music_path, '*', '*', '*.mp3')  # 2 levels deep (artist/album folders)
    ]
    
    for pattern in patterns[:max_depth + 1]:
        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath).lower()
            # Remove special chars for comparison
            normalized = filename.replace('/', '').replace('_', '').replace(' ', '').replace('-','')
            
            # Check if both artist and track are in filename
            if artist_norm in normalized and track_norm in normalized:
                return filepath
    
    return None

def ensureLocalFiles(sp: spotipy.Spotify, playlist: dict):
    """
    Ensures all tracks from a Spotify playlist exist as local files.
    Downloads missing tracks to MUSIC_PATH/<playlist_name>/.
    """
    playlistName = playlist.get('name', '')
    logging.info(f'Ensuring local files for playlist: {playlistName}')
    
    music_path = os.environ.get('MUSIC_PATH', '')
    if not music_path:
        logging.error("MUSIC_PATH not set. Cannot download tracks.")
        return
    
    # Create playlist folder
    playlist_folder = os.path.join(music_path, playlistName)
    createFolder(playlistName)
    logging.info(f"📁 Target download folder: {playlist_folder}")
    
    # Get spotdl log level from env - default to INFO to avoid too much output
    spotdl_log_level = os.environ.get('SPOTDL_LOG_LEVEL', os.environ.get('LOG_LEVEL', 'INFO')).upper()
    
    # Get cookie file path if provided
    cookie_file = os.environ.get('SPOTDL_COOKIE_FILE', '')
    
    # Get delay between downloads (default 2 seconds to avoid rate limits)
    download_delay = int(os.environ.get('DOWNLOAD_DELAY', '2'))
    
    spotifyTracks = getSpotifyTracks(sp, playlist)
    logging.info(f"Processing {len(spotifyTracks)} tracks for playlist: {playlistName}")
    
    for idx, spotifyTrack in enumerate(spotifyTracks, 1):
        track = spotifyTrack.get('track')
        if not track:
            continue
            
        track_name = (track.get('name') or '').title()
        artist_name = (track.get('artists', [{}])[0].get('name') or '').title()
        
        logging.info(f"[{idx}/{len(spotifyTracks)}] Processing: {artist_name} - {track_name}")
        
        # Search for existing file in music library (up to 2 levels deep)
        existing_file = find_existing_file(music_path, artist_name, track_name, max_depth=2)
        
        if existing_file:
            logging.info(f"✓ Found existing file: {existing_file}")
            
            # Copy to playlist folder if not already there
            if not existing_file.startswith(playlist_folder):
                try:
                    import shutil
                    dest_filename = f"{artist_name.replace('/', '_')} - {track_name.replace('/', '_')}.mp3"
                    dest_path = os.path.join(playlist_folder, dest_filename)
                    
                    if not os.path.exists(dest_path):
                        shutil.copy2(existing_file, dest_path)
                        logging.info(f"📋 Copied to playlist folder: {dest_filename}")
                    
                except Exception as e:
                    logging.warning(f"⚠️  Failed to copy file: {e}")
            continue
        
        # Download the track
        sp_uri = track.get('external_urls', {}).get('spotify')
        if not sp_uri:
            logging.warning(f"⚠️  No Spotify URL available, skipping")
            continue
        
        logging.info(f"⬇️  Downloading from Spotify...")
        
        try:
            # Use RELATIVE path for output template (relative to cwd)
            output_template = '{artist} - {title}.{output-ext}'
            
            command = [
                'spotdl',
                '--output', output_template,
                '--log-level', spotdl_log_level,
                '--lyrics',  # Disable lyrics (faster)
                '--print-errors',  # Show errors immediately
            ]
            
            # Add cookie file if provided
            if cookie_file and os.path.exists(cookie_file):
                command.extend(['--cookie-file', cookie_file])
                logging.debug(f"Using cookie file: {cookie_file}")
            
            command.append(sp_uri)
            
            logging.debug(f"🚀 Running: {' '.join(command)}")
            logging.debug(f"📂 Working directory: {playlist_folder}")
            logging.info("=" * 60)
            
            # Run spotdl with UNBUFFERED output for real-time progress
            process = subprocess.Popen(
                command,
                cwd=playlist_folder,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )
            
            # Print output in real-time
            for line in iter(process.stdout.readline, ''):
                if line:
                    line = line.rstrip()
                    if line.strip():
                        logging.info(f"  spotdl: {line}")
            
            # Wait for process to complete
            return_code = process.wait(timeout=300)
            
            logging.info("=" * 60)
            
            if return_code == 0:
                # Find the downloaded file
                artist_norm = artist_name.replace('/', '').replace('_', '').replace(' ', '').lower()
                track_norm = track_name.replace('/', '').replace('_', '').replace(' ', '').lower()
                
                recent_file = None
                for f in glob.glob(os.path.join(playlist_folder, '*.mp3')):
                    if time.time() - os.path.getmtime(f) < 10:
                        filename = os.path.basename(f).lower()
                        normalized = filename.replace('/', '').replace('_', '').replace(' ', '')
                        if artist_norm in normalized and track_norm in normalized:
                            recent_file = f
                            break
                
                if recent_file:
                    file_size = os.path.getsize(recent_file) / (1024 * 1024)
                    logging.info(f"✓ Downloaded: {os.path.basename(recent_file)} ({file_size:.2f} MB)")
                    
                    # Tag the file (suppress warnings)
                    try:
                        audiofile = eyed3.load(recent_file)
                        if audiofile:
                            if not audiofile.tag:
                                audiofile.initTag()
                            audiofile.tag.album_artist = artist_name
                            audiofile.tag.artist = artist_name
                            audiofile.tag.title = track_name
                            audiofile.tag.save()
                            logging.info(f"✓ Tagged successfully")
                    except Exception as e:
                        logging.debug(f"Tagging issue (non-critical): {str(e)}")
                else:
                    logging.warning(f"⚠️  Download completed but file not found")
            else:
                logging.error(f"✗ spotdl exited with code {return_code}")
            
            # Add delay between downloads to avoid rate limits
            if idx < len(spotifyTracks) and download_delay > 0:
                logging.debug(f"Waiting {download_delay}s before next download...")
                time.sleep(download_delay)
                
        except subprocess.TimeoutExpired:
            logging.error(f"✗ Download timed out (300s)")
            try:
                process.kill()
                logging.warning(f"  Killed spotdl process")
            except:
                pass
        except Exception as e:
            logging.error(f"✗ Error: {str(e)}")
    
    logging.info("=" * 60)
    logging.info(f"✅ Finished playlist: {playlistName}")
    try:
        files = [f for f in os.listdir(playlist_folder) if f.endswith('.mp3')]
        logging.info(f"📊 Total MP3 files: {len(files)}")
    except Exception:
        logging.warning(f"Could not count files")