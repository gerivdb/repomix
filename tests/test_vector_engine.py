"""
Tests for VECTOR ENGINE - 3 niveaux de test E2E

Conformément à PATTERN-0025: Always Test This
"""

import pytest
import time
from src.engines.vector_engine import (
    VectorEngine, Intent, State, Drift, Vector,
    DriftSeverity
)


class TestVectorEngineUnit:
    """Tests unitaires - Niveau 1"""

    def test_initialization(self):
        """Test création et état initial"""
        engine = VectorEngine()
        assert engine.current_intent is None
        assert engine.last_drift is None
        assert len(engine.correction_history) == 0

    def test_set_destination(self):
        """Test déclaration de destination"""
        engine = VectorEngine()
        intent = Intent(
            name="test_intent",
            description="Test intention",
            target_metrics={"cpu": 80, "memory": 70}
        )

        engine.set_destination(intent)
        assert engine.current_intent == intent
        assert engine.last_drift is None

    def test_measure_drift_no_destination(self):
        """Test mesure dérive sans destination"""
        engine = VectorEngine()
        state = State(metrics={"cpu": 90}, timestamp=time.time())

        drift = engine.measure_drift(state)
        assert drift.magnitude == 0.0
        assert drift.severity == DriftSeverity.NONE
        assert drift.details["error"] == "no_destination_set"

    def test_measure_drift_perfect_alignment(self):
        """Test mesure dérive parfaite"""
        engine = VectorEngine()
        intent = Intent(
            name="perfect",
            description="Parfait alignement",
            target_metrics={"cpu": 80, "memory": 70}
        )
        engine.set_destination(intent)

        state = State(
            metrics={"cpu": 80, "memory": 70},
            timestamp=time.time()
        )

        drift = engine.measure_drift(state)
        assert drift.magnitude == 0.0
        assert drift.severity == DriftSeverity.NONE
        assert all(abs(v) < 0.001 for v in drift.direction.values())

    def test_measure_drift_with_deviation(self):
        """Test mesure dérive avec écart"""
        engine = VectorEngine()
        intent = Intent(
            name="deviation",
            description="Écart test",
            target_metrics={"cpu": 80, "memory": 70}
        )
        engine.set_destination(intent)

        state = State(
            metrics={"cpu": 90, "memory": 60},  # +12.5%, -14.3%
            timestamp=time.time()
        )

        drift = engine.measure_drift(state)
        assert drift.magnitude > 0
        assert drift.severity in [DriftSeverity.MINOR, DriftSeverity.MODERATE]
        assert "cpu" in drift.direction
        assert "memory" in drift.direction
        assert drift.direction["cpu"] > 0  # Current > target
        assert drift.direction["memory"] < 0  # Current < target

    def test_calculate_correction_no_drift(self):
        """Test calcul correction sans dérive"""
        engine = VectorEngine()
        vector = engine.calculate_correction()
        assert vector is None

    def test_calculate_correction_with_drift(self):
        """Test calcul correction avec dérive"""
        engine = VectorEngine()
        intent = Intent(
            name="correction_test",
            description="Test correction",
            target_metrics={"metric1": 100}
        )
        engine.set_destination(intent)

        state = State(
            metrics={"metric1": 120},  # +20% drift
            timestamp=time.time()
        )

        # Measure drift first
        drift = engine.measure_drift(state)
        assert drift.magnitude > 0

        # Calculate correction
        vector = engine.calculate_correction()
        assert vector is not None
        assert isinstance(vector, Vector)
        assert "metric1" in vector.direction
        assert vector.direction["metric1"] < 0  # Opposite to drift
        assert vector.amplitude > 0
        assert 0 <= vector.urgency <= 1
        assert len(vector.justification) > 0
        assert len(vector.actions) > 0


class TestVectorEngineIntegration:
    """Tests d'intégration - Niveau 2"""

    def test_full_correction_workflow(self):
        """Test workflow complet de correction"""
        engine = VectorEngine()

        # 1. Set destination
        intent = Intent(
            name="workflow_test",
            description="Test workflow complet",
            target_metrics={
                "performance": 95,
                "reliability": 99,
                "efficiency": 85
            }
        )
        engine.set_destination(intent)

        # 2. Simulate drifted state
        state = State(
            metrics={
                "performance": 85,  # -10.5%
                "reliability": 95,  # -4.0%
                "efficiency": 92    # +8.2%
            },
            timestamp=time.time()
        )

        # 3. Measure drift
        drift = engine.measure_drift(state)
        assert drift.magnitude > 0
        assert drift.severity != DriftSeverity.NONE

        # 4. Calculate correction
        vector = engine.calculate_correction()
        assert vector is not None

        # 5. Verify correction history
        assert len(engine.correction_history) == 1
        assert engine.correction_history[0] == vector

    def test_multiple_measurements(self):
        """Test mesures multiples avec évolution"""
        engine = VectorEngine()

        intent = Intent(
            name="evolution_test",
            description="Test évolution",
            target_metrics={"score": 100}
        )
        engine.set_destination(intent)

        # First measurement - drifted
        state1 = State(metrics={"score": 120}, timestamp=time.time())
        drift1 = engine.measure_drift(state1)
        assert drift1.magnitude > 0

        # Second measurement - more drifted
        state2 = State(metrics={"score": 150}, timestamp=time.time() + 1)
        drift2 = engine.measure_drift(state2)
        assert drift2.magnitude > drift1.magnitude

        # Third measurement - better
        state3 = State(metrics={"score": 90}, timestamp=time.time() + 2)
        drift3 = engine.measure_drift(state3)
        assert drift3.magnitude < drift2.magnitude

    def test_drift_severity_progression(self):
        """Test progression des sévérités de dérive"""
        engine = VectorEngine()

        intent = Intent(
            name="severity_test",
            description="Test sévérité",
            target_metrics={"value": 100}
        )
        engine.set_destination(intent)

        test_cases = [
            (100, DriftSeverity.NONE),      # Perfect
            (105, DriftSeverity.MINOR),     # Small drift
            (125, DriftSeverity.MODERATE),  # Medium drift
            (150, DriftSeverity.MAJOR),     # Large drift
            (200, DriftSeverity.CRITICAL),  # Critical drift
        ]

        for target_value, expected_severity in test_cases:
            state = State(
                metrics={"value": target_value},
                timestamp=time.time()
            )
            drift = engine.measure_drift(state)
            assert drift.severity == expected_severity, f"Failed for value {target_value}"


class TestVectorEngineE2E:
    """Tests E2E - Niveau 3"""

    def test_system_convergence_scenario(self):
        """Test scénario complet de convergence systémique"""
        engine = VectorEngine()

        # Define system intent
        intent = Intent(
            name="system_optimization",
            description="Optimisation complète du système",
            target_metrics={
                "cpu_usage": 70,
                "memory_usage": 60,
                "response_time": 100,  # ms
                "error_rate": 0.001,  # 0.1%
                "throughput": 1000    # req/sec
            }
        )
        engine.set_destination(intent)

        # Simulate initial degraded state
        initial_state = State(
            metrics={
                "cpu_usage": 95,      # +35.7%
                "memory_usage": 85,   # +41.7%
                "response_time": 250, # +150%
                "error_rate": 0.05,   # +4900%
                "throughput": 500     # -50%
            },
            timestamp=time.time()
        )

        # Measure initial drift
        initial_drift = engine.measure_drift(initial_state)
        assert initial_drift.severity == DriftSeverity.CRITICAL

        # Calculate correction
        correction_vector = engine.calculate_correction()
        assert correction_vector is not None
        assert correction_vector.urgency > 0.8  # High urgency
        assert len(correction_vector.actions) > 0

        # Simulate partial correction
        partial_state = State(
            metrics={
                "cpu_usage": 80,      # +14.3%
                "memory_usage": 70,   # +16.7%
                "response_time": 150, # +50%
                "error_rate": 0.0012,  # +20% (improved from 4900%)
                "throughput": 750     # -25%
            },
            timestamp=time.time() + 60  # 1 minute later
        )

        partial_drift = engine.measure_drift(partial_state)
        assert partial_drift.severity == DriftSeverity.MAJOR  # Improved
        assert partial_drift.magnitude < initial_drift.magnitude

        # Final convergence
        final_state = State(
            metrics={
                "cpu_usage": 72,      # +2.9%
                "memory_usage": 62,   # +3.3%
                "response_time": 105, # +5%
                "error_rate": 0.00105, # +5%
                "throughput": 980     # -2%
            },
            timestamp=time.time() + 120  # 2 minutes later
        )

        final_drift = engine.measure_drift(final_state)
        assert final_drift.severity in [DriftSeverity.MINOR, DriftSeverity.MODERATE]
        assert final_drift.magnitude < partial_drift.magnitude

    def test_adaptive_correction_over_time(self):
        """Test adaptation des corrections sur longue période"""
        engine = VectorEngine()

        intent = Intent(
            name="adaptive_test",
            description="Test adaptation temporelle",
            target_metrics={"stability": 100}
        )
        engine.set_destination(intent)

        # Simulate oscillating system
        timeline = [
            (95, "minor deviation"),
            (110, "moderate drift"),
            (85, "opposite deviation"),
            (105, "returning to drift"),
            (98, "near convergence"),
            (102, "final approach"),
        ]

        corrections = []
        severities = []

        for i, (value, description) in enumerate(timeline):
            state = State(
                metrics={"stability": value},
                timestamp=time.time() + i * 10
            )

            drift = engine.measure_drift(state)
            severities.append(drift.severity)

            vector = engine.calculate_correction()
            if vector:
                corrections.append(vector.amplitude)

        # Verify adaptation pattern
        assert len(corrections) > 0
        assert severities[0] != DriftSeverity.NONE  # Started with deviation
        assert severities[-1] in [DriftSeverity.NONE, DriftSeverity.MINOR]  # Ended closer

        # Corrections should vary based on drift magnitude
        assert len(set(corrections)) > 1  # Not all corrections identical

    def test_multi_metric_system_stress(self):
        """Test système multi-métriques sous stress"""
        engine = VectorEngine()

        # Complex system with many metrics
        intent = Intent(
            name="complex_system",
            description="Système complexe multi-métriques",
            target_metrics={
                f"metric_{i}": 100 + i * 5 for i in range(20)  # 20 metrics
            }
        )
        engine.set_destination(intent)

        # Stress test: all metrics deviated
        stress_metrics = {
            f"metric_{i}": 100 + i * 5 + (i % 3 - 1) * 20  # Varied deviations
            for i in range(20)
        }

        stress_state = State(
            metrics=stress_metrics,
            timestamp=time.time()
        )

        # Measure system-wide drift
        drift = engine.measure_drift(stress_state)
        assert drift.magnitude > 0
        assert len(drift.direction) == 20  # All metrics measured

        # Calculate correction for complex system
        vector = engine.calculate_correction()
        assert vector is not None
        assert len(vector.direction) == 20  # Correction for all metrics
        assert vector.urgency > 0.5  # Significant urgency
        assert len(vector.actions) >= 13  # Actions for deviated metrics (some have 0 drift)

        # Verify correction opposes drift
        for metric in stress_metrics:
            if metric in drift.direction and abs(drift.direction[metric]) > 0.1:
                assert metric in vector.direction
                # Correction should oppose drift direction
                assert (vector.direction[metric] > 0) != (drift.direction[metric] > 0)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])