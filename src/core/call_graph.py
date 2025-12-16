# src/core/call_graph.py
import networkx as nx
import matplotlib.pyplot as plt

def build_call_graph(call_map):
    graph = nx.DiGraph()
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
