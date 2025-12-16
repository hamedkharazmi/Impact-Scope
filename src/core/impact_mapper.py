# src/core/impact_mapper.py
from pathlib import Path
from typing import Iterable, List, Sequence, Set, Tuple

import networkx as nx

from .parser import get_function_nodes


def map_changes_to_functions(
    repo_path: str, file_path: str, hunks: Sequence[Tuple[int, int]]
) -> List[str]:
    """Map changed line ranges to function names in the target file."""
    full_path = Path(repo_path) / file_path

    functions = get_function_nodes(str(full_path))

    impacted: Set[str] = set()
    for start_line, end_line in hunks:
        for func in functions:
            if not (end_line < func["start"] or start_line > func["end"]):
                impacted.add(func["name"])

    return list(impacted)


def collect_downstream_calls(
    graph: nx.DiGraph, start_funcs: Iterable[str], depth: int
) -> Set[str]:
    """Traverse successors up to `depth` and return collected nodes, excluding seeds."""
    impacted: Set[str] = set()
    frontier: Set[str] = set(start_funcs)

    for _ in range(depth):
        next_frontier: Set[str] = set()
        for func in frontier:
            if func in graph:
                next_frontier.update(graph.successors(func))
        frontier = next_frontier - impacted
        impacted.update(frontier)

    return impacted - set(start_funcs)


def collect_upstream_calls(
    graph: nx.DiGraph, start_funcs: Iterable[str], depth: int
) -> Set[str]:
    """Traverse predecessors up to `depth` and return collected nodes, excluding seeds."""
    impacted: Set[str] = set()
    frontier: Set[str] = set(start_funcs)

    for _ in range(depth):
        next_frontier: Set[str] = set()
        for func in frontier:
            if func in graph:
                next_frontier.update(graph.predecessors(func))
        frontier = next_frontier - impacted
        impacted.update(frontier)

    return impacted - set(start_funcs)
