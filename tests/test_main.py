from spotipy.oauth2 import SpotifyClientCredentials
from unittest.mock import patch, MagicMock
from plexapi.server import PlexServer
from plexapi.audio import Track
import unittest
from utils import runSync

class TestMainFunctions(unittest.TestCase):

    @patch('utils.dumpSpotifyPlaylists')
    @patch('utils.dumpPlexPlaylists')
    @patch('utils.diffAndSyncPlaylists')
    def test_runSync(self, mock_diff_and_sync, mock_dump_plex, mock_dump_spotify):
        plex = MagicMock(spec=PlexServer)
        sp = MagicMock()
        spotify_uris = [{'user': 'username'}]

        runSync(plex, sp, spotify_uris)

        mock_dump_spotify.assert_called_once_with(sp, spotify_uris)
        mock_dump_plex.assert_called_once_with(plex)
        mock_diff_and_sync.assert_called_once()

if __name__ == '__main__':
    unittest.main()