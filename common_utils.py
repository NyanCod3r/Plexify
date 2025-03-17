import os
import logging
from plexapi.audio import Track
from typing import List

def filterPlexArray(plexItems=[], song="", artist="") -> List[Track]:
    plexItems = [
        item for item in plexItems
        if isinstance(item, Track) and
        item.title.lower() == song.lower() and
        item.artist().title.lower() == artist.lower()
    ]
    return plexItems

def createFolder(playlistName):
    if not os.path.exists(os.environ.get('SPOTIPY_PATH') + '/' + playlistName):
        os.makedirs(os.environ.get('SPOTIPY_PATH') + '/' + playlistName)
        logging.info('Created folder %s' % playlistName)
    else:
        logging.info('Folder %s already exists' % playlistName)