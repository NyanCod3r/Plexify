# Plexify

Plexify automatically syncs public Spotify playlists to your Plex server. It can sync all public playlists from a specific user or sync individual public playlists. If a track from a Spotify playlist is not found in your Plex library, Plexify will download it using `spotdl`.

## How it works

The application synchronizes playlists by adding new tracks from Spotify to your Plex playlists.

1.  **Reads Configuration**: The application loads configuration from environment variables, including connection details for Plex and Spotify, and the list of Spotify URIs to sync.
2.  **Fetches Playlists**: It retrieves all tracks from the specified Spotify user profiles and individual playlists. It also fetches the tracks from the corresponding playlists on your Plex server.
3.  **Calculates Differences**: For each playlist, it identifies tracks that are present in the Spotify playlist but are missing from the corresponding Plex playlist.
4.  **Executes Sync Actions**:
    *   For each track that needs to be **added**, the application first checks if it exists in your Plex library. If not, it is downloaded using `spotdl`. The track is then added to the Plex playlist.
    *   **Default behavior**: Tracks removed from the Spotify playlist are **not** removed from the Plex playlist (one-way sync from Spotify -> Plex).
    *   **Special playlists (1:1 bidirectional)**: Playlists named exactly "Discover Weekly" or "Release Radar" (case-insensitive) are synced 1:1. For these playlists Plexify will:
        - Remove items from the Plex playlist that are not present in the corresponding Spotify playlist.
        - When removing such items, Plexify will attempt to delete the underlying local media files only if the file path is under the configured MUSIC_PATH. Files outside MUSIC_PATH will not be deleted.
        - Plexify does not modify Spotify playlists; you must manage Spotify-side edits yourself.
5.  **Loops**: The entire process runs in a continuous loop, with a configurable wait time between syncs.

## Sync behavior (summary)

- One-way (Spotify -> Plex) for all playlists by default:
  - Missing tracks in Plex are downloaded/added.
  - Plex items removed on Spotify are left untouched in Plex.
- Bidirectional (1:1) for playlists named "Discover Weekly" or "Release Radar":
  - Plex playlist will be made identical to Spotify playlist.
  - Plex items not present in Spotify will be removed from the Plex playlist and their local files deleted if they live under MUSIC_PATH.
  - Plexify will never change Spotify playlists.

## Safety and verification

- Deletions only occur for playlists explicitly recognized as bidirectional ("Discover Weekly", "Release Radar").
- Deletion of local files is guarded: files are only deleted when their absolute path starts with the configured MUSIC_PATH.
- Verification steps before enabling deletion:
  1. Ensure MUSIC_PATH is set correctly and points to the folder containing Plex downloads:
     ```bash
     echo "$MUSIC_PATH"
     ls -la "$MUSIC_PATH"
     ```
  2. Run a single sync in debug mode and inspect logs for removal actions:
     ```bash
     PYTHONPATH=src LOG_LEVEL=DEBUG python src/main.py
     ```
  3. Confirm the list of items to be removed in logs before allowing automatic runs.

## Configuration

The application is configured using environment variables.

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `PLEX_URL` | The full URL for your Plex server. | Yes | |
| `PLEX_TOKEN` | Your Plex authentication token. | Yes | |
| `SPOTIFY_CLIENT_ID` | Your Spotify application client ID. | Yes | |
| `SPOTIFY_CLIENT_SECRET` | Your Spotify application client secret. | Yes | |
| `SPOTIFY_URIS` | A comma-separated list of Spotify URIs. Can be user or playlist URIs. | Yes | |
| `MUSIC_PATH` | The absolute path on the host where music files will be downloaded and where deletions are allowed. | Yes | `/music` |
| `SECONDS_TO_WAIT` | The number of seconds to wait between sync cycles. | No | `3600` |
| `LOG_LEVEL` | The logging level for the application. | No | `INFO` |

**Example `SPOTIFY_URIS`:**
`spotify:user:USERNAME,spotify:playlist:PLAYLIST_ID`

## Usage

To run the application, ensure all required environment variables are set and execute the main script:

```bash
python src/main.py
```

You can run this application using Docker:

```bash
docker run -d \
  --name=plexify \
  -e SPOTIFY_CLIENT_ID="your_spotify_client_id" \
  -e SPOTIFY_CLIENT_SECRET="your_spotify_client_secret" \
  -e PLEX_URL="http://your_plex_url:32400" \
  -e PLEX_TOKEN="your_plex_token" \
  -e SPOTIFY_URIS="spotify:user:your_spotify_username" \
  -e MUSIC_PATH="/path/to/your/music" \
  -e LOG_LEVEL="INFO" \
  -v /path/to/your/music:/music \
  nyancod3r/plexify:latest
```
