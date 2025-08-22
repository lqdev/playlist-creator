"""
Configuration module for Spotify Playlist Creator.

Handles environment variables and configuration settings.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    # Try to load .env file from current directory or project root
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try project root
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip
    pass


def get_spotify_credentials() -> tuple[str | None, str | None]:
    """
    Get Spotify credentials from environment variables.

    Returns:
        tuple: (client_id, client_secret) or (None, None) if not found
    """
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    return client_id, client_secret


def validate_credentials(
    client_id: str | None, client_secret: str | None
) -> bool:
    """
    Validate that credentials are provided and not placeholder values.

    Args:
        client_id: Spotify client ID
        client_secret: Spotify client secret

    Returns:
        bool: True if credentials are valid, False otherwise
    """
    if not client_id or not client_secret:
        return False

    # Check for placeholder values
    placeholders = ["your_client_id_here", "your_client_secret_here", ""]

    return client_id not in placeholders and client_secret not in placeholders


def get_config_instructions() -> str:
    """
    Get instructions for setting up Spotify credentials.

    Returns:
        str: Instructions for credential setup
    """
    return """
To use this application, you need Spotify API credentials:

1. Go to https://developer.spotify.com/dashboard/
2. Create a new app
3. Copy your CLIENT_ID and CLIENT_SECRET
4. Set them as environment variables:

   Windows (PowerShell):
   $env:SPOTIFY_CLIENT_ID="your_client_id_here"
   $env:SPOTIFY_CLIENT_SECRET="your_client_secret_here"

   Windows (Command Prompt):
   set SPOTIFY_CLIENT_ID=your_client_id_here
   set SPOTIFY_CLIENT_SECRET=your_client_secret_here

   Linux/Mac:
   export SPOTIFY_CLIENT_ID="your_client_id_here"
   export SPOTIFY_CLIENT_SECRET="your_client_secret_here"

Alternatively, you can create a .env file in the project root:
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
"""
