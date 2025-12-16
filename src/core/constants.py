# src/core/constants.py
"""Shared constants for call graph visualization and reporting."""

from typing import Dict, Set

# Functions considered unimportant for impact visualization (e.g., stdlib-like)
UNIMPORTANT_FUNCS: Set[str] = {"printf", "scanf", "malloc", "free", "fprintf", "perror"}

# Color palette used by visualizations
COLORS: Dict[str, str] = {
    "changed": "#e63946",  # red
    "upstream": "#2a9d8f",  # teal
    "downstream": "#457b9d",  # blue
    "unimportant": "#adb5bd",  # gray
    "other": "#f4a261",  # orange
}
