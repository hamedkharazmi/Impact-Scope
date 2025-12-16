# src/core/call_graph.py
from pathlib import Path
from typing import Dict, Iterable

import networkx as nx

from .parser import get_function_calls


def build_graph_from_call_map(call_map: Dict[str, Iterable[str]]) -> nx.DiGraph:
    """Create a directed call graph from a mapping of caller -> callees.

    Args:
        call_map: Dictionary mapping caller function names to iterables of
                  callee function names.

    Returns:
        A NetworkX directed graph representing the call relationships.
    """
    graph = nx.DiGraph()

    for caller, callees in call_map.items():
        for callee in callees:
            graph.add_edge(caller, callee)

    return graph


def build_call_graph_from_repo(repo_path: str) -> nx.DiGraph:
    """Build a repository-wide call graph by parsing all C files.

    Args:
        repo_path: Path to the repository root.

    Returns:
        A NetworkX directed graph containing all function call relationships
        found in C source files within the repository.
    """
    graph = nx.DiGraph()
    repo_root = Path(repo_path)

    for c_file in repo_root.rglob("*.c"):
        call_map = get_function_calls(str(c_file))
        for caller, callees in call_map.items():
            for callee in callees:
                graph.add_edge(caller, callee)

    return graph
