# src/core/cli.py
from typing import Set

import typer
from rich.console import Console
from rich.tree import Tree

from .call_graph import build_call_graph_from_repo
from .call_mapper import map_calls_for_impacted_functions
from .constants import UNIMPORTANT_FUNCS
from .git_diff import get_commit_diff
from .impact_mapper import (
    collect_downstream_calls,
    collect_upstream_calls,
    map_changes_to_functions,
)
from .visualization import visualize_call_graph_pyvis

console = Console()
app = typer.Typer()


def fmt_func(func_name: str) -> str:
    """Return a Rich-friendly representation for a function name."""
    if func_name in UNIMPORTANT_FUNCS:
        return f"[dim]{func_name}[/dim]"
    return f"[bold]{func_name}[/bold]"


@app.command()
def analyze(
    repo_path: str = typer.Option(..., "--repo-path"),
    commit: str = typer.Option(..., "--commit"),
    depth: int = typer.Option(1, "--depth", min=0),
    visualize: bool = typer.Option(False, "--visualize"),
) -> None:
    """Analyze a commit and display impacted functions and their relationships."""
    console.print(
        f"[bold yellow]Analyzing commit {commit} in repo {repo_path}[/bold yellow]"
    )
    try:
        diff = get_commit_diff(repo_path, commit)
    except ValueError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        return
    if not diff:
        console.print(
            "[dim]No C or header file changes detected for this commit.[/dim]"
        )
        return

    graph = build_call_graph_from_repo(repo_path)

    for file, hunks in diff.items():
        impacted_funcs = map_changes_to_functions(repo_path, file, hunks)
        if not impacted_funcs:
            console.print(
                f"[dim]{file}: no functions impacted by changed lines {hunks}[/dim]"
            )
            continue

        call_map = map_calls_for_impacted_functions(file, impacted_funcs, repo_path)

        downstream: Set[str] = collect_downstream_calls(graph, impacted_funcs, depth)
        upstream: Set[str] = collect_upstream_calls(graph, impacted_funcs, depth)

        console.print(f"\n[bold cyan]{file}[/bold cyan]  Changed lines: {hunks}")

        for func in impacted_funcs:
            tree = Tree(fmt_func(func), guide_style="bold bright_blue")

            if upstream:
                up_branch = tree.add(
                    "Upstream (calls this function)", guide_style="green"
                )
                for up_func in sorted(upstream):
                    if up_func != func:
                        up_branch.add(fmt_func(up_func))

            if downstream:
                down_branch = tree.add(
                    "Downstream (called by this function)", guide_style="magenta"
                )
                for down_func in sorted(downstream):
                    if down_func != func:
                        down_branch.add(fmt_func(down_func))

            console.print(tree)

        if visualize:
            visualize_call_graph_pyvis(
                call_map,
                changed_funcs=set(impacted_funcs),
                upstream_funcs=upstream,
                downstream_funcs=downstream,
                title=f"Call Graph for {file}",
            )
