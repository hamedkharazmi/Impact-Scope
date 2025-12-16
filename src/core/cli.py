# src/core/cli.py
import typer
from .git_diff import get_commit_diff
from .impact_mapper import map_changes_to_functions, traverse_calls, traverse_upstream_calls
from .call_mapper import map_calls_from_impacted
from .call_graph import visualize_call_graph, build_project_call_graph

app = typer.Typer()

@app.command()
def analyze(
    repo_path: str = typer.Option(..., "--repo-path"),
    commit: str = typer.Option(..., "--commit"),
    depth: int = typer.Option(1, "--depth", min=0),
    visualize: bool = typer.Option(False, "--visualize")
):
    print(f"Analyzing commit {commit} in repo {repo_path}")
    diff = get_commit_diff(repo_path, commit)

    graph = build_project_call_graph(repo_path)

    for file, hunks in diff.items():
        impacted_funcs = map_changes_to_functions(repo_path, file, hunks)
        call_map = map_calls_from_impacted(file, impacted_funcs, repo_path)

        # Downstream impact
        all_impacted_downstream = traverse_calls(graph, impacted_funcs, depth)
        # Upstream impact
        all_impacted_upstream = traverse_upstream_calls(graph, impacted_funcs, depth)
        
        print(f"\nFile: {file}")
        print(f" Changed lines: {hunks}")
        print(f" Directly impacted functions: {impacted_funcs}")
        print(f" Functions called by impacted functions: {call_map}")
        print(f" Impacted downstream (depth={depth}): {sorted(all_impacted_downstream)}")
        print(f" Impacted upstream (for tests, depth={depth}): {sorted(all_impacted_upstream)}")
        
        if visualize:
            visualize_call_graph(call_map, title=f"Call Graph for {file}")
