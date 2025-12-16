# src/core/visualization.py
from pathlib import Path
from typing import Iterable, Mapping, Set

from pyvis.network import Network
from rich.console import Console

from .call_graph import build_call_graph_from_repo
from .constants import COLORS, UNIMPORTANT_FUNCS

console = Console()


def visualize_call_graph_pyvis(
    call_map: Mapping[str, Iterable[str]],
    changed_funcs: Set[str] | None = None,
    upstream_funcs: Set[str] | None = None,
    downstream_funcs: Set[str] | None = None,
    title: str = "Call Graph",
    depth: int = 1,
) -> None:
    """Render an interactive call graph highlighting changed/upstream/downstream calls.

    The HTML output is written under ``artifacts/call_graphs`` so that it can be
    safely ignored by version control. JS/CSS resources are loaded from CDNs,
    so no local ``lib/`` directory is generated.
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

    # Always write visualizations under artifacts/call_graphs with a safe filename
    artifacts_dir = Path("artifacts") / "call_graphs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    safe_name = (
        title.replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_")
    )
    filename = f"{safe_name}.html"
    out_path = artifacts_dir / filename

    # Use CDN resources to avoid creating a local lib/ directory.
    net.write_html(str(out_path), local=False)
    console.print(
        f"[bold green]Interactive call graph saved as {out_path}![/bold green]"
    )
