# src/core/path_utils.py
"""Cross-platform path utilities for ImpactScope."""

import re
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename across all platforms.

    Removes or replaces characters that are invalid on Windows, Linux, or macOS:
    - Windows: < > : " / \ | ? *
    - All platforms: null bytes, control characters

    Args:
        name: The string to sanitize.

    Returns:
        A sanitized string safe for use as a filename.
    """
    # Replace invalid characters with underscore
    # Windows invalid: < > : " / \ | ? *
    # Also handle null bytes and control characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, "_", name)

    # Remove leading/trailing dots and spaces (Windows doesn't allow these)
    sanitized = sanitized.strip(". ")

    # Replace multiple consecutive underscores with a single one
    sanitized = re.sub(r"_+", "_", sanitized)

    # Ensure the name isn't empty after sanitization
    if not sanitized:
        sanitized = "unnamed"

    # Windows reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    if sanitized.upper() in reserved_names:
        sanitized = f"_{sanitized}"

    return sanitized


def get_file_url(path: Path) -> str:
    """Get a file:// URL for a path that works cross-platform.

    Uses pathlib's as_uri() which correctly handles:
    - Windows: file:///C:/path/to/file
    - Unix: file:///path/to/file

    Args:
        path: Path object to convert to file:// URL.

    Returns:
        A file:// URL string.
    """
    return path.resolve().as_uri()
