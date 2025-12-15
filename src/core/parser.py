from tree_sitter import Parser, Language
import tree_sitter_c
import os

# Build language wrapper ONCE
C_LANGUAGE = Language(tree_sitter_c.language())

def get_functions(file_path):
    parser = Parser()
    parser.language = C_LANGUAGE

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    tree = parser.parse(code.encode("utf-8"))
    root = tree.root_node

    functions = []

    def walk(node):
        if node.type == "function_definition":
            name_node = node.child_by_field_name("declarator")
            if name_node:
                name = code[name_node.start_byte:name_node.end_byte]
                name = name.split("(")[0].strip()
                functions.append(
                    (name, node.start_point[0] + 1, node.end_point[0] + 1)
                )
        for child in node.children:
            walk(child)

    walk(root)
    return functions
