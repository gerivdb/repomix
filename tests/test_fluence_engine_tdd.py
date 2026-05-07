#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ TESTS TDD FLUENCE ENGINE EPIC-1180
Conforme standard NEXUS TDD v3.0

Spécifications testées:
  🌊 Propagation onde physique
  ⚡ Masse critique nombre d'or
  📡 Résonance et amplification
  🎯 Effets de seuil systémique
"""
import sys
import pytest

# Ajout chemin engines
sys.path.insert(0, '.')
from engines.fluence_engine import FluenceEngine


class TestFluenceEngineTDD:
    """
    Tests TDD unitaires FLUENCE ENGINE
    Conforme: EPIC-1180 PERTURBATION LAYER
    """

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.fluence = FluenceEngine()

    def test_initialization_critical_mass_constant(self):
        """✅ TDD 1: Initialisation utilise nombre d'or pour seuil critique"""
        status = self.fluence.get_fluence_status()
        assert status["critical_mass_threshold"] == 0.618
        assert status["propagation_active"] is True

    def test_launch_propagation_returns_valid_structure(self):
        """✅ TDD 2: Lancement propagation retourne structure correcte"""
        propagation = self.fluence.launch_propagation("test_module", initial_amplitude=1.0)

        assert "signal_id" in propagation
        assert "wave_id" in propagation
        assert propagation["initial_amplitude"] == 1.0
        assert propagation["propagation_active"] is True
        assert len(propagation["signal_id"]) == 36

    def test_propagation_cycle_attenuation_works(self):
        """✅ TDD 3: Cycle propagation applique atténuation correcte"""
        propagation = self.fluence.launch_propagation("test", initial_amplitude=1.0)

        result = self.fluence.propagate_cycle(propagation["signal_id"])

        assert result["distance_travelled"] == 1
        assert 0.7 <= result["current_amplitude"] <= 1.3  # Atténuation + bonus résonance
        assert result["propagation_continues"] is True

    def test_critical_mass_triggers_at_golden_ratio(self):
        """✅ TDD 4: Masse critique se déclenche exactement au nombre d'or"""
        propagation = self.fluence.launch_propagation("test")

        # Juste en dessous seuil
        below = self.fluence.check_critical_mass(propagation["wave_id"], penetration_rate=0.617)
        assert below["critical_mass_reached"] is False

        # Exactement au seuil
        exact = self.fluence.check_critical_mass(propagation["wave_id"], penetration_rate=0.618)
        assert exact["critical_mass_reached"] is True

        # Au dessus seuil
        above = self.fluence.check_critical_mass(propagation["wave_id"], penetration_rate=0.75)
        assert above["critical_mass_reached"] is True
        assert above["resonance_amplification"] == 2.718  # Nombre Euler

    def test_threshold_registration_works(self):
        """✅ TDD 5: Enregistrement seuil fonctionne"""
        threshold = self.fluence.register_threshold(0.8, ["system1", "system2"])

        assert threshold["registered"] is True
        assert threshold["threshold_value"] == 0.8
        assert len(threshold["affected_systems"]) == 2

        status = self.fluence.get_fluence_status()
        assert status["registered_thresholds"] == 1

    def test_propagation_eventually_extinguishes(self):
        """✅ TDD 6: Propagation s'éteint après suffisamment de cycles"""
        propagation = self.fluence.launch_propagation("test", initial_amplitude=1.0)

        extinguishes = False
        for _ in range(50):
            result = self.fluence.propagate_cycle(propagation["signal_id"])
            if not result["propagation_continues"]:
                extinguishes = True
                break

        assert extinguishes is True


if __name__ == "__main__":
    print("\n🧪 TESTS TDD FLUENCE ENGINE")
    print("=" * 60)

    pytest.main([__file__, "-v", "-x"])