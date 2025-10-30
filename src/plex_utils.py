# ...existing code...
import os
import logging
import subprocess
import eyed3
from plexapi.server import PlexServer
from plexapi.audio import Track
from typing import List
from plexapi.exceptions import BadRequest, NotFound
from common_utils import filterPlexArray, createFolder, download_throttle
from spotify_utils import getSpotifyTracks
import spotipy

def _track_identity_from_plex(track: Track) -> tuple:
    title = (getattr(track, "title", "") or "").strip().lower()
    artist = ""
    try:
        artist = (track.grandparentTitle or "").strip().lower()
    except Exception:
        try:
            artist = (track.artist().title or "").strip().lower()
        except Exception:
            artist = ""
    return (title, artist)

def _track_identity_from_spotify_item(spotify_item: dict) -> tuple:
    track = spotify_item.get('track') or {}
    title = (track.get('name') or "").strip().lower()
    artist = (track.get('artists') or [{}])[0].get('name', "")
    artist = (artist or "").strip().lower()
    return (title, artist)

def _safely_delete_local_file(path: str, music_root: str):
    try:
        if not path:
            return False
        if not music_root:
            return False
        path_abs = os.path.abspath(path)
        music_root_abs = os.path.abspath(music_root)
        if not path_abs.startswith(music_root_abs):
            logging.debug(f"Skipping deletion of {path_abs}: outside MUSIC_PATH {music_root_abs}")
            return False
        if os.path.exists(path_abs):
            os.remove(path_abs)
            logging.info(f"Deleted local file: {path_abs}")
            return True
        return False
    except Exception as e:
        logging.debug(f"Failed to delete local file {path}: {str(e)}")
        return False

def getPlexTracks(plex: PlexServer, spotifyTracks: [], playlistName) -> List[Track]:
    plexTracks = []
    music_path = os.environ.get('MUSIC_PATH', '')
    for spotifyTrack in spotifyTracks:
        track = spotifyTrack.get('track')
        if not track:
            continue
        track_name = (track.get('name') or '').title()
        artist_name = (track.get('artists', [{}])[0].get('name') or '').title()
        logging.debug("Searching Plex for: %s by %s" % (track_name, artist_name))
        try:
            musicTracks = plex.search(track_name, mediatype='track')
            exact_track = next((t for t in musicTracks if t.title == track_name and getattr(t, 'grandparentTitle', None) == artist_name), None)
        except Exception as e:
            logging.debug(f"Issue making plex request: {str(e)}")
            continue

        if exact_track is not None:
            plexMusic = filterPlexArray(musicTracks, track.get('name', ''), track.get('artists', [{}])[0].get('name', ''))
            if len(plexMusic) > 0:
                logging.debug("Found Plex Song: %s by %s" % (track.get('name', ''), track.get('artists', [{}])[0].get('name', '')))
                plexTracks.append(plexMusic[0])
            continue

        logging.info("Could not find song in Plex Library: %s by %s , downloading" % (track.get('name', ''), track.get('artists', [{}])[0].get('name', '')))
        sp_uri = track.get('external_urls', {}).get('spotify')
        if not sp_uri:
            logging.debug(f"No Spotify URL for track {track_name}. Skipping download.")
            continue

        createFolder(playlistName)
        try:
            output_template = os.path.join(music_path or '', playlistName, '{artist} - {title}.{output-ext}')
            download_throttle.acquire()
            command = [
                'spotdl', '--output',
                output_template,
                '--download', sp_uri
            ]
            subprocess.run(command, check=True, timeout=120)

            sanitized_artist_name = artist_name.replace('/', '_').replace(':', '_').replace('?', '').replace('\\', '')
            sanitized_track_name = track_name.replace('/', '_').replace(':', '_').replace('?', '').replace('\\', '')

            downloaded_file = os.path.join(music_path or '', playlistName, f"{sanitized_artist_name} - {sanitized_track_name}.mp3")
            if os.path.exists(downloaded_file):
                try:
                    audiofile = eyed3.load(downloaded_file)
                    if audiofile is not None:
                        if audiofile.tag is None:
                            audiofile.initTag()
                        audiofile.tag.album_artist = artist_name
                        audiofile.tag.artist = artist_name
                        audiofile.tag.title = track_name
                        audiofile.tag.save()
                except Exception as e:
                    logging.debug(f"Failed to tag mp3 {downloaded_file}: {str(e)}")
            else:
                logging.debug(f"Downloaded file not found at expected path: {downloaded_file}")

            try:
                basename = os.path.basename(downloaded_file)
                for section in plex.library.sections():
                    if getattr(section, "type", None) in ('artist', 'album'):
                        continue
                    try:
                        search_results = section.searchTracks(basename)
                        if search_results:
                            plexTracks.append(search_results[0])
                            break
                    except Exception:
                        continue
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
    playlistName = playlist.get('name', '')
    logging.info('Starting playlist %s' % playlistName)
    desired_plex_tracks = getPlexTracks(plex, getSpotifyTracks(sp, playlist), playlistName)

    desired_identities = { _track_identity_from_plex(t) for t in desired_plex_tracks }
    special_names = {'discover weekly', 'release radar'}
    is_bidirectional = playlistName.strip().lower() in special_names
    music_root = os.environ.get('MUSIC_PATH', '')

    try:
        playlistNames = [p.title for p in plex.playlists()]
        if playlistName in playlistNames:
            plexPlaylist = plex.playlist(playlistName)
            logging.info('Updating playlist %s' % playlistName)

            existing_items = list(plexPlaylist.items())
            existing_id_map = { _track_identity_from_plex(item): item for item in existing_items }

            if is_bidirectional:
                # Remove items in Plex but not in Spotify (1:1)
                to_remove_identities = [idt for idt in existing_id_map.keys() if idt not in desired_identities]
                to_remove_items = [existing_id_map[idt] for idt in to_remove_identities]

                if to_remove_items:
                    logging.info("Removing %d tracks from Plex playlist %s to match Spotify (1:1)" % (len(to_remove_items), playlistName))
                    try:
                        plexPlaylist.removeItems(to_remove_items)
                    except Exception as e:
                        logging.debug(f"Failed to remove items from playlist {playlistName}: {str(e)}")

                    # Delete underlying files for removed items (only if under MUSIC_PATH)
                    for removed_item in to_remove_items:
                        try:
                            for media in getattr(removed_item, 'media', []) or []:
                                for part in getattr(media, 'parts', []) or []:
                                    file_path = getattr(part, 'file', None)
                                    if file_path:
                                        _safely_delete_local_file(file_path, music_root)
                        except Exception as e:
                            logging.debug(f"Error while deleting local files for removed item {removed_item}: {str(e)}")

                # Add missing tracks
                existing_identities = set(existing_id_map.keys()) - set(to_remove_identities)
                to_add = [t for t in desired_plex_tracks if _track_identity_from_plex(t) not in existing_identities]
                if to_add:
                    logging.info("Adding %d missing tracks to Plex playlist %s (1:1)" % (len(to_add), playlistName))
                    try:
                        plexPlaylist.addItems(to_add)
                    except Exception as e:
                        logging.debug(f"Failed to add items to playlist {playlistName}: {str(e)}")

            else:
                # One-way sync (Spotify -> Plex): only add missing tracks
                existing_identities = { _track_identity_from_plex(item) for item in existing_items }
                to_add = [t for t in desired_plex_tracks if _track_identity_from_plex(t) not in existing_identities]
                if to_add:
                    logging.info("Adding %d missing tracks to Plex playlist %s" % (len(to_add), playlistName))
                    try:
                        plexPlaylist.addItems(to_add)
                    except Exception as e:
                        logging.debug(f"Failed to add items to playlist %playlistName: {str(e)}")
        else:
            # Playlist does not exist in Plex
            if is_bidirectional:
                logging.info("Creating 1:1 Plex playlist %s" % playlistName)
                try:
                    plex.createPlaylist(title=playlistName, items=desired_plex_tracks)
                except Exception as e:
                    logging.debug(f"Failed to create playlist {playlistName}: {str(e)}")
            else:
                if desired_plex_tracks:
                    logging.info("Creating playlist %s" % playlistName)
                    try:
                        plex.createPlaylist(title=playlistName, items=desired_plex_tracks)
                    except Exception as e:
                        logging.debug(f"Failed to create playlist {playlistName}: {str(e)}")
                else:
                    logging.info("No tracks found for playlist %s" % playlistName)
    except (NotFound, BadRequest) as e:
        logging.info("Something wrong for playlist %s: %s" % (playlistName, str(e)))
# ...existing code...