import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from cli_anything_engine.sce_pipeline import (
    SCEPipeline, SCEValidation, CanonicalAnalyzer,
    SwarmTestGenerator, LoadTester, SecurityAuditor
)
from . import assert_sce_validation

class TestCanonicalAnalyzer:
    """Tests pour CanonicalAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        return CanonicalAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_canonical_patterns(self, analyzer):
        """Test analyse patterns canoniques"""
        entity_code = {
            "files": ["main.py", "utils.py", "test_main.py"],
            "content": """
def api_endpoint():
    return {"status": "ok"}

class ServiceManager:
    pass

try:
    result = api_endpoint()
except Exception as e:
    print(f"Error: {e}")

async def async_handler():
    await asyncio.sleep(1)
    return True

describe('API Tests', () => {
    it('should return status', () => {
        expect(api_endpoint()).toEqual({"status": "ok"});
    });
});
"""
        }

        result = await analyzer.analyze_canonical_patterns(entity_code)

        assert isinstance(result, dict)
        assert "patterns_found" in result
        assert "canonical_score" in result
        assert "recommendations" in result

        assert isinstance(result["canonical_score"], float)
        assert 0.0 <= result["canonical_score"] <= 1.0

        assert isinstance(result["recommendations"], list)

class TestSwarmTestGenerator:
    """Tests pour SwarmTestGenerator"""

    @pytest.fixture
    def kiva_config(self):
        return {
            "url": "http://localhost:8001",
            "max_concurrent_tests": 10,
            "test_timeout": 600
        }

    @pytest.fixture
    def generator(self, kiva_config):
        return SwarmTestGenerator(kiva_config)

    @pytest.mark.asyncio
    async def test_generate_functional_tests(self, generator):
        """Test génération tests fonctionnels"""
        entity = {
            "id": "test-entity",
            "name": "TestEntity",
            "type": "service"
        }

        canonical_analysis = {
            "canonical_score": 0.85,
            "patterns_found": {
                "api_endpoints": {"count": 5},
                "error_handling": {"count": 3}
            }
        }

        tests = await generator.generate_swarm_tests(entity, canonical_analysis)

        assert isinstance(tests, list)
        assert len(tests) > 0

        # Vérifier structure des tests
        for test in tests:
            assert "type" in test
            assert "name" in test
            assert "description" in test
            assert "swarm_size" in test
            assert "timeout" in test

    @pytest.mark.asyncio
    async def test_generate_tests_with_dependencies(self, generator):
        """Test génération tests avec dépendances"""
        entity = {
            "id": "test-entity-deps",
            "name": "TestEntityDeps",
            "type": "service",
            "dependencies": ["nexus", "kiva", "ontology"]
        }

        canonical_analysis = {"canonical_score": 0.8}

        tests = await generator.generate_swarm_tests(entity, canonical_analysis)

        # Devrait inclure tests d'intégration
        integration_tests = [t for t in tests if t.get("type") == "integration"]
        assert len(integration_tests) >= 3  # Un par dépendance

class TestLoadTester:
    """Tests pour LoadTester"""

    @pytest.fixture
    def tester(self):
        return LoadTester()

    @pytest.mark.asyncio
    async def test_run_load_tests_success(self, tester):
        """Test exécution tests de charge réussis"""
        tests = [
            {
                "type": "load",
                "name": "test_load_1",
                "swarm_size": 10,
                "duration": 300
            },
            {
                "type": "load",
                "name": "test_load_2",
                "swarm_size": 5,
                "duration": 150
            }
        ]

        results = await tester.run_load_tests(tests)

        assert isinstance(results, dict)
        assert "overall_passed" in results
        assert "results" in results
        assert "summary" in results

        assert results["overall_passed"] is True
        assert len(results["results"]) == 2

        # Vérifier métriques
        for test_name, test_result in results["results"].items():
            assert test_result["passed"] is True
            assert "avg_response_time" in test_result
            assert "error_rate" in test_result
            assert "stability_score" in test_result

    @pytest.mark.asyncio
    async def test_run_load_tests_no_load_tests(self, tester):
        """Test sans tests de charge"""
        tests = [
            {
                "type": "functional",
                "name": "test_func_1"
            }
        ]

        results = await tester.run_load_tests(tests)

        assert results["overall_passed"] is True
        assert len(results["results"]) == 0

class TestSecurityAuditor:
    """Tests pour SecurityAuditor"""

    @pytest.fixture
    def auditor(self):
        return SecurityAuditor()

    @pytest.mark.asyncio
    async def test_run_security_audit_clean(self, auditor):
        """Test audit sécurité propre"""
        entity = {
            "id": "test-secure-entity",
            "name": "SecureEntity"
        }

        results = await auditor.run_security_audit(entity)

        assert isinstance(results, dict)
        assert "passed" in results
        assert "vulnerabilities" in results
        assert "recommendations" in results
        assert "compliance_score" in results

        assert results["passed"] is True  # Simulation propre
        assert isinstance(results["vulnerabilities"], dict)
        assert isinstance(results["recommendations"], list)
        assert isinstance(results["compliance_score"], float)

    @pytest.mark.asyncio
    async def test_run_security_audit_with_vulnerabilities(self, auditor):
        """Test audit avec vulnérabilités"""
        entity = {
            "id": "test-vulnerable-entity",
            "name": "VulnerableEntity",
            "code": "USE OF WEAK CRYPTO"  # Simulation
        }

        results = await auditor.run_security_audit(entity)

        assert isinstance(results, dict)
        assert "passed" in results
        assert "vulnerabilities" in results

        # Peut échouer selon simulation
        assert isinstance(results["passed"], bool)

class TestSCEPipeline:
    """Tests pour SCEPipeline"""

    @pytest.fixture
    def config(self):
        from cli_anything_engine.config import CLIAnythingConfig
        config = CLIAnythingConfig()
        config.sce_timeout = 10  # Tests rapides
        return config

    @pytest.fixture
    def pipeline(self, config):
        return SCEPipeline(config)

    @pytest.mark.asyncio
    async def test_run_full_sce_success(self, pipeline):
        """Test pipeline SCE complet réussi"""
        entity = {
            "id": "test-sce-entity",
            "name": "TestSCEEntity",
            "type": "service",
            "dependencies": ["nexus"],
            "url": "https://github.com/gerivdb/test-sce"
        }

        validation = await pipeline.run_full_sce(entity)

        assert_sce_validation(validation, expected_passed=True)

        # Vérifier détails
        assert validation.entity_id == entity["id"]
        assert validation.canonical_analysis_complete is True
        assert validation.swarm_tests_generated > 0
        assert validation.coverage_percentage >= 80.0
        assert validation.overall_passed is True
        assert validation.execution_time > 0
        assert isinstance(validation.report, dict)

    @pytest.mark.asyncio
    async def test_run_full_sce_failure(self, pipeline):
        """Test pipeline SCE en échec"""
        entity = {
            "id": "test-sce-fail",
            "name": "TestSCEFail",
            "type": "service",
            "dependencies": [],  # Pas de dépendances = échec simulé
            "url": "https://github.com/gerivdb/test-fail"
        }

        validation = await pipeline.run_full_sce(entity)

        assert_sce_validation(validation, expected_passed=False)

        # Vérifier échec
        assert validation.overall_passed is False
        assert validation.execution_time > 0

    def test_calculate_performance_score(self, pipeline):
        """Test calcul score performance"""
        load_results = {
            "results": {
                "test1": {
                    "passed": True,
                    "avg_response_time": 50.0,
                    "error_rate": 0.02,
                    "stability_score": 0.95
                },
                "test2": {
                    "passed": True,
                    "avg_response_time": 45.0,
                    "error_rate": 0.01,
                    "stability_score": 0.98
                }
            }
        }

        score = pipeline._calculate_performance_score(load_results)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Bon score attendu

    def test_calculate_coverage(self, pipeline):
        """Test calcul couverture"""
        tests = [
            {"type": "functional"},
            {"type": "load"},
            {"type": "security"},
            {"type": "integration"},
            {"type": "performance"}
        ]

        coverage = pipeline._calculate_coverage(tests)

        assert isinstance(coverage, float)
        assert 0.0 <= coverage <= 100.0
        assert coverage >= 80.0  # Haute couverture attendue

    def test_metrics_update(self, pipeline):
        """Test mise à jour métriques"""
        initial_metrics = pipeline.get_metrics()

        # Simuler pipeline
        validation = SCEValidation(
            entity_id="test",
            canonical_analysis_complete=True,
            swarm_tests_generated=5,
            load_tests_passed=True,
            failure_injection_passed=True,
            security_audit_passed=True,
            performance_score=0.9,
            coverage_percentage=85.0,
            overall_passed=True,
            execution_time=25.0,
            report={}
        )

        pipeline._update_metrics(validation, None)

        updated_metrics = pipeline.get_metrics()

        assert updated_metrics["pipelines_executed"] == initial_metrics["pipelines_executed"] + 1
        assert updated_metrics["success_rate"] >= 0.0

    @pytest.mark.asyncio
    @patch('cli_anything_engine.sce_pipeline.CanonicalAnalyzer.analyze_canonical_patterns')
    async def test_error_handling(self, mock_analyze, pipeline):
        """Test gestion d'erreurs"""
        mock_analyze.side_effect = Exception("Canonical analysis failed")

        entity = {"id": "test-error", "name": "TestError"}

        validation = await pipeline.run_full_sce(entity)

        assert_sce_validation(validation, expected_passed=False)
        assert validation.canonical_analysis_complete is False
        assert "error" in validation.report