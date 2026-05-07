"""
Tests TDD pour EPIC-9875: SAE Memory & Logging Integration

Tests unitaires complets pour le système de mémoire et logging SAE.
"""

import pytest
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from pathlib import Path

from ml_systems.interpretability.sae_memory_logging import (
    SAEInterventionLogger,
    SAEMemorySystem,
    SAEDashboard,
    SAEInterventionLog,
    get_sae_logger,
    get_sae_memory,
    get_sae_dashboard
)
from ml_systems.interpretability.sae_ontology import SAEFeature, SAEOntologyManager


class TestSAEInterventionLogger:
    """Tests unitaires pour SAEInterventionLogger."""

    def setup_method(self):
        """Configuration des tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = SAEInterventionLogger(log_dir=self.temp_dir)

    def test_initialization(self):
        """Test d'initialisation du logger."""
        assert Path(self.temp_dir).exists()
        assert self.logger.max_logs_per_file == 1000
        assert self.logger.current_file_logs == 0

    def test_log_steering_action(self):
        """Test de logging d'une action de steering."""
        action = {
            "features": ["feature_001"],
            "strengths": [0.8],
            "modes": ["amplification"]
        }
        result = {
            "success": True,
            "applied_actions": 1,
            "performance_impact": {"latency_increase_ms": 2.0}
        }

        log_entry = self.logger.log_steering_action(action, result, "test context")

        assert "intervention_id" in log_entry
        assert log_entry["feature_id"] == "feature_001"
        assert log_entry["action_type"] == "steering"
        assert log_entry["result"]["success"] == True
        assert log_entry["context"] == "test context"

    def test_log_feature_discovery(self):
        """Test de logging de découverte de feature."""
        feature = SAEFeature(
            feature_id="test_feature",
            model_id="qwen-3.5",
            layer=12,
            interpretation_hypothesis="test interpretation",
            steerable=True,
            steering_effects=["effect1"],
            activation_frequency=0.5,
            monosemanticity_score=0.8,
            discovered_at=datetime.now(),
            validation_confidence=0.8,
            related_features=[],
            metadata={}
        )

        self.logger.log_feature_discovery(feature)

        # Vérifier que le log a été créé
        log_files = list(Path(self.temp_dir).glob("sae_logs_*.jsonl"))
        assert len(log_files) == 1

        # Vérifier le contenu du log
        with open(log_files[0], 'r') as f:
            log_data = json.loads(f.read().strip())
            assert log_data["action_type"] == "discovery"
            assert log_data["feature_id"] == "test_feature"

    def test_get_intervention_history(self):
        """Test de récupération de l'historique des interventions."""
        # Créer quelques logs
        self.logger.log_steering_action({"features": ["f1"]}, {"success": True})
        self.logger.log_steering_action({"features": ["f2"]}, {"success": False})

        # Récupérer l'historique
        history = self.logger.get_intervention_history()

        assert len(history) == 2
        assert history[0]["action_type"] == "steering"
        assert history[1]["action_type"] == "steering"

    def test_get_intervention_history_with_filters(self):
        """Test de récupération avec filtres."""
        self.logger.log_steering_action({"features": ["f1"]}, {"success": True})
        self.logger.log_steering_action({"features": ["f2"]}, {"success": False})

        # Filtrer par feature
        history = self.logger.get_intervention_history(feature_id="f1")
        assert len(history) == 1
        assert history[0]["feature_id"] == "f1"

    def test_generate_usage_report(self):
        """Test de génération de rapport d'usage."""
        # Créer des logs de test
        self.logger.log_steering_action({"features": ["f1"]}, {"success": True})
        self.logger.log_steering_action({"features": ["f1"]}, {"success": True})
        self.logger.log_steering_action({"features": ["f2"]}, {"success": False})

        report = self.logger.generate_usage_report()

        assert report["total_interventions"] == 3
        assert report["feature_usage"]["f1"] == 2
        assert report["feature_usage"]["f2"] == 1
        assert report["action_types"]["steering"] == 3
        assert len(report["insights"]) > 0

    def test_log_rotation(self):
        """Test de rotation des fichiers de log."""
        # Simuler beaucoup de logs pour déclencher la rotation
        self.logger.max_logs_per_file = 2

        for i in range(3):
            self.logger.log_steering_action({"features": [f"f{i}"]}, {"success": True})

        # Vérifier qu'un nouveau fichier a été créé
        log_files = list(Path(self.temp_dir).glob("sae_logs_*.jsonl"))
        assert len(log_files) >= 1


class TestSAEMemorySystem:
    """Tests unitaires pour SAEMemorySystem."""

    def setup_method(self):
        """Configuration des tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory = SAEMemorySystem(storage_path=self.temp_dir)

    def test_initialization(self):
        """Test d'initialisation du système de mémoire."""
        assert Path(self.temp_dir).exists()
        assert len(self.memory.interaction_cache) == 0

    def test_store_and_retrieve_interactions(self):
        """Test de stockage et récupération d'interactions."""
        feature_id = "test_feature"
        interaction = {
            "type": "steering",
            "strength": 0.8,
            "outcome": "success"
        }

        # Stocker l'interaction
        self.memory.store_feature_interaction(feature_id, interaction)

        # Récupérer l'historique
        history = self.memory.retrieve_feature_history(feature_id)

        assert len(history) == 1
        assert history[0]["type"] == "steering"
        assert history[0]["strength"] == 0.8
        assert "timestamp" in history[0]

    def test_interaction_cache_size_limit(self):
        """Test de limitation de la taille du cache."""
        feature_id = "test_feature"
        self.memory.max_cache_size = 3

        # Ajouter plus d'interactions que la limite
        for i in range(5):
            self.memory.store_feature_interaction(feature_id, {"index": i})

        # Vérifier que seules les 3 dernières sont conservées
        history = self.memory.retrieve_feature_history(feature_id)
        assert len(history) == 3
        assert history[0]["index"] == 2  # Les 2 premières ont été évincées

    def test_persistence_to_disk(self):
        """Test de persistance sur disque."""
        feature_id = "persistent_feature"
        interaction = {"type": "test", "value": 42}

        # Stocker et vérifier en mémoire
        self.memory.store_feature_interaction(feature_id, interaction)
        history = self.memory.retrieve_feature_history(feature_id)
        assert len(history) == 1

        # Simuler rechargement depuis disque
        new_memory = SAEMemorySystem(storage_path=self.temp_dir)
        new_history = new_memory.retrieve_feature_history(feature_id)

        assert len(new_history) == 1
        assert new_history[0]["type"] == "test"
        assert new_history[0]["value"] == 42

    def test_update_feature_metadata(self):
        """Test de mise à jour des métadonnées de feature."""
        # Créer un ontology manager mock
        ontology = SAEOntologyManager()
        feature = SAEFeature(
            feature_id="test_feature",
            model_id="qwen-3.5",
            layer=12,
            interpretation_hypothesis="test",
            steerable=True,
            steering_effects=[],
            activation_frequency=0.5,
            monosemanticity_score=0.8,
            discovered_at=datetime.now(),
            validation_confidence=0.8,
            related_features=[],
            metadata={"usage_count": 0}
        )
        ontology.add_feature(feature)

        # Créer mémoire avec ontology
        memory = SAEMemorySystem(storage_path=self.temp_dir, ontology_manager=ontology)

        # Mettre à jour métadonnées
        memory.update_feature_metadata("test_feature", {"usage_count": 5, "last_used": "today"})

        # Vérifier la mise à jour
        updated_feature = ontology.get_feature("test_feature")
        assert updated_feature.metadata["usage_count"] == 5
        assert updated_feature.metadata["last_used"] == "today"

    def test_find_similar_features(self):
        """Test de recherche de features similaires."""
        ontology = SAEOntologyManager()

        # Créer des features similaires
        feature1 = SAEFeature(
            feature_id="f1",
            model_id="qwen-3.5",
            layer=12,
            interpretation_hypothesis="répétition boucle",
            steerable=True,
            steering_effects=[],
            activation_frequency=0.5,
            monosemanticity_score=0.8,
            discovered_at=datetime.now(),
            validation_confidence=0.8,
            related_features=[],
            metadata={}
        )

        feature2 = SAEFeature(
            feature_id="f2",
            model_id="qwen-3.5",
            layer=13,  # Layer proche
            interpretation_hypothesis="répétition pattern",  # Mot en commun
            steerable=True,
            steering_effects=[],
            activation_frequency=0.6,
            monosemanticity_score=0.7,
            discovered_at=datetime.now(),
            validation_confidence=0.7,
            related_features=[],
            metadata={}
        )

        ontology.add_feature(feature1)
        ontology.add_feature(feature2)

        memory = SAEMemorySystem(ontology_manager=ontology)

        # Rechercher features similaires
        similar = memory.find_similar_features(feature1, threshold=0.5)

        assert len(similar) >= 1  # Au moins feature2 devrait être trouvé
        assert any(f.feature_id == "f2" for f in similar)

    def test_get_memory_statistics(self):
        """Test de récupération des statistiques mémoire."""
        # Ajouter quelques interactions
        self.memory.store_feature_interaction("f1", {"type": "steering"})
        self.memory.store_feature_interaction("f1", {"type": "analysis"})
        self.memory.store_feature_interaction("f2", {"type": "steering"})

        stats = self.memory.get_memory_statistics()

        assert stats["total_features_with_history"] == 2
        assert stats["total_interactions"] == 3
        assert stats["avg_interactions_per_feature"] == 1.5


class TestSAEDashboard:
    """Tests unitaires pour SAEDashboard."""

    def setup_method(self):
        """Configuration des tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = SAEInterventionLogger(log_dir=self.temp_dir)
        self.memory = SAEMemorySystem(storage_path=self.temp_dir)
        self.dashboard = SAEDashboard(self.logger, self.memory)

    def test_generate_usage_report(self):
        """Test de génération de rapport d'usage."""
        # Ajouter des données de test
        self.logger.log_steering_action({"features": ["f1"]}, {"success": True})
        self.memory.store_feature_interaction("f1", {"type": "steering"})

        report = self.dashboard.generate_usage_report()

        assert "total_interventions" in report
        assert "memory_statistics" in report
        assert "dashboard_generated_at" in report
        assert report["memory_statistics"]["total_features_with_history"] == 1

    def test_analyze_steering_effectiveness(self):
        """Test d'analyse de l'efficacité du steering."""
        # Ajouter des interventions réussies et échouées
        self.logger.log_steering_action({"features": ["f1"]}, {"success": True, "performance_impact": {"latency_increase_ms": 1.0}})
        self.logger.log_steering_action({"features": ["f1"]}, {"success": True, "performance_impact": {"latency_increase_ms": 2.0}})
        self.logger.log_steering_action({"features": ["f2"]}, {"success": False, "performance_impact": {"latency_increase_ms": 3.0}})

        analysis = self.dashboard.analyze_steering_effectiveness()

        assert analysis["total_interventions"] == 3
        assert analysis["success_rate"] == 2/3  # 2 réussites sur 3
        assert analysis["avg_performance_impact_ms"] == 2.0  # Moyenne des impacts
        assert "f1" in analysis["feature_effectiveness"]
        assert "f2" in analysis["feature_effectiveness"]

    def test_identify_underutilized_features(self):
        """Test d'identification des features sous-utilisées."""
        ontology = SAEOntologyManager()

        # Feature sous-utilisée (steerable mais peu utilisée)
        underused_feature = SAEFeature(
            feature_id="underused",
            model_id="qwen-3.5",
            layer=12,
            interpretation_hypothesis="test",
            steerable=True,
            steering_effects=[],
            activation_frequency=0.5,
            monosemanticity_score=0.8,
            discovered_at=datetime.now(),
            validation_confidence=0.8,
            related_features=[],
            metadata={}
        )

        # Feature bien utilisée
        well_used_feature = SAEFeature(
            feature_id="well_used",
            model_id="qwen-3.5",
            layer=12,
            interpretation_hypothesis="test",
            steerable=True,
            steering_effects=[],
            activation_frequency=0.5,
            monosemanticity_score=0.8,
            discovered_at=datetime.now(),
            validation_confidence=0.8,
            related_features=[],
            metadata={}
        )

        ontology.add_feature(underused_feature)
        ontology.add_feature(well_used_feature)

        # Peu d'interactions pour underused
        for i in range(3):  # Moins de 5
            self.memory.store_feature_interaction("underused", {"type": "steering"})

        # Beaucoup d'interactions pour well_used
        for i in range(10):
            self.memory.store_feature_interaction("well_used", {"type": "steering"})

        # Configurer la mémoire avec ontology
        self.memory.ontology_manager = ontology
        self.dashboard.memory_system = self.memory

        underutilized = self.dashboard.identify_underutilized_features()

        assert "underused" in underutilized
        assert "well_used" not in underutilized

    def test_suggest_feature_improvements(self):
        """Test de suggestions d'améliorations de features."""
        # Créer des interventions avec échecs répétés
        for i in range(4):  # 4 échecs pour f1
            self.logger.log_steering_action({"features": ["f1"]}, {"success": False})

        # Quelques succès pour f2
        for i in range(6):  # 6 interventions, dont 2 échecs
            success = i >= 2  # 2 premiers échouent, 4 suivants réussissent
            self.logger.log_steering_action({"features": ["f2"]}, {"success": success})

        suggestions = self.dashboard.suggest_feature_improvements()

        # Devrait suggérer amélioration pour f1 (échecs répétés)
        f1_suggestions = [s for s in suggestions if s.get("feature_id") == "f1"]
        assert len(f1_suggestions) > 0
        assert "retraining" in f1_suggestions[0]["type"]

        # Devrait suggérer amélioration pour f2 (faible taux de succès)
        f2_suggestions = [s for s in suggestions if s.get("feature_id") == "f2"]
        assert len(f2_suggestions) > 0

    def test_export_analytics_data(self):
        """Test d'export des données d'analytics."""
        # Ajouter des données
        self.logger.log_steering_action({"features": ["f1"]}, {"success": True})

        # Exporter en JSON
        exported = self.dashboard.export_analytics_data(format='json')

        # Vérifier que c'est du JSON valide
        data = json.loads(exported)
        assert "usage_report" in data
        assert "effectiveness_analysis" in data
        assert "improvement_suggestions" in data
        assert "export_timestamp" in data


class TestGlobalInstances:
    """Tests des instances globales."""

    def test_get_sae_logger(self):
        """Test de récupération de l'instance globale de logger."""
        logger1 = get_sae_logger()
        logger2 = get_sae_logger()

        # Devrait retourner la même instance
        assert logger1 is logger2
        assert isinstance(logger1, SAEInterventionLogger)

    def test_get_sae_memory(self):
        """Test de récupération de l'instance globale de mémoire."""
        memory1 = get_sae_memory()
        memory2 = get_sae_memory()

        # Devrait retourner la même instance
        assert memory1 is memory2
        assert isinstance(memory1, SAEMemorySystem)

    def test_get_sae_dashboard(self):
        """Test de récupération de l'instance globale de dashboard."""
        dashboard1 = get_sae_dashboard()
        dashboard2 = get_sae_dashboard()

        # Devrait retourner la même instance
        assert dashboard1 is dashboard2
        assert isinstance(dashboard1, SAEDashboard)