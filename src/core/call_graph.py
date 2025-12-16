# src/core/call_graph.py
from pathlib import Path
from typing import Dict, Iterable

import networkx as nx

from .parser import get_function_calls


def build_graph_from_call_map(call_map: Dict[str, Iterable[str]]) -> nx.DiGraph:
    """Create a directed call graph from a mapping of caller -> callees."""
    graph = nx.DiGraph()

    for caller, callees in call_map.items():
        for callee in callees:
            graph.add_edge(caller, callee)

    return graph


def build_call_graph_from_repo(repo_path: str) -> nx.DiGraph:
    """Build a repository-wide call graph by parsing all C files."""
    graph = nx.DiGraph()
    repo_root = Path(repo_path)

    for c_file in repo_root.rglob("*.c"):
        call_map = get_function_calls(str(c_file))
        for caller, callees in call_map.items():
            for callee in callees:
                graph.add_edge(caller, callee)

    return graph
