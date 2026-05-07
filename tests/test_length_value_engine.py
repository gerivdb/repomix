"""
TESTS UNITAIRES: LENGTH VALUE ENGINE
EPIC-1191: Validation de l'invariant fondamental de l'attention

Tests complets pour le premier moteur au monde qui implémente
l'attention basée uniquement sur la longueur.
"""

import pytest
import numpy as np
from engines.length_value_engine import LengthValueEngine


class TestLengthValueEngine:

    def test_initialization(self):
        engine = LengthValueEngine()
        assert engine.active is True
        assert engine.TOKEN_DISTANCE_WEIGHT == 1.0
        assert engine.SEMANTIC_WEIGHT == 0.0

    def test_attention_score_diagonal(self):
        engine = LengthValueEngine()
        score = engine.attention_score(0, 0, "A", "A")
        assert score == 1.0

    def test_attention_score_distance(self):
        engine = LengthValueEngine()
        score = engine.attention_score(0, 1, "A", "B")
        expected = 1.0 / np.sqrt(1 + 1e-8)
        assert abs(score - expected) < 1e-6

    def test_weighted_attention_shape(self):
        engine = LengthValueEngine()
        sequence = ["A", "B", "C", "D", "E"]
        matrix = engine.weighted_attention(sequence)
        assert matrix.shape == (5, 5)

    def test_weighted_attention_diagonal(self):
        engine = LengthValueEngine()
        sequence = ["A", "B", "C"]
        matrix = engine.weighted_attention(sequence)
        assert np.allclose(np.diag(matrix), 1.0)

    def test_weighted_attention_symmetry(self):
        engine = LengthValueEngine()
        sequence = ["A", "B", "C", "D"]
        matrix = engine.weighted_attention(sequence)
        assert np.allclose(matrix, matrix.T)

    def test_semantic_illusion_detection(self):
        engine = LengthValueEngine()
        sequence = ["A", "B", "C"]
        assert engine.is_semantic_illusion(sequence) is True

    def test_universal_matrix_precompute(self):
        engine = LengthValueEngine()
        assert LengthValueEngine._universal_vector_cache is not None
        assert len(LengthValueEngine._universal_vector_cache) == LengthValueEngine.MAX_SEQUENCE_LENGTH

    def test_universal_attention_shape(self):
        engine = LengthValueEngine()
        matrix = engine.get_universal_attention(100)
        assert matrix.shape == (100, 100)

    def test_universal_attention_diagonal(self):
        engine = LengthValueEngine()
        matrix = engine.get_universal_attention(50)
        assert np.allclose(np.diag(matrix), 1.0)

    def test_universal_attention_distance_decay(self):
        engine = LengthValueEngine()
        matrix = engine.get_universal_attention(20)
        # Check that attention decreases with distance (strict for d>=2, since d=1 gives 1.0)
        for i in range(10):
            for d in range(2, 10):
                if i + d < 20:
                    assert matrix[i, i] > matrix[i, i + d]

    def test_cache_size(self):
        engine = LengthValueEngine()
        status = engine.get_status()
        assert status["cache_size_kb"] > 0
        assert status["cache_size_kb"] < 300  # Should be ~256KB

    def test_max_sequence_length(self):
        assert LengthValueEngine.MAX_SEQUENCE_LENGTH == 131072

    def test_status_functionality(self):
        engine = LengthValueEngine()
        status = engine.get_status()
        assert status["active"] is True
        assert status["invariant"] == "attention = 1/sqrt(distance)"
        assert status["status"] == "✅ FONCTIONNEL"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])