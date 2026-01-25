#!/usr/bin/env python3
"""
generate_spotify_token.py - One-time script to generate Spotify refresh token

Run this script ONCE on a machine with a browser to authorize Plexify.
Then copy the refresh token to your docker-compose.yml as SPOTIFY_REFRESH_TOKEN.

Usage:
    1. Set environment variables:
       export SPOTIPY_CLIENT_ID=your_client_id
       export SPOTIPY_CLIENT_SECRET=your_client_secret
    
    2. Run this script:
       python generate_spotify_token.py
    
    3. A browser will open - authorize with Spotify
    
    4. Copy the printed SPOTIFY_REFRESH_TOKEN to your docker-compose.yml

Note: Make sure your Spotify app has http://localhost:8888/callback as a redirect URI
      in your Spotify Developer Dashboard.
"""

import os
import sys

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    print("❌ spotipy not installed. Run: pip install spotipy")
    sys.exit(1)

# Required scopes for playlist modification
SCOPES = "playlist-modify-public playlist-modify-private playlist-read-private"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

def main():
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Error: SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set")
        print()
        print("Set them with:")
        print("  export SPOTIPY_CLIENT_ID=your_client_id")
        print("  export SPOTIPY_CLIENT_SECRET=your_client_secret")
        sys.exit(1)
    
    print("="*60)
    print("🔐 Spotify Token Generator for Plexify")
    print("="*60)
    print()
    print("⚠️  IMPORTANT: Make sure you've added this redirect URI to your")
    print("   Spotify app in the Developer Dashboard:")
    print(f"   {REDIRECT_URI}")
    print()
    print("📱 A browser window will open. Log in and authorize the app.")
    print()
    input("Press Enter to continue...")
    
    # Create OAuth manager - this will open browser for authorization
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=".spotify_token_cache",
        open_browser=True
    )
    
    # Get token (triggers browser auth if needed)
    # First call get_access_token to trigger auth flow, then get cached token
    auth_manager.get_access_token()
    token_info = auth_manager.get_cached_token()
    
    if not token_info:
        print("❌ Failed to get token. Please try again.")
        sys.exit(1)
    
    refresh_token = token_info.get('refresh_token')
    
    if not refresh_token:
        print("❌ No refresh token in response. Please try again.")
        sys.exit(1)
    
    # Verify it works
    sp = spotipy.Spotify(auth_manager=auth_manager)
    user = sp.current_user()
    
    print()
    print("="*60)
    print("✅ SUCCESS! Authorized as:", user['display_name'])
    print("="*60)
    print()
    print("Add this to your docker-compose.yml environment:")
    print()
    print(f"  SPOTIFY_REFRESH_TOKEN={refresh_token}")
    print()
    print("="*60)
    print()
    print("You can delete the .spotify_token_cache file now.")
    print("The refresh token above is all you need.")
    
    # Clean up cache file
    try:
        os.remove(".spotify_token_cache")
    except:
        pass

if __name__ == "__main__":
    main()
