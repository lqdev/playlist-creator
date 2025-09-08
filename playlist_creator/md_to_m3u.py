#!/usr/bin/env python3
"""
Markdown to M3U Converter

This script extracts YouTube links from existing markdown playlist files 
and converts them to M3U format for VLC and other media players.

Usage:
    python -m playlist_creator.md_to_m3u <markdown_file>
    python -m playlist_creator.md_to_m3u <directory_with_markdown_files>
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime


def extract_youtube_links_from_markdown(markdown_content):
    """Extract YouTube links and track information from markdown content."""
    tracks = []
    
    # Pattern to match track entries with YouTube links
    # Matches: 1. **Track Name** by Artist
    track_pattern = r'(\d+)\.\s*\*\*(.+?)\*\*\s*by\s*(.+?)(?:\n|$)'
    
    # Pattern to match YouTube links
    youtube_pattern = r'\[.*?Listen on YouTube.*?\]\((https://www\.youtube\.com/watch\?v=[\w-]+)\)'
    
    # Pattern to match duration
    duration_pattern = r'Duration:\s*(\d+):(\d+)'
    
    lines = markdown_content.split('\n')
    current_track = None
    
    for line in lines:
        # Check for track header
        track_match = re.search(track_pattern, line)
        if track_match:
            track_num = track_match.group(1)
            track_name = track_match.group(2).replace('\\', '')  # Remove escape characters
            artist = track_match.group(3).replace('\\', '')  # Remove escape characters
            
            current_track = {
                'number': int(track_num),
                'name': track_name,
                'artist': artist,
                'duration_seconds': 0,
                'youtube_url': None
            }
            continue
        
        # Check for duration
        if current_track:
            duration_match = re.search(duration_pattern, line)
            if duration_match:
                minutes = int(duration_match.group(1))
                seconds = int(duration_match.group(2))
                current_track['duration_seconds'] = (minutes * 60) + seconds
        
        # Check for YouTube link
        if current_track:
            youtube_match = re.search(youtube_pattern, line)
            if youtube_match:
                current_track['youtube_url'] = youtube_match.group(1)
                tracks.append(current_track)
                current_track = None
    
    return tracks


def generate_m3u_from_tracks(tracks, playlist_name="Playlist"):
    """Generate M3U content from track list."""
    m3u_content = "#EXTM3U\n"
    m3u_content += f"#PLAYLIST:{playlist_name}\n"
    m3u_content += "# Generated from markdown file with YouTube links\n"
    m3u_content += f"# Generated on {datetime.now().strftime('%B %d, %Y')}\n\n"
    
    youtube_count = 0
    
    for track in tracks:
        if track['youtube_url']:
            # Add extended info line
            m3u_content += f"#EXTINF:{track['duration_seconds']},{track['artist']} - {track['name']}\n"
            m3u_content += f"{track['youtube_url']}\n\n"
            youtube_count += 1
        else:
            # Add as comment if no YouTube link found
            m3u_content += f"# Track {track['number']}: {track['artist']} - {track['name']} (No YouTube link found)\n\n"
    
    print(f"Added {youtube_count} YouTube tracks to M3U playlist")
    
    return m3u_content


def extract_playlist_name_from_markdown(markdown_content):
    """Extract playlist name from markdown header."""
    # Look for the first h1 header
    header_match = re.search(r'^#\s+(.+?)$', markdown_content, re.MULTILINE)
    if header_match:
        # Clean up the playlist name
        name = header_match.group(1)
        # Remove emoji and special characters, keep basic punctuation
        name = re.sub(r'[^\w\s\-\(\)&\.,]', '', name).strip()
        return name
    return "Playlist"


def process_markdown_file(markdown_file_path, output_dir=None):
    """Process a single markdown file and generate M3U."""
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"Processing: {markdown_file_path}")
        
        # Extract playlist name from markdown
        playlist_name = extract_playlist_name_from_markdown(markdown_content)
        print(f"Playlist name: {playlist_name}")
        
        # Extract tracks with YouTube links
        tracks = extract_youtube_links_from_markdown(markdown_content)
        
        if not tracks:
            print("No tracks with YouTube links found in this file.")
            return False
        
        print(f"Found {len(tracks)} tracks")
        
        # Generate M3U content
        m3u_content = generate_m3u_from_tracks(tracks, playlist_name)
        
        # Determine output file path
        if output_dir is None:
            output_dir = Path(markdown_file_path).parent
        
        # Create safe filename
        safe_name = re.sub(r'[^\w\s\-]', '', playlist_name).strip()
        safe_name = re.sub(r'[-\s]+', '-', safe_name)
        output_file = Path(output_dir) / f"{safe_name}-youtube.m3u"
        
        # Save M3U file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        
        print(f"✅ Generated: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {markdown_file_path}: {e}")
        return False


def process_directory(directory_path, output_dir=None):
    """Process all markdown files in a directory."""
    directory = Path(directory_path)
    
    # Find all markdown files
    markdown_files = list(directory.glob("*.md")) + list(directory.glob("**/*.md"))
    
    if not markdown_files:
        print(f"No markdown files found in {directory_path}")
        return 0
    
    print(f"Found {len(markdown_files)} markdown files")
    
    success_count = 0
    for md_file in markdown_files:
        if process_markdown_file(md_file, output_dir):
            success_count += 1
        print()  # Add blank line between files
    
    return success_count


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Convert markdown playlist files to M3U format using YouTube links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m playlist_creator.md_to_m3u playlist.md
  python -m playlist_creator.md_to_m3u output/
  python -m playlist_creator.md_to_m3u output/my-playlist/ --output-dir converted/
        """
    )
    
    parser.add_argument(
        "input",
        help="Path to markdown file or directory containing markdown files"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for M3U files (default: same as input)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        sys.exit(1)
    
    print("🎵 Markdown to M3U Converter")
    print("=" * 40)
    
    success_count = 0
    
    if input_path.is_file():
        if input_path.suffix.lower() != '.md':
            print(f"Error: {input_path} is not a markdown file")
            sys.exit(1)
        
        if process_markdown_file(input_path, args.output_dir):
            success_count = 1
    
    elif input_path.is_dir():
        success_count = process_directory(input_path, args.output_dir)
    
    else:
        print(f"Error: {input_path} is neither a file nor a directory")
        sys.exit(1)
    
    print("=" * 40)
    if success_count > 0:
        print(f"✅ Successfully converted {success_count} file(s) to M3U format!")
        print("\nTo play in VLC: File → Open File → Select the .m3u file")
        print("The M3U files contain direct YouTube links that should play automatically.")
    else:
        print("❌ No files were successfully converted.")
        print("\nMake sure your markdown files contain YouTube links in this format:")
        print("   [Listen on YouTube](https://www.youtube.com/watch?v=VIDEO_ID)")


if __name__ == "__main__":
    main()
