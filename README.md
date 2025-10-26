# Plexify

Plexify synchronizes your Spotify playlists to your Plex server. It fetches specified Spotify playlists and creates corresponding playlists in Plex, adding any tracks that it can find in your Plex library.

## How it works

1.  **Connects to Plex and Spotify**: The application uses your provided credentials to connect to both services.
2.  **Fetches Spotify Playlists**: It retrieves all playlists for the user(s) specified in the `SPOTIFY_URIS` environment variable.
3.  **Searches for Tracks in Plex**: For each track in a Spotify playlist, Plexify searches your Plex library to find a match based on the track title and artist.
4.  **Creates/Updates Plex Playlists**:
    *   If a corresponding playlist does not exist in Plex, it will be created.
    *   Matching tracks found in your Plex library are added to the playlist.
    *   Tracks that are in the Plex playlist but not in the Spotify playlist are **kept**. The sync is additive only.
5.  **Loops**: The process repeats after a configurable interval (`SECONDS_TO_WAIT`).

## Configuration

The application is configured using environment variables.

| Variable              | Description                                                                                             | Example                                                              |
| --------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `SPOTIPY_CLIENT_ID`   | Your Spotify application client ID.                                                                     | `your_spotify_client_id`                                             |
| `SPOTIPY_CLIENT_SECRET` | Your Spotify application client secret.                                                                 | `your_spotify_client_secret`                                         |
| `PLEX_URL`            | The base URL of your Plex server.                                                                       | `http://192.168.1.100:32400`                                         |
| `PLEX_TOKEN`          | Your Plex authentication token.                                                                         | `your_plex_token`                                                    |
| `SPOTIFY_URIS`        | A comma-separated list of Spotify URIs for the users whose playlists you want to sync.                    | `spotify:user:user1,spotify:user:user2`                              |
| `MUSIC_PATH`          | The path to your music library, used for organizing downloaded files (if downloading is implemented).   | `/music`                                                             |
| `SECONDS_TO_WAIT`     | The number of seconds to wait between synchronization cycles.                                           | `3600` (for 1 hour)                                                  |
| `LOG_LEVEL`           | The logging level for the application.                                                                  | `INFO` or `DEBUG`                                                    |

## Usage

You can run this application using Docker.

````bash
docker run -d \
  --name=plexify \
  -e SPOTIPY_CLIENT_ID="your_spotify_client_id" \
  -e SPOTIPY_CLIENT_SECRET="your_spotify_client_secret" \
  -e PLEX_URL="http://your_plex_url:32400" \
  -e PLEX_TOKEN="your_plex_token" \
  -e SPOTIFY_URIS="spotify:user:your_spotify_username" \
  -e LOG_LEVEL="INFO" \
  nyancod3r/plexify:latest