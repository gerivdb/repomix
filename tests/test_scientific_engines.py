# -----------------------------------------------------------------------------
# Tests TDD pour EPIC-9858: Scientific Engines (Joker Engine)
# Tests unitaires du framework d'engines scientifiques
# Couverture: Joker Engine, registry, perturbations, pipeline
# -----------------------------------------------------------------------------

import pytest
import random
import math
from unittest.mock import patch, MagicMock

# Import des engines
try:
    from engines import (
        ScientificEngine, JokerEngine, EngineRegistry,
        EngineResult, EngineConfig, EngineStatus, EnginePhase,
        PerturbationType, engine_registry, create_engine_result_summary
    )
except ImportError:
    pytest.skip("Engines module not available", allow_module_level=True)

class TestEngineConfig:
    """Tests pour EngineConfig"""

    def test_engine_config_creation(self):
        """Test création d'une configuration d'engine"""
        config = EngineConfig("TestEngine")
        assert config.engine_id == "TestEngine"
        assert config.enabled == True
        assert config.max_execution_time == 30.0
        assert config.perturbation_intensity == 0.1

    def test_engine_config_custom_params(self):
        """Test paramètres personnalisés"""
        custom_params = {"custom_param": "value", "threshold": 0.8}
        config = EngineConfig("TestEngine", custom_params=custom_params)
        assert config.custom_params["custom_param"] == "value"
        assert config.custom_params["threshold"] == 0.8

class TestEngineResult:
    """Tests pour EngineResult"""

    def test_engine_result_creation(self):
        """Test création d'un résultat d'engine"""
        result = EngineResult(
            engine_id="TestEngine",
            success=True,
            data="test_data"
        )

        assert result.engine_id == "TestEngine"
        assert result.success == True
        assert result.data == "test_data"
        assert result.validation_score == 0.0
        assert result.phase == EnginePhase.SPARK

    def test_engine_result_is_valid(self):
        """Test propriété is_valid"""
        # Résultat valide
        valid_result = EngineResult("Test", True, "data", validation_score=0.9)
        assert valid_result.is_valid == True

        # Résultat invalide - pas de succès
        invalid_result1 = EngineResult("Test", False, "data", validation_score=0.9)
        assert invalid_result1.is_valid == False

        # Résultat invalide - score trop bas
        invalid_result2 = EngineResult("Test", True, "data", validation_score=0.5)
        assert invalid_result2.is_valid == False

class TestScientificEngine:
    """Tests pour la classe de base ScientificEngine"""

    def test_scientific_engine_initialization(self):
        """Test initialisation d'un engine scientifique"""
        config = EngineConfig("TestEngine")
        engine = ScientificEngine(config)

        assert engine.config == config
        assert engine.status == EngineStatus.READY
        assert isinstance(engine.execution_history, list)

    def test_scientific_engine_abstract_methods(self):
        """Test que les méthodes abstraites lèvent NotImplementedError"""
        engine = ScientificEngine()

        with pytest.raises(NotImplementedError):
            engine.process("test_data")

        with pytest.raises(NotImplementedError):
            engine.validate(EngineResult("Test", True, "data"))

    def test_scientific_engine_get_metrics_empty(self):
        """Test métriques d'un engine sans historique"""
        engine = ScientificEngine()
        metrics = engine.get_metrics()

        assert metrics["executions"] == 0
        assert metrics["success_rate"] == 0.0

class TestJokerEngine:
    """Tests pour le Joker Engine"""

    def test_joker_engine_creation(self):
        """Test création du Joker Engine"""
        engine = JokerEngine()
        assert engine.config.engine_id == "JokerEngine"
        assert engine.status == EngineStatus.READY
        assert hasattr(engine, 'perturbation_generators')

    def test_joker_engine_process_basic(self):
        """Test traitement basique du Joker Engine"""
        engine = JokerEngine()
        result = engine.process("test_data")

        assert result.engine_id == "JOKER"
        assert result.success == True
        assert "joker_phase" in result.metadata
        assert "perturbation_intensity" in result.metadata
        assert isinstance(result.perturbations_applied, list)

    def test_joker_engine_process_with_perturbations(self):
        """Test traitement avec perturbations spécifiées"""
        engine = JokerEngine()
        perturbations = [PerturbationType.RANDOM_NOISE, PerturbationType.BOUNDARY_TEST]
        result = engine.process("test_data", perturbations=perturbations)

        assert result.success == True
        assert len(result.perturbations_applied) > 0
        assert "random_noise" in result.perturbations_applied

    def test_joker_engine_validate(self):
        """Test validation du Joker Engine"""
        engine = JokerEngine()

        # Résultat réussi
        good_result = EngineResult("JOKER", True, "data", perturbations_applied=["noise", "boundary"])
        score = engine.validate(good_result)
        assert 0.0 <= score <= 0.9  # Score JOKER toujours < 0.9

        # Résultat échoué
        bad_result = EngineResult("JOKER", False, "data")
        score = engine.validate(bad_result)
        assert score == 0.0

    def test_joker_engine_execute(self):
        """Test exécution complète du Joker Engine"""
        engine = JokerEngine()
        result = engine.execute("test_data")

        assert isinstance(result, EngineResult)
        assert result.engine_id == "JOKER"
        assert result.execution_time >= 0
        assert result.timestamp is not None

    def test_joker_engine_select_perturbation_for_phase(self):
        """Test sélection des perturbations par phase"""
        engine = JokerEngine()

        # Test phase SPARK
        perturbations = engine._select_perturbation_for_phase(EnginePhase.SPARK)
        assert PerturbationType.CHAOS_INJECTION in perturbations
        assert PerturbationType.RANDOM_NOISE in perturbations

        # Test phase SHIP (perturbation légère)
        perturbations = engine._select_perturbation_for_phase(EnginePhase.SHIP)
        assert perturbations == [PerturbationType.RANDOM_NOISE]

    def test_joker_engine_random_noise_perturbation(self):
        """Test perturbation random noise"""
        engine = JokerEngine()

        # Test avec nombre
        original = 100.0
        perturbed = engine._generate_random_noise(original)
        assert isinstance(perturbed, float)
        # Vérifier que c'est perturbé (avec faible probabilité d'être exactement identique)
        assert abs(perturbed - original) < original * (engine.config.perturbation_intensity * 2)

    def test_joker_engine_boundary_test_perturbation(self):
        """Test perturbation boundary test"""
        engine = JokerEngine()

        # Test avec nombre
        original = 1.0
        perturbed = engine._generate_boundary_test(original)

        # Devrait retourner une valeur limite ou l'original
        boundary_values = [0, 1, -1, float('inf'), float('-inf'), float('nan'), original]
        assert perturbed in boundary_values or perturbed == original

    def test_joker_engine_inversion_test_perturbation(self):
        """Test perturbation inversion test"""
        engine = JokerEngine()

        # Test avec nombre non nul
        original = 2.0
        perturbed = engine._generate_inversion_test(original)
        assert perturbed == 0.5  # 1/2

        # Test avec booléen
        original_bool = True
        perturbed_bool = engine._generate_inversion_test(original_bool)
        assert perturbed_bool == False

        # Test avec liste
        original_list = [1, 2, 3]
        perturbed_list = engine._generate_inversion_test(original_list)
        assert perturbed_list == [3, 2, 1]

    def test_joker_engine_chaos_injection_perturbation(self):
        """Test perturbation chaos injection"""
        engine = JokerEngine()

        original = "test"
        perturbed = engine._generate_chaos_injection(original)

        # Devrait retourner une valeur chaotique ou None
        chaos_values = [None, float('nan'), float('inf'), [], {}, "", 0]
        assert perturbed in chaos_values or "CHAOS_INJECTED" in str(perturbed)

    def test_joker_engine_adversarial_input_perturbation(self):
        """Test perturbation adversarial input"""
        engine = JokerEngine()

        # Test avec string
        original = "safe_input"
        perturbed = engine._generate_adversarial_input(original)

        # Devrait être une string adversarial ou l'original
        adversarial_patterns = ["'; DROP", "<script>", "../../../", "eval(", "\x00"]
        is_adversarial = any(pattern in perturbed for pattern in adversarial_patterns)
        assert is_adversarial or perturbed == original

class TestEngineRegistry:
    """Tests pour le EngineRegistry"""

    def test_engine_registry_creation(self):
        """Test création du registre d'engines"""
        registry = EngineRegistry()
        assert hasattr(registry, 'engines')
        assert hasattr(registry, 'configs')
        assert len(registry.engines) > 0  # Au moins JokerEngine

    def test_engine_registry_get_engine(self):
        """Test récupération d'engine"""
        registry = EngineRegistry()

        # Récupération d'un engine existant
        joker = registry.get_engine("JokerEngine")
        assert joker is not None
        assert isinstance(joker, JokerEngine)

        # Récupération d'un engine inexistant
        nonexistent = registry.get_engine("NonExistentEngine")
        assert nonexistent is None

    def test_engine_registry_register_engine(self):
        """Test enregistrement d'un engine"""
        registry = EngineRegistry()

        # Créer et enregistrer un mock engine
        mock_engine = MagicMock()
        mock_engine.__class__.__name__ = "MockEngine"
        mock_engine.config = EngineConfig("MockEngine")

        initial_count = len(registry.engines)
        registry.register_engine(mock_engine)

        assert len(registry.engines) == initial_count + 1
        assert "MockEngine" in registry.engines

    def test_engine_registry_execute_pipeline(self):
        """Test exécution de pipeline"""
        registry = EngineRegistry()

        # Pipeline simple avec Joker
        pipeline = ["JokerEngine"]
        results = registry.execute_pipeline("test_data", pipeline)

        assert len(results) == 1
        assert results[0].engine_id == "JOKER"
        assert results[0].success == True

    def test_engine_registry_execute_pipeline_nonexistent_engine(self):
        """Test pipeline avec engine inexistant"""
        registry = EngineRegistry()

        pipeline = ["NonExistentEngine"]
        results = registry.execute_pipeline("test_data", pipeline)

        assert len(results) == 1
        assert results[0].engine_id == "NonExistentEngine"
        assert results[0].success == False
        assert "not found" in results[0].error_message

    def test_engine_registry_system_health(self):
        """Test état de santé du système"""
        registry = EngineRegistry()
        health = registry.get_system_health()

        assert "total_engines" in health
        assert "ready_engines" in health
        assert "system_health" in health
        assert "engine_status" in health

        assert health["total_engines"] > 0
        assert health["system_health"] >= 0.0
        assert health["system_health"] <= 1.0

class TestEnginePipeline:
    """Tests pour les pipelines d'engines"""

    def test_create_engine_result_summary_empty(self):
        """Test résumé avec résultats vides"""
        summary = create_engine_result_summary([])
        assert summary["total_results"] == 0
        assert summary["success_rate"] == 0.0

    def test_create_engine_result_summary_with_results(self):
        """Test résumé avec résultats"""
        results = [
            EngineResult("Engine1", True, "data1", execution_time=1.0, validation_score=0.8),
            EngineResult("Engine2", False, "data2", execution_time=2.0, validation_score=0.0),
            EngineResult("Engine3", True, "data3", execution_time=1.5, validation_score=0.9)
        ]

        summary = create_engine_result_summary(results)

        assert summary["total_results"] == 3
        assert summary["successful_results"] == 2
        assert summary["success_rate"] == 2/3
        assert summary["total_execution_time"] == 4.5
        assert abs(summary["average_validation_score"] - 0.567) < 0.001  # (0.8 + 0 + 0.9) / 3
        assert "spark" in summary["pipeline_phases"]
        assert "Engine1" in summary["engines_used"]

class TestJokerEngineRobustness:
    """Tests de robustesse du Joker Engine"""

    def test_joker_engine_handles_various_input_types(self):
        """Test que Joker gère différents types d'entrée"""
        engine = JokerEngine()

        test_inputs = [
            42,           # int
            3.14,         # float
            "string",     # str
            [1, 2, 3],    # list
            {"key": "value"},  # dict
            None,         # None
            True          # bool
        ]

        for input_data in test_inputs:
            result = engine.process(input_data)
            assert result.success == True
            assert result.engine_id == "JOKER"

    def test_joker_engine_config_perturbation_intensity(self):
        """Test configuration de l'intensité de perturbation"""
        config = EngineConfig("JokerEngine", perturbation_intensity=0.5)
        engine = JokerEngine(config)

        assert engine.config.perturbation_intensity == 0.5

        # Test avec intensité élevée
        result = engine.process(100.0)
        assert result.success == True

    def test_joker_engine_error_handling(self):
        """Test gestion d'erreurs du Joker Engine"""
        engine = JokerEngine()

        # Simuler une erreur dans une perturbation
        with patch.object(engine, '_generate_random_noise', side_effect=Exception("Test error")):
            result = engine.execute(100.0)
            assert result.success == False
            assert result.error_message is not None

class TestGlobalRegistry:
    """Tests pour le registre global"""

    def test_global_registry_has_joker(self):
        """Test que le registre global contient Joker"""
        from engines import engine_registry

        joker = engine_registry.get_engine("JokerEngine")
        assert joker is not None
        assert isinstance(joker, JokerEngine)

    def test_global_registry_system_health(self):
        """Test santé du système global"""
        from engines import engine_registry

        health = engine_registry.get_system_health()
        assert health["total_engines"] >= 1  # Au moins Joker
        assert health["system_health"] >= 0.0

# -----------------------------------------------------------------------------
# Tests d'intégration
# -----------------------------------------------------------------------------

class TestEngineIntegration:
    """Tests d'intégration des engines"""

    def test_joker_engine_full_pipeline(self):
        """Test pipeline complet avec Joker"""
        # Configuration d'un pipeline simple
        from engines import engine_registry

        input_data = {
            "numbers": [1, 2, 3, 4, 5],
            "text": "test input",
            "value": 100.0
        }

        # Exécuter pipeline
        results = engine_registry.execute_pipeline(input_data, ["JokerEngine"])

        assert len(results) == 1
        result = results[0]

        assert result.engine_id == "JOKER"
        assert result.success == True
        assert "joker_principle" in result.metadata
        assert result.metadata["joker_principle"] == "perturber_pour_prouver"

    def test_multiple_engine_execution(self):
        """Test exécution multiple d'engines"""
        from engines import engine_registry

        # Exécuter Joker plusieurs fois
        for i in range(3):
            result = engine_registry.execute_pipeline(f"input_{i}", ["JokerEngine"])
            assert len(result) == 1
            assert result[0].success == True

        # Vérifier métriques
        joker = engine_registry.get_engine("JokerEngine")
        metrics = joker.get_metrics()

        assert metrics["executions"] >= 3
        assert metrics["success_rate"] > 0

    def test_engine_error_recovery(self):
        """Test récupération après erreur d'engine"""
        from engines import engine_registry

        # Forcer une erreur (simulée)
        joker = engine_registry.get_engine("JokerEngine")

        # Le Joker devrait gérer les erreurs gracieusement
        result = joker.execute(None)  # None peut causer des problèmes
        assert result is not None  # Quel que soit le résultat, pas de crash

if __name__ == "__main__":
    pytest.main([__file__, "-v"])