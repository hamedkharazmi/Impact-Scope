# src/core/git_diff.py
from typing import Dict, List, Tuple

from git import BadName, Repo


def get_commit_diff(
    repo_path: str, commit_hash: str
) -> Dict[str, List[Tuple[int, int]]]:
    """Return changed line ranges for C/H files in a commit.

    Args:
        repo_path: Path to the Git repository.
        commit_hash: Commit hash or ref to analyze.

    Returns:
        Dictionary mapping file paths to lists of (start_line, end_line) tuples
        representing changed line ranges.

    Raises:
        ValueError: If the commit hash does not exist in the repository.
    """
    repo = Repo(repo_path)
    try:
        commit = repo.commit(commit_hash)
    except (BadName, ValueError) as exc:
        msg = f"Commit '{commit_hash}' does not exist in repository '{repo_path}'"
        raise ValueError(msg) from exc
    diff_data: Dict[str, List[Tuple[int, int]]] = {}

    for diff in commit.diff(
        commit.parents[0] if commit.parents else None, create_patch=True
    ):
        # Some diffs (e.g., renames, deletions) may not have an a_path;
        # guard against None before checking the extension.
        path = diff.a_path or diff.b_path
        if path is None:
            continue

        if path.endswith(".c") or path.endswith(".h"):
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

            diff_data[path] = hunks

    return diff_data
