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

            # Parse hunk by hunk to find actual changed lines
            i = 0
            changed_lines: set[Tuple[int, int]] = set()
            while i < len(patch_lines):
                if patch_lines[i].startswith("@@"):
                    # Parse hunk header to get the new file line offset
                    parts = patch_lines[i].split()
                    new_start_line = None
                    for part in parts[1:]:
                        if part.startswith("+"):
                            # Extract the starting line number in the new file
                            try:
                                new_start_line = int(part.split(",")[0][1:])
                                break
                            except (ValueError, IndexError):
                                continue

                    if new_start_line is None:
                        i += 1
                        continue

                    # Parse the hunk content to find actual changed lines
                    i += 1  # Move to first line after header
                    current_line = new_start_line

                    while i < len(patch_lines) and not patch_lines[i].startswith("@@"):
                        line = patch_lines[i]
                        if line.startswith("+") or line.startswith("-"):
                            # This is an added or deleted line - record it as a changed line
                            changed_lines.add((current_line, current_line))
                            if line.startswith("+"):
                                current_line += 1
                            # Note: deleted lines don't advance the line counter for the new file
                        elif not line.startswith("\\"):
                            # This is a context line
                            current_line += 1

                        i += 1
                else:
                    i += 1

            # Group consecutive changed lines into ranges
            if changed_lines:
                sorted_lines = sorted(changed_lines)
                grouped_ranges = []
                start_line = end_line = sorted_lines[0][
                    0
                ]  # Get the line number from (line, line) tuple

                for line_tuple in sorted_lines[1:]:
                    current_line = line_tuple[0]
                    if current_line == end_line + 1:
                        # Consecutive line, extend the range
                        end_line = current_line
                    else:
                        # Gap found, save current range and start new one
                        grouped_ranges.append((start_line, end_line))
                        start_line = end_line = current_line

                # Add the last range
                grouped_ranges.append((start_line, end_line))
                diff_data[path_str] = grouped_ranges
            else:
                diff_data[path_str] = []

    return diff_data
