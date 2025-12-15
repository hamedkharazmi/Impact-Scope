import typer
from .git_diff import get_commit_diff

app = typer.Typer()

@app.command()
def analyze(
    repo_path: str = typer.Option(..., "--repo-path"),
    commit: str = typer.Option(..., "--commit"),
):
    diff = get_commit_diff(repo_path, commit)
