# src/core/parser.py
from typing import Dict, List, TypedDict

import tree_sitter_c
from tree_sitter import Language, Parser, Query, QueryCursor

# Create the Language object correctly
C_LANGUAGE = Language(tree_sitter_c.language())


def get_functions(file_path: str) -> List[str]:
    """Return all function names defined in a C source file."""
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
                function_name = code[node.start_byte : node.end_byte]
                function_names.append(function_name)

    return function_names


def get_function_calls(file_path: str) -> Dict[str, List[str]]:
    """Return mapping of function -> list of function names it calls."""
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
            func_name = code[func_node.start_byte : func_node.end_byte]

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
                        called_func = code[
                            called_node.start_byte : called_node.end_byte
                        ]
                        called_funcs.append(called_func)

            call_map[func_name] = called_funcs

    return call_map


class FunctionNode(TypedDict):
    """Description of a function's location in a C file."""

    name: str
    start: int
    end: int


def get_function_nodes(file_path: str) -> List[FunctionNode]:
    """Return function names with start/end line numbers for a C file."""
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

    functions: List[FunctionNode] = []
    for _, captures_dict in matches:
        if "func_name" in captures_dict:
            for node in captures_dict["func_name"]:
                func_name = code[node.start_byte : node.end_byte]
                start_line = node.start_point[0] + 1  # Tree-sitter lines start at 0
                end_line = node.end_point[0] + 1
                functions.append(
                    {"name": func_name, "start": start_line, "end": end_line}
                )
    return functions
