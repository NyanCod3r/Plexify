import os
import logging
import subprocess
import eyed3
from plexapi.server import PlexServer
from plexapi.audio import Track
from typing import List
from plexapi.exceptions import BadRequest, NotFound
from common_utils import filterPlexArray, createFolder
from spotify_utils import getSpotifyTracks
import spotipy

def getPlexTracks(plex: PlexServer, spotifyTracks: [], playlistName) -> List[Track]:
    plexTracks = []
    music_path = os.environ.get('MUSIC_PATH', '')
    for spotifyTrack in spotifyTracks:
        track = spotifyTrack['track']
        track_name = track['name'].title()
        artist_name = track['artists'][0]['name'].title()
        logging.debug("Searching Plex for: %s by %s" % (track_name, artist_name))
        try:
            musicTracks = plex.search(track_name, mediatype='track')
            exact_track = next((t for t in musicTracks if t.title == track_name and t.grandparentTitle == artist_name), None)
        except Exception as e:
            logging.debug(f"Issue making plex request: {str(e)}")
            continue
        if exact_track is not None:
            plexMusic = filterPlexArray(musicTracks, track['name'], track['artists'][0]['name'])
            if len(plexMusic) > 0:
                logging.debug("Found Plex Song: %s by %s" % (track['name'], track['artists'][0]['name']))
                plexTracks.append(plexMusic[0])
        else:
            logging.info("Could not find song in Plex Library: %s by %s , downloading" % (track['name'], track['artists'][0]['name']))
            sp_uri = track.get('external_urls', {}).get('spotify')
            if not sp_uri:
                logging.debug(f"No Spotify URL for track {track_name}. Skipping download.")
                continue
            createFolder(playlistName)
            try:
                output_template = os.path.join(music_path or '', playlistName, '{artist} - {title}.{output-ext}')
                command = [
                    'spotdl', '--output',
                    output_template,
                    '--download', sp_uri
                ]
                subprocess.run(command, check=True, timeout=120)

                sanitized_artist_name = artist_name.replace('/', '_').replace(':', '_').replace('?', '').replace('\\', '')
                sanitized_track_name = track_name.replace('/', '_').replace(':', '_').replace('?', '').replace('\\', '')

                downloaded_file = None
                for ext in ['mp3', 'flac', 'wav']:
                    candidate = os.path.join(music_path or '', playlistName, f"{sanitized_artist_name} - {sanitized_track_name}.{ext}")
                    if os.path.exists(candidate):
                        downloaded_file = candidate
                        found_ext = ext
                        break

                if not downloaded_file:
                    logging.warning(f"Downloaded file not found for track {track_name} in expected extensions (.mp3,.flac,.wav).")
                    continue

                # Tag mp3 files using eyed3; skip tagging for flac/wav to avoid adding new dependency
                if found_ext == 'mp3':
                    try:
                        audiofile = eyed3.load(downloaded_file)
                        if audiofile is None:
                            logging.debug(f"eyed3 could not load file {downloaded_file}")
                        else:
                            if audiofile.tag is None:
                                audiofile.initTag()
                            audiofile.tag.album_artist = artist_name
                            audiofile.tag.artist = artist_name
                            audiofile.tag.title = track_name
                            audiofile.tag.save()
                    except Exception as e:
                        logging.debug(f"Failed to tag mp3 {downloaded_file}: {str(e)}")
                else:
                    logging.debug(f"Skipping tagging for non-mp3 file: {downloaded_file}")

                # Try to locate the downloaded track in Plex by searching for the filename in music sections
                try:
                    basename = os.path.basename(downloaded_file)
                    found_in_plex = False
                    for section in plex.library.sections():
                        if section.type == 'artist' or section.type == 'album':
                            continue
                        try:
                            search_results = section.searchTracks(basename)
                            if search_results:
                                logging.debug(f"Found downloaded track in Plex section {section.title}: {basename}")
                                plexTracks.append(search_results[0])
                                found_in_plex = True
                                break
                        except Exception:
                            # ignore errors searching individual sections
                            continue
                    if not found_in_plex:
                        logging.info(f"Downloaded file {basename} not yet visible in Plex. It will be picked up on next sync after library scan.")
                except Exception as e:
                    logging.debug(f"Error searching Plex for downloaded file {downloaded_file}: {str(e)}")

            except subprocess.TimeoutExpired:
                logging.debug(f"Download timed out for song: {track_name}")
                continue
            except Exception as e:
                logging.debug(f"Issue downloading song or no song found. Error: {str(e)}")
                continue
    return plexTracks

def getPlexPlaylists(plex: PlexServer) -> List:
    return plex.playlists()

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
                plex.createPlaylist(title=playlistName, items=plexTracks)
        except (NotFound, BadRequest):
            logging.info("Something wrong for playlist %s" % playlistName)
    else:
        logging.info("No tracks found for playlist %s" % playlistName)