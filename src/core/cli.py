# src/core/cli.py
import typer
from .git_diff import get_commit_diff
from .impact_mapper import map_changes_to_functions

app = typer.Typer()

@app.command()
def analyze(
    repo_path: str = typer.Option(..., "--repo-path"),
    commit: str = typer.Option(..., "--commit"),
):
    print(f"Analyzing commit {commit} in repo {repo_path}")
    diff = get_commit_diff(repo_path, commit)

    for file, hunks in diff.items():
        impacted_funcs = map_changes_to_functions(repo_path, file, hunks)
        print(f"\nFile: {file}")
        print(f" Changed lines: {hunks}")
        print(f" Directly impacted functions: {impacted_funcs}")

