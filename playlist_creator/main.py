#!/usr/bin/env python3
"""
Spotify Playlist to Markdown and M3U Converter

This script extracts data from a Spotify playlist and converts it to markdown and M3U files.
The YouTube M3U option creates playable playlists for VLC and other media players.

You'll need to set up a Spotify app at https://developer.spotify.com/dashboard/
to get your CLIENT_ID and CLIENT_SECRET.
"""

import os
import re
import time
import urllib.parse
from datetime import datetime
from pathlib import Path

import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .config import (
    get_config_instructions,
    get_spotify_credentials,
    validate_credentials,
)


def setup_spotify_client(client_id, client_secret):
    """Initialize and return Spotify client."""
    try:
        credentials = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=credentials)
        return sp
    except Exception as e:
        print(f"Error setting up Spotify client: {e}")
        return None


def extract_playlist_id(url):
    """Extract playlist ID from Spotify URL."""
    # Handle different URL formats
    patterns = [r"playlist/([a-zA-Z0-9]+)", r"spotify:playlist:([a-zA-Z0-9]+)"]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # If it's already just an ID
    if re.match(r"^[a-zA-Z0-9]+$", url):
        return url

    return None


def get_playlist_data(sp, playlist_id):
    """Fetch playlist data from Spotify API."""
    try:
        # Get playlist info
        playlist = sp.playlist(playlist_id)

        # Get all tracks (handle pagination)
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        tracks.extend(results["items"])

        while results["next"]:
            results = sp.next(results)
            tracks.extend(results["items"])

        return playlist, tracks

    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 404:
            print(
                "Playlist not found. Make sure the playlist is public or you have access to it."
            )
        else:
            print(f"Spotify API error: {e}")
        return None, None
    except Exception as e:
        print(f"Error fetching playlist data: {e}")
        return None, None


def format_duration(duration_ms):
    """Convert milliseconds to MM:SS format."""
    seconds = duration_ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"


def clean_text(text):
    """Clean text for markdown (escape special characters)."""
    if not text:
        return ""
    # Escape markdown special characters
    special_chars = ["*", "_", "`", "[", "]", "(", ")", "#", "+", "-", ".", "!"]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text


def generate_markdown(playlist, tracks):
    """Generate markdown content from playlist data with YouTube link priority."""

    # Header
    playlist_name = clean_text(playlist["name"])
    description = clean_text(playlist.get("description", ""))
    owner = playlist["owner"]["display_name"]
    total_tracks = playlist["tracks"]["total"]

    print(f"Generating markdown for playlist with {total_tracks} tracks...")
    print("Searching YouTube for track links (this may take a moment)...")

    # Calculate total duration
    total_duration_ms = sum(
        track["track"]["duration_ms"]
        for track in tracks
        if track["track"] and track["track"]["duration_ms"]
    )
    total_duration = format_duration(total_duration_ms)

    markdown = f"""# {playlist_name}

**Created by:** {owner}
**Total tracks:** {total_tracks}
**Total duration:** {total_duration}
**Generated on:** {datetime.now().strftime('%B %d, %Y')}

"""

    if description:
        markdown += f"**Description:** {description}\n\n"

    markdown += "---\n\n## Tracks\n\n"

    # Track list
    youtube_found_count = 0
    for i, item in enumerate(tracks, 1):
        track = item["track"]

        if not track:  # Handle None tracks (deleted/unavailable)
            markdown += f"{i}. *[Track unavailable]*\n"
            continue

        track_name = clean_text(track["name"])
        artists = ", ".join([clean_text(artist["name"]) for artist in track["artists"]])
        album = clean_text(track["album"]["name"])
        duration = format_duration(track["duration_ms"])

        print(f"Processing {i}/{total_tracks}: {artists} - {track_name}")

        # Add track with basic info
        markdown += f"{i}. **{track_name}** by {artists}\n"
        markdown += f"   - Album: *{album}*\n"
        markdown += f"   - Duration: {duration}\n"

        # Try to find YouTube link first, fall back to Spotify
        search_query = f"{artists} {track_name}"
        youtube_url = search_youtube(search_query)
        
        if youtube_url and "watch?v=" in youtube_url:
            # Found a direct YouTube video link
            markdown += f"   - [Listen on YouTube]({youtube_url})\n"
            youtube_found_count += 1
            # Add Spotify as backup
            if track["external_urls"].get("spotify"):
                markdown += (
                    f"   - [Backup: Listen on Spotify]({track['external_urls']['spotify']})\n"
                )
        else:
            # YouTube search failed, use Spotify as primary
            if track["external_urls"].get("spotify"):
                markdown += (
                    f"   - [Listen on Spotify]({track['external_urls']['spotify']})\n"
                )

        markdown += "\n"
        
        # Small delay to be respectful to YouTube
        time.sleep(0.5)

    print(f"Found YouTube links for {youtube_found_count}/{total_tracks} tracks")

    markdown += "---\n\n"
    markdown += "*Generated using Spotify Web API with YouTube link integration*\n\n"
    
    # Add original Spotify playlist link
    if playlist.get("external_urls", {}).get("spotify"):
        markdown += f"**Original Spotify Playlist:** [Listen on Spotify]({playlist['external_urls']['spotify']})\n"

    return markdown


def generate_m3u(playlist, tracks):
    """Generate M3U playlist content from playlist data."""

    playlist_name = playlist["name"]

    # M3U header
    m3u_content = "#EXTM3U\n"
    m3u_content += f"#PLAYLIST:{playlist_name}\n\n"

    for item in tracks:
        track = item["track"]

        if not track:  # Handle None tracks (deleted/unavailable)
            continue

        track_name = track["name"]
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        duration_seconds = track["duration_ms"] // 1000

        # Add extended info line
        m3u_content += f"#EXTINF:{duration_seconds},{artists} - {track_name}\n"

        # Add Spotify URL (most M3U players can handle Spotify URLs)
        if track["external_urls"].get("spotify"):
            m3u_content += f"{track['external_urls']['spotify']}\n"
        else:
            # Fallback: create a search URL or comment
            search_query = f"{artists} {track_name}".replace(" ", "%20")
            m3u_content += f"# Search: https://open.spotify.com/search/{search_query}\n"

        m3u_content += "\n"

    return m3u_content


def search_youtube(query, max_retries=3):
    """Search for a track on YouTube and return the first video URL."""

    # Clean and encode the search query
    clean_query = re.sub(r"[^\w\s-]", "", query).strip()
    encoded_query = urllib.parse.quote_plus(clean_query)

    # YouTube search URL (we'll scrape the results page)
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Look for video IDs in the response
            # YouTube video IDs are 11 characters long and alphanumeric with - and _
            video_id_pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
            matches = re.findall(video_id_pattern, response.text)

            if matches:
                # Return the first video URL
                video_id = matches[0]
                return f"https://www.youtube.com/watch?v={video_id}"

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for '{query}': {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retrying
            continue

    # If all attempts fail, return a search URL that users can manually check
    return f"https://www.youtube.com/results?search_query={encoded_query}"


def generate_youtube_m3u(playlist, tracks, include_search_fallback=True):
    """Generate M3U playlist with YouTube URLs that VLC can play."""

    playlist_name = playlist["name"]

    # M3U header
    m3u_content = "#EXTM3U\n"
    m3u_content += f"#PLAYLIST:{playlist_name}\n"
    m3u_content += "# YouTube playlist generated from Spotify - playable in VLC\n"
    m3u_content += f"# Generated on {datetime.now().strftime('%B %d, %Y')}\n\n"

    total_tracks = len([t for t in tracks if t["track"]])
    print(f"Searching YouTube for {total_tracks} tracks...")

    found_count = 0

    for i, item in enumerate(tracks, 1):
        track = item["track"]

        if not track:  # Handle None tracks (deleted/unavailable)
            continue

        track_name = track["name"]
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        duration_seconds = track["duration_ms"] // 1000

        # Create search query
        search_query = f"{artists} {track_name}"

        print(f"Searching {i}/{total_tracks}: {search_query}")

        # Search YouTube
        youtube_url = search_youtube(search_query)

        # Add extended info line
        m3u_content += f"#EXTINF:{duration_seconds},{artists} - {track_name}\n"

        # Check if we got a direct video URL or a search URL
        if "watch?v=" in youtube_url:
            m3u_content += f"{youtube_url}\n"
            found_count += 1
        else:
            # Fallback: add as comment if requested
            if include_search_fallback:
                m3u_content += f"# Search: {youtube_url}\n"
            else:
                m3u_content += "# Not found on YouTube\n"

        m3u_content += "\n"

        # Small delay to be respectful to YouTube
        time.sleep(0.5)

    print(f"Found direct YouTube links for {found_count}/{total_tracks} tracks")

    return m3u_content


def generate_youtube_m3u_fast(playlist, tracks):
    """Generate M3U playlist with YouTube search URLs (faster, no API calls)."""

    playlist_name = playlist["name"]

    # M3U header
    m3u_content = "#EXTM3U\n"
    m3u_content += f"#PLAYLIST:{playlist_name}\n"
    m3u_content += (
        "# YouTube search playlist - manually verify URLs for best results\n"
    )
    m3u_content += f"# Generated on {datetime.now().strftime('%B %d, %Y')}\n\n"

    for item in tracks:
        track = item["track"]

        if not track:  # Handle None tracks (deleted/unavailable)
            continue

        track_name = track["name"]
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        duration_seconds = track["duration_ms"] // 1000

        # Create search query
        search_query = f"{artists} {track_name}"
        encoded_query = urllib.parse.quote_plus(search_query)

        # Add extended info line
        m3u_content += f"#EXTINF:{duration_seconds},{artists} - {track_name}\n"

        # Add YouTube search URL
        youtube_search_url = (
            f"https://www.youtube.com/results?search_query={encoded_query}"
        )
        m3u_content += f"# Manual search needed: {youtube_search_url}\n"
        m3u_content += f"# Spotify: {track['external_urls'].get('spotify', 'N/A')}\n"
        m3u_content += "\n"

    return m3u_content


def save_file(content, filename, output_dir="output"):
    """Save content to file in organized directory structure."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create full file path
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"File saved: {file_path}")
        return True
    except Exception as e:
        print(f"Error saving file {file_path}: {e}")
        return False


def main():
    """Main function."""
    # Get credentials from environment variables
    client_id, client_secret = get_spotify_credentials()

    # Validate credentials
    if not validate_credentials(client_id, client_secret):
        print("Spotify credentials not found or invalid!")
        print(get_config_instructions())
        return

    # Setup Spotify client
    sp = setup_spotify_client(client_id, client_secret)
    if not sp:
        return

    # Get playlist URL from user
    playlist_url = input("Enter Spotify playlist URL or ID: ").strip()

    # Extract playlist ID
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        print("Invalid Spotify playlist URL or ID.")
        return

    print(f"Fetching playlist data for ID: {playlist_id}")

    # Get playlist data
    playlist, tracks = get_playlist_data(sp, playlist_id)
    if not playlist:
        return

    print(f"Found playlist: '{playlist['name']}' with {len(tracks)} tracks")

    # Ask user what formats they want
    print("\nWhat formats would you like to generate?")
    print("1. Markdown with YouTube links (falls back to Spotify)")
    print("2. M3U with Spotify URLs")
    print("3. YouTube M3U (VLC playable - searches YouTube)")
    print("4. YouTube M3U (fast - search URLs only)")
    print("5. All formats")

    choice = input("Enter choice (1-5): ").strip()

    # Create safe filename base and output directory
    safe_name = re.sub(r"[^\w\s-]", "", playlist["name"]).strip()
    safe_name = re.sub(r"[-\s]+", "-", safe_name)
    
    # Create output directory structure: output/playlist-name/
    output_dir = os.path.join("output", safe_name)
    print(f"\nFiles will be saved to: {output_dir}/")

    success_count = 0

    # Generate requested formats
    if choice in ["1", "5"]:
        # Generate and save markdown
        print("Generating markdown...")
        markdown_content = generate_markdown(playlist, tracks)
        filename = f"{safe_name}-playlist.md"
        if save_file(markdown_content, filename, output_dir):
            success_count += 1

    if choice in ["2", "5"]:
        # Generate and save M3U with Spotify URLs
        print("Generating Spotify M3U...")
        m3u_content = generate_m3u(playlist, tracks)
        filename = f"{safe_name}-spotify.m3u"
        if save_file(m3u_content, filename, output_dir):
            success_count += 1

    if choice in ["3", "5"]:
        # Generate and save YouTube M3U (with actual searches)
        print("Generating YouTube M3U (this may take a while)...")
        print("Searching YouTube for each track...")
        youtube_m3u_content = generate_youtube_m3u(playlist, tracks)
        filename = f"{safe_name}-youtube.m3u"
        if save_file(youtube_m3u_content, filename, output_dir):
            success_count += 1

    if choice in ["4", "5"]:
        # Generate and save fast YouTube M3U (search URLs only)
        print("Generating fast YouTube M3U...")
        youtube_fast_content = generate_youtube_m3u_fast(playlist, tracks)
        filename = f"{safe_name}-youtube-search.m3u"
        if save_file(youtube_fast_content, filename, output_dir):
            success_count += 1

    if success_count > 0:
        print(f"\nSuccessfully generated {success_count} file(s)!")
        print("\nHow to use your files:")
        print("📄 Markdown: Host on GitHub, your website, etc. (now with YouTube links!)")
        print("🎵 Spotify M3U: Import into players that support Spotify")
        print("▶️  YouTube M3U: Open directly in VLC - should play automatically!")
        print("🔍 YouTube Search M3U: Contains search URLs you can manually verify")
        print("\nTo play in VLC: File → Open File → Select the .m3u file")
    else:
        print("No files were generated.")


if __name__ == "__main__":
    main()
