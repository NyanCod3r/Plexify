# Plexify

**⚠️ This is a breaking change that drops automatic Plex playlist management in favor of Plex Smart Playlists**

Plexify automatically syncs Spotify playlists to your local filesystem, downloading tracks using `spotdl`. Files are organized by playlist, then artist and album for seamless Plex library integration. Use **Plex Smart Playlists** (filtered by folder path) to surface these files in Plex.

---

## ✨ Features

### ✅ Currently Implemented

- **🎵 Spotify Playlist Sync** - Automatically downloads all tracks from specified Spotify playlists
- **📦 Smart File Organization** - Files organized as `MUSIC_PATH/<Playlist>/<Artist>/<Album>/<Track>.mp3`
- **💾 Intelligent Caching** - Uses `snapshot_id` to detect playlist changes and minimize API calls
- **🔄 Continuous Sync** - Runs in a loop with configurable wait time between syncs
- **🎧 High-Quality Downloads** - Downloads tracks using spotdl (MP3 format)
- **🎼 Format-Agnostic Detection** - Skips downloads if track exists in any audio format (mp3, flac, m4a, opus, ogg, wav)
- **🏷️ Metadata Tagging** - Automatically tags downloaded files with artist, track, and album information
- **📊 Detailed Logging** - Configurable log levels for both application and spotdl
- **⚡ Rate Limit Protection** - Built-in retry logic with exponential backoff for API calls and download delays
- **🔑 Credential Passthrough** - Automatically passes your Spotify credentials to spotdl to prevent rate limiting
- **🐳 Docker Support** - Ready-to-use Docker container for easy deployment
- **⭐ 1-Star Rating Cleanup** - Automatically remove tracks rated 1-star in Plex from Spotify playlists and local storage

### 🚧 Coming Soon

- **🔄 Resume Failed Downloads** - Retry tracks that failed to download
- **📈 Download Statistics** - Track counts, storage usage per playlist
- **🎛️ Configurable File Naming** - Custom filename patterns

---

## ⚠️ What Changed in This Version

**REMOVED:**
- ❌ Automatic Plex playlist creation/updates
- ❌ Plex API playlist operations
- ❌ Bidirectional sync logic
- ❌ Track removal from Plex playlists

**NEW APPROACH:**
- ✅ Downloads tracks to `MUSIC_PATH/<Playlist>/<Artist>/<Album>/`
- ✅ Smart playlist caching with snapshot-based change detection
- ✅ **Plex library sections must match Spotify playlist names** for 1-star deletion feature
- ✅ **Spotify credentials automatically passed to spotdl** to prevent rate limiting
- ✅ **Configurable download delays** to respect Spotify API rate limits (20 req/sec max)
- ✅ **Format-agnostic file detection** - Won't re-download if FLAC or other formats exist
- ✅ You create Plex Smart Playlists manually (one-time setup)
- ✅ Plex Smart Playlists auto-update based on folder contents

**Why this change?** Plex Smart Playlists are more reliable, faster, and eliminate API sync issues. Smart caching dramatically reduces Spotify API calls and prevents rate limiting.

---

## 🎯 Plex Library Setup (Important!)

**For the 1-star deletion feature to work, your Plex library structure must match Spotify playlist names.**

### Recommended Setup:

1. **Create separate Plex libraries for each Spotify playlist you want to sync**
   - Library name **must exactly match** Spotify playlist name
   - Example: Spotify playlist `Stoner.Blues.Rock` → Plex library `Stoner.Blues.Rock`

2. **Point each library to its corresponding folder**
   - Library `Stoner.Blues.Rock` → Folder `/data/Music/Stoner.Blues.Rock`
   - Library `Chill.Vibes` → Folder `/data/Music/Chill.Vibes`

3. **How it works:**
   - When you rate a track 1-star in Plex, the app knows which Spotify playlist to remove it from
   - The library name acts as the link between Plex and Spotify
   - Without matching names, 1-star deletion won't work

### Example Configuration:

**Spotify Playlists:**
- `Stoner.Blues.Rock`
- `Chill.Vibes`
- `Workout Mix`

**File Structure:**
```
/data/Music/
├── Stoner.Blues.Rock/
│   └── Black Sabbath/...
├── Chill.Vibes/
│   └── Tycho/...
└── Workout Mix/
    └── Run The Jewels/...
```

**Plex Libraries (Settings → Libraries → Add Library):**
- Name: `Stoner.Blues.Rock` → Folder: `/data/Music/Stoner.Blues.Rock`
- Name: `Chill.Vibes` → Folder: `/data/Music/Chill.Vibes`
- Name: `Workout Mix` → Folder: `/data/Music/Workout Mix`

---

## Setting up Plex Smart Playlists

**One-time setup per playlist:**

1. In Plex Web UI, go to **Music** → **Playlists** → **+ New Playlist** → **Smart Playlist**
2. Configure filters:
   - **Type**: `Music`
   - **Folder** → **contains** → `<MUSIC_PATH>/<PlaylistName>`
   - Additional filters as needed (genre, artist, etc.)
3. Save the playlist
4. Plex will automatically include all tracks from matching folders
5. Repeat for each collection you want

**Example Smart Playlist filters:**
- Specific Spotify Playlist: `Folder contains /data/Music/Stoner.Blues.Rock`
- All Rock Artists: `Folder contains /data/Music/Rock` AND `Genre is Rock`
- Specific Artist Across Playlists: `Folder contains /data/Music` AND `Artist is AC/DC`

As Plexify downloads new tracks, your Smart Playlists auto-update. No API calls needed!

---

## ⚠️ Configuration

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `SPOTIPY_CLIENT_ID` | Your Spotify application client ID. | Yes | |
| `SPOTIPY_CLIENT_SECRET` | Your Spotify application client secret. | Yes | |
| `SPOTIFY_URIS` | Comma-separated Spotify URIs (user or playlist). | Yes | |
| `MUSIC_PATH` | Absolute path where music files are stored/downloaded. | Yes | `/music` |
| `PLEX_URL` | Full URL for your Plex server (e.g., http://localhost:32400). | Yes | |
| `PLEX_TOKEN` | Your Plex authentication token. | Yes | |
| `SECONDS_TO_WAIT` | Seconds to wait between sync cycles. | No | `3600` |
| `LOG_LEVEL` | Python logging level (DEBUG, INFO, WARNING, ERROR). | No | `INFO` |
| `SPOTDL_LOG_LEVEL` | spotdl logging level (separate from LOG_LEVEL). | No | Same as `LOG_LEVEL` |
| `DOWNLOAD_DELAY` | Seconds to wait between track downloads (rate limiting). | No | `0.05` |

### Environment Variables Explained

**`SPOTIPY_CLIENT_ID` & `SPOTIPY_CLIENT_SECRET`**  
Your personal Spotify API credentials. These are automatically passed to spotdl to prevent rate limiting. Without your own credentials, spotdl uses public/shared keys that quickly hit rate limits.

**`SPOTDL_LOG_LEVEL`**  
Controls verbosity of spotdl output. Set to `DEBUG` to see detailed download progress, or `INFO` for cleaner logs. If not set, inherits from `LOG_LEVEL`.

**`DOWNLOAD_DELAY`**  
Time to wait between each track download. Default is `0.05` seconds (20 requests/second), which respects Spotify's recommended rate limit of ~180 requests/minute. Increase this value if you still encounter rate limiting (e.g., `0.1` for 10 req/sec).

**Example SPOTIFY_URIS:**
```
spotify:user:USERNAME,spotify:playlist:PLAYLIST_ID,spotify:playlist:ANOTHER_ID
```

### Getting Your Spotify Credentials

**⚠️ Important: Use your own credentials to avoid rate limiting!**

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy your Client ID and Client Secret
4. Set redirect URI to `http://localhost:8888/callback`

Your credentials are passed to spotdl automatically - no manual configuration needed.

### Getting Your Plex Token

1. Open Plex Web UI
2. Play any media item
3. Click the three-dot menu → "Get Info" → "View XML"
4. Look for `X-Plex-Token=` in the URL
5. Copy the token value

---

## Usage

### Local

```bash
export SPOTIPY_CLIENT_ID="your_spotify_client_id"
export SPOTIPY_CLIENT_SECRET="your_spotify_client_secret"
export SPOTIFY_URIS="spotify:user:your_username"
export MUSIC_PATH="/data/Music"
export PLEX_URL="http://localhost:32400"
export PLEX_TOKEN="your_plex_token"
export LOG_LEVEL="INFO"
export DOWNLOAD_DELAY="0.05"  # Optional: 20 req/sec (default)

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
  -e PLEX_URL="http://plex:32400" \
  -e PLEX_TOKEN="your_plex_token" \
  -e LOG_LEVEL="INFO" \
  -e SPOTDL_LOG_LEVEL="INFO" \
  -e DOWNLOAD_DELAY="0.05" \
  -v /path/to/your/music:/music \
  nyancod3r/plexify:latest
```

---

## File Organization

```
MUSIC_PATH/
├── Stoner.Blues.Rock/           (Playlist 1 = Plex Library 1)
│   ├── Black Sabbath/
│   │   ├── Paranoid/
│   │   │   ├── War Pigs.mp3      (or .flac, .m4a, etc.)
│   │   │   └── Paranoid.flac
│   │   └── Master of Reality/
│   │       └── Sweet Leaf.mp3
│   └── Kyuss/
│       └── Blues for the Red Sun/
│           └── Thumb.mp3
└── Chill.Vibes/                 (Playlist 2 = Plex Library 2)
    └── Tycho/
        └── Dive/
            └── A Walk.m4a
```

**Structure explained:**
1. **Level 1:** `MUSIC_PATH` - Your root music folder
2. **Level 2:** Spotify playlist name (sanitized for filesystem) - **This must match your Plex library name**
3. **Level 3:** Artist name from track metadata
4. **Level 4:** Album name from track metadata
5. **Level 5:** Track file in any supported format (`.mp3`, `.flac`, `.m4a`, `.opus`, `.ogg`, `.wav`)

**File naming:** All files follow the pattern `Artist - Track.extension`

This structure allows you to:
- Create Plex libraries that map directly to Spotify playlists
- Enable 1-star deletion (library name = playlist name = folder name)
- Create Plex Smart Playlists per Spotify playlist (`Folder contains /music/Stoner.Blues.Rock`)
- Mix different audio formats - Plexify won't re-download if any format exists
- Group all music together while keeping playlists organized
- Easily identify which playlist a track belongs to

---

## 🔧 Feature Details

### 🚀 Smart Playlist Caching
Plexify uses Spotify's `snapshot_id` to detect playlist changes. This dramatically reduces API calls:

**First run:** Fetches all playlists and tracks  
**Subsequent runs:** Only checks snapshot IDs (1 API call per playlist)  
**If unchanged:** No additional API calls needed  
**If changed:** Only re-fetches that specific playlist

This prevents rate limiting and saves bandwidth.

### ⚡ Rate Limit Protection
Multiple layers of protection against Spotify API rate limits:

1. **Credential Passthrough**: Your `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` are automatically passed to spotdl via command-line arguments
2. **Download Delays**: Configurable delay between downloads (default 0.05s = 20 req/sec)
3. **Exponential Backoff**: Built-in retry logic for failed API calls
4. **Smart Caching**: Minimizes API calls by only fetching changed playlists

**Spotify's Rate Limits:**
- Approximate limit: 180 requests per minute
- Measurement window: Rolling 30-second timeframe
- Recommended: Max 20 requests per second
- Error code: 429 (Too Many Requests)

### 🎼 Format-Agnostic File Detection

Before downloading a track, Plexify checks if it already exists in **any** supported audio format:
- `.mp3` - MPEG Audio Layer 3
- `.flac` - Free Lossless Audio Codec
- `.m4a` - MPEG-4 Audio
- `.opus` - Opus Interactive Audio Codec
- `.ogg` - Ogg Vorbis
- `.wav` - Waveform Audio File Format

**Example scenario:**
- Playlist has "Black Sabbath - War Pigs"
- You already have `War Pigs.flac` in your library
- Plexify detects the FLAC file and **skips** the MP3 download
- No duplicate files, saves bandwidth and storage

This is especially useful if you've manually added high-quality FLAC files and don't want them replaced with MP3s.

### 🎵 Intelligent File Organization
Files are organized using Spotify metadata with a 4-level hierarchy:
- Playlist name (sanitized)
- Artist name from track metadata
- Album name from track metadata
- Track name with sanitized filenames (removes invalid characters: `< > : " / \ | ? *`)

**File naming convention:** `Artist - Track.extension`

Examples:
- `AC/DC` becomes `AC_DC`
- `Stoner.Blues.Rock` becomes `Stoner.Blues.Rock` (dots are valid)
- `My Playlist: Best Of` becomes `My Playlist_ Best Of`
- File: `Black Sabbath - War Pigs.mp3`

### 🏷️ Metadata Tagging
All downloaded files are automatically tagged with:
- Artist name
- Track title
- Album name
- Album artist

### 📦 Plex Library Compatibility
The `<Playlist>/<Artist>/<Album>/<Track>` structure allows precise Plex Smart Playlist targeting. Point your Plex library at `MUSIC_PATH` and all playlists will be available for filtering.

### ⭐ 1-Star Rating Cleanup

**Status:** Fully implemented and enabled

When you rate a track 1-star in Plex, Plexify will:
1. Detect the 1-star rating during the next sync cycle
2. Find which Plex library the track belongs to (e.g., `Stoner.Blues.Rock`)
3. Match the track in the corresponding Spotify playlist by title and artist
4. Remove it from the Spotify playlist via API
5. Delete the track from your Plex library
6. Delete the local file from the filesystem

**Requirements:**
- Plex library name must exactly match Spotify playlist name
- Track must exist in the corresponding Spotify playlist
- Track matching is done by normalized title and artist name (case-insensitive)

**Usage:**
1. Play a track in Plex you want to remove
2. Rate it 1-star (2 thumbs down)
3. Wait for next sync cycle (or restart Plexify)
4. Track will be automatically removed from everywhere

---

## Migration from v1.x

**Breaking Changes:**
- Environment variables changed: `SPOTIFY_CLIENT_ID` → `SPOTIPY_CLIENT_ID`
- Plex playlist management removed (use Plex Smart Playlists instead)
- File organization changed to `<Playlist>/<Artist>/<Album>/<Track>` structure (added playlist folder level)
- **Plex libraries must now be named to match Spotify playlists** for 1-star deletion
- Removed bidirectional sync for Discover Weekly/Release Radar
- Added required `PLEX_URL` and `PLEX_TOKEN` variables
- Added `DOWNLOAD_DELAY` for rate limit control

**What stays the same:**
- Download functionality
- Spotify playlist fetching
- Basic configuration approach

**Migration steps:**
1. Update environment variable names in your config
2. Set `PLEX_URL` and `PLEX_TOKEN`
3. **Ensure you're using your own Spotify credentials** (not shared/public keys)
4. Point `MUSIC_PATH` to your Plex music library root
5. **Create new Plex libraries with names matching Spotify playlists** (see Plex Library Setup section)
6. Create Plex Smart Playlists to replace old automatic playlists
7. Remove any old Docker volumes or cache files (`spotify_playlists.json` will be recreated)
8. First run will re-download metadata but skip existing files (including FLAC/M4A)
9. **File reorganization:** Existing files in `<Artist>/<Album>/` will not be moved. New structure is `<Playlist>/<Artist>/<Album>/`. Consider reorganizing manually or starting fresh.

---

## Troubleshooting

### 🚫 Rate Limiting from Spotify/spotdl
**Problem:** Logs show `Your application has reached a rate/request limit. Retry will occur after: 86400`

**Root Cause:** spotdl makes Spotify API calls for each track download. When combined with your app's API calls, rate limits are hit quickly.

**Solutions:**
1. **✅ Verify your credentials are being used:**
   ```bash
   # Set LOG_LEVEL to DEBUG
   export LOG_LEVEL="DEBUG"
   # Run Plexify and check logs for:
   # "DEBUG: Passing credentials to spotdl: client_id=abcd1234..."
   ```

2. **Create your own Spotify credentials** if using shared/public keys:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app to get fresh API quota
   - Update `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`

3. **Increase download delay:**
   ```bash
   export DOWNLOAD_DELAY="0.1"  # 10 req/sec instead of 20
   ```

4. **Reduce sync frequency:**
   ```bash
   export SECONDS_TO_WAIT="7200"  # 2 hours between syncs
   ```

5. **Reduce number of playlists:**
   - Temporarily remove some URIs from `SPOTIFY_URIS`
   - Process large playlists separately

6. **Smart caching (enabled by default)** should prevent this on subsequent runs

**Why it happens:** 
- Spotify limits ~180 requests/minute per application
- Each track download = 1+ API calls from spotdl
- Large playlists (900+ tracks) can exceed limits quickly
- Public/shared credentials are already rate-limited by other users

### 📁 Files Not Appearing in Plex
**Problem:** Downloaded files don't show up in Plex

**Solutions:**
1. Verify `MUSIC_PATH` matches your Plex library path exactly
2. Trigger a manual library scan: Plex Web UI → Library → Three-dot menu → Scan Library Files
3. Check Plex scan logs for errors: Settings → Console → Logs
4. Verify file permissions: Plex user needs read access to `MUSIC_PATH`
5. Check if files exist: `ls -la $MUSIC_PATH/<Playlist>/<Artist>/<Album>/`
6. Verify Smart Playlist filter matches folder path exactly
7. **Check library names match playlist names** for proper organization

### ⚠️ Invalid Library Section Error
**Problem:** `Error fetching 1-star tracks from library 'Stoner.Blues.Rock': Invalid library section`

**Cause:** Your Plex library name doesn't match the Spotify playlist name.

**Solution:**
1. Check your Plex library names: Settings → Libraries
2. Rename library to match Spotify playlist exactly (including dots, spaces, capitalization)
3. Or create a new library with the correct name pointing to the playlist folder

**Example:**
- ❌ Plex library: `Music` → Playlist folder: `/data/Music/Stoner.Blues.Rock` (Won't work)
- ✅ Plex library: `Stoner.Blues.Rock` → Playlist folder: `/data/Music/Stoner.Blues.Rock` (Works)

### 💾 Cache Issues
**Problem:** Plexify keeps re-fetching playlists or shows wrong track counts

**Solutions:**
1. Delete cache file: `rm spotify_playlists.json`
2. Restart Plexify (will do a full refresh)
3. Check cache file is valid JSON: `cat spotify_playlists.json | python3 -m json.tool`

### ⏱️ Download Timeouts
**Problem:** Downloads timeout after 300 seconds

**Solutions:**
1. Check your internet connection speed
2. Verify `spotdl` is installed: `spotdl --version`
3. Test manual download: `spotdl 'Artist - Track Name'`
4. Check spotdl output in logs for specific errors (YouTube blocks, regional restrictions, etc.)

### 🔇 No Download Progress Visible
**Problem:** Logs stuck at "Downloading: Artist - Track"

**Solution:** Set `SPOTDL_LOG_LEVEL=DEBUG` to see detailed spotdl output. If still stuck for >5 minutes:
1. Check if spotdl process is running: `ps aux | grep spotdl`
2. Kill hung process: `pkill spotdl`
3. Restart Plexify

### 🔄 Environment Variables Not Working
**Problem:** Application can't find environment variables

**Solutions:**
1. Verify variables are exported: `echo $SPOTIPY_CLIENT_ID`
2. If empty, export again in current shell session
3. For persistent variables, add to `~/.bashrc` or `~/.zshrc`:
   ```bash
   export SPOTIPY_CLIENT_ID="..."
   export SPOTIPY_CLIENT_SECRET="..."
   # etc.
   ```
4. Source the file: `source ~/.bashrc`

---

## Requirements

- Python 3.11+
- `spotipy` (Spotify API client)
- `spotdl` (YouTube Music downloader)
- `plexapi` (Plex server integration)
- `eyed3` (MP3 metadata handling)

Install with:
```bash
pip install -r requirements.txt
```

---

## Support

For issues, feature requests, or questions:
- GitHub Issues: [nyancod3r/plexify](https://github.com/nyancod3r/plexify/issues)