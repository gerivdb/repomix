"""
Démonstration LeCun Auto-supervision VERSE
Test de la prédiction de clusters manquants
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from autosupervision_engine import LecunPredictor
from tql_fusion_verse.ternary_cluster import TernaryCluster

def create_test_clusters():
    """Créer des clusters de test pour la démonstration"""

    clusters = []

    # Cluster Think (début du cycle)
    think_cluster = TernaryCluster(
        name="think_function",
        source="code-gen",
        signature=(2, 1, 0, 1, 1, 0, 0),  # Think VALIDE, autres PARTIEL/NEUTRE
        embedding=[2, 1, 0, 2, 1, 1, 0, 2],
        tags={"function", "definition", "think"}
    )

    # Cluster Do (milieu du cycle)
    do_cluster = TernaryCluster(
        name="do_implementation",
        source="code-gen",
        signature=(1, 2, 1, 1, 1, 0, 0),  # Do VALIDE, Think PARTIEL
        embedding=[1, 2, 1, 2, 1, 1, 0, 2],
        tags={"function", "implementation", "do"}
    )

    # Cluster Check (fin du cycle)
    check_cluster = TernaryCluster(
        name="check_validation",
        source="test-gen",
        signature=(0, 1, 2, 1, 1, 0, 0),  # Check VALIDE, autres NEUTRE/PARTIEL
        embedding=[0, 1, 2, 2, 1, 1, 0, 2],
        tags={"function", "validation", "check"}
    )

    clusters.extend([think_cluster, do_cluster, check_cluster])

    # Ajouter des clusters similaires pour l'apprentissage
    similar_think = TernaryCluster(
        name="think_class",
        source="code-gen",
        signature=(2, 0, 1, 1, 1, 0, 0),
        embedding=[2, 0, 1, 2, 1, 1, 0, 2],
        tags={"class", "definition", "think"}
    )

    clusters.append(similar_think)
    return clusters

def demonstrate_autosupervision():
    """Démontre l'auto-supervision Lecun"""

    print("LeCun Auto-supervision VERSE - Demonstration")
    print("=" * 50)

    # Créer les clusters de test
    all_clusters = create_test_clusters()
    print(f"Created {len(all_clusters)} test clusters")

    # Initialiser le prédicteur
    predictor = LecunPredictor()

    # Phase d'apprentissage auto-supervisé
    print("\nLearning phase (auto-supervision)...")

    # Simuler un graphe avec tous les clusters
    class MockGraph:
        def __init__(self, vertices):
            self.vertices = vertices

    full_graph = MockGraph(all_clusters)
    predictor.learn_from_graph(full_graph, missing_ratio=0.25)

    print(f"Learned {len(predictor.knowledge_base)} patterns from auto-supervision")

    # Phase de test : masquer des clusters et prédire
    print("\nPrediction phase:")

    # Test 1: Masquer le cluster Check, prédire depuis Think+Do
    observed = [all_clusters[0], all_clusters[1]]  # Think + Do
    actual_missing = all_clusters[2]  # Check

    print(f"\nTest 1: Missing cluster from {len(observed)} observed")
    prediction = predictor.predict_missing(observed)

    print(f"Predicted: {prediction.predicted_cluster.name if prediction.predicted_cluster else 'None'}")
    print(".2f")
    print("Reasoning:")
    for reason in prediction.reasoning_path:
        print(f"  - {reason}")

    # Test 2: Masquer le cluster Do, prédire depuis Think+Check
    observed2 = [all_clusters[0], all_clusters[2]]  # Think + Check
    actual_missing2 = all_clusters[1]  # Do

    print(f"\nTest 2: Missing cluster from {len(observed2)} observed")
    prediction2 = predictor.predict_missing(observed2)

    print(f"Predicted: {prediction2.predicted_cluster.name if prediction2.predicted_cluster else 'None'}")
    print(".2f")

    # Test 3: Évaluation globale de l'accuracy
    print("
Global accuracy evaluation:"    accuracy = predictor.evaluate_accuracy(full_graph, missing_ratio=0.2)
    print(".2f")

    # Rapport final
    print("
Final Report:"    print(predictor.get_performance_report())

    print("\nDemonstration completed!")

if __name__ == "__main__":
    demonstrate_autosupervision()