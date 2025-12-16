# src/core/impact_mapper.py
from pathlib import Path
from .parser import get_functions, get_function_calls, get_function_nodes

def map_changes_to_functions(repo_path, file_path, hunks):
    """
    Map changed lines (hunks) to impacted functions accurately.
    """
    full_path = Path(repo_path) / file_path

    # Get functions along with their start/end line numbers
    # Returns list of dicts: [{'name': 'func_name', 'start': 5, 'end': 15}, ...]
    functions = get_function_nodes(full_path)

    impacted = set()
    for start_line, end_line in hunks:
        for func in functions:
            # Check if function overlaps with the hunk
            if not (end_line < func['start'] or start_line > func['end']):
                impacted.add(func['name'])

    return list(impacted)

def traverse_calls(graph, start_funcs, depth):
    impacted = set(start_funcs)
    frontier = set(start_funcs)

    for _ in range(depth):
        next_frontier = set()
        for func in frontier:
            if func in graph:
                next_frontier.update(graph.successors(func))
        frontier = next_frontier - impacted
        impacted.update(frontier)

    return impacted
