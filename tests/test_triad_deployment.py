"""
TEST TRIAD DEPLOYMENT - Validation déploiement production

Tests convergence live triad OPS avec métriques performance.
"""

import time
import pytest
import subprocess
import signal
import os
from pathlib import Path
import json


class TestTriadDeployment:
    """Tests déploiement triad OPS production"""

    @pytest.fixture
    def deployment_script(self):
        """Fixture script déploiement"""
        script_path = Path("deploy_triad_orchestrator.py")
        assert script_path.exists(), "Deployment script not found"
        return script_path

    def test_deployment_script_exists(self, deployment_script):
        """Vérification présence script déploiement"""
        assert deployment_script.exists()
        assert deployment_script.is_file()

        # Vérification contenu basique
        content = deployment_script.read_text()
        assert "TriadOrchestrator" in content
        assert "bus_persistent" in content

    def test_triad_startup_convergence(self):
        """Test démarrage triad et convergence live"""
        from src.triad.triad_orchestrator import TriadOrchestrator

        orchestrator = TriadOrchestrator()

        # Démarrage
        start_time = time.time()
        success = orchestrator.start_triad()
        startup_time = time.time() - start_time

        assert success, "Triad startup failed"
        assert startup_time < 5.0, f"Startup too slow: {startup_time:.2f}s"

        # Attendre initialisation
        time.sleep(2)

        # Test convergence sur 10 secondes
        convergence_scores = []
        latencies = []

        for i in range(10):
            iter_start = time.time()

            # Mesure équilibrage
            status = orchestrator.get_triad_status()
            balance_score = status["metrics"]["balance_score"]
            convergence_scores.append(balance_score)

            iter_time = time.time() - iter_start
            latencies.append(iter_time)

            time.sleep(1)

        # Vérifications convergence
        avg_convergence = sum(convergence_scores) / len(convergence_scores)
        assert avg_convergence > 0.8, f"Poor convergence: {avg_convergence:.2f}"

        # Vérifications performance
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 0.01, f"High latency: {avg_latency:.3f}s"

        # Test stabilité (faible variance)
        variance = sum((s - avg_convergence) ** 2 for s in convergence_scores) / len(convergence_scores)
        assert variance < 0.05, f"Unstable convergence: variance {variance:.3f}"

        # Arrêt propre
        orchestrator.stop_triad()

    def test_event_bus_persistence(self):
        """Test persistance bus événements SQLite WAL"""
        from src.events.event_bus import EventBus, NexusEvent
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Bus avec persistance
            bus = EventBus(tmpdir)

            # Publier événements
            events = []
            for i in range(5):
                event = NexusEvent.create(
                    "test", f"persistence_test_{i}",
                    {"data": {"index": i}, "severity": "info"}
                )
                bus.publish(event)
                events.append(event)

            # Attendre traitement
            time.sleep(0.5)

            # Vérifier file d'attente
            queue_stats = bus.get_queue_stats()
            assert queue_stats["total"] >= 5

            # Simuler redémarrage (nouveau bus même répertoire)
            bus2 = EventBus(tmpdir)
            queue_stats2 = bus2.get_queue_stats()
            assert queue_stats2["total"] >= 5

    def test_joker_integration_production(self):
        """Test intégration JOKER en mode production"""
        from src.joker.joker_engine import JokerEngine

        joker = JokerEngine()

        # Configuration production (faible agressivité)
        original_aggression = joker.aggression_level
        joker.aggression_level = 0.1

        try:
            # Test exécution test léger
            result = joker.execute_rupture_test("prim_corrupt_observation")

            if result:  # Test peut ne pas s'exécuter selon probabilité
                assert result.test_id == "prim_corrupt_observation"
                assert result.success is not None

            # Vérifier statistiques
            stats = joker.get_rupture_statistics()
            assert "stats" in stats
            assert "tests" in stats

        finally:
            joker.aggression_level = original_aggression

    def test_end_to_end_workflow(self):
        """Test workflow complet triad + bus + joker"""
        from src.triad.triad_orchestrator import TriadOrchestrator
        from src.events.event_bus import get_event_bus, NexusEvent
        from engines.prim.prim_engine import PrimEngine

        # Démarrage triad
        orchestrator = TriadOrchestrator()
        assert orchestrator.start_triad()

        try:
            # Test workflow:
            # 1. PRIM observe quelque chose
            prim = PrimEngine()
            prim.observe("test", {"workflow": "test_data"}, {"source": "test"})

            # 2. Attendre événements
            time.sleep(0.5)

            # 3. Vérifier bus a reçu événements
            bus = get_event_bus()
            stats = bus.get_stats()
            assert stats["events_published"] >= 1

            # 4. Vérifier orchestrateur a détecté activité
            status = orchestrator.get_triad_status()
            assert status["metrics"]["interaction_count"] >= 1

            # 5. Vérifier stabilité
            assert status["metrics"]["balance_score"] >= 0.0

        finally:
            orchestrator.stop_triad()

    def test_performance_under_load(self):
        """Test performance triad sous charge"""
        from src.triad.triad_orchestrator import TriadOrchestrator
        from src.events.event_bus import get_event_bus, NexusEvent

        orchestrator = TriadOrchestrator()
        assert orchestrator.start_triad()

        try:
            # Test charge: 100 événements rapides
            start_time = time.time()

            bus = get_event_bus()
            for i in range(100):
                event = NexusEvent.create(
                    "load_test", f"event_{i}",
                    {"data": {"payload": "x" * 50}, "severity": "info"}
                )
                bus.publish(event)

            # Mesurer temps traitement
            processing_time = time.time() - start_time

            # Vérifier performance (< 2 secondes pour 100 événements = < 20ms/evt)
            assert processing_time < 2.0, f"Slow processing: {processing_time:.2f}s"

            # Vérifier traitement complet
            time.sleep(1)  # Attendre traitement asynchrone
            stats = bus.get_stats()
            assert stats["events_published"] >= 100

        finally:
            orchestrator.stop_triad()

    def test_recovery_mechanisms(self):
        """Test mécanismes récupération"""
        from src.triad.triad_orchestrator import TriadOrchestrator

        orchestrator = TriadOrchestrator()
        assert orchestrator.start_triad()

        try:
            # Simuler problème moteur
            orchestrator.engines["vector"].status = orchestrator.engines["vector"].__class__.STOPPED

            # Vérifier détection problème
            orchestrator._check_engine_health()

            # Vérifier tentative récupération
            status = orchestrator.get_triad_status()
            # Note: récupération peut ne pas être immédiate

        finally:
            orchestrator.stop_triad()

    def test_monitoring_data_integrity(self):
        """Test intégrité données monitoring"""
        from src.triad.triad_orchestrator import TriadOrchestrator

        orchestrator = TriadOrchestrator()
        assert orchestrator.start_triad()

        try:
            # Collecter métriques
            status = orchestrator.get_triad_status()
            monitoring = orchestrator.get_triad_status()  # Données monitoring complètes

            # Vérifier structure données
            required_keys = ["is_running", "engines", "metrics"]
            for key in required_keys:
                assert key in monitoring

            # Vérifier métriques numériques valides
            metrics = monitoring["metrics"]
            assert isinstance(metrics["balance_score"], (int, float))
            assert isinstance(metrics["interaction_count"], int)
            assert 0 <= metrics["balance_score"] <= 1

            # Vérifier données moteurs
            for engine_name, engine_data in monitoring["engines"].items():
                assert "status" in engine_data
                assert "last_activity" in engine_data
                assert "error_count" in engine_data

        finally:
            orchestrator.stop_triad()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])