# src/core/parser.py
from typing import Dict, List, TypedDict

import tree_sitter_c
from tree_sitter import Language, Parser, Query, QueryCursor

# Create the Language object correctly
C_LANGUAGE = Language(tree_sitter_c.language())


def _normalize_name(name: str) -> str:
    """Normalize a function-like identifier to a canonical name.

    Strips surrounding whitespace and any trailing ``(`` so that both
    ``foo`` and ``foo(`` become ``foo`` in the call graph.

    Args:
        name: Raw function identifier string, possibly with trailing parentheses.

    Returns:
        Normalized function name with whitespace and trailing parentheses removed.
    """
    stripped = name.strip()
    # Remove a single trailing "(" if present (covers "foo(" or "foo (" styles)
    if stripped.endswith("("):
        stripped = stripped[:-1].rstrip()
    return stripped


def get_functions(file_path: str) -> List[str]:
    """Return all function names defined in a C source file.

    Args:
        file_path: Path to the C source file to parse.

    Returns:
        List of normalized function names found in the file.
    """
    parser = Parser()
    parser.language = C_LANGUAGE

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    tree = parser.parse(code.encode("utf-8"))

    query = Query(
        C_LANGUAGE,
        """
        (function_definition
            declarator: (function_declarator
                declarator: (identifier) @func_name))
        """,
    )

    cursor = QueryCursor(query)
    matches = cursor.matches(tree.root_node)

    function_names: List[str] = []
    for _, captures_dict in matches:
        if "func_name" in captures_dict:
            for node in captures_dict["func_name"]:
                raw_name = code[node.start_byte : node.end_byte]
                function_names.append(_normalize_name(raw_name))

    return function_names


def get_function_calls(file_path: str) -> Dict[str, List[str]]:
    """Return mapping of function -> list of function names it calls.

    Args:
        file_path: Path to the C source file to parse.

    Returns:
        Dictionary mapping function names to lists of functions they call.
    """
    parser = Parser()
    parser.language = C_LANGUAGE

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    tree = parser.parse(code.encode("utf-8"))

    func_query = Query(
        C_LANGUAGE,
        """
        (function_definition
            declarator: (function_declarator
                declarator: (identifier) @func_name)
            body: (compound_statement) @body)
        """,
    )

    func_cursor = QueryCursor(func_query)
    func_matches = func_cursor.matches(tree.root_node)

    call_map: Dict[str, List[str]] = {}
    for _, captures_dict in func_matches:
        if "func_name" in captures_dict and "body" in captures_dict:
            func_node = captures_dict["func_name"][0]
            body_node = captures_dict["body"][0]
            func_name = _normalize_name(code[func_node.start_byte : func_node.end_byte])

            call_query = Query(
                C_LANGUAGE,
                """
                (call_expression
                    function: (identifier) @called_name)
                """,
            )

            call_cursor = QueryCursor(call_query)
            call_matches = call_cursor.matches(body_node)

            called_funcs: List[str] = []
            for _, call_captures_dict in call_matches:
                if "called_name" in call_captures_dict:
                    for called_node in call_captures_dict["called_name"]:
                        called_raw = code[called_node.start_byte : called_node.end_byte]
                        called_funcs.append(_normalize_name(called_raw))

            call_map[func_name] = called_funcs

    return call_map


class FunctionNode(TypedDict):
    """Description of a function's location in a C file."""

    name: str
    start: int
    end: int


def get_function_nodes(file_path: str) -> List[FunctionNode]:
    """Return function names with start/end line numbers for a C file.

    Args:
        file_path: Path to the C source file to parse.

    Returns:
        List of FunctionNode dictionaries, each containing the function name,
        start line number, and end line number.
    """
    parser = Parser()
    parser.language = C_LANGUAGE

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    tree = parser.parse(code.encode("utf-8"))

    query = Query(
        C_LANGUAGE,
        """
        (function_definition
            declarator: (function_declarator
                declarator: (identifier) @func_name)) @func_def
        """,
    )
    cursor = QueryCursor(query)
    matches = cursor.matches(tree.root_node)

    functions: List[FunctionNode] = []
    for _, captures_dict in matches:
        if "func_name" in captures_dict and "func_def" in captures_dict:
            func_name_nodes = captures_dict["func_name"]
            func_def_nodes = captures_dict["func_def"]

            # Match function names to their definitions
            for func_name_node in func_name_nodes:
                func_name = _normalize_name(
                    code[func_name_node.start_byte : func_name_node.end_byte]
                )

                # Find the corresponding function definition node
                for func_def_node in func_def_nodes:
                    # Check if this function definition contains our function name
                    if (
                        func_def_node.start_byte <= func_name_node.start_byte
                        and func_name_node.end_byte <= func_def_node.end_byte
                    ):
                        start_line = (
                            func_def_node.start_point[0] + 1
                        )  # Tree-sitter lines start at 0
                        end_line = func_def_node.end_point[0] + 1
                        functions.append(
                            {"name": func_name, "start": start_line, "end": end_line}
                        )
                        break
    return functions
