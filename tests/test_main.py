"""Basic tests for the main module."""

from playlist_creator.main import clean_text, extract_playlist_id, format_duration


def test_extract_playlist_id():
    """Test playlist ID extraction from various URL formats."""
    # Standard Spotify URL
    url1 = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    assert extract_playlist_id(url1) == "37i9dQZF1DXcBWIGoYBM5M"

    # Spotify URI
    url2 = "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"
    assert extract_playlist_id(url2) == "37i9dQZF1DXcBWIGoYBM5M"

    # Just the ID
    url3 = "37i9dQZF1DXcBWIGoYBM5M"
    assert extract_playlist_id(url3) == "37i9dQZF1DXcBWIGoYBM5M"

    # Invalid URL
    url4 = "https://example.com/invalid"
    assert extract_playlist_id(url4) is None


def test_format_duration():
    """Test duration formatting."""
    assert format_duration(60000) == "1:00"  # 1 minute
    assert format_duration(125000) == "2:05"  # 2 minutes 5 seconds
    assert format_duration(30000) == "0:30"  # 30 seconds


def test_clean_text():
    """Test text cleaning for markdown."""
    assert clean_text("Normal text") == "Normal text"
    assert clean_text("Text with *asterisk*") == "Text with \\*asterisk\\*"
    assert clean_text("Text with [brackets]") == "Text with \\[brackets\\]"
    assert clean_text(None) == ""
