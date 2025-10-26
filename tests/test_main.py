import unittest
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from unittest.mock import patch, MagicMock
from plexapi.server import PlexServer
from plexapi.audio import Track

# Import functions from their correct modules
from common_utils import retry_with_backoff, createFolder
from spotify_utils import getSpotifyPlaylist, getSpotifyUserPlaylists, getSpotifyTracks, parseSpotifyURI
from plex_utils import getPlexTracks, createPlaylist, delete_unmatched_files
from utils import runSync


class TestMainFunctions(unittest.TestCase):
    def setUp(self):
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            self.fail("SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set")

        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        ))
        self.plex = MagicMock(spec=PlexServer)
        self.dummy_song = {
            'name': 'SONG',
            'artists': [{'name': 'ARTIST'}],
            'external_urls': {'spotify': 'TRACKURL'}
        }

    def test_retry_with_backoff(self):
        func = MagicMock(side_effect=[spotipy.exceptions.SpotifyException(429, -1, "Rate limit exceeded", headers={}), "Success"])
        result = retry_with_backoff(func)
        self.assertEqual(result, "Success")
        self.assertEqual(func.call_count, 2)

    def test_getSpotifyPlaylist(self):
        with patch('spotify_utils.retry_with_backoff') as mock_retry:
            mock_retry.return_value = {'name': 'Test Playlist', 'tracks': {'items': [], 'next': None}}
            result = getSpotifyPlaylist(self.sp, 'spotify', '37i9dQZF1DXcBWIGoYBM5M')
            self.assertIsNotNone(result)
            self.assertIn('name', result)
            mock_retry.assert_called_once()

    def test_getSpotifyUserPlaylists(self):
        with patch('spotify_utils.retry_with_backoff') as mock_retry:
            mock_retry.side_effect = [
                {'items': [{'owner': {'id': 'spotify'}, 'id': 'playlist1', 'name': 'Playlist 1'}], 'next': None},
                {'name': 'Playlist 1', 'tracks': {'items': [], 'next': None}}
            ]
            result = getSpotifyUserPlaylists(self.sp, 'spotify')
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 1)

    def test_getSpotifyTracks(self):
        playlist = {'name': 'Test Playlist', 'tracks': {'items': [{'track': self.dummy_song}], 'next': None}}
        with patch('spotify_utils.retry_with_backoff') as mock_retry:
            result = getSpotifyTracks(self.sp, playlist)
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 1)
            mock_retry.assert_not_called() # No 'next' page

    @patch('plex_utils.filterPlexArray')
    @patch('plex_utils.createFolder')
    @patch('plex_utils.subprocess.run')
    @patch('plex_utils.eyed3.load')
    def test_getPlexTracks(self, mock_eyed3, mock_subprocess, mock_createFolder, mock_filterPlexArray):
        mock_track = MagicMock(spec=Track, title='SONG', grandparentTitle='ARTIST')
        mock_filterPlexArray.return_value = [mock_track]
        self.plex.library.search.return_value = [mock_track]
        spotifyTracks = [{'track': self.dummy_song}]
        result = getPlexTracks(self.plex, spotifyTracks, 'Test Playlist')
        self.assertEqual(len(result), 1)
        mock_subprocess.assert_not_called()

    @patch('common_utils.os.makedirs')
    @patch('common_utils.os.path.exists')
    @patch('common_utils.os.environ.get')
    def test_createFolder(self, mock_environ_get, mock_exists, mock_makedirs):
        mock_environ_get.return_value = '/music'
        mock_exists.return_value = False
        createFolder('Test Playlist')
        mock_makedirs.assert_called_once_with('/music/Test Playlist')

    @patch('plex_utils.getPlexTracks')
    @patch('plex_utils.getSpotifyTracks')
    def test_createPlaylist(self, mock_getSpotifyTracks, mock_getPlexTracks):
        self.plex.playlists.return_value = []
        mock_getSpotifyTracks.return_value = [{'track': self.dummy_song}]
        mock_getPlexTracks.return_value = [MagicMock(spec=Track)]
        createPlaylist(self.plex, self.sp, {'name': 'Test Playlist'})
        self.plex.createPlaylist.assert_called_once()

    def test_parseSpotifyURI(self):
        uri = 'spotify:user:username:playlist:playlist_id'
        result = parseSpotifyURI(uri)
        self.assertEqual(result['user'], 'username')
        self.assertEqual(result['playlist'], 'playlist_id')

    @patch('plex_utils.PlexServer.playlist')
    def test_delete_unmatched_files(self, mock_playlist_method):
        mock_playlist = MagicMock()
        mock_playlist.items.return_value = [MagicMock(title='Test Track')]
        self.plex.playlist.return_value = mock_playlist
        spotifyTracks = [{'track': {'name': 'Another Track'}}]
        delete_unmatched_files(self.plex, spotifyTracks, 'Test Playlist')
        mock_playlist.removeItems.assert_called_once()

    @patch('utils.dumpSpotifyPlaylists')
    @patch('utils.dumpPlexPlaylists')
    @patch('utils.diffAndSyncPlaylists')
    def test_runSync(self, mock_diff, mock_dump_plex, mock_dump_spotify):
        runSync(self.plex, self.sp, [{'user': 'username'}])
        mock_dump_spotify.assert_called_once()
        mock_dump_plex.assert_called_once()
        mock_diff.assert_called_once()

if __name__ == '__main__':
    unittest.main()