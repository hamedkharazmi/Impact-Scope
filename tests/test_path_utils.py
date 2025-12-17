# tests/test_path_utils.py
"""Unit tests for the path utilities module."""

from pathlib import Path

import pytest

from src.utils.path_utils import get_file_url, sanitize_filename


class TestSanitizeFilename:
    """Test filename sanitization functionality."""

    def test_basic_filename(self):
        """Test basic filename without special characters."""
        assert sanitize_filename("test.txt") == "test.txt"
        assert sanitize_filename("my_file.c") == "my_file.c"

    def test_windows_invalid_characters(self):
        """Test removing Windows invalid characters."""
        assert sanitize_filename("test<file>") == "test_file"
        assert sanitize_filename("test:file") == "test_file"
        assert sanitize_filename('test"file') == "test_file"
        assert sanitize_filename("test/file") == "test_file"
        assert sanitize_filename("test\\file") == "test_file"
        assert sanitize_filename("test|file") == "test_file"
        assert sanitize_filename("test?file") == "test_file"
        assert sanitize_filename("test*file") == "test_file"

    def test_leading_trailing_dots_spaces(self):
        """Test removing leading/trailing dots and spaces."""
        assert sanitize_filename(" test ") == "test"
        assert sanitize_filename(".test") == "test"
        assert sanitize_filename("test.") == "test"
        assert sanitize_filename(" test ") == "test"

    def test_consecutive_underscores(self):
        """Test replacing multiple consecutive underscores."""
        assert sanitize_filename("test__file") == "test_file"
        assert sanitize_filename("test<>file") == "test_file"

    def test_empty_and_whitespace_only(self):
        """Test handling of empty or whitespace-only strings."""
        assert sanitize_filename("") == "unnamed"
        assert sanitize_filename("   ") == "unnamed"
        assert sanitize_filename("...") == "unnamed"

    def test_windows_reserved_names(self):
        """Test prefixing Windows reserved names."""
        reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "LPT1", "LPT9"]
        for name in reserved_names:
            assert sanitize_filename(name) == f"_{name}"
            assert sanitize_filename(name.lower()) == f"_{name.lower()}"
            assert sanitize_filename(name.upper()) == f"_{name.upper()}"

    def test_control_characters(self):
        """Test removing control characters."""
        assert sanitize_filename("test\x00file") == "test_file"  # Null byte
        assert sanitize_filename("test\x01file") == "test_file"  # Control character
        assert sanitize_filename("test\x1ffile") == "test_file"  # Control character

    def test_commit_hashes(self):
        """Test sanitizing commit hashes (common use case)."""
        assert sanitize_filename("a1b2c3d4") == "a1b2c3d4"
        assert sanitize_filename("a1b2:c3d4") == "a1b2_c3d4"
        assert sanitize_filename("feature/branch") == "feature_branch"

    def test_complex_cases(self):
        """Test complex filename cases."""
        # Multiple issues
        assert sanitize_filename("  test<file>  ") == "test_file"
        # Reserved name with special chars
        assert sanitize_filename("CON.txt") == "_CON.txt"
        # Very long with multiple issues
        complex_name = "feature/branch:name<file>with*lots|of?issues"
        result = sanitize_filename(complex_name)
        # Should not contain any invalid characters
        invalid_chars = '<>:"/\\|?*'
        assert not any(char in result for char in invalid_chars)
        assert not result.startswith(".")
        assert not result.endswith(".")
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_edge_cases(self):
        """Test edge cases."""
        # Only invalid characters
        assert sanitize_filename('<>:"|?*') == "unnamed"
        # Mixed valid/invalid
        assert sanitize_filename("a<b>c") == "a_b_c"
        # Unicode characters (should be preserved if valid)
        assert sanitize_filename("test_ñáme") == "test_ñáme"


class TestGetFileUrl:
    """Test file URL generation."""

    def test_basic_path(self):
        """Test basic path to URL conversion."""
        path = Path("/tmp/test.html")
        url = get_file_url(path)
        # On Windows, this will be file:///C:/tmp/test.html
        # On Unix, this will be file:///tmp/test.html
        assert url.startswith("file://")
        assert url.endswith("/tmp/test.html")

    def test_windows_path_simulation(self):
        """Test Windows-style path simulation."""
        # On Windows, this would be C:\tmp\test.html -> file:///C:/tmp/test.html
        # But pathlib handles it correctly on all platforms
        path = Path("C:/tmp/test.html")
        url = get_file_url(path)
        assert url.startswith("file://")
        assert "C:/tmp/test.html" in url

    def test_relative_path(self):
        """Test relative path conversion."""
        path = Path("test.html")
        url = get_file_url(path)
        assert url.startswith("file://")
        assert url.endswith("test.html")

    def test_path_with_spaces(self):
        """Test path with spaces."""
        path = Path("/path with spaces/test.html")
        url = get_file_url(path)
        # URL encoding will handle spaces
        assert url.startswith("file://")
        assert "path%20with%20spaces" in url
        assert url.endswith("test.html")

    def test_path_with_special_chars(self):
        """Test path with special characters."""
        path = Path("/path/with[special]chars.html")
        url = get_file_url(path)
        # URL encoding will handle special characters
        assert url.startswith("file://")
        assert "with%5Bspecial%5Dchars" in url
        assert url.endswith(".html")

    def test_absolute_path_resolution(self):
        """Test that paths are resolved to absolute."""
        relative_path = Path("test.html")
        absolute_url = get_file_url(relative_path)

        absolute_path = Path("test.html").resolve()
        expected_url = absolute_path.as_uri()

        assert absolute_url == expected_url

    def test_subdirectory_path(self):
        """Test path with subdirectories."""
        path = Path("artifacts/project/commit/call_graphs/graph.html")
        url = get_file_url(path)
        assert url.startswith("file://")
        assert "artifacts/project/commit/call_graphs/graph.html" in url
