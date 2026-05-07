#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ TESTS TDD FLUID ENGINE EPIC-1181
Conforme standard NEXUS TDD v3.0

Spécifications testées:
  🧪 Détection rigidité excessive
  🌱 Alternatives polymorphes
  ⚖️ Équilibre rigidité / flexibilité
"""
import sys
import pytest

# Ajout chemin engines
sys.path.insert(0, '.')
from engines.fluid_engine import FluidEngine


class TestFluidEngineTDD:
    """
    Tests TDD unitaires FLUID ENGINE
    Conforme: EPIC-1181 TRIAD OPS
    """

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.fluid = FluidEngine()

    def test_initialization_uses_inverse_golden_ratio_threshold(self):
        """✅ TDD 1: Initialisation utilise l'inverse du nombre d'or comme seuil"""
        status = self.fluid.get_fluid_status()
        assert status["rigidity_threshold"] == 0.732
        assert status["fluid_mode_active"] is True

    def test_rigidity_detection_triggers_at_correct_threshold(self):
        """✅ TDD 2: Détection rigidité se déclenche au seuil exact"""
        # Juste en dessous seuil
        below = self.fluid.detect_rigidity("test", decision_stability=0.269)
        assert below["rigidity_excessive"] is False

        # Exactement au seuil
        exact = self.fluid.detect_rigidity("test", decision_stability=0.268)
        assert exact["rigidity_excessive"] is True

        # Au dessus seuil
        above = self.fluid.detect_rigidity("test", decision_stability=0.20)
        assert above["rigidity_excessive"] is True
        assert above["severity"] == "critical"

    def test_generate_alternatives_returns_exactly_three(self):
        """✅ TDD 3: Génération alternatives retourne exactement 3 variantes"""
        alternatives = self.fluid.generate_alternatives("test_decision")

        assert alternatives["alternatives_generated"] == 3
        assert len(alternatives["alternatives"]) == 3
        assert alternatives["total_flexibility_gain"] > 0.0

    def test_all_alternatives_have_high_equivalence(self):
        """✅ TDD 4: Toutes les alternatives ont un score d'équivalence > 0.9"""
        alternatives = self.fluid.generate_alternatives("test_decision")

        for alt in alternatives["alternatives"]:
            assert alt["equivalence"] >= 0.9
            assert alt["flexibility_gain"] > 0.0

    def test_adaptation_activation_works(self):
        """✅ TDD 5: Activation stratégie fonctionne"""
        strategy = self.fluid.activate_adaptation("test_strategy")

        assert strategy["activated"] is True
        assert strategy["flexibility_increased"] is True

        status = self.fluid.get_fluid_status()
        assert status["active_strategies"] == 1

    def test_status_returns_correct_metrics(self):
        """✅ TDD 6: État moteur retourne métriques correctes"""
        # Générer des opérations
        self.fluid.detect_rigidity("test1", 0.1)
        self.fluid.detect_rigidity("test2", 0.5)
        self.fluid.generate_alternatives("dec1")

        status = self.fluid.get_fluid_status()

        assert status["rigidity_detections"] == 2
        assert status["alternatives_generated"] == 3


if __name__ == "__main__":
    print("\n🧪 TESTS TDD FLUID ENGINE")
    print("=" * 60)

    pytest.main([__file__, "-v", "-x"])