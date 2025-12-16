# src/core/call_mapper.py
from pathlib import Path
from typing import Dict, Iterable, List, Union

from .parser import get_function_calls


def map_calls_for_impacted_functions(
    file_path: Union[str, Path],
    impacted_funcs: Iterable[str],
    repo_path: Union[str, Path, None] = None,
) -> Dict[str, List[str]]:
    """Return calls made by the impacted functions in a given file.

    Args:
        file_path: Path to the C file (str or Path). If `repo_path` is provided,
                   `file_path` is considered relative to `repo_path`.
        impacted_funcs: Iterable of function names to map.
        repo_path: Optional repository root to resolve `file_path`.

    Returns:
        Dictionary mapping function name to list of called function names.
    """
    if repo_path:
        full_path = Path(repo_path) / file_path
    else:
        full_path = Path(file_path)

    all_calls = get_function_calls(str(full_path))  # returns {func: [called funcs]}
    result = {func: all_calls.get(func, []) for func in impacted_funcs}

    return result
