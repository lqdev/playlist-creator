# Spotify Playlist Creator

A Python tool that converts Spotify playlists to various formats including Markdown documentation and M3U playlists with YouTube integration.

## Features

- 📝 **Markdown Export**: Convert playlists to beautifully formatted Markdown files with YouTube links
- 🎵 **M3U Playlists**: Generate M3U files with Spotify URLs
- ▶️ **YouTube Integration**: Create VLC-compatible M3U files with YouTube URLs
- 🔍 **Smart Link Priority**: YouTube links first, Spotify as backup
- 📊 **Detailed Info**: Track duration, album info, and artist details

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

### Command Line

```bash
# Run directly
uv run python -m playlist_creator.main

# Or if installed as package
uv run playlist-creator
```

### What you can generate:

1. **Markdown with YouTube links** - Beautiful documentation with YouTube as primary, Spotify as backup
2. **M3U with Spotify URLs** - For Spotify-compatible players
3. **YouTube M3U (VLC playable)** - Automatically searches YouTube
4. **YouTube M3U (fast)** - Search URLs only
5. **All formats** - Generate everything

## Output Files

- `{playlist-name}-playlist.md` - Markdown documentation
- `{playlist-name}-spotify.m3u` - Spotify URLs
- `{playlist-name}-youtube.m3u` - VLC-playable YouTube links
- `{playlist-name}-youtube-search.m3u` - YouTube search URLs

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
