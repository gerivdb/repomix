"""
Poincaré Topology VERSE - Invariants Topologiques pour Graphes Cognitifs

Ce package implémente les invariants topologiques de Poincaré pour valider
et corriger automatiquement la structure des graphes issus de fusion TQL.

Modules principaux:
- topology_engine: Moteur d'analyse topologique avec invariants Poincaré
- demo_topology: Démonstration des capacités d'analyse
"""

__version__ = "1.0.0"
__author__ = "Kilo AI"

from .topology_engine import (
    TernaryGraph,
    TopologyMetrics,
    TopologyInvariant
)

__all__ = [
    "TernaryGraph",
    "TopologyMetrics",
    "TopologyInvariant"
]