# src/core/visualization.py
import webbrowser
from pathlib import Path
from typing import Iterable, Mapping, Set

from pyvis.network import Network
from rich.console import Console

from .call_graph import build_call_graph_from_repo
from .constants import COLORS, UNIMPORTANT_FUNCS
from .path_utils import get_file_url, sanitize_filename

console = Console()


def visualize_call_graph_pyvis(
    call_map: Mapping[str, Iterable[str]],
    changed_funcs: Set[str] | None = None,
    upstream_funcs: Set[str] | None = None,
    downstream_funcs: Set[str] | None = None,
    title: str = "Call Graph",
    depth: int = 1,
    repo_path: str | None = None,
    commit_hash: str | None = None,
    source_file: str | None = None,
) -> Path:
    """Render an interactive call graph highlighting changed/upstream/downstream calls.

    The HTML output is written under ``artifacts/{project_name}/{commit_hash}/call_graphs/``
    with a meaningful filename. JS/CSS resources are loaded from CDNs, so no local
    ``lib/`` directory is generated. The HTML file is automatically opened in the browser.

    Args:
        call_map: Mapping of function names to their callees.
        changed_funcs: Set of function names that were directly changed.
        upstream_funcs: Set of functions that call into the changed functions.
        downstream_funcs: Set of functions called by the changed functions.
        title: Display title for the graph.
        depth: Traversal depth (currently unused but kept for API consistency).
        repo_path: Path to the repository being analyzed (used to extract project name).
        commit_hash: Commit hash being analyzed (used in filename and path).
        source_file: Source file path (used in filename for disambiguation).

    Returns:
        Path to the generated HTML file.
    """
    if changed_funcs is None:
        changed_funcs = set()
    if upstream_funcs is None:
        upstream_funcs = set()
    if downstream_funcs is None:
        downstream_funcs = set()

    graph = build_call_graph_from_repo(".")
    for caller, callees in call_map.items():
        for callee in callees:
            graph.add_edge(caller, callee)

    for up_func in upstream_funcs:
        for changed_func in changed_funcs:
            if not graph.has_edge(up_func, changed_func):
                graph.add_edge(up_func, changed_func)

    def bfs_nodes(start_nodes: Set[str], direction: str = "down") -> Set[str]:
        visited: Set[str] = set()
        queue: list[tuple[str, int]] = [(node, 0) for node in start_nodes]
        result: Set[str] = set()

        while queue:
            node, d = queue.pop(0)
            if node in visited or d > depth:
                continue
            visited.add(node)
            result.add(node)
            neighbors = (
                graph.successors(node)
                if direction == "down"
                else graph.predecessors(node)
            )
            for n in neighbors:
                queue.append((n, d + 1))
        return result

    nodes_to_include = set(changed_funcs)
    nodes_to_include |= bfs_nodes(changed_funcs, direction="down")
    nodes_to_include |= bfs_nodes(changed_funcs, direction="up")

    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")
    net.force_atlas_2based()

    for node in nodes_to_include:
        if node in changed_funcs:
            color = COLORS["changed"]
            title_text = f"{node} (Changed)"
            size = 35
        elif node in upstream_funcs:
            color = COLORS["upstream"]
            title_text = f"{node} (Upstream)"
            size = 25
        elif node in downstream_funcs:
            color = COLORS["downstream"]
            title_text = f"{node} (Downstream)"
            size = 25
        elif node in UNIMPORTANT_FUNCS:
            color = COLORS["unimportant"]
            title_text = f"{node} (Unimportant)"
            size = 20
        else:
            color = COLORS["other"]
            title_text = f"{node}"
            size = 20

        net.add_node(node, label=node, color=color, title=title_text, size=size)

    for source, target in graph.edges():
        if source in nodes_to_include and target in nodes_to_include:
            net.add_edge(source, target, color="lightgray", arrows="to")

    # Organize artifacts by project and commit for better structure
    # Extract project name from repo_path (last folder name)
    if repo_path:
        project_name = Path(repo_path).name
    else:
        project_name = "unknown"

    # Sanitize commit hash for filesystem (use first 8 chars for readability)
    if commit_hash:
        commit_short = commit_hash[:8] if len(commit_hash) >= 8 else commit_hash
        commit_short = sanitize_filename(commit_short)
    else:
        commit_short = "unknown"

    # Build output directory: artifacts/{project}/{commit}/call_graphs/
    artifacts_base = Path("artifacts") / project_name / commit_short / "call_graphs"
    artifacts_base.mkdir(parents=True, exist_ok=True)

    # Create meaningful filename: {project}_{commit}_{file}.html
    if source_file:
        # Extract just the filename (not full path) and sanitize
        file_part = sanitize_filename(Path(source_file).stem)
        filename = f"{sanitize_filename(project_name)}_{commit_short}_{file_part}.html"
    else:
        # Fallback to sanitized title
        safe_title = sanitize_filename(title)
        filename = f"{sanitize_filename(project_name)}_{commit_short}_{safe_title}.html"

    out_path = artifacts_base / filename

    # Use CDN resources to avoid creating a local lib/ directory.
    net.write_html(str(out_path), local=False)

    # Automatically open the HTML file in the default browser
    try:
        # Use pathlib's as_uri() for cross-platform file:// URLs
        file_url = get_file_url(out_path)
        webbrowser.open(file_url)
        console.print(
            f"[bold green]Interactive call graph saved and opened: {out_path}[/bold green]"
        )
    except Exception as e:
        console.print(
            f"[bold green]Interactive call graph saved: {out_path}[/bold green]"
        )
        console.print(f"[dim]Could not open browser automatically: {e}[/dim]")

    return out_path
