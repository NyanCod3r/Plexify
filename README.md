# Plexify

Plexify automatically syncs public Spotify playlists to your Plex server. It can sync all public playlists from a specific user or sync individual public playlists. If a track from a Spotify playlist is not found in your Plex library, Plexify will download it using `spotdl`.

## How it works

<video src="files/run_example.gif" controls width="600"></video>

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

# Plexify (Beta - Smart Playlist Edition)

**🎉 This is a beta version that drops automatic Plex playlist management in favor of Plex Smart Playlists**

Plexify automatically downloads tracks from Spotify playlists to your local filesystem, organized by playlist name. Use **Plex Smart Playlists** (filtered by folder path) to surface these files in Plex.

## ⚠️ What Changed in This Version

**REMOVED:**
- ❌ Automatic Plex playlist creation/updates
- ❌ Plex API playlist operations
- ❌ Bidirectional sync logic
- ❌ Track removal from Plex playlists

**NEW APPROACH:**
- ✅ Downloads tracks to `MUSIC_PATH/<playlist_name>/`
- ✅ Searches existing music library before downloading (up to 2 folder levels deep)
- ✅ Copies found files to playlist folder instead of re-downloading
- ✅ You create Plex Smart Playlists manually (one-time setup)
- ✅ Plex Smart Playlists auto-update based on folder contents

**Why this change?** Plex Smart Playlists are more reliable, faster, and eliminate API sync issues. This approach also reduces redundant downloads by finding tracks you already have.

---

## Setting up Plex Smart Playlists

**One-time setup per playlist:**

1. In Plex Web UI, go to **Music** → **Playlists** → **+ New Playlist** → **Smart Playlist**
2. Configure filters:
   - **Type**: `Music`
   - **Folder** → **contains** → `<MUSIC_PATH>/<playlist_name>`
   - Example: `/data/Music/Discover Weekly`
3. Save the playlist
4. Plex will automatically include all tracks from that folder
5. Repeat for each Spotify playlist you want to sync

**Example Smart Playlist filters:**
- Discover Weekly: `Folder contains /data/Music/Discover Weekly`
- Release Radar: `Folder contains /data/Music/Release Radar`
- My Playlist: `Folder contains /data/Music/My Playlist`

As Plexify downloads new tracks to these folders, your Smart Playlists auto-update. No API calls needed!

---

## ⚠️ Configuration

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `SPOTIPY_CLIENT_ID` | Your Spotify application client ID. | Yes | |
| `SPOTIPY_CLIENT_SECRET` | Your Spotify application client secret. | Yes | |
| `SPOTIFY_URIS` | Comma-separated Spotify URIs (user or playlist). | Yes | |
| `MUSIC_PATH` | Absolute path where music files are stored/downloaded. | Yes | `/music` |
| `SECONDS_TO_WAIT` | Seconds to wait between sync cycles. | No | `3600` |
| `LOG_LEVEL` | Python logging level (DEBUG, INFO, WARNING, ERROR). | No | `INFO` |
| `SPOTDL_LOG_LEVEL` | spotdl logging level (separate from LOG_LEVEL). | No | Same as `LOG_LEVEL` |
| `SPOTDL_COOKIE_FILE` | Path to YouTube cookies file (highly recommended). | No | None |
| `DOWNLOAD_DELAY` | Delay in seconds between downloads (avoid rate limits). | No | `2` |

### New Environment Variables Explained

**`SPOTDL_LOG_LEVEL`**  
Controls verbosity of spotdl output. Set to `DEBUG` to see detailed download progress, or `INFO` for cleaner logs. If not set, inherits from `LOG_LEVEL`.

**`SPOTDL_COOKIE_FILE`**  
Path to YouTube Music cookies file. **Highly recommended** to avoid rate limiting. Without cookies, you'll hit YouTube's API limits quickly (causing "Retry will occur after X seconds" warnings). With cookies, you get much higher limits.

**How to get cookies:**
```bash
# Install yt-dlp
pip install yt-dlp
```
# Export cookies from your browser
# Firefox:
yt-dlp --cookies-from-browser firefox --cookies cookies.txt "https://music.youtube.com"

# Chrome:
yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://music.youtube.com"

# Then set the path:
export SPOTDL_COOKIE_FILE="/path/to/cookies.txt"

**DOWNLOAD_DELAY**  
Number of seconds to wait between each download. Default is 2 seconds to help avoid rate limits. Increase if you still hit limits even with cookies.

**Example SPOTIFY_URIS:**
```
spotify:user:USERNAME,spotify:playlist:PLAYLIST_ID,spotify:playlist:ANOTHER_ID
```

---

## Usage

### Local

```bash
# Set environment variables
export SPOTIPY_CLIENT_ID="your_spotify_client_id"
export SPOTIPY_CLIENT_SECRET="your_spotify_client_secret"
export SPOTIFY_URIS="spotify:user:your_username"
export MUSIC_PATH="/data/Music"
export LOG_LEVEL="INFO"
export SPOTDL_COOKIE_FILE="/path/to/cookies.txt"  # Optional but recommended
export DOWNLOAD_DELAY="2"  # Optional
```
# Run
```
python src/main.py
```

### Docker

```bash
docker run -d \
  --name=plexify \
  -e SPOTIPY_CLIENT_ID="your_spotify_client_id" \
  -e SPOTIPY_CLIENT_SECRET="your_spotify_client_secret" \
  -e SPOTIFY_URIS="spotify:user:your_spotify_username" \
  -e MUSIC_PATH="/music" \
  -e LOG_LEVEL="INFO" \
  -e SPOTDL_LOG_LEVEL="INFO" \
  -e SPOTDL_COOKIE_FILE="/config/cookies.txt" \
  -e DOWNLOAD_DELAY="2" \
  -v /path/to/your/music:/music \
  -v /path/to/cookies.txt:/config/cookies.txt \
  nyancod3r/plexify:latest
```

---

## File Organization

```
MUSIC_PATH/
├── Discover Weekly/
│   ├── Artist1 - Song1.mp3
│   └── Artist2 - Song2.mp3
├── Release Radar/
│   └── Artist3 - Song3.mp3
├── My Awesome Playlist/
│   ├── Artist4 - Song4.mp3
│   └── Artist5 - Song5.mp3
└── Existing Music/        # Your existing library
    ├── Artist6/
    │   └── Album1/
    │       └── Track.mp3  # Will be found and copied instead of re-downloaded
    └── Artist7/
        └── Single.mp3
```

---

## Features

### 🔍 Smart File Discovery
Before downloading, Plexify searches your entire `MUSIC_PATH` up to 2 levels deep for existing files. This helps:
- **Reduce redundant downloads** (finds tracks you already have)
- **Avoid YouTube rate limits** (fewer API calls)
- **Save bandwidth and time**

### 🎵 Intelligent Matching
Files are matched using normalized artist and track names, ignoring:
- Special characters (`/`, `_`, `:`, `?`)
- Spaces and capitalization
- Different naming conventions

Examples of matched files:
- `AC/DC - T.N.T..mp3` matches `ACDC - TNT.mp3`
- `Ke$ha - TiK ToK.mp3` matches `Kesha - Tik Tok.mp3`

### 📋 File Copying
If a track exists elsewhere in your library, Plexify copies it to the playlist folder instead of re-downloading. Original files remain untouched.

### 🏷️ Metadata Tagging
All downloaded files are automatically tagged with:
- Artist name
- Track title
- Album artist

### ⏱️ Rate Limit Management
- Configurable delay between downloads
- YouTube cookie support for higher API limits
- Real-time download progress logging

---

## Troubleshooting

### Rate Limiting Issues
**Problem:** Logs show `WARNING:root:Your application has reached a rate/request limit. Retry will occur after: X`

**Solution:**
1. Set up YouTube cookies (see `SPOTDL_COOKIE_FILE` above)
2. Increase `DOWNLOAD_DELAY` to `5` or higher
3. Let spotdl retry automatically (it will wait and retry)

### Files Not Being Found
**Problem:** Plexify downloads files you already have

**Solution:**
1. Ensure `MUSIC_PATH` points to your main music library
2. Check that existing files are within 2 folder levels (e.g., `Artist/Album/Track.mp3`)
3. Verify file names contain artist and track name

### Download Timeouts
**Problem:** Downloads timeout after 300 seconds

**Solution:**
1. Check your internet connection
2. Verify `spotdl` is installed: `spotdl --version`
3. Try downloading manually: `spotdl 'https://open.spotify.com/track/TRACK_ID'`

### Logs Too Verbose
**Problem:** Too much debug output

**Solution:**
```bash
export LOG_LEVEL="INFO"           # Python app logs
export SPOTDL_LOG_LEVEL="WARNING" # spotdl logs only warnings/errors
```

---

## Migration from Old Version

If you used the old Plexify with automatic Plex playlist management:

1. **Existing Plex playlists are safe** - this version doesn't touch them
2. **Create Smart Playlists** for each playlist you want to keep synced
3. **Point Smart Playlists** to the folders Plexify creates
4. **Optional:** Delete old Plex playlists once Smart Playlists are working

Your downloaded music files remain unchanged. Only the playlist management approach changes.

---

## Requirements

- Python 3.11+
- `spotipy` (Spotify API)
- `spotdl` (YouTube Music downloader)
- `eyed3` (MP3 tagging)
- `yt-dlp` (optional, for cookie extraction)

Install with:
```bash
pip install spotipy spotdl eyed3 yt-dlp
```

---

## License

MIT License - see LICENSE file for details.

---

## Support

For issues, feature requests, or questions:
- GitHub Issues: [nyancod3r/plexify](https://github.com/nyancod3r/plexify/issues)
- Remember: This is a **beta version** focused on Smart Playlists!
