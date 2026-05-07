#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests TDD pour ENGINE.FLUENCE
3 tests par mthode publique
"""

import pytest
from unittest.mock import MagicMock, patch
from engines.fluence_engine import FluenceEngine


class TestFluenceEngine:
    """Tests TDD pour FluenceEngine"""

    @pytest.fixture
    def fluence_engine(self):
        """Fixture pour crer une instance de FluenceEngine"""
        return FluenceEngine()

    def test_launch_propagation_basic_functionality(self, fluence_engine):
        """Test 1: launch_propagation() - Fonctionnalit basique"""
        result = fluence_engine.launch_propagation("source_node", initial_amplitude=1.0)

        assert "signal_id" in result
        assert "wave_id" in result
        assert "origin" in result
        assert result["origin"] == "source_node"
        assert "initial_amplitude" in result
        assert result["initial_amplitude"] == 1.0
        assert result["propagation_active"] is True

    def test_launch_propagation_amplitude_variation(self, fluence_engine):
        """Test 2: launch_propagation() - Variation d'amplitude"""
        low_amp = fluence_engine.launch_propagation("node1", initial_amplitude=0.5)
        high_amp = fluence_engine.launch_propagation("node2", initial_amplitude=2.0)

        assert low_amp["initial_amplitude"] == 0.5
        assert high_amp["initial_amplitude"] == 2.0
        assert low_amp["signal_id"] != high_amp["signal_id"]

    def test_launch_propagation_storage_and_tracking(self, fluence_engine):
        """Test 3: launch_propagation() - Stockage et suivi"""
        initial_signals = len(fluence_engine.active_signals)
        initial_waves = len(fluence_engine.propagation_waves)

        fluence_engine.launch_propagation("test_source")

        assert len(fluence_engine.active_signals) == initial_signals + 1
        assert len(fluence_engine.propagation_waves) == initial_waves + 1

    def test_propagate_cycle_basic_functionality(self, fluence_engine):
        """Test 1: propagate_cycle() - Fonctionnalit basique"""
        launch_result = fluence_engine.launch_propagation("test", initial_amplitude=1.0)
        signal_id = launch_result["signal_id"]

        result = fluence_engine.propagate_cycle(signal_id)

        assert "signal_id" in result
        assert result["signal_id"] == signal_id
        assert "distance_travelled" in result
        assert result["distance_travelled"] == 1
        assert "current_amplitude" in result
        assert "propagation_continues" in result

    def test_propagate_cycle_amplitude_attenuation(self, fluence_engine):
        """Test 2: propagate_cycle() - Attnuation d'amplitude"""
        launch_result = fluence_engine.launch_propagation("test", initial_amplitude=1.0)
        signal_id = launch_result["signal_id"]

        result = fluence_engine.propagate_cycle(signal_id)

        # L'amplitude devrait diminuer selon ATTENUATION_FACTOR (0.85)
        assert result["current_amplitude"] < 1.0
        assert result["current_amplitude"] > 0.8  # Environ 0.85

    def test_propagate_cycle_signal_extinction(self, fluence_engine):
        """Test 3: propagate_cycle() - Extinction du signal"""
        launch_result = fluence_engine.launch_propagation("test", initial_amplitude=0.01)
        signal_id = launch_result["signal_id"]

        # Propager jusqu' l'extinction
        cycles = 0
        while cycles < 20:  # Scurit contre boucle infinie
            result = fluence_engine.propagate_cycle(signal_id)
            cycles += 1
            if not result["propagation_continues"]:
                break

        # Le signal devrait s'teindre  un moment
        assert not result["propagation_continues"]
        assert result["current_amplitude"] < 0.05

    def test_check_critical_mass_basic_functionality(self, fluence_engine):
        """Test 1: check_critical_mass() - Fonctionnalit basique"""
        launch_result = fluence_engine.launch_propagation("test")
        wave_id = launch_result["wave_id"]

        result = fluence_engine.check_critical_mass(wave_id, penetration_rate=0.5)

        assert "wave_id" in result
        assert result["wave_id"] == wave_id
        assert "penetration_rate" in result
        assert result["penetration_rate"] == 0.5
        assert "critical_threshold" in result
        assert result["critical_threshold"] == fluence_engine.CRITICAL_MASS_THRESHOLD
        assert "critical_mass_reached" in result

    def test_check_critical_mass_threshold_detection(self, fluence_engine):
        """Test 2: check_critical_mass() - Dtection du seuil"""
        launch_result = fluence_engine.launch_propagation("test")
        wave_id = launch_result["wave_id"]

        below_threshold = fluence_engine.check_critical_mass(wave_id, penetration_rate=0.5)
        above_threshold = fluence_engine.check_critical_mass(wave_id, penetration_rate=0.7)

        assert not below_threshold["critical_mass_reached"]
        assert above_threshold["critical_mass_reached"]
        assert above_threshold["resonance_amplification"] > 1.0

    def test_check_critical_mass_wave_state_update(self, fluence_engine):
        """Test 3: check_critical_mass() - Mise  jour de l'tat de l'onde"""
        launch_result = fluence_engine.launch_propagation("test")
        wave_id = launch_result["wave_id"]

        # Vrifier tat initial
        wave = fluence_engine.propagation_waves[wave_id]
        assert not wave.critical_mass_reached

        # Atteindre la masse critique
        fluence_engine.check_critical_mass(wave_id, penetration_rate=0.7)

        # Vrifier que l'tat a t mis  jour
        wave = fluence_engine.propagation_waves[wave_id]
        assert wave.critical_mass_reached
        assert wave.resonance_factor > 1.0

    def test_register_threshold_basic_functionality(self, fluence_engine):
        """Test 1: register_threshold() - Fonctionnalit basique"""
        affected_systems = ["system1", "system2"]
        result = fluence_engine.register_threshold(0.8, affected_systems)

        assert "threshold_id" in result
        assert "threshold_value" in result
        assert result["threshold_value"] == 0.8
        assert "affected_systems" in result
        assert result["affected_systems"] == affected_systems
        assert result["registered"] is True

    def test_register_threshold_storage(self, fluence_engine):
        """Test 2: register_threshold() - Stockage"""
        initial_count = len(fluence_engine.thresholds)

        fluence_engine.register_threshold(0.6, ["sys1"])
        fluence_engine.register_threshold(0.9, ["sys2", "sys3"])

        assert len(fluence_engine.thresholds) == initial_count + 2

    def test_register_threshold_uniqueness(self, fluence_engine):
        """Test 3: register_threshold() - Unicit des IDs"""
        threshold1 = fluence_engine.register_threshold(0.7, ["sys1"])
        threshold2 = fluence_engine.register_threshold(0.7, ["sys2"])

        assert threshold1["threshold_id"] != threshold2["threshold_id"]
        assert threshold1["threshold_id"] in fluence_engine.thresholds
        assert threshold2["threshold_id"] in fluence_engine.thresholds

    def test_get_fluence_status_comprehensive(self, fluence_engine):
        """Test: get_fluence_status() - tat complet"""
        # Gnrer quelques donnes de test
        fluence_engine.launch_propagation("source1")
        fluence_engine.launch_propagation("source2")
        fluence_engine.register_threshold(0.8, ["sys1"])

        status = fluence_engine.get_fluence_status()

        assert "active_signals" in status
        assert "propagation_waves" in status
        assert "registered_thresholds" in status
        assert "critical_mass_threshold" in status
        assert "propagation_active" in status
        assert status["propagation_active"] is True
        assert status["active_signals"] >= 2
        assert status["registered_thresholds"] >= 1

    @patch('engines.fluence_engine.bus')
    def test_event_bus_integration(self, mock_bus, fluence_engine):
        """Test: Intgration avec le bus d'evenements"""
        fluence_engine.launch_propagation("test")
        fluence_engine.propagate_cycle(list(fluence_engine.active_signals.keys())[0])
        fluence_engine.check_critical_mass(list(fluence_engine.propagation_waves.keys())[0], 0.8)

        # Vrifier que les evenements ont t mis
        assert mock_bus.emit.call_count >= 3  # Au moins 3 evenements mis

    def test_propagation_constants_correctness(self, fluence_engine):
        """Test: Constantes de propagation correctes"""
        assert fluence_engine.SPEED_OF_THOUGHT == 7
        assert fluence_engine.CRITICAL_MASS_THRESHOLD == 0.618  # Nombre d'or
        assert fluence_engine.RESONANCE_AMPLIFICATION == 2.718  # Nombre d'Euler
        assert fluence_engine.ATTENUATION_FACTOR == 0.85

    def test_invalid_signal_handling(self, fluence_engine):
        """Test: Gestion des signaux invalides"""
        result = fluence_engine.propagate_cycle("invalid_signal_id")

        assert "error" in result
        assert result["error"] == "Signal inconnu"
        assert result["propagated"] is False