# Plexify

**⚠️ This is a breaking change that drops automatic Plex playlist management in favor of Plex Smart Playlists**

Plexify automatically syncs Spotify playlists to your local filesystem, downloading tracks using **YouTube search + yt-dlp**. Files are organized by playlist, then artist and album for seamless Plex library integration. Use **Plex Smart Playlists** (filtered by folder path) to surface these files in Plex.

---

## ✨ Features

### ✅ Currently Implemented

- **🎵 Spotify Playlist Sync** - Automatically downloads all tracks from specified Spotify playlists
- **📦 Smart File Organization** - Files organized as `MUSIC_PATH/<Playlist>/<Artist>/<Album>/<Track>.flac`
- **💾 Intelligent Caching** - Uses `snapshot_id` to detect playlist changes and minimize API calls
- **🔄 Continuous Sync** - Runs in a loop with configurable wait time between syncs
- **🎧 High-Quality Downloads** - Downloads tracks using YouTube search + yt-dlp (FLAC preferred, MP3 fallback)
- **🎼 Smart Format Detection** - Automatically checks for existing FLAC files first, then MP3
- **🏷️ Metadata Tagging** - Automatically tags downloaded files with artist, track, and album information
- **📊 Detailed Logging** - Configurable log levels for both application and yt-dlp
- **⚡ Rate Limit Protection** - Built-in retry logic with exponential backoff for API calls and download delays
- **🔑 Credential Passthrough** - Automatically passes your Spotify credentials to prevent rate limiting
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
- ❌ `spotdl` dependency (replaced with YouTube search + yt-dlp)

**NEW APPROACH:**
- ✅ **YouTube search + yt-dlp** replaces spotdl for reliable track downloads
- ✅ **Automatic FLAC preference** - Downloads FLAC when available, MP3 as fallback
- ✅ Downloads tracks to `MUSIC_PATH/<Playlist>/<Artist>/<Album>/`
- ✅ Smart playlist caching with snapshot-based change detection
- ✅ **Plex library sections must match Spotify playlist names** for 1-star deletion feature
- ✅ **Spotify credentials automatically passed** to prevent rate limiting
- ✅ **Configurable download delays** to respect API rate limits
- ✅ **Smart format detection** - Checks for FLAC first, then MP3
- ✅ You create Plex Smart Playlists manually (one-time setup)
- ✅ Plex Smart Playlists auto-update based on folder contents

**Why this change?** 
- `spotdl` was downloading wrong tracks due to lyrics processing corruption
- YouTube search + yt-dlp provides more reliable track matching
- FLAC-first preference gives you the best quality available
- Plex Smart Playlists are more reliable than API sync

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
| `SPOTIFY_REFRESH_TOKEN` | OAuth refresh token for playlist modifications. See [OAuth Setup](#-oauth-setup-for-playlist-modifications). | Yes* | |
| `SPOTIFY_URIS` | Comma-separated Spotify URIs (user or playlist). | Yes | |
| `MUSIC_PATH` | Absolute path where music files are stored/downloaded. | Yes | `/music` |
| `PLEX_URL` | Full URL for your Plex server (e.g., http://localhost:32400). | Yes | |
| `PLEX_TOKEN` | Your Plex authentication token. | Yes | |

*Required for 1-star deletion feature. Without it, the app runs in read-only mode (downloads work, but track removal from Spotify playlists won't).
| `PREFER_FLAC` | Download FLAC when available, MP3 fallback (true/false). | No | `true` |
| `SECONDS_TO_WAIT` | Seconds to wait between sync cycles. | No | `3600` |
| `LOG_LEVEL` | Python logging level (DEBUG, INFO, WARNING, ERROR). | No | `INFO` |
| `DOWNLOAD_DELAY` | Seconds to wait between track downloads (rate limiting). | No | `0.1` |

### Environment Variables Explained

**`PREFER_FLAC`**  
Controls download format preference:
- `true` (default): Downloads FLAC when available, falls back to MP3 if FLAC fails
- `false`: Downloads MP3 only (saves storage space)

File detection always checks for both FLAC and MP3 regardless of this setting - won't re-download if either format exists.

**`SPOTIPY_CLIENT_ID` & `SPOTIPY_CLIENT_SECRET`**  
Your personal Spotify API credentials. These are automatically passed to prevent rate limiting. Without your own credentials, the app uses shared keys that quickly hit rate limits.

**`DOWNLOAD_DELAY`**  
Time to wait between each track download. Default is `0.1` seconds (10 requests/second), which respects Spotify's recommended rate limit. Increase this value if you still encounter rate limiting (e.g., `0.2` for 5 req/sec).

**Example SPOTIFY_URIS:**
```
spotify:user:USERNAME,spotify:playlist:PLAYLIST_ID,spotify:playlist:ANOTHER_ID
```

### Getting Your Spotify Credentials

**⚠️ Important: Use your own credentials to avoid rate limiting!**

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy your Client ID and Client Secret
4. Add redirect URI: `http://127.0.0.1:8888/callback` (required for OAuth setup)
5. See [OAuth Setup](#-oauth-setup-for-playlist-modifications) to generate your refresh token

Your credentials are automatically used - no manual configuration needed.

### Getting Your Plex Token

1. Open Plex Web UI
2. Play any media item
3. Click the three-dot menu → "Get Info" → "View XML"
4. Look for `X-Plex-Token=` in the URL
5. Copy the token value

### 🔐 OAuth Setup for Playlist Modifications

**Why is this needed?**  
Spotify's basic "Client Credentials" authentication only allows read-only access. To **remove tracks from playlists** (1-star deletion feature), you need OAuth user authorization.

**The solution:** Generate a **refresh token** once on your local machine, then use it forever in Docker.

#### Step 1: Add Redirect URI to Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click your app → **Settings**
3. Under **Redirect URIs**, add:
   ```
   http://127.0.0.1:8888/callback
   ```
4. Click **Save**

#### Step 2: Generate Refresh Token (One-Time Setup)

Run this **on your local machine** (not on the NAS/Docker host) - it requires a browser:

```bash
# Clone or download the repo
cd Plexify

# Set your credentials
export SPOTIPY_CLIENT_ID="your_client_id"
export SPOTIPY_CLIENT_SECRET="your_client_secret"

# Run the token generator
python generate_spotify_token.py
```

A browser window will open → Log in to Spotify → Authorize the app → The script prints your refresh token.

#### Step 3: Add Token to Docker Configuration

Copy the printed `SPOTIFY_REFRESH_TOKEN` value to your `docker-compose.yml`:

```yaml
environment:
  - SPOTIPY_CLIENT_ID=your_client_id
  - SPOTIPY_CLIENT_SECRET=your_client_secret
  - SPOTIFY_REFRESH_TOKEN=AQDxxxxxxxxxxxxxxxx   # <-- Add this line
  # ... rest of your env vars
```

#### Step 4: Restart Docker

```bash
docker-compose down && docker-compose up -d
```

**That's it!** The refresh token is permanent (doesn't expire unless you revoke access in Spotify settings). You only need to do this once.

**What if I don't set SPOTIFY_REFRESH_TOKEN?**  
The app will run in **read-only mode**:
- ✅ Downloading tracks works
- ✅ Playlist syncing works  
- ❌ Removing tracks from Spotify playlists (1-star feature) won't work
- ⚠️ You'll see warnings in the logs about read-only mode

---

## Usage

### Local

```bash
export SPOTIPY_CLIENT_ID="your_spotify_client_id"
export SPOTIPY_CLIENT_SECRET="your_spotify_client_secret"
export SPOTIFY_REFRESH_TOKEN="your_refresh_token"  # Required for 1-star deletion
export SPOTIFY_URIS="spotify:user:your_username"
export MUSIC_PATH="/data/Music"
export PLEX_URL="http://localhost:32400"
export PLEX_TOKEN="your_plex_token"
export PREFER_FLAC="true"  # Optional: FLAC preferred (default), set to "false" for MP3-only
export LOG_LEVEL="INFO"
export DOWNLOAD_DELAY="0.1"  # Optional: 10 req/sec (default)

python src/main.py
```

### Docker 
```bash
docker run -d \
  --name=plexify \
  -e SPOTIPY_CLIENT_ID="your_spotify_client_id" \
  -e SPOTIPY_CLIENT_SECRET="your_spotify_client_secret" \
  -e SPOTIFY_REFRESH_TOKEN="your_refresh_token" \
  -e SPOTIFY_URIS="spotify:user:your_spotify_username" \
  -e MUSIC_PATH="/music" \
  -e PLEX_URL="http://plex:32400" \
  -e PLEX_TOKEN="your_plex_token" \
  -e PREFER_FLAC="true" \
  -e LOG_LEVEL="INFO" \
  -e DOWNLOAD_DELAY="0.1" \
  -v /path/to/your/music:/music \
  nyancod3r/plexify:latest
```

---

## File Organization

```
MUSIC_PATH/
├── Stoner.Blues.Rock/                    (Playlist 1 = Plex Library 1)
│   ├── Black Sabbath/
│   │   ├── Paranoid/
│   │   │   ├── Black Sabbath - War Pigs.flac
│   │   │   └── Black Sabbath - Paranoid.mp3
│   │   └── Master of Reality/
│   │       └── Black Sabbath - Sweet Leaf.flac
│   └── Kyuss/
│       └── Blues for the Red Sun/
│           └── Kyuss - Thumb.flac
└── Chill.Vibes/                          (Playlist 2 = Plex Library 2)
    └── Tycho/
        └── Dive/
            └── Tycho - A Walk.flac
```

**Structure explained:**
1. **Level 1:** `MUSIC_PATH` - Your root music folder
2. **Level 2:** Spotify playlist name (sanitized for filesystem) - **This must match your Plex library name**
3. **Level 3:** Artist name from track metadata
4. **Level 4:** Album name from track metadata
5. **Level 5:** Track file: `Artist - Track.flac` (or `.mp3` if FLAC unavailable)

**File naming convention:** `Artist - Track.extension`

**Format priority:** FLAC preferred, MP3 fallback - automatic, no configuration needed.

This structure allows you to:
- Create Plex libraries that map directly to Spotify playlists
- Enable 1-star deletion (library name = playlist name = folder name)
- Create Plex Smart Playlists per Spotify playlist (`Folder contains /music/Stoner.Blues.Rock`)
- Get the highest quality available (FLAC when possible)
- Identify tracks easily: artist name is always in the filename
- Avoid filename collisions when multiple artists have same track names

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
Multiple layers of protection against API rate limits:

1. **Credential Management**: Your `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` are automatically used
2. **Download Delays**: Configurable delay between downloads (default 0.1s = 10 req/sec)
3. **Exponential Backoff**: Built-in retry logic for failed API calls
4. **Smart Caching**: Minimizes API calls by only fetching changed playlists

### 🎼 Smart Format Detection & Download

**File Detection (when checking if track exists):**
1. First checks for `Artist - Track.flac`
2. Then checks for `Artist - Track.mp3`
3. If either exists, skips download

**Download Priority (when downloading new tracks):**
1. Attempts to download FLAC from best available YouTube source
2. If FLAC unavailable or fails, downloads MP3
3. Uses yt-dlp format selector: `bestaudio[ext=flac]/bestaudio[acodec*=flac]/bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best`

**Example scenarios:**
- New track: Downloads FLAC if available from YouTube, MP3 otherwise
- Existing FLAC: Skips download entirely
- Existing MP3: Skips download entirely (won't upgrade to FLAC)
- No existing file: Downloads best quality available

### 🎯 YouTube Search + yt-dlp Download Process

**Why we replaced spotdl:**
- spotdl was downloading wrong tracks due to lyrics processing corruption
- Example: Requesting "Dirty Streets - White Horse" would download "Bonez MC - bissu dumm"
- YouTube search + yt-dlp provides direct control over track selection

**Download process:**
1. **Search Phase**: Use yt-dlp to search YouTube for "Artist - Track"
2. **Selection Phase**: Get the top result video ID
3. **Download Phase**: Use yt-dlp with format selectors to download audio
4. **Fallback**: If YouTube fails, try spotdl as last resort (rarely used)

**Format Selection:**
- `bestaudio[ext=flac]` - Real FLAC if YouTube has it
- `bestaudio[acodec*=flac]` - Any FLAC codec
- `bestaudio[ext=m4a]` - High-quality AAC for conversion
- `bestaudio[ext=webm]` - Usually Opus, good for conversion  
- `bestaudio` - Any audio-only format
- `best[height<=480]` - Low-res video as last resort (has audio)

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
- File: `Black Sabbath - War Pigs.flac`

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
- Download engine changed: spotdl → YouTube search + yt-dlp
- Format support reduced: Only FLAC and MP3 supported (automatic preference)
- Plex playlist management removed (use Plex Smart Playlists instead)
- File organization changed to `<Playlist>/<Artist>/<Album>/<Track>` structure (added playlist folder level)
- **Plex libraries must now be named to match Spotify playlists** for 1-star deletion
- Removed bidirectional sync for Discover Weekly/Release Radar
- Added required `PLEX_URL` and `PLEX_TOKEN` variables
- Added `DOWNLOAD_DELAY` for rate limit control

**What stays the same:**
- Basic configuration approach
- Spotify playlist fetching
- File organization structure

**Migration steps:**
1. Update environment variable names in your config
2. Set `PLEX_URL` and `PLEX_TOKEN`
3. **Ensure you're using your own Spotify credentials** (not shared/public keys)
4. Point `MUSIC_PATH` to your Plex music library root
5. **Create new Plex libraries with names matching Spotify playlists** (see Plex Library Setup section)
6. Create Plex Smart Playlists to replace old automatic playlists
7. Remove any old Docker volumes or cache files (`spotify_playlists.json` will be recreated)
8. First run will re-download metadata but skip existing files
9. **File reorganization:** Existing files in `<Artist>/<Album>/` will not be moved. New structure is `<Playlist>/<Artist>/<Album>/`. Consider reorganizing manually or starting fresh.

---

## Troubleshooting

### 🚫 Rate Limiting from Spotify
**Problem:** Logs show `Your application has reached a rate/request limit. Retry will occur after: 86400`

**Root Cause:** Too many API calls to Spotify during downloads.

**Solutions:**
1. **✅ Verify your credentials are being used:**
   ```bash
   # Set LOG_LEVEL to DEBUG
   export LOG_LEVEL="DEBUG"
   # Run Plexify and check logs for credential usage confirmation
   ```

2. **Create your own Spotify credentials** if using shared/public keys:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app to get fresh API quota
   - Update `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`

3. **Increase download delay:**
   ```bash
   export DOWNLOAD_DELAY="0.2"  # 5 req/sec instead of 10
   ```

4. **Reduce sync frequency:**
   ```bash
   export SECONDS_TO_WAIT="7200"  # 2 hours between syncs
   ```

5. **Reduce number of playlists:**
   - Temporarily remove some URIs from `SPOTIFY_URIS`
   - Process large playlists separately

6. **Smart caching (enabled by default)** should prevent this on subsequent runs

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
2. Verify `yt-dlp` is installed: `yt-dlp --version`
3. Test manual download: `yt-dlp "ytsearch:Artist - Track Name"`
4. Check yt-dlp output in logs for specific errors (YouTube blocks, regional restrictions, etc.)

### 🔇 No Download Progress Visible
**Problem:** Logs stuck at "Downloading: Artist - Track"

**Solution:** Set `LOG_LEVEL=DEBUG` to see detailed yt-dlp output. If still stuck for >5 minutes:
1. Check if yt-dlp process is running: `ps aux | grep yt-dlp`
2. Kill hung process: `pkill yt-dlp`
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

### 🎵 Wrong Tracks Downloaded
**Problem:** App downloads songs that don't match the Spotify track

**This should no longer happen** with the YouTube search approach. If it does:
1. Set `LOG_LEVEL=DEBUG` to see search queries
2. Check if the YouTube search query matches your expected track
3. Manually search YouTube for the same query to verify results
4. Report as a bug with specific track details

---

## Requirements

- Python 3.11+
- `spotipy` (Spotify API client)
- `yt-dlp` (YouTube downloader)
- `youtubesearchpython` (YouTube search)
- `plexapi` (Plex server integration)
- `mutagen` (Audio metadata handling)

Install with:
```bash
pip install -r requirements.txt
```

---

## Support

For issues, feature requests, or questions:
- GitHub Issues: [nyancod3r/plexify](https://github.com/nyancod3r/plexify/issues)