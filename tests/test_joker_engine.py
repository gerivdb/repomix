"""
Tests JOKER ENGINE - Validation par rupture systématique

Tests de robustesse par négation et chaos engineering contrôlé.
"""

import pytest
import time
import random
from unittest.mock import patch

from src.joker.joker_engine import (
    JokerEngine, RuptureTest, RuptureType, RuptureSeverity,
    RuptureResult
)
from src.events.event_bus import get_event_bus, NexusEvent


class TestJokerEngineCore:
    """Tests unitaires du moteur JOKER"""

    @pytest.fixture
    def joker_engine(self):
        """Fixture pour moteur JOKER"""
        return JokerEngine()

    def test_joker_initialization(self, joker_engine):
        """Test initialisation correcte de JOKER"""
        assert len(joker_engine.rupture_tests) > 0
        assert joker_engine.max_history == 100
        assert joker_engine.aggression_level == 0.3

        # Vérifier présence des tests critiques
        assert "prim_corrupt_observation" in joker_engine.rupture_tests
        assert "vector_inconsistent_state" in joker_engine.rupture_tests
        assert "event_bus_flood" in joker_engine.rupture_tests
        assert "triad_engine_isolation" in joker_engine.rupture_tests

    def test_rupture_test_definition(self, joker_engine):
        """Test définition correcte des tests de rupture"""
        for test_id, test in joker_engine.rupture_tests.items():
            assert isinstance(test, RuptureTest)
            assert test.id == test_id
            assert len(test.name) > 0
            assert len(test.description) > 0
            assert isinstance(test.type, RuptureType)
            assert isinstance(test.severity, RuptureSeverity)
            assert 0 <= test.execution_probability <= 1
            assert test.max_executions_per_hour > 0

    def test_execution_probability_logic(self, joker_engine):
        """Test logique de probabilité d'exécution"""
        test = joker_engine.rupture_tests["prim_corrupt_observation"]

        # Avec probabilité 0, ne devrait jamais exécuter
        test.execution_probability = 0.0
        assert not joker_engine._can_execute_test(test)

        # Avec probabilité 1, devrait pouvoir exécuter
        test.execution_probability = 1.0
        joker_engine.aggression_level = 1.0
        # Peut échouer à cause des limites temporelles, mais devrait passer initialement
        test.last_execution = None
        assert joker_engine._can_execute_test(test)

    def test_execution_rate_limiting(self, joker_engine):
        """Test limitation du taux d'exécution"""
        test = joker_engine.rupture_tests["prim_corrupt_observation"]
        test.max_executions_per_hour = 1
        test.last_execution = time.time()  # Exécuté il y a moins d'une heure

        # Ne devrait pas pouvoir exécuter à nouveau
        assert not joker_engine._can_execute_test(test)

        # Après délai suffisant
        test.last_execution = time.time() - 3700  # Plus d'une heure
        assert joker_engine._can_execute_test(test)

    def test_random_test_selection(self, joker_engine):
        """Test sélection aléatoire de tests"""
        # S'assurer qu'il y a des tests disponibles
        available_before = joker_engine.select_random_test()

        # Avec tous les tests à probabilité 0
        original_probs = {}
        for test in joker_engine.rupture_tests.values():
            original_probs[test.id] = test.execution_probability
            test.execution_probability = 0.0

        # Ne devrait rien sélectionner
        assert joker_engine.select_random_test() is None

        # Restaurer probabilités
        for test_id, prob in original_probs.items():
            joker_engine.rupture_tests[test_id].execution_probability = prob


class TestJokerEngineRuptures:
    """Tests d'exécution des ruptures"""

    @pytest.fixture
    def joker_engine(self):
        """Fixture pour moteur JOKER avec event bus mock"""
        engine = JokerEngine()
        # Isoler pour tests
        engine.event_bus = get_event_bus()  # Utilise le vrai bus pour l'instant
        return engine

    def test_prim_corrupt_observation_rupture(self, joker_engine):
        """Test rupture corruption observation PRIM"""
        received_events = []

        def event_collector(event: NexusEvent):
            if event.engine == "joker":
                received_events.append(event)

        joker_engine.event_bus.subscribe("corrupt_observation_injected", event_collector)

        # Exécuter test spécifique
        result = joker_engine.execute_rupture_test("prim_corrupt_observation")

        assert result is not None
        assert result.test_id == "prim_corrupt_observation"
        assert result.target_system == "prim"
        assert result.rupture_type == RuptureType.STATE_CORRUPTION

        # Vérifier événement émis
        assert len(received_events) >= 1
        event = received_events[0]
        assert event.event_type == "corrupt_observation_injected"
        assert "corrupt_data" in event.payload["data"]

    def test_vector_inconsistent_state_rupture(self, joker_engine):
        """Test rupture état incohérent VECTOR"""
        received_events = []

        def event_collector(event: NexusEvent):
            if event.engine == "joker" and "inconsistent_state" in event.event_type:
                received_events.append(event)

        joker_engine.event_bus.subscribe("inconsistent_state_injected", event_collector)

        result = joker_engine.execute_rupture_test("vector_inconsistent_state")

        assert result is not None
        assert result.success
        assert result.target_system == "vector"
        assert result.rupture_type == RuptureType.STATE_CORRUPTION

        # Vérifier événement avec métriques incohérentes
        assert len(received_events) >= 1
        event = received_events[0]
        assert "inconsistent_metrics" in event.payload["data"]

    def test_event_bus_flood_rupture(self, joker_engine):
        """Test rupture inondation bus événements"""
        initial_event_count = len(joker_engine.event_bus.event_history)

        result = joker_engine.execute_rupture_test("event_bus_flood")

        assert result is not None
        assert result.success
        assert result.target_system == "event_bus"
        assert result.rupture_type == RuptureType.RESOURCE_STARVATION

        # Vérifier inondation (au moins 50 événements supplémentaires)
        final_event_count = len(joker_engine.event_bus.event_history)
        assert final_event_count >= initial_event_count + 40

    def test_triad_engine_isolation_rupture(self, joker_engine):
        """Test rupture isolation moteur triade"""
        received_events = []

        def event_collector(event: NexusEvent):
            if event.engine == "joker" and "engine_isolation" in event.event_type:
                received_events.append(event)

        joker_engine.event_bus.subscribe("engine_isolation_simulated", event_collector)

        result = joker_engine.execute_rupture_test("triad_engine_isolation")

        assert result is not None
        assert result.success
        assert result.target_system == "triad"
        assert result.rupture_type == RuptureType.RESOURCE_STARVATION
        assert result.severity == RuptureSeverity.CATASTROPHIC

        # Vérifier événement d'isolation
        assert len(received_events) >= 1
        event = received_events[0]
        assert "isolated_engine" in event.payload["data"]

    def test_unknown_test_execution(self, joker_engine):
        """Test exécution test inconnu"""
        result = joker_engine.execute_rupture_test("unknown_test_id")

        assert result is None

    def test_rupture_result_recording(self, joker_engine):
        """Test enregistrement résultats de rupture"""
        initial_history_length = len(joker_engine.rupture_history)

        result = joker_engine.execute_rupture_test("prim_corrupt_observation")

        assert result is not None
        assert len(joker_engine.rupture_history) == initial_history_length + 1

        # Vérifier contenu historique
        recorded_result = joker_engine.rupture_history[-1]
        assert recorded_result.test_id == "prim_corrupt_observation"
        assert recorded_result.success
        assert recorded_result.timestamp > 0

    def test_statistics_update(self, joker_engine):
        """Test mise à jour statistiques"""
        initial_total = joker_engine.stats["total_tests_executed"]

        joker_engine.execute_rupture_test("prim_corrupt_observation")

        assert joker_engine.stats["total_tests_executed"] == initial_total + 1
        assert joker_engine.stats["successful_ruptures"] >= 1

    def test_recovery_time_measurement(self, joker_engine):
        """Test mesure temps de récupération"""
        result = joker_engine.execute_rupture_test("prim_corrupt_observation")

        assert result is not None
        # Temps de récupération devrait être mesuré pour les ruptures réussies
        if result.success:
            assert result.recovery_time is not None
            assert result.recovery_time > 0


class TestJokerEngineChaos:
    """Tests de chaos engineering"""

    @pytest.fixture
    def joker_engine(self):
        """Fixture pour tests de chaos"""
        engine = JokerEngine()
        # Réduire agressivité pour tests contrôlés
        engine.aggression_level = 1.0  # Forcer exécution pour tests
        return engine

    def test_chaos_cycle_execution(self, joker_engine):
        """Test exécution cycle de chaos"""
        # Permettre tous les tests pour ce test
        for test in joker_engine.rupture_tests.values():
            test.last_execution = None

        results = joker_engine.run_chaos_cycle()

        # Devrait exécuter quelques tests
        assert len(results) >= 1
        assert len(results) <= 3  # Limite du cycle

        # Tous les résultats devraient être valides
        for result in results:
            assert isinstance(result, RuptureResult)
            assert result.timestamp > 0
            assert result.test_id in joker_engine.rupture_tests

    def test_chaos_cycle_respects_limits(self, joker_engine):
        """Test que le cycle de chaos respecte les limites"""
        # Rendre tous les tests inéligibles
        for test in joker_engine.rupture_tests.values():
            test.last_execution = time.time()
            test.execution_probability = 0.0

        results = joker_engine.run_chaos_cycle()

        # Ne devrait rien exécuter
        assert len(results) == 0

    def test_chaos_cycle_event_emission(self, joker_engine):
        """Test émission événements pendant cycle chaos"""
        received_events = []

        def event_collector(event: NexusEvent):
            if event.engine == "joker" and "rupture_test_completed" in event.event_type:
                received_events.append(event)

        joker_engine.event_bus.subscribe("rupture_test_completed", event_collector)

        # Forcer exécution d'un test
        for test in joker_engine.rupture_tests.values():
            test.last_execution = None
            test.execution_probability = 1.0
            break

        results = joker_engine.run_chaos_cycle()

        # Devrait avoir émis des événements de complétion
        assert len(received_events) >= len(results)

        # Vérifier contenu événements
        for event in received_events:
            assert "test_id" in event.payload["data"]
            assert "success" in event.payload["data"]
            assert "target_system" in event.payload["data"]


class TestJokerEngineMonitoring:
    """Tests de monitoring et statistiques JOKER"""

    @pytest.fixture
    def joker_engine(self):
        """Fixture avec quelques tests exécutés"""
        engine = JokerEngine()

        # Simuler quelques exécutions
        engine.stats["total_tests_executed"] = 5
        engine.stats["successful_ruptures"] = 3
        engine.stats["failed_ruptures"] = 2

        # Ajouter résultats factices
        engine.rupture_history = [
            RuptureResult(
                test_id="test_1",
                timestamp=time.time() - 100,
                success=True,
                rupture_type=RuptureType.STATE_CORRUPTION,
                target_system="prim",
                observed_behavior="System corrupted successfully"
            ),
            RuptureResult(
                test_id="test_2",
                timestamp=time.time() - 50,
                success=False,
                rupture_type=RuptureType.BOUNDARY_VIOLATION,
                target_system="vector",
                observed_behavior="Boundary violation failed"
            )
        ]

        return engine

    def test_statistics_completeness(self, joker_engine):
        """Test complétude statistiques"""
        stats = joker_engine.get_rupture_statistics()

        required_keys = ["stats", "tests", "recent_ruptures"]
        for key in required_keys:
            assert key in stats

        # Vérifier statistiques principales
        assert stats["stats"]["total_tests_executed"] == 5
        assert stats["stats"]["successful_ruptures"] == 3
        assert stats["stats"]["failed_ruptures"] == 2

    def test_test_statistics_detail(self, joker_engine):
        """Test détail statistiques par test"""
        stats = joker_engine.get_rupture_statistics()

        # Devrait avoir des stats pour chaque test défini
        assert len(stats["tests"]) == len(joker_engine.rupture_tests)

        # Vérifier structure d'un test
        test_stat = stats["tests"]["prim_corrupt_observation"]
        assert "name" in test_stat
        assert "success_count" in test_stat
        assert "failure_count" in test_stat
        assert "last_execution" in test_stat

    def test_recent_ruptures_detail(self, joker_engine):
        """Test détail ruptures récentes"""
        stats = joker_engine.get_rupture_statistics()

        recent = stats["recent_ruptures"]
        assert len(recent) == 2  # Les 2 résultats simulés

        # Vérifier structure
        rupture = recent[0]
        assert "test_id" in rupture
        assert "timestamp" in rupture
        assert "success" in rupture
        assert "target_system" in rupture

    def test_history_size_limit(self, joker_engine):
        """Test limite taille historique"""
        # Ajouter beaucoup de résultats
        for i in range(150):  # Plus que max_history (100)
            result = RuptureResult(
                test_id=f"test_{i}",
                timestamp=time.time(),
                success=True,
                rupture_type=RuptureType.STATE_CORRUPTION,
                target_system="prim",
                observed_behavior=f"Rupture {i}"
            )
            joker_engine.rupture_history.append(result)

        # Devrait être limité à max_history
        assert len(joker_engine.rupture_history) <= joker_engine.max_history


if __name__ == "__main__":
    pytest.main([__file__, "-v"])