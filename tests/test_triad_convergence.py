"""
Tests de convergence triadique - Validation équilibre dynamique OPS

Tests E2E pour vérifier que la triade PRIM + VECTOR + FLUID converge
vers un état d'équilibre stable sur des scénarios réels.
"""

import pytest
import asyncio
import time
import threading
from typing import Dict, Any

from src.triad.triad_orchestrator import TriadOrchestrator, TriadBalance, EngineStatus
from src.engines.vector_engine import VectorEngine, Intent, State
from engines.prim.prim_engine import PrimEngine
from src.events.event_bus import get_event_bus, NexusEvent


class TestTriadConvergence:
    """Tests de convergence de la triade OPS"""

    @pytest.fixture
    def orchestrator(self):
        """Fixture pour orchestrateur triadique"""
        return TriadOrchestrator()

    @pytest.fixture
    def prim_engine(self):
        """Fixture pour moteur PRIM"""
        return PrimEngine()

    @pytest.fixture
    def vector_engine(self):
        """Fixture pour moteur VECTOR"""
        return VectorEngine()

    def test_triad_initialization(self, orchestrator):
        """Test initialisation correcte de la triade"""
        status = orchestrator.get_triad_status()

        assert not status["is_running"]
        assert len(status["engines"]) == 4  # PRIM, VECTOR, FLUID, JOKER

        for engine_name in ["prim", "vector", "fluid", "joker"]:
            assert engine_name in status["engines"]
            assert status["engines"][engine_name]["status"] == "stopped"
            assert status["engines"][engine_name]["error_count"] == 0

    def test_triad_startup_sequence(self, orchestrator):
        """Test séquence de démarrage PRIM -> VECTOR -> FLUID"""
        # Démarrage devrait réussir (même si FLUID n'est pas encore implémenté)
        success = orchestrator.start_triad()
        assert success

        status = orchestrator.get_triad_status()
        assert status["is_running"]

        # Vérifier que PRIM et VECTOR sont démarrés
        assert status["engines"]["prim"]["status"] == "running"
        assert status["engines"]["vector"]["status"] == "running"

        # Arrêt propre
        orchestrator.stop_triad()
        status = orchestrator.get_triad_status()
        assert not status["is_running"]

    def test_balance_calculation_perfect_balance(self, orchestrator):
        """Test calcul d'équilibre parfait"""
        # Simuler activité équilibrée
        current_time = time.time()
        orchestrator.engines["prim"].last_activity = current_time
        orchestrator.engines["vector"].last_activity = current_time
        orchestrator.engines["fluid"].last_activity = current_time

        orchestrator._check_triad_balance()

        # Devrait être équilibré avec score élevé
        assert orchestrator.metrics.balance_score > 0.8
        assert orchestrator.balance_history[-1] == TriadBalance.BALANCED

    def test_balance_calculation_prim_dominant(self, orchestrator):
        """Test détection dominance PRIM"""
        current_time = time.time()

        # PRIM très actif, autres inactifs
        orchestrator.engines["prim"].last_activity = current_time
        orchestrator.engines["vector"].last_activity = current_time - 120  # 2min
        orchestrator.engines["fluid"].last_activity = current_time - 120

        orchestrator._check_triad_balance()

        # Devrait détecter dominance PRIM
        assert orchestrator.balance_history[-1] == TriadBalance.PRIM_DOMINANT
        assert orchestrator.metrics.balance_score < 0.7

    def test_balance_calculation_vector_dominant(self, orchestrator):
        """Test détection dominance VECTOR"""
        current_time = time.time()

        # VECTOR très actif
        orchestrator.engines["prim"].last_activity = current_time - 120
        orchestrator.engines["vector"].last_activity = current_time
        orchestrator.engines["fluid"].last_activity = current_time - 120

        orchestrator._check_triad_balance()

        assert orchestrator.balance_history[-1] == TriadBalance.VECTOR_DOMINANT

    def test_convergence_scenario_simple(self, orchestrator, prim_engine, vector_engine):
        """Test scénario de convergence simple"""
        # Configuration initiale
        intent = Intent(
            name="convergence_test",
            description="Test de convergence triadique",
            target_metrics={"performance": 95, "stability": 99}
        )

        # Démarrage triade
        orchestrator.start_triad()

        # Injection d'activité PRIM
        for i in range(5):
            prim_engine.observe("code", {"pattern": f"test_{i}"}, {"file": f"test_{i}.py"})

        # Injection d'activité VECTOR
        for i in range(3):
            state = State(metrics={"performance": 90 + i, "stability": 95 + i}, timestamp=time.time())
            vector_engine.measure_drift(state)

        # Attendre traitement asynchrone
        time.sleep(0.5)

        # Vérifier interactions
        status = orchestrator.get_triad_status()
        assert status["metrics"]["interaction_count"] >= 8  # 5 PRIM + 3 VECTOR

        # Vérifier équilibrage
        orchestrator._check_triad_balance()
        balance_score = orchestrator.metrics.balance_score

        # Devrait avoir un équilibre raisonnable
        assert 0.3 <= balance_score <= 1.0

        orchestrator.stop_triad()

    def test_convergence_scenario_complex(self, orchestrator, vector_engine):
        """Test scénario de convergence complexe avec évolution temporelle"""
        orchestrator.start_triad()

        # Phase 1: VECTOR dominant (nouveau système)
        intent = Intent(
            name="complex_test",
            description="Test convergence complexe",
            target_metrics={"accuracy": 98, "speed": 100, "reliability": 99.9}
        )
        vector_engine.set_destination(intent)

        # Simuler évolution sur 5 étapes
        convergence_progress = []

        for step in range(5):
            # État dégradé initial, s'améliorant progressivement
            degradation_factor = max(0, 1.0 - step * 0.2)

            state = State(metrics={
                "accuracy": 98 - degradation_factor * 10,
                "speed": 100 - degradation_factor * 5,
                "reliability": 99.9 - degradation_factor * 0.5
            }, timestamp=time.time())

            vector_engine.measure_drift(state)

            # Forcer vérification équilibrage
            orchestrator._check_triad_balance()

            convergence_progress.append({
                "step": step,
                "balance_score": orchestrator.metrics.balance_score,
                "stability_index": orchestrator.metrics.stability_index,
                "drift_magnitude": vector_engine.last_drift.magnitude if vector_engine.last_drift else 0
            })

            time.sleep(0.1)

        # Vérifier progression de convergence
        initial_balance = convergence_progress[0]["balance_score"]
        final_balance = convergence_progress[-1]["balance_score"]

        # L'équilibre devrait s'améliorer ou se stabiliser
        assert final_balance >= initial_balance * 0.8  # Pas de dégradation majeure

        # La stabilité devrait augmenter
        initial_stability = convergence_progress[0]["stability_index"]
        final_stability = convergence_progress[-1]["stability_index"]
        assert final_stability >= initial_stability * 0.9

        orchestrator.stop_triad()

    def test_recovery_from_engine_failure(self, orchestrator):
        """Test récupération automatique après panne moteur"""
        orchestrator.start_triad()

        # Simuler panne PRIM
        orchestrator.engines["prim"].status = EngineStatus.ERROR
        orchestrator.engines["prim"].error_count = 1

        # Vérification santé devrait détecter
        orchestrator._check_engine_health()

        # État devrait être en récupération
        assert orchestrator.engines["prim"].status == EngineStatus.RECOVERING
        assert orchestrator.engines["prim"].restart_count == 1

        orchestrator.stop_triad()

    def test_triad_monitoring_emission(self, orchestrator):
        """Test émission d'événements de monitoring"""
        received_events = []

        def event_collector(event: NexusEvent):
            if event.engine == "triad_orchestrator":
                received_events.append(event)

        # Abonnement aux événements orchestrateur
        get_event_bus().subscribe("metrics_update", event_collector)
        get_event_bus().subscribe("balance_adjusted", event_collector)

        orchestrator.start_triad()

        # Forcer émission métriques
        orchestrator._emit_triad_metrics()

        # Attendre traitement
        time.sleep(0.2)

        # Devrait avoir reçu au moins un événement métriques
        assert len(received_events) >= 1

        metrics_event = received_events[0]
        assert metrics_event.event_type == "metrics_update"
        assert "balance_score" in metrics_event.payload["data"]

        orchestrator.stop_triad()

    def test_stability_index_calculation(self, orchestrator):
        """Test calcul de l'indice de stabilité"""
        # Simuler historique d'équilibre stable
        stable_states = [TriadBalance.BALANCED] * 8
        orchestrator.balance_history = stable_states

        orchestrator._check_triad_balance()

        # Indice de stabilité devrait être élevé (1 / 1 type d'état = 1.0)
        assert orchestrator.metrics.stability_index == 1.0

        # Simuler instabilité
        unstable_states = [TriadBalance.BALANCED, TriadBalance.PRIM_DOMINANT,
                          TriadBalance.VECTOR_DOMINANT, TriadBalance.BALANCED,
                          TriadBalance.PRIM_DOMINANT]
        orchestrator.balance_history = unstable_states

        orchestrator._check_triad_balance()

        # Indice plus bas avec 3 types d'états différents
        assert orchestrator.metrics.stability_index == 1.0 / 3.0

    def test_interaction_count_tracking(self, orchestrator, prim_engine, vector_engine):
        """Test suivi du nombre d'interactions"""
        orchestrator.start_triad()

        initial_count = orchestrator.metrics.interaction_count

        # Générer des événements
        prim_engine.observe("code", {"test": "interaction"}, {"file": "test.py"})
        state = State(metrics={"test": 100}, timestamp=time.time())
        vector_engine.measure_drift(state)

        # Attendre traitement
        time.sleep(0.2)

        final_count = orchestrator.metrics.interaction_count

        # Devrait avoir compté au moins 2 interactions
        assert final_count >= initial_count + 2

        orchestrator.stop_triad()

    def test_triad_shutdown_cleanup(self, orchestrator):
        """Test nettoyage propre à l'arrêt"""
        orchestrator.start_triad()

        # Vérifier état de démarrage
        assert orchestrator.is_running
        assert orchestrator.monitoring_thread is not None
        assert orchestrator.monitoring_thread.is_alive()

        orchestrator.stop_triad()

        # Vérifier nettoyage
        assert not orchestrator.is_running

        # Thread devrait être arrêté (peut prendre un moment)
        orchestrator.monitoring_thread.join(timeout=2.0)
        assert not orchestrator.monitoring_thread.is_alive()

    def test_balance_adjustment_triggering(self, orchestrator):
        """Test déclenchement d'ajustements d'équilibre"""
        received_adjustments = []

        def adjustment_collector(event: NexusEvent):
            if event.event_type == "balance_adjusted":
                received_adjustments.append(event)

        get_event_bus().subscribe("balance_adjusted", adjustment_collector)

        orchestrator.start_triad()

        # Forcer état déséquilibré
        orchestrator.engines["prim"].last_activity = time.time()
        orchestrator.engines["vector"].last_activity = time.time() - 300  # 5min inactive
        orchestrator.engines["fluid"].last_activity = time.time() - 300

        # Déclencher ajustement
        orchestrator._adjust_triad_balance(TriadBalance.PRIM_DOMINANT)

        # Attendre traitement
        time.sleep(0.2)

        # Devrait avoir émis un événement d'ajustement
        assert len(received_adjustments) == 1

        adjustment_event = received_adjustments[0]
        assert adjustment_event.payload["data"]["previous_state"] == "prim_dominant"

        orchestrator.stop_triad()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])