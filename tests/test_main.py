import unittest
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotify_sync import (
    retry_with_backoff,
    filterPlexArray,
    getSpotifyPlaylist,
    getSpotifyUserPlaylists,
    getSpotifyTracks,
    getPlexTracks,
    createFolder,
    createPlaylist,
    parseSpotifyURI,
    delete_unmatched_files,
    runSync
)
from plexapi.server import PlexServer
from unittest.mock import patch, MagicMock

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
        func = MagicMock(side_effect=[spotipy.exceptions.SpotifyException(429, "Rate limit exceeded"), "Success"])
        result = retry_with_backoff(func)
        self.assertEqual(result, "Success")
        self.assertEqual(func.call_count, 2)

    def test_getSpotifyPlaylist(self):
        result = getSpotifyPlaylist(self.sp, 'spotify', '37i9dQZF1DXcBWIGoYBM5M')  # Example playlist ID
        self.assertIsNotNone(result)
        self.assertIn('name', result)

    def test_getSpotifyUserPlaylists(self):
        result = getSpotifyUserPlaylists(self.sp, 'spotify')
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    def test_getSpotifyTracks(self):
        playlist = getSpotifyPlaylist(self.sp, 'spotify', '37i9dQZF1DXcBWIGoYBM5M')  # Example playlist ID
        result = getSpotifyTracks(self.sp, playlist)
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    @patch('spotify_sync.filterPlexArray')
    @patch('spotify_sync.createFolder')
    @patch('spotify_sync.subprocess.run')
    @patch('spotify_sync.eyed3.load')
    def test_getPlexTracks(self, mock_eyed3, mock_subprocess, mock_createFolder, mock_filterPlexArray):
        mock_filterPlexArray.return_value = [MagicMock(spec=Track)]
        mock_eyed3.return_value = MagicMock()
        spotifyTracks = [{'track': self.dummy_song}]
        result = getPlexTracks(self.plex, spotifyTracks, 'Test Playlist')
        self.assertEqual(len(result), 1)

    @patch('spotify_sync.os.makedirs')
    @patch('spotify_sync.os.path.exists')
    def test_createFolder(self, mock_exists, mock_makedirs):
        mock_exists.return_value = False
        createFolder('Test Playlist')
        mock_makedirs.assert_called_once()

    @patch('spotify_sync.getPlexTracks')
    @patch('spotify_sync.getSpotifyTracks')
    @patch('spotify_sync.PlexServer.playlist')
    @patch('spotify_sync.PlexServer.playlists')
    def test_createPlaylist(self, mock_playlists, mock_playlist, mock_getSpotifyTracks, mock_getPlexTracks):
        mock_playlists.return_value = []
        mock_getSpotifyTracks.return_value = []
        mock_getPlexTracks.return_value = []
        createPlaylist(self.plex, self.sp, {'name': 'Test Playlist'})
        mock_playlists.assert_called_once()

    def test_parseSpotifyURI(self):
        uri = 'spotify:user:username:playlist:playlist_id'
        result = parseSpotifyURI(uri)
        self.assertEqual(result['user'], 'username')
        self.assertEqual(result['playlist'], 'playlist_id')

    @patch('spotify_sync.PlexServer.playlist')
    def test_delete_unmatched_files(self, mock_playlist):
        mock_playlist.return_value.items.return_value = [MagicMock(title='Test Track')]
        spotifyTracks = [{'track': {'name': 'Another Track'}}]
        delete_unmatched_files(self.plex, spotifyTracks, 'Test Playlist')
        mock_playlist.return_value.removeItems.assert_called_once()

    @patch('spotify_sync.getSpotifyUserPlaylists')
    @patch('spotify_sync.getSpotifyPlaylist')
    @patch('spotify_sync.createPlaylist')
    @patch('spotify_sync.delete_unmatched_files')
    def test_runSync(self, mock_delete, mock_create, mock_getPlaylist, mock_getUserPlaylists):
        mock_getUserPlaylists.return_value = [{'name': 'Test Playlist'}]
        mock_getPlaylist.return_value = {'name': 'Test Playlist'}
        runSync(self.plex, self.sp, [{'user': 'username'}])
        mock_create.assert_called_once()
        mock_delete.assert_called_once()

if __name__ == '__main__':
    unittest.main()