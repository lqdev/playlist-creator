"""Test configuration module."""

import os

from playlist_creator.config import get_spotify_credentials, validate_credentials


def test_validate_credentials():
    """Test credential validation."""
    # Valid credentials
    assert validate_credentials("valid_id", "valid_secret") is True

    # Invalid credentials
    assert validate_credentials(None, None) is False
    assert validate_credentials("", "") is False
    assert validate_credentials("your_client_id_here", "valid_secret") is False
    assert validate_credentials("valid_id", "your_client_secret_here") is False


def test_get_spotify_credentials_no_env():
    """Test getting credentials when environment variables are not set."""
    # Clear any existing env vars for this test
    old_id = os.environ.get("SPOTIFY_CLIENT_ID")
    old_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if "SPOTIFY_CLIENT_ID" in os.environ:
        del os.environ["SPOTIFY_CLIENT_ID"]
    if "SPOTIFY_CLIENT_SECRET" in os.environ:
        del os.environ["SPOTIFY_CLIENT_SECRET"]

    try:
        client_id, client_secret = get_spotify_credentials()
        assert client_id is None
        assert client_secret is None
    finally:
        # Restore original values
        if old_id:
            os.environ["SPOTIFY_CLIENT_ID"] = old_id
        if old_secret:
            os.environ["SPOTIFY_CLIENT_SECRET"] = old_secret


def test_get_spotify_credentials_with_env():
    """Test getting credentials when environment variables are set."""
    os.environ["SPOTIFY_CLIENT_ID"] = "test_id"
    os.environ["SPOTIFY_CLIENT_SECRET"] = "test_secret"

    try:
        client_id, client_secret = get_spotify_credentials()
        assert client_id == "test_id"
        assert client_secret == "test_secret"
    finally:
        # Clean up
        del os.environ["SPOTIFY_CLIENT_ID"]
        del os.environ["SPOTIFY_CLIENT_SECRET"]
