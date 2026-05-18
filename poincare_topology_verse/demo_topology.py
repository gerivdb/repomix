"""
Démonstration Poincaré Topology VERSE
Test des invariants topologiques sur des graphes d'exemple
"""

import sys
from pathlib import Path

# Ajouter le répertoire au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from topology_engine import TernaryGraph

def create_example_graphs():
    """Crée des graphes d'exemple pour tester les invariants"""

    graphs = {}

    # Graphe 1: Graphe planaire simple (χ = 1, β₀=1, β₁=0, g=0)
    g1 = TernaryGraph()
    g1.add_vertex("A")  # 0
    g1.add_vertex("B")  # 1
    g1.add_vertex("C")  # 2
    g1.add_vertex("D")  # 3

    g1.add_edge(0, 1)
    g1.add_edge(1, 2)
    g1.add_edge(2, 3)
    g1.add_edge(3, 0)
    # Pas de faces pour rester planaire

    graphs["planar_simple"] = g1

    # Graphe 2: Avec un triangle (χ = 0, β₁=1 - cycle!)
    g2 = TernaryGraph()
    g2.add_vertex("X")  # 0
    g2.add_vertex("Y")  # 1
    g2.add_vertex("Z")  # 2

    g2.add_edge(0, 1)
    g2.add_edge(1, 2)
    g2.add_edge(2, 0)  # Cycle!
    g2.add_face(0, 1, 2)  # Face triangulaire

    graphs["with_cycle"] = g2

    # Graphe 3: Deux composantes (β₀=2)
    g3 = TernaryGraph()
    g3.add_vertex("P")  # 0
    g3.add_vertex("Q")  # 1
    g3.add_vertex("R")  # 2
    g3.add_vertex("S")  # 3

    g3.add_edge(0, 1)  # Composante 1
    g3.add_edge(2, 3)  # Composante 2 isolée

    graphs["two_components"] = g3

    return graphs

def demonstrate_topology():
    """Démontre l'analyse topologique"""

    print("Poincare Topology VERSE - Demonstration")
    print("=" * 50)

    graphs = create_example_graphs()

    for name, graph in graphs.items():
        print(f"\n--- Graphe: {name} ---")
        print(f"Sommets: {len(graph.vertices)}, Arêtes: {len(graph.edges)}, Faces: {len(graph.faces)}")

        # Analyser la topologie
        topology = graph.validate_topology()

        print(f"Euler characteristic: {topology.euler_characteristic}")
        print(f"Betti numbers (b0, b1, b2): {topology.betti_numbers}")
        print(f"Genus: {topology.genus}")
        print(f"Valid topology: {topology.is_valid}")

        if topology.issues:
            print("Issues detected:")
            for issue in topology.issues:
                print(f"  - {issue}")

            print("\nAutomatic repair...")
            graph.repair_topology()
            print("After repair:")
            print(graph.get_topology_report())
        else:
            print("Topology is healthy")

    print("\n" + "=" * 50)
    print("Démonstration terminée!")

if __name__ == "__main__":
    demonstrate_topology()