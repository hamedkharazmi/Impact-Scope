# src/core/git_diff.py
from typing import Dict, List, Tuple

from git import Repo


def get_commit_diff(
    repo_path: str, commit_hash: str
) -> Dict[str, List[Tuple[int, int]]]:
    """Return changed line ranges for C/H files in a commit."""
    repo = Repo(repo_path)
    commit = repo.commit(commit_hash)
    diff_data: Dict[str, List[Tuple[int, int]]] = {}

    for diff in commit.diff(
        commit.parents[0] if commit.parents else None, create_patch=True
    ):
        if diff.a_path.endswith(".c") or diff.a_path.endswith(".h"):
            hunks: List[Tuple[int, int]] = []
            patch_lines = (
                diff.diff.decode(errors="ignore").replace("\r\n", "\n").split("\n")
            )

            for line in patch_lines:
                if line.startswith("@@"):
                    parts = line.split()
                    added = parts[2]
                    start_line = int(added.split(",")[0][1:])
                    line_count = int(added.split(",")[1]) if "," in added else 1
                    end_line = start_line + line_count - 1
                    hunks.append((start_line, end_line))

            diff_data[diff.a_path] = hunks

    return diff_data
