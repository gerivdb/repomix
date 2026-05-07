#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ TESTS TDD LENGTH VALUE ENGINE
Conforme standard NEXUS TDD v3.0

Invariant testé: L'attention est 1/sqrt(distance)
"""
import sys
import math
import numpy as np
import pytest

sys.path.insert(0, '.')
from engines.length_value_engine import LengthValueEngine


class TestLengthValueEngineTDD:
    """
    Tests TDD unitaires LENGTH VALUE ENGINE
    """

    def setup_method(self):
        self.engine = LengthValueEngine()

    def test_engine_initializes_correctly(self):
        """✅ TDD 1: Moteur initialise correctement"""
        status = self.engine.get_status()
        assert status["active"] is True
        assert status["semantic_weight"] == 0.0

    def test_attention_score_only_depends_on_distance(self):
        """✅ TDD 2: Score attention ne dépend QUE de la distance"""
        score1 = self.engine.attention_score(0, 5, "A", "B")
        score2 = self.engine.attention_score(0, 5, "XYZ", "1234")
        score3 = self.engine.attention_score(0, 5, None, None)

        # Même distance = même score, quelque soit la valeur
        assert score1 == score2 == score3

    def test_attention_score_decreases_with_distance(self):
        """✅ TDD 3: Score diminue avec la racine carrée de la distance"""
        score_1 = self.engine.attention_score(0, 1, "A", "B")
        score_4 = self.engine.attention_score(0, 4, "A", "B")

        assert np.isclose(score_4, score_1 / 2)

    def test_same_position_score_is_one(self):
        """✅ TDD 4: Score pour même position est exactement 1"""
        score = self.engine.attention_score(7, 7, "X", "Y")
        assert score == 1.0

    def test_semantic_contribution_is_zero(self):
        """✅ TDD 5: Contribution sémantique est nulle"""
        sequence = ["le", "chat", "est", "sur", "le", "tapis"]
        illusion = self.engine.is_semantic_illusion(sequence)
        assert illusion is True

    def test_attention_matrix_is_symmetric(self):
        """✅ TDD 6: Matrice d'attention est symétrique"""
        sequence = list(range(20))
        matrix = self.engine.weighted_attention(sequence)

        assert np.allclose(matrix, matrix.T)

    def test_invariant_equation_holds(self):
        """✅ TDD 7: L'invariant fondamental tient exactement"""
        for d in range(1, 100):
            score = self.engine.attention_score(0, d, "A", "B")
            expected = 1.0 / math.sqrt(d)
            assert np.isclose(score, expected, atol=1e-7)

    def test_all_scores_are_positive(self):
        """✅ TDD 8: Tous les scores sont positifs"""
        matrix = self.engine.weighted_attention(list(range(50)))
        assert np.all(matrix > 0.0)


if __name__ == "__main__":
    print("\n🧠 TESTS TDD LENGTH VALUE ENGINE")
    print("=" * 70)

    pytest.main([__file__, "-v", "-x"])