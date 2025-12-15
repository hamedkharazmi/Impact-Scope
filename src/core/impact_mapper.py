# src/core/impact_mapper.py
from pathlib import Path
from .parser import get_functions

def map_changes_to_functions(repo_path, file_path, hunks):
    full_path = Path(repo_path) / file_path
    functions = get_functions(full_path)

    impacted = []
    for start, end in hunks:
        for name, func_start, func_end in functions:
            if not (end < func_start or start > func_end):
                impacted.append(name)

    return list(set(impacted))
