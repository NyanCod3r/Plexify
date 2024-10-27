import unittest
import os
from unittest.mock import patch, MagicMock
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
from plexapi.audio import Track

class TestMainFunctions(unittest.TestCase):
    def setUp(self):
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            self.fail("SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set")

        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        self.plex = MagicMock(spec=PlexServer)

    def test_retry_with_backoff(self):
        func = MagicMock(side_effect=[spotipy.exceptions.SpotifyException(429, "Rate limit exceeded"), "Success"])
        result = retry_with_backoff(func)
        self.assertEqual(result, "Success")
        self.assertEqual(func.call_count, 2)

    @patch('spotify_sync.retry_with_backoff')
    def test_getSpotifyPlaylist(self, mock_retry):
        mock_retry.return_value = {'name': 'Test Playlist'}
        result = getSpotifyPlaylist(self.sp, 'user_id', 'playlist_id')
        self.assertEqual(result['name'], 'Test Playlist')

    @patch('spotify_sync.retry_with_backoff')
    def test_getSpotifyUserPlaylists(self, mock_retry):
        mock_retry.return_value = {'items': [{'owner': {'id': 'user_id'}, 'id': 'playlist_id'}], 'next': None}
        result = getSpotifyUserPlaylists(self.sp, 'user_id')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'playlist_id')

    @patch('spotify_sync.retry_with_backoff')
    def test_getSpotifyTracks(self, mock_retry):
        mock_retry.return_value = {'items': [{'track': {'name': 'Test Track'}}], 'next': None}
        playlist = {'tracks': {'items': [{'track': {'name': 'Test Track'}}], 'next': None}}
        result = getSpotifyTracks(self.sp, playlist)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['track']['name'], 'Test Track')

    @patch('spotify_sync.filterPlexArray')
    @patch('spotify_sync.createFolder')
    @patch('spotify_sync.subprocess.run')
    @patch('spotify_sync.eyed3.load')
    def test_getPlexTracks(self, mock_eyed3, mock_subprocess, mock_createFolder, mock_filterPlexArray):
        mock_filterPlexArray.return_value = [MagicMock(spec=Track)]
        mock_eyed3.return_value = MagicMock()
        spotifyTracks = [{'track': {'name': 'Test Track', 'artists': [{'name': 'Test Artist'}], 'external_urls': {'spotify': 'spotify:track:123'}}}]
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