import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from cli_anything_engine.entity_evaluator import (
    EntityEvaluator, Entity, EligibilityScore, CodeAnalyzer,
    UtilityScorer, MaturityAssessor
)
from . import assert_eligibility_score

class TestCodeAnalyzer:
    """Tests pour CodeAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        return CodeAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_python_repo(self, analyzer):
        """Test analyse dépôt Python"""
        result = await analyzer.analyze_repository(
            "https://github.com/gerivdb/test-python-repo", "python"
        )

        assert isinstance(result, dict)
        assert "public_functions" in result
        assert "classes" in result
        assert "test_coverage_estimate" in result
        assert isinstance(result["public_functions"], int)
        assert result["public_functions"] >= 0

    @pytest.mark.asyncio
    async def test_analyze_javascript_repo(self, analyzer):
        """Test analyse dépôt JavaScript"""
        result = await analyzer.analyze_repository(
            "https://github.com/gerivdb/test-js-repo", "javascript"
        )

        assert isinstance(result, dict)
        assert "public_functions" in result
        assert "imports" in result

    @pytest.mark.asyncio
    async def test_analyze_unsupported_language(self, analyzer):
        """Test langue non supportée"""
        result = await analyzer.analyze_repository(
            "https://github.com/gerivdb/test-repo", "cobol"
        )

        assert isinstance(result, dict)
        assert "error" in result
        assert "non supporté" in result["error"].lower()

class TestUtilityScorer:
    """Tests pour UtilityScorer"""

    @pytest.fixture
    def gateway_config(self):
        return {
            "url": "http://localhost:8002",
            "default_model": "claude-3-sonnet",
            "max_tokens": 4000
        }

    @pytest.fixture
    def scorer(self, gateway_config):
        return UtilityScorer(gateway_config)

    @pytest.mark.asyncio
    async def test_score_high_utility_entity(self, scorer):
        """Test scoring entité haute utilité"""
        entity = Entity(
            id="test-high-utility",
            name="APIManager",
            type="service",
            url="https://github.com/gerivdb/api-manager",
            language="python",
            dependencies=["nexus"],
            description="REST API manager for distributed systems"
        )

        code_analysis = {
            "public_functions": 25,
            "test_coverage_estimate": 0.85,
            "complexity_score": 0.3
        }

        score = await scorer.score_agent_utility(entity, code_analysis)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.7  # Haute utilité attendue

    @pytest.mark.asyncio
    async def test_score_low_utility_entity(self, scorer):
        """Test scoring entité basse utilité"""
        entity = Entity(
            id="test-low-utility",
            name="LegacyScript",
            type="script",
            url="https://github.com/gerivdb/legacy-script",
            language="python",
            dependencies=["old-lib"],
            description="Legacy maintenance script"
        )

        code_analysis = {
            "public_functions": 2,
            "test_coverage_estimate": 0.1,
            "complexity_score": 0.9
        }

        score = await scorer.score_agent_utility(entity, code_analysis)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Basse utilité attendue

class TestMaturityAssessor:
    """Tests pour MaturityAssessor"""

    @pytest.fixture
    def assessor(self):
        return MaturityAssessor()

    @pytest.mark.asyncio
    async def test_assess_mature_entity(self, assessor):
        """Test évaluation entité mature"""
        entity = Entity(
            id="test-mature",
            name="MatureService",
            type="service",
            url="https://github.com/gerivdb/mature-service",
            language="python",
            dependencies=["nexus", "kiva", "ontology"],
            description="Well documented service with README"
        )

        score = await assessor.assess_maturity(entity)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.7  # Maturité élevée attendue

    @pytest.mark.asyncio
    async def test_assess_immature_entity(self, assessor):
        """Test évaluation entité immature"""
        entity = Entity(
            id="test-immature",
            name="NewScript",
            type="script",
            url="https://github.com/gerivdb/new-script",
            language="python",
            dependencies=[],
            description="New experimental script"
        )

        score = await assessor.assess_maturity(entity)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # Score peut être plus bas

class TestEntityEvaluator:
    """Tests pour EntityEvaluator"""

    @pytest.fixture
    def config(self):
        from cli_anything_engine.config import CLIAnythingConfig
        config = CLIAnythingConfig()
        config.evaluation_timeout = 5  # Tests rapides
        return config

    @pytest.fixture
    def evaluator(self, config):
        return EntityEvaluator(config)

    @pytest.mark.asyncio
    async def test_evaluate_eligible_entity(self, evaluator):
        """Test évaluation entité éligible"""
        entity = Entity(
            id="test-eligible",
            name="EligibleService",
            type="service",
            url="https://github.com/gerivdb/eligible-service",
            language="python",
            dependencies=["nexus", "kiva", "ontology"],
            description="REST API service with comprehensive documentation"
        )

        score = await evaluator.evaluate_eligibility(entity)

        assert_eligibility_score(score, expected_recommended=True, min_score=0.6)

        # Vérifier métriques mises à jour
        metrics = evaluator.get_metrics()
        assert metrics["evaluations_performed"] == 1
        assert isinstance(metrics["avg_evaluation_time"], float)

    @pytest.mark.asyncio
    async def test_evaluate_ineligible_entity(self, evaluator):
        """Test évaluation entité inéligible"""
        entity = Entity(
            id="test-ineligible",
            name="IneligibleScript",
            type="script",
            url="https://github.com/gerivdb/ineligible-script",
            language="unknown",
            dependencies=[],
            description="Simple script"
        )

        score = await evaluator.evaluate_eligibility(entity)

        assert_eligibility_score(score, expected_recommended=False)

        # Vérifier que c'est marqué non recommandé
        assert not score.recommended
        assert "non supporté" in score.reasoning.lower()

    @pytest.mark.asyncio
    async def test_cache_functionality(self, evaluator):
        """Test fonctionnalité cache"""
        entity = Entity(
            id="test-cache",
            name="CacheTest",
            type="service",
            url="https://github.com/gerivdb/cache-test",
            language="python",
            dependencies=["nexus"],
            description="Test cache functionality"
        )

        # Première évaluation
        score1 = await evaluator.evaluate_eligibility(entity)
        assert score1 is not None

        # Deuxième évaluation (devrait utiliser cache)
        score2 = await evaluator.evaluate_eligibility(entity)
        assert score2 is not None

        # Vérifier que c'est le même objet (cache)
        assert score1 is score2

        # Métriques
        metrics = evaluator.get_metrics()
        assert metrics["evaluations_performed"] == 2
        assert metrics["cache_hit_rate"] > 0

    @pytest.mark.asyncio
    @patch('cli_anything_engine.entity_evaluator.CodeAnalyzer.analyze_repository')
    async def test_error_handling(self, mock_analyze, evaluator):
        """Test gestion d'erreurs"""
        # Simuler erreur dans analyse
        mock_analyze.side_effect = Exception("Test error")

        entity = Entity(
            id="test-error",
            name="ErrorTest",
            type="service",
            url="https://github.com/gerivdb/error-test",
            language="python",
            dependencies=[],
            description="Test error handling"
        )

        score = await evaluator.evaluate_eligibility(entity)

        assert_eligibility_score(score, expected_recommended=False)
        assert "erreur" in score.reasoning.lower()

    def test_metrics_initialization(self, evaluator):
        """Test initialisation métriques"""
        metrics = evaluator.get_metrics()

        expected_keys = [
            "evaluations_performed",
            "cache_hit_rate",
            "avg_evaluation_time"
        ]

        for key in expected_keys:
            assert key in metrics
            assert isinstance(metrics[key], (int, float))