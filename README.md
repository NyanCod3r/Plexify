# Plexify

Plexify automatically syncs public Spotify playlists to your Plex server. It can sync all public playlists from a specific user or sync individual public playlists. If a track from a Spotify playlist is not found in your Plex library, Plexify will download it using `spotdl`.

## How it works

The application synchronizes playlists by adding new tracks from Spotify to your Plex playlists.

1.  **Reads Configuration**: The application loads configuration from environment variables, including connection details for Plex and Spotify, and the list of Spotify URIs to sync.
2.  **Fetches Playlists**: It retrieves all tracks from the specified Spotify user profiles and individual playlists. It also fetches the tracks from the corresponding playlists on your Plex server.
3.  **Calculates Differences**: For each playlist, it identifies tracks that are present in the Spotify playlist but are missing from the corresponding Plex playlist.
4.  **Executes Sync Actions**:
    *   For each track that needs to be **added**, the application first checks if it exists in your Plex library. If not, it is downloaded using `spotdl`. The track is then added to the Plex playlist.
    *   **Note**: Tracks that are removed from the Spotify playlist are **not** removed from the Plex playlist. This must be done manually.
5.  **Loops**: The entire process runs in a continuous loop, with a configurable wait time between syncs.

## Configuration

The application is configured using environment variables.

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `PLEX_URL` | The full URL for your Plex server. | Yes | |
| `PLEX_TOKEN` | Your Plex authentication token. | Yes | |
| `SPOTIFY_CLIENT_ID` | Your Spotify application client ID. | Yes | |
| `SPOTIFY_CLIENT_SECRET` | Your Spotify application client secret. | Yes | |
| `SPOTIFY_URIS` | A comma-separated list of Spotify URIs. Can be user or playlist URIs. | Yes | |
| `MUSIC_PATH` | The absolute path on the host where music files will be downloaded. | Yes | `/music` |
| `SECONDS_TO_WAIT` | The number of seconds to wait between sync cycles. | No | `3600` |
| `LOG_LEVEL` | The logging level for the application. | No | `INFO` |

**Example `SPOTIFY_URIS`:**
`spotify:user:USERNAME,spotify:playlist:PLAYLIST_ID`

## Usage

To run the application, ensure all required environment variables are set and execute the main script:

````bash
python src/main.py
````

You can run this application using Docker.

````bash
docker run -d \
  --name=plexify \
  -e SPOTIFY_CLIENT_ID="your_spotify_client_id" \
  -e SPOTIFY_CLIENT_SECRET="your_spotify_client_secret" \
  -e PLEX_URL="http://your_plex_url:32400" \
  -e PLEX_TOKEN="your_plex_token" \
  -e SPOTIFY_URIS="spotify:user:your_spotify_username" \
  -e LOG_LEVEL="INFO" \
  -v /path/to/your/music:/music \
  nyancod3r/plexify:latest
  ````