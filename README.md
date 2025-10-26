![](https://img.shields.io/docker/pulls/nyancod3r/plexify?logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fnyancod3r%2Fplexify) ![](https://img.shields.io/docker/stars/nyancod3r/plexify?logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fnyancod3r%2Fplexify)

# Plexify - A Spotify to Plex Synchronization
This application synchronizes your Spotify playlists with your Plex music library. It converts Spotify URIs to Plex playlists and updates them at a specified interval. Download missing tracks with spotdl.

# Disclaimer

This project is intended for educational and demonstration purposes only. It is not intended to be used for illegal activities, including but not limited to the unauthorized downloading or distribution of copyrighted music or other media.

The author of this project does not condone or support illegal activities. The author is not responsible for any misuse of this project for illegal activities, and will not be held liable for any damages or legal issues that arise from such misuse.

Users are responsible for ensuring that their use of this project complies with all applicable laws and regulations, including copyright laws. If you choose to use this project, you do so at your own risk.

## Features

- Synchronizes all public playlists of a Spotify user
- Synchronizes specific public Spotify playlists
- Only creates playlists on Plex for songs that exist in your Plex library
- Downloads songs not found in Plex library for local storage and playback
- Supports setting synchronization interval
  
![](files/run_example.gif)

## Setup

To set up the application, you need to configure several environment variables:

- `SPOTIPY_CLIENT_ID`: Your Spotify client ID. You can create one [here](https://developer.spotify.com/dashboard/login).
- `SPOTIPY_CLIENT_SECRET`: The client secret of your Spotify client ID.
- `MUSIC_PATH`: The path of your music archive. SpotDL will download the tracks to this location under a folder named as the Spotify playlist.
- `PLEX_URL`: The URL of your Plex server, e.g., `http://plex:32400`.
- `PLEX_TOKEN`: Your Plex token. You can find it by following [these instructions](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
- `SPOTIFY_URIS`: A comma-separated list of the Spotify URIs you want to import. You can specify either a user's URI to import all public playlists owned by the user, or a playlist URI to import a specific public playlist. For example: `spotify:user:sonosplay,spotify:user:sonosplay:playlist:6nQjiSQhdf84s2AAxweRBv`.
- `SECONDS_TO_WAIT`: The number of seconds to wait between synchronizations.
- `PLEXIFY_DEBUG` : 0 Info 1 Verbose

The following URI's are supported:
* A user's URI which will import all public playlists a user owns: `spotify:user:sonosplay`
* A playlist URI which imports a specific playlist (must be public): `spotify:user:sonosplay:playlist:6nQjiSQhdf84s2AAxweRBv`

Playlists will only be created on Plex if your Plex instance has at least one of the songs. Only songs found on your Plex will be created in the Plex Playlilst

## Usage

### Script Logic

The application consists of several Python scripts that work together to synchronize Spotify playlists with a Plex music library. Below is an overview of the logic:

1. **Environment Configuration**:
   - The application retrieves necessary configuration values (e.g., Spotify credentials, Plex server details, synchronization interval) from environment variables.

2. **Spotify Playlist Retrieval**:
   - The application uses the Spotify API to fetch playlists based on the provided Spotify URIs. It supports fetching all public playlists of a user or specific playlists.

3. **Plex Playlist Retrieval**:
   - The application connects to the Plex server using the provided URL and token to retrieve existing playlists and their tracks.

4. **Comparison and Synchronization**:
   - The application compares the tracks in Spotify playlists with those in Plex playlists:
     - Tracks that exist in both Spotify and Plex are added to the corresponding Plex playlist.
     - Tracks that are missing in Plex are downloaded using SpotDL and added to the Plex library.

5. **Track Downloading**:
   - If a track from a Spotify playlist is not found in the Plex library, the application uses SpotDL to download the track to a specified folder.

6. **Playlist Creation and Updates**:
   - New playlists are created in Plex if they do not already exist.
   - Existing Plex playlists are updated to reflect changes in the corresponding Spotify playlists.

7. **Continuous Synchronization**:
   - The application runs in a loop, performing the synchronization process at the specified interval.

## Synchronization Process

The synchronization process ensures that Spotify playlists are reflected in your Plex library, with the following steps:

1. **Retrieve Playlists**:
   - Spotify playlists are fetched using the Spotify API based on the provided URIs.
   - Existing Plex playlists and their tracks are retrieved from the Plex server.

2. **Compare Playlists**:
   - Tracks in Spotify playlists are compared with those in Plex playlists.
   - Tracks missing in Plex are identified for addition.

3. **Add Missing Tracks**:
   - Missing tracks are downloaded using SpotDL and added to the Plex library.
   - New Plex playlists are created if they do not already exist.

4. **Update Playlists**:
   - Existing Plex playlists are updated to include tracks from Spotify playlists.
   - **Tracks are never removed from Plex playlists**, even if they are no longer available on Spotify. This ensures that tracks removed from Spotify (e.g., due to legal or licensing issues) remain in your Plex library.

5. **Continuous Sync**:
   - The process runs in a loop, updating playlists at the specified interval.

## Docker

This application is available as a Docker image.

## To Do
- [X] Throttle API calls to avoid banning
- [ ] Add the possibility to create a Plex Playlist from "Liked Songs"
- [ ] Add auto-rating to 5 stars at playlist creation
- [ ] Add selection for folder hieranchy (follow Plex folder structure or create a personal)
- [ ] Add Beets to force metadata and folder hierarchy
- [ ] Create web UI
- [ ] Create Plex playlists from "Discover Weekly" and "Release Radar"
