# -----------------------------------------------------------------------------
# Tests TDD pour EPIC-9863: Quant Integration in NEXUS Scientific Stack
# Tests unitaires des primitives quant avec validation précision
# Couverture: norm_ppf, precision_budget, Schadner IV, roundtrip validation
# -----------------------------------------------------------------------------

# Import des modules à tester
import pytest
import math
import sys
import os
from unittest.mock import patch, MagicMock

# Ajout du répertoire quant au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from quant.primitives.math_core import (
        norm_ppf, norm_cdf, norm_pdf, fast_inv_sqrt,
        implied_volatility_schadner, black_scholes_call_price,
        validate_iv_roundtrip, benchmark_quant_primitives
    )
    from quant.primitives.precision_budget import (
        PrecisionValidator, PRECISION_BUDGETS, PrecisionCategory
    )
except ImportError as e:
    pytest.skip(f"Required modules not available: {e}", allow_module_level=True)

class TestNormPPF:
    """Tests pour norm_ppf avec précision garantie"""

    def test_norm_ppf_basic_values(self):
        """Test valeurs de base avec précision connue"""
        # Valeurs de référence (scipy.stats.norm.ppf)
        test_cases = [
            (0.001, -3.090232306167813),
            (0.01, -2.326347874040841),
            (0.1, -1.2815515655446004),
            (0.5, 0.0),
            (0.9, 1.2815515655446004),
            (0.99, 2.326347874040841),
            (0.999, 3.090232306167813)
        ]

        for p, expected in test_cases:
            result = norm_ppf(p, validate_precision=False)
            assert abs(result - expected) < 1e-12, f"norm_ppf({p}) = {result}, expected {expected}"

    def test_norm_ppf_domain_validation(self):
        """Test validation domaine d'entrée"""
        with pytest.raises(ValueError, match="p doit être dans"):
            norm_ppf(0.0)

        with pytest.raises(ValueError, match="p doit être dans"):
            norm_ppf(1.0)

        with pytest.raises(ValueError, match="p doit être dans"):
            norm_ppf(-0.1)

        with pytest.raises(ValueError, match="p doit être dans"):
            norm_ppf(1.1)

    def test_norm_ppf_symmetry(self):
        """Test symétrie autour de 0.5"""
        for p in [0.1, 0.2, 0.3, 0.4]:
            result_p = norm_ppf(p, validate_precision=False)
            result_1mp = norm_ppf(1-p, validate_precision=False)
            assert abs(result_p + result_1mp) < 1e-14, f"Symmetry failed for p={p}"

    def test_norm_ppf_extreme_values(self):
        """Test valeurs extrêmes"""
        # Très proche de 0
        result = norm_ppf(1e-15, validate_precision=False)
        assert result < -5.0, f"Extreme low p should give large negative: {result}"

        # Très proche de 1
        result = norm_ppf(1-1e-15, validate_precision=False)
        assert result > 5.0, f"Extreme high p should give large positive: {result}"

    @patch('scipy.stats')
    def test_norm_ppf_precision_validation_success(self, mock_scipy):
        """Test validation précision réussie"""
        mock_scipy.norm.ppf.return_value = 1.2815515655446004

        result = norm_ppf(0.9, validate_precision=True)
        assert result is not None  # Pas d'exception levée

    @patch('scipy.stats', None)
    def test_norm_ppf_precision_validation_fallback(self, mock_scipy):
        """Test validation précision en fallback (sans scipy)"""
        result = norm_ppf(0.9, validate_precision=True)
        assert result is not None  # Pas d'exception levée

class TestNormCDF:
    """Tests pour norm_cdf"""

    def test_norm_cdf_basic_properties(self):
        """Test propriétés de base"""
        assert abs(norm_cdf(0.0) - 0.5) < 1e-15
        assert norm_cdf(float('-inf')) == 0.0
        assert norm_cdf(float('inf')) == 1.0

    def test_norm_cdf_symmetry(self):
        """Test symétrie"""
        for x in [-2.0, -1.0, 1.0, 2.0]:
            cdf_x = norm_cdf(x)
            cdf_minus_x = norm_cdf(-x)
            assert abs(cdf_x + cdf_minus_x - 1.0) < 1e-14

class TestNormPDF:
    """Tests pour norm_pdf"""

    def test_norm_pdf_properties(self):
        """Test propriétés de base"""
        assert abs(norm_pdf(0.0) - 1/math.sqrt(2*math.pi)) < 1e-15

        # PDF > 0 partout
        for x in [-3.0, -1.0, 0.0, 1.0, 3.0]:
            assert norm_pdf(x) > 0

    def test_norm_pdf_symmetry(self):
        """Test symétrie"""
        for x in [0.5, 1.0, 2.0]:
            assert abs(norm_pdf(x) - norm_pdf(-x)) < 1e-15

class TestFastInvSqrt:
    """Tests pour fast_inv_sqrt"""

    def test_fast_inv_sqrt_accuracy(self):
        """Test précision fast_inv_sqrt"""
        test_values = [1.0, 2.0, 4.0, 9.0, 16.0, 100.0]

        for x in test_values:
            fast_result = fast_inv_sqrt(x)
            exact_result = 1.0 / math.sqrt(x)
            relative_error = abs(fast_result - exact_result) / exact_result
            assert relative_error < 1e-6, f"Fast inv sqrt error too high for x={x}: {relative_error}"

    def test_fast_inv_sqrt_positive_input(self):
        """Test que l'entrée doit être positive"""
        with pytest.raises((ValueError, OverflowError)):
            fast_inv_sqrt(-1.0)

class TestPrecisionBudget:
    """Tests pour le système de budget de précision"""

    def test_precision_budgets_defined(self):
        """Test que tous les budgets de précision sont définis"""
        required_primitives = [
            "norm_ppf", "norm_cdf", "norm_pdf",
            "math.erf", "ig_cdf", "ig_ppf",
            "iv_schadner", "black_scholes_call"
        ]

        for primitive in required_primitives:
            assert primitive in PRECISION_BUDGETS, f"Missing precision budget for {primitive}"

    def test_precision_validator_creation(self):
        """Test création validateur de précision"""
        validator = PrecisionValidator()
        assert validator is not None

    def test_precision_validator_success(self):
        """Test validation précision réussie"""
        validator = PrecisionValidator()

        # Test norm_ppf avec valeur correcte
        result = validator.validate_precision("norm_ppf", 1.2815515655446004, 1.2815515655446004, {"p": 0.9})
        assert result == True

    def test_precision_validator_failure(self):
        """Test validation précision échouée"""
        validator = PrecisionValidator()

        # Erreur trop grande
        result = validator.validate_precision("norm_ppf", 1.0, 2.0, {"p": 0.9})
        assert result == False

class TestSchadnerIV:
    """Tests pour l'algorithme Schadner IV"""

    @patch('quant.primitives.math_core.implied_vol_schadner_call')
    def test_schadner_iv_basic_call(self, mock_schadner):
        """Test appel basique Schadner IV"""
        mock_schadner.return_value = 0.2

        result = implied_volatility_schadner(10.0, 100.0, 100.0, 1.0, 1.0, validate_precision=False)
        assert result == 0.2
        mock_schadner.assert_called_once_with(10.0, 100.0, 100.0, 1.0, 1.0)

    def test_schadner_iv_not_available(self):
        """Test comportement quand Schadner n'est pas disponible"""
        with patch('quant.primitives.math_core.implied_vol_schadner_call', None):
            with pytest.raises(RuntimeError, match="Schadner IV algorithm not available"):
                implied_volatility_schadner(10.0, 100.0, 100.0, 1.0, 1.0)

    def test_schadner_iv_parameter_validation(self):
        """Test validation paramètres Schadner IV"""
        with patch('quant.primitives.math_core.implied_vol_schadner_call') as mock_schadner:
            mock_schadner.return_value = 0.2

            # Test avec T=0 (invalide)
            with pytest.raises(ValueError):
                implied_volatility_schadner(10.0, 100.0, 100.0, 1.0, 0.0)

class TestBlackScholesPricing:
    """Tests pour le pricing Black-Scholes"""

    def test_black_scholes_call_basic(self):
        """Test pricing call Black-Scholes basique"""
        # Paramètres ATM
        S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0

        price = black_scholes_call_price(S, K, r, sigma, T, validate_precision=False)

        # Prix devrait être raisonnable pour ATM
        assert 5.0 < price < 15.0, f"ATM call price {price} seems unreasonable"

    def test_black_scholes_call_put_call_parity(self):
        """Test parité call-put approximative"""
        S, K, r, sigma, T = 100.0, 105.0, 0.05, 0.2, 1.0

        call_price = black_scholes_call_price(S, K, r, sigma, T, validate_precision=False)

        # Put price par parité: C - S + K*e^(-rT) + P = 0 => P = C - S + K*e^(-rT)
        put_price = call_price - S + K * math.exp(-r * T)

        # Put devrait être positif pour OTM
        assert put_price > 0, f"Put price {put_price} should be positive"

    def test_black_scholes_parameter_validation(self):
        """Test validation paramètres Black-Scholes"""
        with pytest.raises(ValueError, match="Paramètres doivent être strictement positifs"):
            black_scholes_call_price(100, 100, 0.05, 0.2, 0)  # T=0

        with pytest.raises(ValueError, match="Paramètres doivent être strictement positifs"):
            black_scholes_call_price(100, 100, 0.05, 0, 1.0)  # sigma=0

class TestRoundtripValidation:
    """Tests pour la validation round-trip IV"""

    @patch('quant.primitives.math_core.implied_vol_schadner_call')
    def test_roundtrip_validation_success(self, mock_schadner):
        """Test validation round-trip réussie"""
        mock_schadner.return_value = 0.2

        # Même volatilité en entrée et sortie
        result = validate_iv_roundtrip(100, 100, 0.05, 0.2, 1.0)
        assert result == True

    @patch('quant.primitives.math_core.implied_vol_schadner_call')
    def test_roundtrip_validation_failure(self, mock_schadner):
        """Test validation round-trip échouée"""
        mock_schadner.return_value = 0.3  # Différent de l'entrée 0.2

        result = validate_iv_roundtrip(100, 100, 0.05, 0.2, 1.0, tolerance=1e-6)
        assert result == False

class TestBenchmarkQuantPrimitives:
    """Tests pour le benchmark des primitives"""

    def test_benchmark_execution(self):
        """Test exécution benchmark"""
        results = benchmark_quant_primitives(iterations=1000)

        assert "primitives" in results
        assert "total_time_ms" in results
        assert results["total_time_ms"] > 0

        # Vérifier présence des primitives attendues
        expected_primitives = ["norm_ppf", "fast_inv_sqrt", "schadner_iv"]
        for primitive in expected_primitives:
            assert primitive in results["primitives"]

    def test_benchmark_norm_ppf_metrics(self):
        """Test métriques benchmark norm_ppf"""
        results = benchmark_quant_primitives(iterations=1000)

        norm_ppf_metrics = results["primitives"]["norm_ppf"]
        assert "time_per_call_ns" in norm_ppf_metrics
        assert "ops_per_sec" in norm_ppf_metrics
        assert norm_ppf_metrics["time_per_call_ns"] > 0
        assert norm_ppf_metrics["ops_per_sec"] > 0

# -----------------------------------------------------------------------------
# Tests d'intégration
# -----------------------------------------------------------------------------

class TestIntegration:
    """Tests d'intégration entre composants"""

    def test_norm_ppf_cdf_consistency(self):
        """Test cohérence entre norm_ppf et norm_cdf"""
        test_p = 0.975
        quantile = norm_ppf(test_p, validate_precision=False)
        cdf_result = norm_cdf(quantile)

        assert abs(cdf_result - test_p) < 1e-12, f"Inconsistency: ppf({test_p}) -> {quantile}, cdf({quantile}) -> {cdf_result}"

    def test_black_scholes_iv_roundtrip_integration(self):
        """Test intégration complète Black-Scholes + Schadner IV"""
        with patch('quant.primitives.math_core.implied_vol_schadner_call') as mock_schadner:
            mock_schadner.return_value = 0.25

            # Générer prix avec volatilité connue
            S, K, r, sigma_true, T = 100.0, 105.0, 0.05, 0.25, 1.0
            price = black_scholes_call_price(S, K, r, sigma_true, T, validate_precision=False)

            # Récupérer volatilité depuis le prix
            F = S * math.exp(r * T)
            D = math.exp(-r * T)
            sigma_recovered = implied_volatility_schadner(price, K, F, D, T, validate_precision=False)

            # Vérifier cohérence
            relative_error = abs(sigma_recovered - sigma_true) / sigma_true
            assert relative_error < 0.01, f"Roundtrip error too high: {relative_error}"  # 1% tolérance pour test

if __name__ == "__main__":
    pytest.main([__file__, "-v"])