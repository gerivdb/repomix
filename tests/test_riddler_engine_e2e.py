#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ TESTS E2E RIDDLER ENGINE EPIC-XXXX
Conforme standard NEXUS E2E v2.1

Tests d'intégration complets:
  🔌 Intégration bus événements
  🔄 Cycle complet génération → test → détection → mitigation
  📊 Métriques et observabilité
  🧩 Interopérabilité avec les autres moteurs
"""
import sys
import time
import pytest

sys.path.insert(0, '.')
from engines.riddler_engine import RiddlerEngine
from engines.common.event_bus import bus, Event


class TestRiddlerEngineE2E:
    """
    Tests E2E complets RIDDLER ENGINE
    Conforme: EPIC-XXXX PERTURBATION LAYER
    """

    def setup_method(self):
        """Initialisation environnement E2E"""
        self.riddler = RiddlerEngine()
        self.events_received = []

        # Enregistrement écouteur bus
        def event_listener(event):
            if event.origin.startswith("riddler.engine"):
                self.events_received.append(event)

        bus.subscribe(event_listener)

    def test_complete_arrogance_mitigation_cycle(self):
        """✅ E2E 1: Cycle complet détection arrogance → mitigation"""
        # 1. Détection arrogance
        detection = self.riddler.detect_arrogance(0.995)
        assert detection["arrogance_detected"] is True

        # 2. Attente événement
        time.sleep(0.1)
        arrogance_event = next((e for e in self.events_received if e.origin == "riddler.engine.arrogance"), None)
        assert arrogance_event is not None
        assert arrogance_event.phase == "warning"

        # 3. Application mitigation
        mitigation = self.riddler.apply_doubt_injection(0.82)
        assert mitigation["doubt_injected"] is True

        # 4. Vérification événement mitigation
        time.sleep(0.1)
        doubt_event = next((e for e in self.events_received if e.origin == "riddler.engine.doubt"), None)
        assert doubt_event is not None
        assert doubt_event.phase == "applied"

        # 5. Vérification état final
        status = self.riddler.get_riddler_status()
        assert status["arrogance_events_detected"] == 1

    def test_robustness_test_full_execution(self):
        """✅ E2E 2: Exécution complète test de robustesse"""
        test_result = self.riddler.test_semantic_robustness("cognitive_core", test_intensity=0.9)

        assert test_result["test_intensity"] == 0.9
        assert test_result["test_vectors_count"] == 9
        assert len(self.riddler.tests_executed) == 1

        time.sleep(0.1)
        test_event = next((e for e in self.events_received if e.origin == "riddler.engine.test"), None)
        assert test_event is not None
        assert test_event.payload["intensity"] == 0.9

    def test_sustained_paradox_generation(self):
        """✅ E2E 3: Génération continue et variée de paradoxes"""
        generated_riddles = []
        formulations = set()

        for i in range(20):
            riddle = self.riddler.generate_riddle(difficulty=random.uniform(0.5, 0.95))
            generated_riddles.append(riddle)
            formulations.add(riddle["formulation"])

        # Vérification aucune duplication
        assert len(formulations) == len(generated_riddles)
        # Vérification diversité types
        types = {r["type"] for r in generated_riddles}
        assert len(types) >= 3  # Au moins 3 types différents sur 20 générations

    def test_engine_interoperability(self):
        """✅ E2E 4: Interopérabilité avec les autres moteurs de la triade"""
        # Simulation interaction avec PRIM ENGINE
        from engines.prim_engine import PrimEngine
        prim = PrimEngine()

        # RIDDLER teste la robustesse de PRIM
        test = self.riddler.test_semantic_robustness("prim_engine.pattern_extractor", 0.8)

        assert test["target_module"] == "prim_engine.pattern_extractor"
        assert test["failure_mode"] in ["contradiction_tolerance", "limit_recognition"]

    def test_stress_1000_riddles_generation(self):
        """✅ E2E 5: Test de charge 1000 énigmes générées"""
        start_time = time.time()

        for _ in range(1000):
            self.riddler.generate_riddle()

        duration = time.time() - start_time
        status = self.riddler.get_riddler_status()

        assert status["paradoxes_registered"] == 1004  # 4 initiales + 1000
        assert duration < 1.0  # Moins d'une seconde pour 1000 générations


if __name__ == "__main__":
    print("\n🔌 TESTS E2E RIDDLER ENGINE")
    print("=" * 60)

    pytest.main([__file__, "-v", "-x", "--tb=short"])