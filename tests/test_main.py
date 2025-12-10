from spotipy.oauth2 import SpotifyClientCredentials
from unittest.mock import patch, MagicMock
from plexapi.server import PlexServer
from plexapi.audio import Track
import unittest
from utils import runSync

class TestMainFunctions(unittest.TestCase):

    @patch('utils.dumpSpotifyPlaylists')
    def test_runSync(self, mock_dump_spotify):
        sp = MagicMock()
        spotify_uris = [{'user': 'username'}]

        runSync(sp, spotify_uris)

        mock_dump_spotify.assert_called_once_with(sp, spotify_uris)

if __name__ == '__main__':
    unittest.main()