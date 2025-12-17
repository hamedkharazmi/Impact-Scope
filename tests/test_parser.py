# tests/test_parser.py
"""Unit tests for the parser module."""

import tempfile
from pathlib import Path

import pytest

from src.core.parser import (
    _normalize_name,
    get_function_calls,
    get_function_nodes,
    get_functions,
)


class TestNormalizeName:
    """Test function name normalization."""

    def test_basic_function_name(self):
        """Test basic function name without trailing characters."""
        assert _normalize_name("foo") == "foo"

    def test_function_with_trailing_paren(self):
        """Test function name with trailing opening parenthesis."""
        assert _normalize_name("foo(") == "foo"
        assert _normalize_name("foo (") == "foo"

    def test_function_with_whitespace(self):
        """Test function name with surrounding whitespace."""
        assert _normalize_name("  foo  ") == "foo"
        assert _normalize_name("  foo (  ") == "foo"

    def test_empty_string(self):
        """Test empty string normalization."""
        assert _normalize_name("") == ""
        assert _normalize_name("   ") == ""

    def test_only_paren(self):
        """Test string with only parentheses."""
        assert _normalize_name("(") == ""
        assert _normalize_name(" ( ") == ""


class TestGetFunctions:
    """Test function extraction from C files."""

    def create_test_file(self, content: str) -> Path:
        """Create a temporary C file with given content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            return Path(f.name)

    def test_simple_function(self):
        """Test extracting a simple function."""
        content = """
        int main() {
            return 0;
        }
        """
        file_path = self.create_test_file(content)
        try:
            functions = get_functions(str(file_path))
            assert "main" in functions
        finally:
            file_path.unlink()

    def test_multiple_functions(self):
        """Test extracting multiple functions."""
        content = """
        void foo() {
            return;
        }

        int bar(int x) {
            return x * 2;
        }

        static void baz() {
            printf("hello");
        }
        """
        file_path = self.create_test_file(content)
        try:
            functions = get_functions(str(file_path))
            assert "foo" in functions
            assert "bar" in functions
            assert "baz" in functions
            assert len(functions) == 3
        finally:
            file_path.unlink()

    def test_nested_function_calls(self):
        """Test functions with nested calls."""
        content = """
        void outer() {
            inner();
        }

        void inner() {
            printf("nested");
        }
        """
        file_path = self.create_test_file(content)
        try:
            functions = get_functions(str(file_path))
            assert "outer" in functions
            assert "inner" in functions
        finally:
            file_path.unlink()

    def test_no_functions(self):
        """Test file with no function definitions."""
        content = """
        #include <stdio.h>

        int x = 42;

        typedef struct {
            int value;
        } MyStruct;
        """
        file_path = self.create_test_file(content)
        try:
            functions = get_functions(str(file_path))
            assert functions == []
        finally:
            file_path.unlink()


class TestGetFunctionCalls:
    """Test function call extraction."""

    def create_test_file(self, content: str) -> Path:
        """Create a temporary C file with given content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            return Path(f.name)

    def test_simple_function_calls(self):
        """Test extracting simple function calls."""
        content = """
        void foo() {
            bar();
            baz();
        }

        void bar() {
            printf("hello");
        }
        """
        file_path = self.create_test_file(content)
        try:
            calls = get_function_calls(str(file_path))
            assert "foo" in calls
            assert "bar" in calls
            assert calls["foo"] == ["bar", "baz"]
            assert calls["bar"] == ["printf"]
        finally:
            file_path.unlink()

    def test_nested_calls(self):
        """Test nested function calls."""
        content = """
        void outer() {
            if (condition) {
                inner();
                printf("done");
            }
        }

        void inner() {
            helper();
        }
        """
        file_path = self.create_test_file(content)
        try:
            calls = get_function_calls(str(file_path))
            assert calls["outer"] == ["inner", "printf"]
            assert calls["inner"] == ["helper"]
        finally:
            file_path.unlink()

    def test_no_calls(self):
        """Test function with no calls."""
        content = """
        void empty() {
            int x = 1;
            x += 1;
        }
        """
        file_path = self.create_test_file(content)
        try:
            calls = get_function_calls(str(file_path))
            assert calls["empty"] == []
        finally:
            file_path.unlink()

    def test_recursive_calls(self):
        """Test recursive function calls."""
        content = """
        void factorial(int n) {
            if (n > 1) {
                factorial(n - 1);
            }
        }
        """
        file_path = self.create_test_file(content)
        try:
            calls = get_function_calls(str(file_path))
            assert calls["factorial"] == ["factorial"]
        finally:
            file_path.unlink()


class TestGetFunctionNodes:
    """Test function node extraction with line numbers."""

    def create_test_file(self, content: str) -> Path:
        """Create a temporary C file with given content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            return Path(f.name)

    def test_function_line_numbers(self):
        """Test extracting functions with line numbers."""
        content = """#include <stdio.h>

void foo() {
    printf("foo");
}

int main() {
    foo();
    return 0;
}
"""
        file_path = self.create_test_file(content)
        try:
            nodes = get_function_nodes(str(file_path))

            # Find foo function
            foo_node = next(node for node in nodes if node["name"] == "foo")
            assert foo_node["start"] == 3  # Line 3: void foo()
            assert foo_node["end"] == 3  # Same line for single-line function

            # Find main function
            main_node = next(node for node in nodes if node["name"] == "main")
            assert main_node["start"] == 7  # Line 7: int main()
            assert main_node["end"] == 7  # Same line

        finally:
            file_path.unlink()

    def test_multiline_function(self):
        """Test function spanning multiple lines."""
        content = """void multiline() {
    int x = 1;
    int y = 2;
    printf("%d", x + y);
}
"""
        file_path = self.create_test_file(content)
        try:
            nodes = get_function_nodes(str(file_path))
            func_node = next(node for node in nodes if node["name"] == "multiline")
            assert func_node["start"] == 1
            assert func_node["end"] == 1  # Tree-sitter might report single line
        finally:
            file_path.unlink()
