# src/core/call_graph.py
import networkx as nx

def build_call_graph(call_map):
    """
    Build a directed graph of function calls.
    """
    graph = nx.DiGraph()
    for caller, callees in call_map.items():
        for callee in callees:
            graph.add_edge(caller, callee)
    return graph
