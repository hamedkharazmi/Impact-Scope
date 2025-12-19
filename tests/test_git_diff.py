# tests/test_git_diff.py
"""Unit tests for the git diff module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from git import BadName

from src.core.git_diff import get_commit_diff


class TestGetCommitDiff:
    """Test Git diff parsing functionality."""

    def test_valid_commit_with_changes(self):
        """Test parsing a valid commit with C file changes."""
        # Mock Git objects
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]

        # Mock diff with C file changes
        mock_diff = Mock()
        mock_diff.a_path = "src/main.c"
        mock_diff.b_path = "src/main.c"
        mock_diff.diff.decode.return_value = """diff --git a/src/main.c b/src/main.c
index 1234567..abcdef0 100644
--- a/src/main.c
+++ b/src/main.c
@@ -1,5 +1,5 @@
 #include <stdio.h>

 int main() {
-    printf("hello");
+    printf("hello world");
     return 0;
 }
"""

        mock_commit.diff.return_value = [mock_diff]

        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.return_value = mock_commit

            result = get_commit_diff("/fake/path", "abc123")

            assert "src/main.c" in result
            assert result["src/main.c"] == [(4, 4)]

    def test_commit_with_multiple_hunks(self):
        """Test parsing a commit with multiple change hunks."""
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]

        mock_diff = Mock()
        mock_diff.a_path = "src/utils.c"
        mock_diff.b_path = "src/utils.c"
        mock_diff.diff.decode.return_value = """diff --git a/src/utils.c b/src/utils.c
index 1234567..abcdef0 100644
--- a/src/utils.c
+++ b/src/utils.c
@@ -10,3 +10,3 @@
 void foo() {
-    return 1;
+    return 2;
 }
@@ -20,3 +20,3 @@
 void bar() {
-    return 3;
+    return 4;
 }
"""

        mock_commit.diff.return_value = [mock_diff]

        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.return_value = mock_commit

            result = get_commit_diff("/fake/path", "abc123")

            assert "src/utils.c" in result
            assert set(result["src/utils.c"]) == {(11, 11), (21, 21)}

    def test_commit_with_consecutive_changes(self):
        """Test parsing a commit with consecutive changed lines."""
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]

        mock_diff = Mock()
        mock_diff.a_path = "src/main.c"
        mock_diff.b_path = "src/main.c"
        mock_diff.diff.decode.return_value = """diff --git a/src/main.c b/src/main.c
index 1234567..abcdef0 100644
--- a/src/main.c
+++ b/src/main.c
@@ -5,6 +5,6 @@
 int func() {
-    printf("line 1");
-    printf("line 2");
-    printf("line 3");
+    printf("modified line 1");
+    printf("modified line 2");
+    printf("modified line 3");
     printf("line 4");
     return 0;
 }
"""

        mock_commit.diff.return_value = [mock_diff]

        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.return_value = mock_commit

            result = get_commit_diff("/fake/path", "abc123")

            assert "src/main.c" in result
            # Consecutive lines 6, 7, 8 should be grouped into (6, 8)
            assert result["src/main.c"] == [(6, 8)]

    def test_commit_with_header_file_changes(self):
        """Test parsing a commit with header file changes."""
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]

        mock_diff = Mock()
        mock_diff.a_path = "include/utils.h"
        mock_diff.b_path = "include/utils.h"
        mock_diff.diff.decode.return_value = """diff --git a/include/utils.h b/include/utils.h
index 1234567..abcdef0 100644
--- a/include/utils.h
+++ b/include/utils.h
@@ -5,3 +5,3 @@
 #define VERSION "1.0"
-#define DEBUG 0
+#define DEBUG 1
"""

        mock_commit.diff.return_value = [mock_diff]

        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.return_value = mock_commit

            result = get_commit_diff("/fake/path", "abc123")

            assert "include/utils.h" in result
            assert result["include/utils.h"] == [(6, 6)]

    def test_commit_with_no_c_changes(self):
        """Test parsing a commit with no C/C++ file changes."""
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]

        mock_diff = Mock()
        mock_diff.a_path = "README.md"
        mock_diff.b_path = "README.md"
        mock_diff.diff.decode.return_value = """diff --git a/README.md b/README.md
index 1234567..abcdef0 100644
--- a/README.md
+++ b/README.md
@@ -1,1 +1,1 @@
-# Project
+# My Project
"""

        mock_commit.diff.return_value = [mock_diff]

        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.return_value = mock_commit

            result = get_commit_diff("/fake/path", "abc123")

            assert result == {}

    def test_commit_with_mixed_file_types(self):
        """Test parsing a commit with both C files and other files."""
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]

        # C file diff
        mock_diff_c = Mock()
        mock_diff_c.a_path = "src/main.c"
        mock_diff_c.b_path = "src/main.c"
        mock_diff_c.diff.decode.return_value = """diff --git a/src/main.c b/src/main.c
index 1234567..abcdef0 100644
--- a/src/main.c
+++ b/src/main.c
@@ -1,2 +1,2 @@
 int main() {
-    return 0;
+    return 1;
 }
"""

        # Non-C file diff
        mock_diff_md = Mock()
        mock_diff_md.a_path = "README.md"
        mock_diff_md.b_path = "README.md"
        mock_diff_md.diff.decode.return_value = """diff --git a/README.md b/README.md
index 1234567..abcdef0 100644
--- a/README.md
+++ b/README.md
@@ -1,1 +1,1 @@
-# Old
+# New
"""

        mock_commit.diff.return_value = [mock_diff_c, mock_diff_md]

        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.return_value = mock_commit

            result = get_commit_diff("/fake/path", "abc123")

            assert "src/main.c" in result
            assert result["src/main.c"] == [(2, 2)]
            assert "README.md" not in result

    def test_invalid_commit_hash(self):
        """Test error handling for invalid commit hash."""
        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.side_effect = BadName("invalid commit")

            with pytest.raises(ValueError, match="Commit 'invalid' does not exist"):
                get_commit_diff("/fake/path", "invalid")

    def test_initial_commit_no_parents(self):
        """Test handling of initial commit with no parents."""
        mock_commit = Mock()
        mock_commit.parents = []  # No parents

        mock_diff = Mock()
        mock_diff.a_path = "src/main.c"
        mock_diff.b_path = "src/main.c"
        mock_diff.diff.decode.return_value = """diff --git a/src/main.c b/src/main.c
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/main.c
@@ -0,0 +1,5 @@
+#include <stdio.h>
+int main() {
+    return 0;
+}
"""

        mock_commit.diff.return_value = [mock_diff]

        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.return_value = mock_commit

            result = get_commit_diff("/fake/path", "initial")

            assert "src/main.c" in result
            assert result["src/main.c"] == [(1, 4)]

    def test_renamed_file(self):
        """Test handling of renamed files."""
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]

        mock_diff = Mock()
        mock_diff.a_path = "old_name.c"
        mock_diff.b_path = "new_name.c"
        mock_diff.diff.decode.return_value = """diff --git a/old_name.c b/new_name.c
similarity index 100%
rename from old_name.c
rename to new_name.c
"""

        mock_commit.diff.return_value = [mock_diff]

        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.return_value = mock_commit

            result = get_commit_diff("/fake/path", "rename")

            # Should use b_path (new name) for renamed files
            assert "new_name.c" in result
            assert result["new_name.c"] == []

    def test_deleted_file(self):
        """Test handling of deleted files."""
        mock_commit = Mock()
        mock_parent = Mock()
        mock_commit.parents = [mock_parent]

        mock_diff = Mock()
        mock_diff.a_path = "deleted.c"
        mock_diff.b_path = None  # Deleted file
        mock_diff.diff.decode.return_value = """diff --git a/deleted.c b/deleted.c
deleted file mode 100644
index 1234567..0000000
--- a/deleted.c
+++ /dev/null
@@ -1,3 +0,0 @@
 void foo() {
     return;
 }
"""

        mock_commit.diff.return_value = [mock_diff]

        with patch("src.core.git_diff.Repo") as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.commit.return_value = mock_commit

            result = get_commit_diff("/fake/path", "delete")

            # For pure deletions, we don't capture the deleted line ranges
            # as they represent removed content, not changed content
            assert "deleted.c" in result
            assert result["deleted.c"] == []
