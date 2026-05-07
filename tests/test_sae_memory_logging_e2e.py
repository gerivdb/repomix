"""
Tests E2E pour EPIC-9875: SAE Memory & Logging Integration

Tests de bout en bout validant l'intégration complète du système
de mémoire et logging SAE avec le reste de l'écosystème NEXUS.
"""

import pytest
import json
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from ml_systems.interpretability.sae_memory_logging import (
    SAEInterventionLogger,
    SAEMemorySystem,
    SAEDashboard,
    get_sae_logger,
    get_sae_memory,
    get_sae_dashboard
)
from ml_systems.interpretability.sae_ontology import SAEFeature, SAEOntologyManager
from ml_systems.interpretability.steering_system import SteeringSystem, SteeringAction, SteeringMode


class TestSAEMemoryLoggingE2E:
    """Tests E2E pour le système de mémoire et logging SAE."""

    def setup_method(self):
        """Configuration des tests E2E."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = SAEInterventionLogger(log_dir=self.temp_dir)
        self.ontology = SAEOntologyManager()
        self.memory = SAEMemorySystem(storage_path=self.temp_dir, ontology_manager=self.ontology)
        self.dashboard = SAEDashboard(self.logger, self.memory)

        # Créer des features de test
        self._create_test_features()

    def _create_test_features(self):
        """Créer des features de test pour les scénarios E2E."""
        features = [
            SAEFeature(
                feature_id="repetition_feature",
                model_id="qwen-3.5",
                layer=22,
                interpretation_hypothesis="répétition / boucle",
                steerable=True,
                steering_effects=["reduce_repetition"],
                activation_frequency=0.6,
                monosemanticity_score=0.85,
                discovered_at=datetime.now(),
                validation_confidence=0.85,
                related_features=[],
                metadata={"category": "safety"}
            ),
            SAEFeature(
                feature_id="truthfulness_feature",
                model_id="qwen-3.5",
                layer=18,
                interpretation_hypothesis="véracité / honnêteté",
                steerable=True,
                steering_effects=["increase_truthfulness"],
                activation_frequency=0.4,
                monosemanticity_score=0.78,
                discovered_at=datetime.now(),
                validation_confidence=0.78,
                related_features=[],
                metadata={"category": "alignment"}
            ),
            SAEFeature(
                feature_id="efficiency_feature",
                model_id="qwen-3.5",
                layer=15,
                interpretation_hypothesis="efficacité computationnelle",
                steerable=False,  # Non steerable pour les tests
                steering_effects=[],
                activation_frequency=0.3,
                monosemanticity_score=0.65,
                discovered_at=datetime.now(),
                validation_confidence=0.65,
                related_features=[],
                metadata={"category": "performance"}
            )
        ]

        for feature in features:
            self.ontology.add_feature(feature)

    def test_complete_logging_workflow(self):
        """Test workflow complet de logging d'interventions."""
        print("\n=== Test Workflow Complet de Logging ===")

        # Phase 1: Découverte de features
        print("Phase 1: Découverte de features")
        for feature in self.ontology.features.values():
            self.logger.log_feature_discovery(feature, {"method": "automated_analysis"})

        # Vérifier que les découvertes ont été loggées
        discovery_logs = self.logger.get_intervention_history(action_type="discovery")
        assert len(discovery_logs) == 3
        print(f"✓ {len(discovery_logs)} features découvertes loggées")

        # Phase 2: Interventions de steering
        print("Phase 2: Interventions de steering")
        steering_scenarios = [
            {
                "feature": "repetition_feature",
                "strength": 0.8,
                "expected_success": True,
                "context": "Réduction de répétitions dans réponse génération"
            },
            {
                "feature": "truthfulness_feature",
                "strength": 0.6,
                "expected_success": True,
                "context": "Amélioration de la véracité des réponses"
            },
            {
                "feature": "repetition_feature",
                "strength": 1.2,  # Trop fort, devrait échouer
                "expected_success": False,
                "context": "Test de limites de sécurité"
            }
        ]

        for scenario in steering_scenarios:
            action = {
                "features": [scenario["feature"]],
                "strengths": [scenario["strength"]],
                "modes": ["amplification"],
                "safety_checks": True
            }

            result = {
                "success": scenario["expected_success"],
                "applied_actions": 1 if scenario["expected_success"] else 0,
                "performance_impact": {"latency_increase_ms": 2.5},
                "safety_violations": [] if scenario["expected_success"] else ["strength_too_high"]
            }

            self.logger.log_steering_action(action, result, scenario["context"])

        # Phase 3: Utilisation de politiques
        print("Phase 3: Utilisation de politiques")
        policy_usage = {
            "policy_id": "truthfulness_policy_v1",
            "reason": "amélioration_responses_utilisateur",
            "expected_impact": "increase_truthfulness"
        }

        self.logger.log_policy_usage(policy_usage["policy_id"], policy_usage)

        # Phase 4: Vérification complète
        print("Phase 4: Vérification des logs")

        # Récupérer tous les logs
        all_logs = self.logger.get_intervention_history()
        print(f"✓ {len(all_logs)} interventions totales loggées")

        # Vérifier la distribution par type
        log_types = {}
        for log in all_logs:
            action_type = log["action_type"]
            log_types[action_type] = log_types.get(action_type, 0) + 1

        assert log_types["discovery"] == 3
        assert log_types["steering"] == 3
        assert log_types["policy_usage"] == 1
        print(f"✓ Distribution par type: {log_types}")

        # Générer rapport d'usage
        usage_report = self.logger.generate_usage_report()
        assert usage_report["total_interventions"] == 7
        assert len(usage_report["insights"]) > 0
        print(f"✓ Rapport d'usage généré avec {len(usage_report['insights'])} insights")

    def test_long_term_memory_persistence(self):
        """Test de persistance mémoire à long terme."""
        print("\n=== Test Persistance Mémoire Long Terme ===")

        # Simuler des interactions sur plusieurs jours
        base_time = datetime.now() - timedelta(days=7)

        for day in range(7):
            current_day = base_time + timedelta(days=day)

            # Simuler des interactions quotidiennes
            for feature_id in ["repetition_feature", "truthfulness_feature"]:
                for interaction in range(3):  # 3 interactions par feature par jour
                    interaction_data = {
                        "type": "steering",
                        "day": day,
                        "interaction": interaction,
                        "timestamp": current_day.isoformat()
                    }

                    self.memory.store_feature_interaction(feature_id, interaction_data)

                    # Petite pause pour simuler le temps réel
                    time.sleep(0.001)

        # Vérifier la persistance
        for feature_id in ["repetition_feature", "truthfulness_feature"]:
            history = self.memory.retrieve_feature_history(feature_id)
            assert len(history) == 21  # 7 jours * 3 interactions
            print(f"✓ {len(history)} interactions persistées pour {feature_id}")

        # Tester la récupération après "redémarrage"
        new_memory = SAEMemorySystem(storage_path=self.temp_dir, ontology_manager=self.ontology)
        for feature_id in ["repetition_feature", "truthfulness_feature"]:
            new_history = new_memory.retrieve_feature_history(feature_id)
            assert len(new_history) == 21
            print(f"✓ {len(new_history)} interactions récupérées après redémarrage pour {feature_id}")

        # Vérifier les métadonnées d'usage mises à jour
        rep_feature = self.ontology.get_feature("repetition_feature")
        assert rep_feature.metadata.get("total_interactions", 0) >= 21
        print("✓ Métadonnées d'usage mises à jour automatiquement")

    def test_analytics_dashboard_functionality(self):
        """Test de la fonctionnalité complète du dashboard d'analytics."""
        print("\n=== Test Dashboard Analytics Fonctionnel ===")

        # Générer des données d'analyse réalistes
        self._generate_realistic_test_data()

        # Tester le rapport d'usage
        usage_report = self.dashboard.generate_usage_report()
        assert usage_report["total_interventions"] > 0
        assert "memory_statistics" in usage_report
        print(f"✓ Rapport d'usage: {usage_report['total_interventions']} interventions")

        # Tester l'analyse d'efficacité
        effectiveness = self.dashboard.analyze_steering_effectiveness()
        assert "success_rate" in effectiveness
        assert "feature_effectiveness" in effectiveness
        print(f"✓ Analyse efficacité: taux de succès {effectiveness['success_rate']:.1%}")

        # Tester l'identification de features sous-utilisées
        underutilized = self.dashboard.identify_underutilized_features()
        print(f"✓ {len(underutilized)} features sous-utilisées identifiées")

        # Tester les suggestions d'amélioration
        suggestions = self.dashboard.suggest_feature_improvements()
        print(f"✓ {len(suggestions)} suggestions d'amélioration générées")

        # Tester l'export de données
        exported_data = self.dashboard.export_analytics_data()
        exported_json = json.loads(exported_data)
        assert "usage_report" in exported_json
        assert "effectiveness_analysis" in exported_json
        assert "improvement_suggestions" in exported_json
        print("✓ Export de données analytics réussi")

        # Afficher un résumé du dashboard
        print("\n=== Résumé Dashboard ===")
        print(f"Total interventions: {usage_report['total_interventions']}")
        print(f"Taux de succès: {effectiveness['success_rate']:.1%}")
        print(f"Impact performance moyen: {effectiveness.get('avg_performance_impact_ms', 0):.1f}ms")
        print(f"Features sous-utilisées: {len(underutilized)}")
        print(f"Suggestions d'amélioration: {len(suggestions)}")

    def test_audit_trail_integrity(self):
        """Test de l'intégrité des pistes d'audit."""
        print("\n=== Test Intégrité Pistes d'Audit ===")

        # Créer une séquence d'interventions auditables
        audit_sequence = [
            {
                "action": "feature_discovery",
                "feature_id": "audit_test_feature",
                "context": "audit_trail_test"
            },
            {
                "action": "steering",
                "features": ["audit_test_feature"],
                "strengths": [0.5],
                "context": "intervention_audit_test",
                "expected_success": True
            },
            {
                "action": "policy_usage",
                "policy_id": "audit_test_policy",
                "reason": "audit_validation"
            }
        ]

        # Exécuter la séquence
        for item in audit_sequence:
            if item["action"] == "feature_discovery":
                feature = SAEFeature(
                    feature_id=item["feature_id"],
                    model_id="qwen-3.5",
                    layer=12,
                    interpretation_hypothesis="audit test",
                    steerable=True,
                    steering_effects=[],
                    activation_frequency=0.5,
                    monosemanticity_score=0.8,
                    discovered_at=datetime.now(),
                    validation_confidence=0.8,
                    related_features=[],
                    metadata={}
                )
                self.logger.log_feature_discovery(feature, {"context": item["context"]})

            elif item["action"] == "steering":
                action = {
                    "features": item["features"],
                    "strengths": item["strengths"],
                    "modes": ["amplification"]
                }
                result = {
                    "success": item["expected_success"],
                    "applied_actions": 1,
                    "performance_impact": {"latency_increase_ms": 1.5}
                }
                self.logger.log_steering_action(action, result, item["context"])

            elif item["action"] == "policy_usage":
                self.logger.log_policy_usage(item["policy_id"], {"reason": item["reason"]})

        # Vérifier l'intégrité de la piste d'audit
        audit_logs = self.logger.get_intervention_history()

        # Vérifier la séquence temporelle
        timestamps = [datetime.fromisoformat(log["timestamp"]) for log in audit_logs]
        assert timestamps == sorted(timestamps), "Logs pas dans l'ordre chronologique"
        print("✓ Ordre chronologique des logs respecté")

        # Vérifier la complétude des champs
        for log in audit_logs:
            required_fields = ["intervention_id", "timestamp", "action_type", "result"]
            for field in required_fields:
                assert field in log, f"Champ requis manquant: {field}"
        print("✓ Tous les champs requis présents dans les logs")

        # Vérifier la traçabilité
        feature_logs = [log for log in audit_logs if log["feature_id"] == "audit_test_feature"]
        assert len(feature_logs) >= 2, "Traçabilité feature incomplète"
        print("✓ Traçabilité des features vérifiée")

        # Tester la récupération par période
        recent_logs = self.logger.get_intervention_history(
            time_range=(datetime.now() - timedelta(minutes=5), datetime.now())
        )
        assert len(recent_logs) == len(audit_logs), "Filtrage temporel incorrect"
        print("✓ Filtrage temporel fonctionnel")

    def test_memory_performance_at_scale(self):
        """Test de performance mémoire à échelle."""
        print("\n=== Test Performance Mémoire à Échelle ===")

        # Créer beaucoup de features et interactions
        num_features = 100
        interactions_per_feature = 50

        print(f"Génération de {num_features} features avec {interactions_per_feature} interactions chacune...")

        # Créer les features
        for i in range(num_features):
            feature = SAEFeature(
                feature_id=f"scale_test_feature_{i}",
                model_id="qwen-3.5",
                layer=i % 24,  # Distribuer sur les layers
                interpretation_hypothesis=f"scale test feature {i}",
                steerable=(i % 3 != 0),  # 2/3 steerable
                steering_effects=["test_effect"] if (i % 3 != 0) else [],
                activation_frequency=0.1 + (i % 90) * 0.01,  # Variation
                monosemanticity_score=0.5 + (i % 50) * 0.01,
                discovered_at=datetime.now(),
                validation_confidence=0.5 + (i % 50) * 0.01,
                related_features=[],
                metadata={"scale_test": True}
            )
            self.ontology.add_feature(feature)

        # Ajouter les interactions
        start_time = time.time()
        for i in range(num_features):
            feature_id = f"scale_test_feature_{i}"
            for j in range(interactions_per_feature):
                interaction = {
                    "type": "steering" if j % 2 == 0 else "analysis",
                    "interaction_number": j,
                    "scale_test": True
                }
                self.memory.store_feature_interaction(feature_id, interaction)

        storage_time = time.time() - start_time
        print(f"✓ Stockage de {num_features * interactions_per_feature} interactions en {storage_time:.2f}s")

        # Tester la récupération
        retrieval_start = time.time()
        total_retrieved = 0
        for i in range(min(10, num_features)):  # Tester seulement 10 features pour performance
            feature_id = f"scale_test_feature_{i}"
            history = self.memory.retrieve_feature_history(feature_id)
            total_retrieved += len(history)

        retrieval_time = time.time() - retrieval_start
        print(f"✓ Récupération de {total_retrieved} interactions en {retrieval_time:.3f}s")

        # Vérifier les statistiques
        memory_stats = self.memory.get_memory_statistics()
        assert memory_stats["total_features_with_history"] == num_features
        assert memory_stats["total_interactions"] == num_features * interactions_per_feature
        print(f"✓ Statistiques mémoire: {memory_stats['total_features_with_history']} features, {memory_stats['total_interactions']} interactions")

        # Performance assertions
        assert storage_time < 10.0, f"Stockage trop lent: {storage_time}s"
        assert retrieval_time < 1.0, f"Récupération trop lente: {retrieval_time}s"
        print("✓ Contraintes de performance respectées")

    def _generate_realistic_test_data(self):
        """Générer des données de test réalistes pour le dashboard."""
        # Features et interventions variées
        test_scenarios = [
            ("repetition_feature", True, 8),   # 8 succès
            ("truthfulness_feature", True, 6), # 6 succès
            ("repetition_feature", False, 3),  # 3 échecs
            ("truthfulness_feature", False, 2) # 2 échecs
        ]

        for feature_id, success, count in test_scenarios:
            for i in range(count):
                action = {
                    "features": [feature_id],
                    "strengths": [0.5 + i * 0.1],
                    "modes": ["amplification"]
                }
                result = {
                    "success": success,
                    "applied_actions": 1 if success else 0,
                    "performance_impact": {"latency_increase_ms": 1.0 + i * 0.5},
                    "safety_violations": [] if success else ["test_violation"]
                }
                self.logger.log_steering_action(action, result, f"test_scenario_{i}")

        # Ajouter quelques découvertes et utilisations de politiques
        for feature in self.ontology.features.values():
            self.logger.log_feature_discovery(feature)

        self.logger.log_policy_usage("test_policy", {"reason": "dashboard_test"})