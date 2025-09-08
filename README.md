# Spotify Playlist Creator

A Python tool that converts Spotify playlists to various formats including Markdown documentation and M3U playlists with YouTube integration.

## Features

- 📝 **Markdown Export**: Convert playlists to beautifully formatted Markdown files with YouTube links
- 🎵 **M3U Playlists**: Generate M3U files with Spotify URLs
- ▶️ **YouTube Integration**: Create VLC-compatible M3U files with YouTube URLs
- 🔍 **Smart Link Priority**: YouTube links first, Spotify as backup
- 📊 **Detailed Info**: Track duration, album info, and artist details
- 🔄 **Markdown to M3U**: Convert existing markdown playlist files to M3U format

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd playlist-creator

# Install with uv
uv sync
```

### Manual Installation

```bash
pip install spotipy requests
```

## Setup

1. **Get Spotify API Credentials**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Create a new app
   - Copy your `CLIENT_ID` and `CLIENT_SECRET`

2. **Configure the Application**
   - Copy `.env.example` to `.env`: `cp .env.example .env`
   - Edit `.env` and replace the placeholder values with your actual credentials:
     ```
     SPOTIFY_CLIENT_ID=your_actual_client_id
     SPOTIFY_CLIENT_SECRET=your_actual_client_secret
     ```
   
   **Alternative**: Set environment variables directly:
   ```powershell
   # Windows PowerShell
   $env:SPOTIFY_CLIENT_ID="your_actual_client_id"
   $env:SPOTIFY_CLIENT_SECRET="your_actual_client_secret"
   ```
   ```bash
   # Linux/Mac
   export SPOTIFY_CLIENT_ID="your_actual_client_id"
   export SPOTIFY_CLIENT_SECRET="your_actual_client_secret"
   ```

## Usage

### Creating Playlists from Spotify

```bash
# Run directly
uv run python -m playlist_creator.main

# Or if installed as package
uv run playlist-creator
```

### Converting Markdown to M3U

If you already have markdown playlist files (created by this tool or manually), you can convert them to M3U format:

```bash
# Convert a single markdown file
uv run python -m playlist_creator.md_to_m3u playlist.md

# Convert all markdown files in a directory
uv run python -m playlist_creator.md_to_m3u output/

# Convert with custom output directory
uv run python -m playlist_creator.md_to_m3u input/ --output-dir converted/

# Show help and all options
uv run python -m playlist_creator.md_to_m3u --help
```

**Examples:**
```bash
# Convert the crazy Four Tet playlist
uv run python -m playlist_creator.md_to_m3u "output/o/o-playlist.md"

# Batch convert all playlists
uv run python -m playlist_creator.md_to_m3u output/ --verbose
```

### What you can generate:

**From Spotify playlists:**
1. **Markdown with YouTube links** - Beautiful documentation with YouTube as primary, Spotify as backup
2. **M3U with Spotify URLs** - For Spotify-compatible players
3. **YouTube M3U (VLC playable)** - Automatically searches YouTube
4. **YouTube M3U (fast)** - Search URLs only
5. **All formats** - Generate everything

**From existing markdown files:**
- **YouTube M3U playlists** - Extract YouTube links from markdown and create VLC-compatible M3U files
- **Batch processing** - Convert multiple markdown files at once
- **Smart parsing** - Automatically extracts track info, artist, duration, and YouTube links

## Output Files

**From Spotify conversion:**
- `{playlist-name}-playlist.md` - Markdown documentation
- `{playlist-name}-spotify.m3u` - Spotify URLs
- `{playlist-name}-youtube.m3u` - VLC-playable YouTube links
- `{playlist-name}-youtube-search.m3u` - YouTube search URLs

**From markdown conversion:**
- `{playlist-name}-youtube.m3u` - VLC-playable YouTube M3U extracted from markdown

## Examples

**Playing in VLC:**
1. Open VLC Media Player
2. File → Open File → Select the `.m3u` file
3. YouTube links play automatically!

## Requirements

- Python 3.12+
- Spotify Developer Account
- Internet connection for YouTube search

## Dependencies

- `spotipy` - Spotify Web API wrapper
- `requests` - HTTP library for YouTube search

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run ruff check .
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

### Troubleshooting

**Markdown to M3U conversion:**
- Ensure your markdown files contain YouTube links in the format: `[Listen on YouTube](https://www.youtube.com/watch?v=VIDEO_ID)`
- Check that track entries follow the pattern: `1. **Track Name** by Artist`
- Duration should be formatted as: `Duration: MM:SS`
- Use `--verbose` flag to see detailed processing information
