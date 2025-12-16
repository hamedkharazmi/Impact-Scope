# src/core/call_graph.py
import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt
from .parser import get_function_calls

def build_call_graph(call_map):
    graph = nx.DiGraph()
    for caller, callees in call_map.items():
        for callee in callees:
            graph.add_edge(caller, callee)
    return graph

def build_project_call_graph(repo_path: str):
    graph = nx.DiGraph()
    repo_path = Path(repo_path)

    for c_file in repo_path.rglob("*.c"):
        call_map = get_function_calls(c_file)
        for caller, callees in call_map.items():
            for callee in callees:
                graph.add_edge(caller, callee)
    return graph

def visualize_call_graph(call_map, title="Call Graph"):
    graph = build_call_graph(call_map)
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, arrows=True)
    plt.title(title)
    plt.show()
