# src/core/call_mapper.py
from pathlib import Path
from .parser import get_function_calls

def map_calls_from_impacted(file_path, impacted_funcs, repo_path=None):
    """
    Given a file and impacted functions, find all function calls inside them.
    """
    if repo_path:
        full_path = Path(repo_path) / file_path
    else:
        full_path = Path(file_path)

    all_calls = get_function_calls(full_path)  # returns {func: [called funcs]}
    result = {func: all_calls.get(func, []) for func in impacted_funcs}

    return result
