# tests/test_impact_mapper.py
"""Unit tests for the impact mapper module."""

import tempfile
from pathlib import Path

import networkx as nx
import pytest

from src.core.impact_mapper import (
    collect_downstream_calls,
    collect_upstream_calls,
    map_changes_to_functions,
)


class TestMapChangesToFunctions:
    """Test mapping changed line ranges to affected functions."""

    def create_test_file(self, content: str) -> Path:
        """Create a temporary C file with given content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            return Path(f.name)

    def test_single_function_change(self):
        """Test when a single function is modified."""
        content = """void foo() {
    printf("foo");
}

void bar() {
    printf("bar");
}
"""
        file_path = self.create_test_file(content)
        try:
            # Change affects foo function (lines 1-3)
            hunks = [(1, 3)]
            # Use the actual directory and filename
            repo_path = str(file_path.parent)
            file_name = file_path.name
            impacted = map_changes_to_functions(repo_path, file_name, hunks)
            assert impacted == ["foo"]
        finally:
            file_path.unlink()

    def test_multiple_function_changes(self):
        """Test when multiple functions are modified."""
        content = """void foo() {
    printf("foo");
}

void bar() {
    printf("bar");
}

void baz() {
    printf("baz");
}
"""
        file_path = self.create_test_file(content)
        try:
            # Changes affect both foo and bar
            hunks = [(1, 3), (5, 7)]
            repo_path = str(file_path.parent)
            file_name = file_path.name
            impacted = map_changes_to_functions(repo_path, file_name, hunks)
            assert set(impacted) == {"foo", "bar"}
        finally:
            file_path.unlink()

    def test_partial_overlap(self):
        """Test when change affects multiple functions."""
        content = """void foo() {
    printf("hello");
}

void bar() {
    printf("world");
}

void baz() {
    printf("test");
}
"""
        file_path = self.create_test_file(content)
        try:
            # Change affects both foo and bar functions
            hunks = [(1, 6)]
            repo_path = str(file_path.parent)
            file_name = file_path.name
            impacted = map_changes_to_functions(repo_path, file_name, hunks)
            assert set(impacted) == {"foo", "bar"}
        finally:
            file_path.unlink()

    def test_no_function_changes(self):
        """Test when changes don't affect any functions."""
        content = """#include <stdio.h>

void foo() {
    printf("foo");
}

/* This is a comment */
"""
        file_path = self.create_test_file(content)
        try:
            # Change only affects comment/include
            hunks = [(1, 2)]
            repo_path = str(file_path.parent)
            file_name = file_path.name
            impacted = map_changes_to_functions(repo_path, file_name, hunks)
            assert impacted == []
        finally:
            file_path.unlink()

    def test_empty_hunks(self):
        """Test with empty hunks list."""
        content = """void foo() {
    printf("foo");
}
"""
        file_path = self.create_test_file(content)
        try:
            repo_path = str(file_path.parent)
            file_name = file_path.name
            impacted = map_changes_to_functions(repo_path, file_name, [])
            assert impacted == []
        finally:
            file_path.unlink()


class TestCollectDownstreamCalls:
    """Test downstream call collection (functions called by changed functions)."""

    def create_test_graph(self) -> nx.DiGraph:
        """Create a test call graph."""
        graph = nx.DiGraph()
        # A -> B -> C -> D
        # A -> E
        # F -> G
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "D")
        graph.add_edge("A", "E")
        graph.add_edge("F", "G")
        return graph

    def test_depth_zero(self):
        """Test with depth 0 (no traversal)."""
        graph = self.create_test_graph()
        result = collect_downstream_calls(graph, ["A"], 0)
        assert result == set()

    def test_depth_one(self):
        """Test with depth 1."""
        graph = self.create_test_graph()
        result = collect_downstream_calls(graph, ["A"], 1)
        assert result == {"B", "E"}

    def test_depth_two(self):
        """Test with depth 2."""
        graph = self.create_test_graph()
        result = collect_downstream_calls(graph, ["A"], 2)
        assert result == {"B", "E", "C"}

    def test_depth_three(self):
        """Test with depth 3."""
        graph = self.create_test_graph()
        result = collect_downstream_calls(graph, ["A"], 3)
        assert result == {"B", "E", "C", "D"}

    def test_multiple_start_functions(self):
        """Test with multiple starting functions."""
        graph = self.create_test_graph()
        result = collect_downstream_calls(graph, ["A", "F"], 1)
        assert result == {"B", "E", "G"}

    def test_no_downstream_calls(self):
        """Test function with no downstream calls."""
        graph = self.create_test_graph()
        result = collect_downstream_calls(graph, ["D"], 1)
        assert result == set()

    def test_nonexistent_function(self):
        """Test with non-existent starting function."""
        graph = self.create_test_graph()
        result = collect_downstream_calls(graph, ["Z"], 1)
        assert result == set()


class TestCollectUpstreamCalls:
    """Test upstream call collection (functions that call changed functions)."""

    def create_test_graph(self) -> nx.DiGraph:
        """Create a test call graph."""
        graph = nx.DiGraph()
        # A -> B -> C -> D
        # E -> C
        # F -> G
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "D")
        graph.add_edge("E", "C")
        graph.add_edge("F", "G")
        return graph

    def test_depth_zero(self):
        """Test with depth 0 (no traversal)."""
        graph = self.create_test_graph()
        result = collect_upstream_calls(graph, ["D"], 0)
        assert result == set()

    def test_depth_one(self):
        """Test with depth 1."""
        graph = self.create_test_graph()
        result = collect_upstream_calls(graph, ["D"], 1)
        assert result == {"C"}

    def test_depth_two(self):
        """Test with depth 2."""
        graph = self.create_test_graph()
        result = collect_upstream_calls(graph, ["D"], 2)
        assert result == {"C", "B", "E"}

    def test_depth_three(self):
        """Test with depth 3."""
        graph = self.create_test_graph()
        result = collect_upstream_calls(graph, ["D"], 3)
        assert result == {"C", "B", "E", "A"}

    def test_multiple_start_functions(self):
        """Test with multiple starting functions."""
        graph = self.create_test_graph()
        result = collect_upstream_calls(graph, ["C", "G"], 1)
        assert result == {"B", "E", "F"}

    def test_no_upstream_calls(self):
        """Test function with no upstream calls."""
        graph = self.create_test_graph()
        result = collect_upstream_calls(graph, ["A"], 1)
        assert result == set()

    def test_nonexistent_function(self):
        """Test with non-existent starting function."""
        graph = self.create_test_graph()
        result = collect_upstream_calls(graph, ["Z"], 1)
        assert result == set()
