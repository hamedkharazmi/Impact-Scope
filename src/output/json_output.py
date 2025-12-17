# src/core/json_output.py
"""JSON output schema and serialization for ImpactScope analysis results."""

import json
from typing import Dict, List, Set

# JSON schema version for future compatibility
JSON_SCHEMA_VERSION = "1.0.0"


def generate_impact_json(
    file: str,
    changed_functions: List[str],
    downstream: Set[str],
    upstream: Set[str],
    depth: int,
    changed_lines: List[tuple[int, int]] | None = None,
) -> Dict[str, str | List[str] | int | List[Dict[str, int]]]:
    """Generate a JSON object representing impact analysis for a single file.

    Args:
        file: Source file path relative to repository root.
        changed_functions: List of function names directly affected by the commit.
        downstream: Set of function names potentially impacted downstream.
        upstream: Set of function names calling into the changed code.
        depth: Impact propagation depth used for analysis.
        changed_lines: Optional list of (start, end) line ranges that changed.

    Returns:
        A dictionary conforming to the ImpactScope JSON output schema.
    """
    result: Dict[str, str | List[str] | int | List[Dict[str, int]]] = {
        "file": file,
        "changed_functions": sorted(changed_functions),
        "downstream": sorted(list(downstream)),
        "upstream": sorted(list(upstream)),
        "depth": depth,
    }

    if changed_lines:
        result["changed_lines"] = [
            {"start": start, "end": end} for start, end in changed_lines
        ]

    return result


def format_analysis_results(
    results: List[Dict[str, str | List[str] | int | List[Dict[str, int]]]],
    repo_path: str,
    commit: str,
    depth: int,
) -> Dict[
    str, str | int | List[Dict[str, str | List[str] | int | List[Dict[str, int]]]]
]:
    """Format complete analysis results as a structured JSON document.

    Args:
        results: List of per-file impact analysis results.
        repo_path: Path to the analyzed repository.
        commit: Commit hash or ref that was analyzed.
        depth: Analysis depth used.

    Returns:
        A complete JSON document with metadata and results array.
    """
    return {
        "schema_version": JSON_SCHEMA_VERSION,
        "repo_path": repo_path,
        "commit": commit,
        "depth": depth,
        "files": results,
    }


def print_json_output(data: Dict) -> None:
    """Print JSON output to stdout in a compact, machine-readable format.

    Args:
        data: The JSON-serializable dictionary to output.
    """
    print(json.dumps(data, indent=2, ensure_ascii=False))
