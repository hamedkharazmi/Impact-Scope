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
        # For renamed files, use the new name (b_path). Otherwise use a_path or b_path.
        if diff.a_path and diff.b_path and diff.a_path != diff.b_path:
            # This is a rename - use the new name
            path_candidate = diff.b_path
        else:
            # Normal case: use whichever path is available
            path_candidate = diff.a_path or diff.b_path  # type: ignore[assignment]

        if path_candidate is None:
            continue

        # Now we know path_candidate is not None, so it must be a string
        path_str = path_candidate

        if path_str.endswith(".c") or path_str.endswith(".h"):
            hunks: List[Tuple[int, int]] = []
            # Handle the case where diff.diff might be None or already a string
            diff_content = diff.diff
            if diff_content is None:
                continue

            # Try to decode if it's bytes, otherwise convert to string
            try:
                if hasattr(diff_content, "decode"):
                    decoded_content = diff_content.decode(errors="ignore")
                else:
                    decoded_content = str(diff_content)
            except (AttributeError, UnicodeDecodeError):
                decoded_content = str(diff_content)

            patch_lines = decoded_content.replace("\r\n", "\n").split("\n")

            for line in patch_lines:
                if line.startswith("@@"):
                    parts = line.split()
                    # Format: @@ -old_start,old_count +new_start,new_count @@
                    # We want to capture changed lines, preferring additions over deletions
                    added_part = None
                    deleted_part = None

                    for part in parts[1:]:  # Skip @@
                        if part.startswith("+"):
                            added_part = part
                        elif part.startswith("-"):
                            deleted_part = part

                    # For additions: use the + part
                    # For pure deletions (no additions): use the - part
                    if added_part and not added_part.endswith("/dev/null"):
                        target_part = added_part
                    elif deleted_part and not deleted_part.endswith("/dev/null"):
                        target_part = deleted_part
                    else:
                        continue

                    start_line = int(target_part.split(",")[0][1:])
                    line_count = (
                        int(target_part.split(",")[1]) if "," in target_part else 1
                    )
                    if line_count > 0:
                        end_line = start_line + line_count - 1
                        hunks.append((start_line, end_line))

            diff_data[path_str] = hunks

    return diff_data
