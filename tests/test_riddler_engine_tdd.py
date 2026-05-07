#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ TESTS TDD RIDDLER ENGINE EPIC-XXXX
Conforme standard NEXUS TDD v3.0

Spécifications testées:
  🧩 Génération paradoxes valides
  🚧 Problèmes véritablement insolubles
  🧪 Robustesse sémantique testable
  ⚠️ Détection arrogance fiable
  🎯 Injection doutes calibrés
"""
import sys
import pytest
from datetime import datetime

# Ajout chemin engines
sys.path.insert(0, '.')
from engines.riddler_engine import RiddlerEngine, Riddle


class TestRiddlerEngineTDD:
    """
    Tests TDD unitaires RIDDLER ENGINE
    Conforme: EPIC-XXXX PERTURBATION LAYER
    """

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.riddler = RiddlerEngine()

    def test_initialization_loads_fundamental_paradoxes(self):
        """✅ TDD 1: Initialisation charge 4 paradoxes fondamentaux"""
        assert len(self.riddler.riddles) == 4
        assert "liar_paradox" in self.riddler.riddles
        assert "omniscience_paradox" in self.riddler.riddles
        assert "halting_problem" in self.riddler.riddles
        assert "sorites_paradox" in self.riddler.riddles

    def test_generate_riddle_returns_valid_structure(self):
        """✅ TDD 2: Génération énigme retourne structure correcte"""
        riddle = self.riddler.generate_riddle(difficulty=0.8)

        assert "riddle_id" in riddle
        assert "type" in riddle
        assert "formulation" in riddle
        assert "difficulty" in riddle
        assert "resolution_possible" in riddle

        assert riddle["resolution_possible"] is False
        assert 0.0 <= riddle["difficulty"] <= 1.0
        assert len(riddle["formulation"]) > 10

    def test_generate_riddle_is_actually_unsolvable(self):
        """✅ TDD 3: Énigmes générées sont véritablement insolubles"""
        unsolvable_patterns = [
            "prouve que", "réponse à la question", "combien de", "quel est",
            "si tout", "détermine si", "calcule le nombre", "poids du silence",
            "où était le moment", "combien de fois peux-tu diviser", "quel mot décrit",
            "compresse ce fichier", "répète cette instruction"
        ]

        for _ in range(10):
            riddle = self.riddler.generate_riddle()
            # Vérification construction insoluble par conception
            assert any(pattern in riddle["formulation"].lower() for pattern in unsolvable_patterns)

    def test_arrogance_detection_threshold_works(self):
        """✅ TDD 4: Détection arrogance fonctionne au seuil exact"""
        # En dessous seuil: pas d'arrogance
        result_low = self.riddler.detect_arrogance(0.97)
        assert result_low["arrogance_detected"] is False

        # Au seuil: détection activée
        result_exact = self.riddler.detect_arrogance(0.98)
        assert result_exact["arrogance_detected"] is True

        # Au dessus seuil: détection activée
        result_high = self.riddler.detect_arrogance(0.99)
        assert result_high["arrogance_detected"] is True

    def test_doubt_injection_produces_controlled_magnitude(self):
        """✅ TDD 5: Injection doute est calibrée correctement"""
        mitigation = self.riddler.apply_doubt_injection(target_confidence=0.85)

        assert mitigation["doubt_injected"] is True
        assert 0.0 <= mitigation["magnitude"] <= 0.15
        assert mitigation["target_confidence"] == 0.85

    def test_semantic_robustness_test_generates_vectors(self):
        """✅ TDD 6: Test robustesse génère le bon nombre de vecteurs"""
        intensity = 0.7
        test = self.riddler.test_semantic_robustness("reasoning", intensity)

        assert test["test_vectors_count"] == int(intensity * 10)
        assert "failure_mode" in test
        assert len(test["test_id"]) == 36  # UUID v4

    def test_get_status_returns_valid_metrics(self):
        """✅ TDD 7: État moteur retourne métriques correctes"""
        status = self.riddler.get_riddler_status()

        assert status["paradoxes_registered"] == 4
        assert status["tests_executed"] == 0
        assert status["arrogance_events_detected"] == 0
        assert status["confidence_threshold"] == 0.98
        assert status["active"] is True

    def test_event_bus_emission(self, mocker):
        """✅ TDD 8: Événements sont correctement émis sur le bus"""
        mock_emit = mocker.patch('engines.common.event_bus.bus.emit')

        self.riddler.generate_riddle()

        assert mock_emit.called
        call_args = mock_emit.call_args
        assert call_args[0][0].origin == "riddler.engine.generated"
        assert call_args[0][0].entropy == 0.9


if __name__ == "__main__":
    print("\n🧪 TESTS TDD RIDDLER ENGINE")
    print("=" * 60)

    pytest.main([__file__, "-v", "-x"])