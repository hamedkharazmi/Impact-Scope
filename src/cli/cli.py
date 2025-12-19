# src/cli/cli.py
from typing import Literal, Set

import typer
from rich.console import Console
from rich.tree import Tree

from ..core.call_graph import build_call_graph_from_repo
from ..core.call_mapper import map_calls_for_impacted_functions
from ..core.constants import UNIMPORTANT_FUNCS
from ..core.git_diff import get_commit_diff
from ..core.impact_mapper import (
    collect_downstream_calls,
    collect_upstream_calls,
    map_changes_to_functions,
)
from ..output.json_output import (
    format_analysis_results,
    generate_impact_json,
    print_json_output,
)
from ..visualization.visualization import visualize_call_graph_pyvis

console = Console()
app = typer.Typer()


def fmt_func(func_name: str) -> str:
    """Return a Rich-friendly representation for a function name.

    Args:
        func_name: The function name to format.

    Returns:
        A Rich-formatted string with bold or dim styling based on importance.
    """
    if func_name in UNIMPORTANT_FUNCS:
        return f"[dim]{func_name}[/dim]"
    return f"[bold]{func_name}[/bold]"


@app.command()
def analyze(
    repo_path: str = typer.Option(..., "--repo-path"),
    commit: str = typer.Option(..., "--commit"),
    depth: int = typer.Option(1, "--depth", min=0),
    visualize: bool = typer.Option(False, "--visualize"),
    output: Literal["text", "json"] = typer.Option("text", "--output"),
) -> None:
    """Analyze a commit and display impacted functions and their relationships.

    Use --output json for machine-readable JSON output suitable for CI/automation.
    """
    try:
        diff = get_commit_diff(repo_path, commit)
    except ValueError as exc:
        if output == "json":
            print_json_output({"error": str(exc)})
        else:
            console.print(f"[bold red]{exc}[/bold red]")
        return

    if not diff:
        if output == "json":
            print_json_output(format_analysis_results([], repo_path, commit, depth))
        else:
            console.print(
                "[dim]No C or header file changes detected for this commit.[/dim]"
            )
        return

    graph = build_call_graph_from_repo(repo_path)
    json_results = []

    for file, hunks in diff.items():
        impacted_funcs = map_changes_to_functions(repo_path, file, hunks)
        if not impacted_funcs:
            if output == "text":
                console.print(
                    f"[dim]{file}: no functions impacted by changed lines {hunks}[/dim]"
                )
            continue

        call_map = map_calls_for_impacted_functions(file, impacted_funcs, repo_path)

        # Compute combined upstream/downstream for JSON output and visualization
        downstream: Set[str] = collect_downstream_calls(graph, impacted_funcs, depth)
        upstream: Set[str] = collect_upstream_calls(graph, impacted_funcs, depth)

        # Generate JSON result for this file
        if output == "json":
            json_results.append(
                generate_impact_json(
                    file=file,
                    changed_functions=impacted_funcs,
                    downstream=downstream,
                    upstream=upstream,
                    depth=depth,
                    changed_lines=hunks,
                )
            )
        else:
            # Terminal-friendly text output - compute relationships per function
            console.print(f"\n[bold cyan]{file}[/bold cyan]  Changed lines: {hunks}")

            for func in impacted_funcs:
                tree = Tree(fmt_func(func), guide_style="bold bright_blue")

                # Compute upstream and downstream for this specific function
                func_upstream: Set[str] = collect_upstream_calls(graph, [func], depth)
                func_downstream: Set[str] = collect_downstream_calls(
                    graph, [func], depth
                )

                if func_upstream:
                    up_branch = tree.add(
                        "Upstream (calls this function)", guide_style="green"
                    )
                    for up_func in sorted(func_upstream):
                        if up_func != func:
                            up_branch.add(fmt_func(up_func))

                if func_downstream:
                    down_branch = tree.add(
                        "Downstream (called by this function)", guide_style="magenta"
                    )
                    for down_func in sorted(func_downstream):
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
                repo_path=repo_path,
                commit_hash=commit,
                source_file=file,
            )

    # Output JSON if requested
    if output == "json":
        print_json_output(
            format_analysis_results(json_results, repo_path, commit, depth)
        )
