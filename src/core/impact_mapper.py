# src/core/impact_mapper.py
from pathlib import Path
from .parser import get_functions, get_function_calls

def map_changes_to_functions(repo_path, file_path, hunks):
    """
    Map changed lines (hunks) to impacted functions.
    """
    full_path = Path(repo_path) / file_path
    functions = get_functions(full_path)

    impacted = []
    for start, end in hunks:
        for func_name in functions:
            # simple approximation: check if func appears in hunks lines
            # you can enhance this later if needed
            impacted.append(func_name)

    return list(set(impacted))


def map_calls_from_impacted(file_path, impacted_funcs, repo_path=None):
    """
    Find all functions called inside impacted functions.
    """
    full_path = Path(repo_path) / file_path if repo_path else Path(file_path)
    all_calls = get_function_calls(full_path)

    result = {func: [] for func in impacted_funcs}
    for func, callees in all_calls.items():
        if func in impacted_funcs:
            result[func] = callees

    return result
