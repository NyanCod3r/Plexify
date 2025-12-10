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
    # Use separate SPOTDL_LOG_LEVEL or default to same as LOG_LEVEL
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
        
        # Check if file already exists with flexible matching
        # Look for any file matching "artist - title.mp3" (case-insensitive, ignore special chars)
        artist_pattern = artist_name.replace('/', '').replace('_', '').replace(' ', '').lower()
        track_pattern = track_name.replace('/', '').replace('_', '').replace(' ', '').lower()
        
        file_exists = False
        for existing_file in glob.glob(os.path.join(playlist_folder, '*.mp3')):
            filename = os.path.basename(existing_file).lower()
            # Remove special chars and spaces for comparison
            normalized = filename.replace('/', '').replace('_', '').replace(' ', '')
            
            if artist_pattern in normalized and track_pattern in normalized:
                logging.info(f"✓ File already exists: {os.path.basename(existing_file)}")
                file_exists = True
                break
        
        if file_exists:
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
                bufsize=0,  # Unbuffered
                universal_newlines=True,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}  # Force Python unbuffered
            )
            
            # Print output in real-time
            for line in iter(process.stdout.readline, ''):
                if line:
                    line = line.rstrip()
                    # Filter out empty lines
                    if line.strip():
                        logging.info(f"  spotdl: {line}")
            
            # Wait for process to complete
            return_code = process.wait(timeout=300)
            
            logging.info("=" * 60)
            
            if return_code == 0:
                # Find the downloaded file (spotdl may name it differently)
                new_files = glob.glob(os.path.join(playlist_folder, '*.mp3'))
                # Look for files modified in the last 10 seconds
                import time as time_module
                recent_file = None
                for f in new_files:
                    if time_module.time() - os.path.getmtime(f) < 10:
                        filename = os.path.basename(f).lower()
                        normalized = filename.replace('/', '').replace('_', '').replace(' ', '')
                        if artist_pattern in normalized and track_pattern in normalized:
                            recent_file = f
                            break
                
                if recent_file:
                    file_size = os.path.getsize(recent_file) / (1024 * 1024)
                    logging.info(f"✓ Downloaded: {os.path.basename(recent_file)} ({file_size:.2f} MB)")
                    
                    # Tag the file
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
                        logging.warning(f"⚠️  Failed to tag: {str(e)}")
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