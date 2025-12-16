# src/core/parser.py
from tree_sitter import Parser, Language, Query, QueryCursor
import tree_sitter_c

# Create the Language object correctly
C_LANGUAGE = Language(tree_sitter_c.language())

def get_functions(file_path):
    parser = Parser()
    parser.language = C_LANGUAGE
    
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    tree = parser.parse(code.encode("utf-8"))

    # Create query
    query = Query(
        C_LANGUAGE,
        """
        (function_definition
            declarator: (function_declarator
                declarator: (identifier) @func_name))
        """
    )
    
    # Create QueryCursor with the query
    cursor = QueryCursor(query)
    
    # Execute the query on the tree
    matches = cursor.matches(tree.root_node)
    
    function_names = []
    for match in matches:
        # match is a tuple: (pattern_index, captures_dict)
        pattern_index, captures_dict = match
        # Get the 'func_name' capture from the dictionary
        if 'func_name' in captures_dict:
            for node in captures_dict['func_name']:
                function_name = code[node.start_byte:node.end_byte]
                function_names.append(function_name)
    
    return function_names


def get_function_calls(file_path):
    parser = Parser()
    parser.language = C_LANGUAGE
    
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    tree = parser.parse(code.encode("utf-8"))

    # Query for function definitions and their bodies
    func_query = Query(
        C_LANGUAGE,
        """
        (function_definition
            declarator: (function_declarator
                declarator: (identifier) @func_name)
            body: (compound_statement) @body)
        """
    )
    
    # Create QueryCursor with the function query
    func_cursor = QueryCursor(func_query)
    
    # Execute function query
    func_matches = func_cursor.matches(tree.root_node)
    
    call_map = {}
    for pattern_index, captures_dict in func_matches:
        if 'func_name' in captures_dict and 'body' in captures_dict:
            func_node = captures_dict['func_name'][0]
            body_node = captures_dict['body'][0]
            func_name = code[func_node.start_byte:func_node.end_byte]

            # Query for call expressions within the function body
            call_query = Query(
                C_LANGUAGE,
                """
                (call_expression
                    function: (identifier) @called_name)
                """
            )
            
            # Create QueryCursor with the call query
            call_cursor = QueryCursor(call_query)
            
            # Execute call query on the function body
            call_matches = call_cursor.matches(body_node)
            
            called_funcs = []
            for call_pattern_index, call_captures_dict in call_matches:
                if 'called_name' in call_captures_dict:
                    for called_node in call_captures_dict['called_name']:
                        called_func = code[called_node.start_byte:called_node.end_byte]
                        called_funcs.append(called_func)
            
            call_map[func_name] = called_funcs

    return call_map


def get_function_nodes(file_path):
    """
    Return functions with start/end line numbers
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
        """
    )
    cursor = QueryCursor(query)
    matches = cursor.matches(tree.root_node)

    functions = []
    for match in matches:
        _, captures_dict = match
        if 'func_name' in captures_dict:
            for node in captures_dict['func_name']:
                func_name = code[node.start_byte:node.end_byte]
                start_line = node.start_point[0] + 1  # Tree-sitter lines start at 0
                end_line = node.end_point[0] + 1
                functions.append({'name': func_name, 'start': start_line, 'end': end_line})
    return functions
