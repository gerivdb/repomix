#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests TDD pour ENGINE.RIDDLER
3 tests par mthode publique
"""

import pytest
from unittest.mock import MagicMock, patch
from engines.riddler_engine import RiddlerEngine


class TestRiddlerEngine:
    """Tests TDD pour RiddlerEngine"""

    @pytest.fixture
    def riddler_engine(self):
        """Fixture pour crer une instance de RiddlerEngine"""
        return RiddlerEngine()

    def test_generate_riddle_basic_functionality(self, riddler_engine):
        """Test 1: generate_riddle() - Fonctionnalit basique"""
        result = riddler_engine.generate_riddle(difficulty=0.5)

        assert "riddle_id" in result
        assert "type" in result
        assert result["type"] in ["logical", "semantic", "computational", "metaphysical"]
        assert "formulation" in result
        assert "difficulty" in result
        assert 0.0 <= result["difficulty"] <= 1.0
        assert result["resolution_possible"] is False

    def test_generate_riddle_difficulty_levels(self, riddler_engine):
        """Test 2: generate_riddle() - Niveaux de difficult"""
        easy_riddle = riddler_engine.generate_riddle(difficulty=0.2)
        hard_riddle = riddler_engine.generate_riddle(difficulty=0.9)

        assert easy_riddle["difficulty"] == 0.2
        assert hard_riddle["difficulty"] == 0.9
        assert easy_riddle["difficulty"] <= hard_riddle["difficulty"]

    def test_generate_riddle_uniqueness(self, riddler_engine):
        """Test 3: generate_riddle() - Unicit des nigmes"""
        riddle1 = riddler_engine.generate_riddle()
        riddle2 = riddler_engine.generate_riddle()

        assert riddle1["riddle_id"] != riddle2["riddle_id"]
        assert len(riddler_engine.riddles) == 6  # 4 paradoxes + 2 gnres

    def test_test_semantic_robustness_basic_functionality(self, riddler_engine):
        """Test 1: test_semantic_robustness() - Fonctionnalit basique"""
        result = riddler_engine.test_semantic_robustness("test_module", test_intensity=0.5)

        assert "test_id" in result
        assert "target_module" in result
        assert result["target_module"] == "test_module"
        assert "test_intensity" in result
        assert result["test_intensity"] == 0.5
        assert "failure_mode" in result
        assert "test_vectors_count" in result

    def test_test_semantic_robustness_intensity_scaling(self, riddler_engine):
        """Test 2: test_semantic_robustness() - Mise  l'chelle de l'intensit"""
        low_intensity = riddler_engine.test_semantic_robustness("module1", test_intensity=0.2)
        high_intensity = riddler_engine.test_semantic_robustness("module2", test_intensity=0.8)

        assert low_intensity["test_vectors_count"] < high_intensity["test_vectors_count"]

    def test_test_semantic_robustness_failure_modes(self, riddler_engine):
        """Test 3: test_semantic_robustness() - Modes de dfaillance"""
        result = riddler_engine.test_semantic_robustness("test_module")

        expected_modes = [
            "contradiction_tolerance",
            "ambiguity_handling",
            "limit_recognition",
            "certainty_modulation",
            "unknown_acknowledgement"
        ]
        assert result["failure_mode"] in expected_modes
        assert len(riddler_engine.tests_executed) == 1

    def test_detect_arrogance_confidence_thresholds(self, riddler_engine):
        """Test 1: detect_arrogance() - Seuils de confiance"""
        low_confidence = riddler_engine.detect_arrogance(0.5)
        high_confidence = riddler_engine.detect_arrogance(0.99)

        assert not low_confidence["arrogance_detected"]
        assert high_confidence["arrogance_detected"]
        assert low_confidence["threshold"] == high_confidence["threshold"] == 0.98

    def test_detect_arrogance_event_logging(self, riddler_engine):
        """Test 2: detect_arrogance() - Journalisation des evenements"""
        initial_events = len(riddler_engine.arrogance_events)

        riddler_engine.detect_arrogance(0.99)
        riddler_engine.detect_arrogance(0.5)

        assert len(riddler_engine.arrogance_events) == initial_events + 2

    def test_detect_arrogance_recommendations(self, riddler_engine):
        """Test 3: detect_arrogance() - Recommandations"""
        detected = riddler_engine.detect_arrogance(0.99)
        not_detected = riddler_engine.detect_arrogance(0.5)

        assert "doutes calibrés" in detected["recommendation"]
        assert detected["recommendation"] != not_detected["recommendation"]

    def test_apply_doubt_injection_basic_functionality(self, riddler_engine):
        """Test 1: apply_doubt_injection() - Fonctionnalit basique"""
        result = riddler_engine.apply_doubt_injection(0.8)

        assert result["doubt_injected"] is True
        assert result["target_confidence"] == 0.8
        assert "magnitude" in result
        assert "effect" in result

    def test_apply_doubt_injection_magnitude_calculation(self, riddler_engine):
        """Test 2: apply_doubt_injection() - Calcul de magnitude"""
        high_confidence = riddler_engine.apply_doubt_injection(0.95)
        low_confidence = riddler_engine.apply_doubt_injection(0.7)

        # Plus la confiance est basse, plus on injecte de doute
        assert low_confidence["magnitude"] > high_confidence["magnitude"]
        assert low_confidence["magnitude"] <= 0.15  # Max magnitude
        assert high_confidence["magnitude"] >= 0.0   # Min magnitude

    def test_apply_doubt_injection_bounds_checking(self, riddler_engine):
        """Test 3: apply_doubt_injection() - Vrification des limites"""
        # Test avec confiance > 1.0 (devrait tre limit)
        result = riddler_engine.apply_doubt_injection(1.2)
        assert result["magnitude"] <= 0.15  # Maximum doubt magnitude

    def test_get_riddler_status_comprehensive(self, riddler_engine):
        """Test: get_riddler_status() - tat complet"""
        # Gnrer quelques donnes de test
        riddler_engine.generate_riddle()
        riddler_engine.test_semantic_robustness("test")
        riddler_engine.detect_arrogance(0.99)

        status = riddler_engine.get_riddler_status()

        assert "paradoxes_registered" in status
        assert "tests_executed" in status
        assert "arrogance_events_detected" in status
        assert "confidence_threshold" in status
        assert "active" in status
        assert status["active"] is True

    def test_riddler_complete_workflow(self, riddler_engine):
        """Test: Workflow complet RIDDLER"""
        # Test sequence complète
        riddle = riddler_engine.generate_riddle(difficulty=0.8)
        assert riddle["difficulty"] == 0.8

        test = riddler_engine.test_semantic_robustness("module", 0.7)
        assert test["test_intensity"] == 0.7

        arrogance = riddler_engine.detect_arrogance(0.99)
        assert arrogance["confidence_level"] == 0.99

        doubt = riddler_engine.apply_doubt_injection(0.8)
        assert doubt["target_confidence"] == 0.8

        status = riddler_engine.get_riddler_status()
        assert status["active"] is True