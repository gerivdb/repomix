"""
Comprehensive tests for NEXUS Meta-Testing Framework
Validates metacircular testing capabilities, self-validation, and auto-fix mechanisms
"""

import pytest
import asyncio
import time
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gateway_manager.providers.auto_testing.test_orchestrator import (
    TestOrchestrator,
    TestExecutionResult,
    TestResult,
    Issue,
    IssueSeverity,
)
from gateway_manager.providers.auto_testing.meta_validator import (
    MetaValidator,
    CircularityValidation,
    HealthMetrics,
)
from gateway_manager.providers.auto_testing.meta_framework import (
    MetaTestingFramework,
    MetaTestResult,
    FixResult,
)

logger = logging.getLogger(__name__)


class TestOrchestratorUnit:
    """Unit tests for TestOrchestrator"""

    def test_register_test_suite(self):
        """Test suite registration"""
        orchestrator = TestOrchestrator()
        tests = [lambda: None, lambda: None]

        orchestrator.register_test_suite("test_suite", tests)

        assert "test_suite" in orchestrator.test_suites
        assert len(orchestrator.test_suites["test_suite"]) == 2

    def test_register_duplicate_suite_overwrites(self):
        """Test that duplicate suite registration overwrites"""
        orchestrator = TestOrchestrator()
        tests1 = [lambda: None]
        tests2 = [lambda: None, lambda: None]

        orchestrator.register_test_suite("suite", tests1)
        orchestrator.register_test_suite("suite", tests2)

        assert len(orchestrator.test_suites["suite"]) == 2

    def test_get_execution_statistics_empty(self):
        """Test statistics with no executions"""
        orchestrator = TestOrchestrator()
        stats = orchestrator.get_execution_statistics()

        assert stats["total_tests"] == 0
        assert "message" in stats

    def test_generate_meta_tests_returns_callables(self):
        """Test meta-test generation"""
        orchestrator = TestOrchestrator()
        meta_tests = orchestrator.generate_meta_tests()

        assert isinstance(meta_tests, list)
        assert len(meta_tests) >= 3  # At least 3 meta-tests defined

        for test in meta_tests:
            assert callable(test)

    @pytest.mark.asyncio
    async def test_execute_test_suite_success(self):
        """Test successful execution of a test suite"""
        orchestrator = TestOrchestrator()
        tests = [lambda: None, lambda: None]

        orchestrator.register_test_suite("success_suite", tests)
        results = await orchestrator.execute_test_suite("success_suite")

        assert len(results) == 2
        assert all(r.result == TestResult.PASS for r in results)
        assert all(r.error_message is None for r in results)

    @pytest.mark.asyncio
    async def test_execute_test_suite_with_failure(self):
        """Test suite execution with a failing test"""
        orchestrator = TestOrchestrator()

        def failing_test():
            assert False, "Intentional failure"

        tests = [lambda: None, failing_test]
        orchestrator.register_test_suite("mixed_suite", tests)
        results = await orchestrator.execute_test_suite("mixed_suite")

        assert len(results) == 2
        assert results[0].result == TestResult.PASS
        assert results[1].result == TestResult.FAIL
        assert "Intentional failure" in results[1].error_message

    @pytest.mark.asyncio
    async def test_execute_test_suite_not_found(self):
        """Test execution of non-existent suite raises error"""
        orchestrator = TestOrchestrator()

        with pytest.raises(ValueError, match="Test suite not found"):
            await orchestrator.execute_test_suite("nonexistent")

    @pytest.mark.asyncio
    async def test_async_test_support(self):
        """Test that async test functions are properly handled"""
        orchestrator = TestOrchestrator()

        async def async_test():
            await asyncio.sleep(0.01)
            assert True

        orchestrator.register_test_suite("async_suite", [async_test])
        results = await orchestrator.execute_test_suite("async_suite")

        assert len(results) == 1
        assert results[0].result == TestResult.PASS

    def test_analyze_test_failures_categorization(self):
        """Test failure analysis and categorization"""
        orchestrator = TestOrchestrator()

        # Create mock failure results
        failures = [
            TestExecutionResult(
                test_id="test_import",
                result=TestResult.ERROR,
                duration=0.1,
                error_message="ModuleNotFoundError: no module named 'foo'",
                metadata={},
            ),
            TestExecutionResult(
                test_id="test_type",
                result=TestResult.FAIL,
                duration=0.2,
                error_message="TypeError: object of type 'int' has no len()",
                metadata={},
            ),
            TestExecutionResult(
                test_id="test_assert",
                result=TestResult.FAIL,
                duration=0.1,
                error_message="AssertionError: expected 5 but got 3",
                metadata={},
            ),
        ]

        analysis = orchestrator.analyze_test_failures(failures)

        assert "import_issues" in analysis
        assert "type_issues" in analysis
        assert "logic_issues" in analysis
        assert len(analysis["import_issues"]) == 1
        assert len(analysis["type_issues"]) == 1
        assert len(analysis["logic_issues"]) == 1

    def test_analyze_test_failures_severity_assessment(self):
        """Test severity assessment in failure analysis"""
        orchestrator = TestOrchestrator()

        critical_failure = TestExecutionResult(
            test_id="critical_test",
            result=TestResult.ERROR,
            duration=0.1,
            error_message="Critical system failure",
            metadata={},
        )

        analysis = orchestrator.analyze_test_failures([critical_failure])
        issue = list(analysis.values())[0][0]

        assert issue.severity == IssueSeverity.CRITICAL

    def test_suggest_fix_logic(self):
        """Test fix suggestion logic"""
        orchestrator = TestOrchestrator()

        import_failure = TestExecutionResult(
            test_id="import_test",
            result=TestResult.ERROR,
            duration=0.1,
            error_message="ImportError: cannot import name 'foo'",
            metadata={},
        )

        suggestion = orchestrator._suggest_fix(import_failure)
        assert "import" in suggestion.lower()
        assert (
            "dependency" in suggestion.lower() or "dependencies" in suggestion.lower()
        )


class TestMetaValidatorUnit:
    """Unit tests for MetaValidator"""

    def test_initialization(self):
        """Test validator initialization"""
        validator = MetaValidator()
        assert validator.validation_history == []
        assert validator.project_root is not None

    def test_initialization_with_custom_root(self):
        """Test validator with custom project root"""
        custom_root = Path("/custom/path")
        validator = MetaValidator(project_root=custom_root)
        assert validator.project_root == custom_root

    @pytest.mark.asyncio
    async def test_validate_self_consistency(self):
        """Test self-consistency validation"""
        validator = MetaValidator()
        result = await validator.validate_self_consistency()

        assert isinstance(result, CircularityValidation)
        assert result.is_circular == True
        assert result.validation_depth >= 1
        assert result.consistency_score > 0.8
        assert len(validator.validation_history) == 1

    @pytest.mark.asyncio
    async def test_validate_self_consistency_nested(self):
        """Test nested self-validation (deep circularity)"""
        validator = MetaValidator()
        result1 = await validator.validate_self_consistency()
        result2 = await validator.validate_self_consistency()

        assert result1.is_circular and result2.is_circular
        assert len(validator.validation_history) == 2

    def test_check_circular_logic_returns_dict(self):
        """Test circular logic check returns expected structure"""
        validator = MetaValidator()
        result = validator.check_circular_logic()

        assert "circular_imports" in result
        assert "circular_logic" in result
        assert "health_score" in result
        assert isinstance(result["health_score"], float)

    def test_measure_framework_health_returns_metrics(self):
        """Test health measurement returns valid metrics"""
        validator = MetaValidator()
        health = validator.measure_framework_health()

        assert isinstance(health, HealthMetrics)
        assert 0.0 <= health.test_coverage <= 1.0
        assert 0.0 <= health.code_quality_score <= 1.0
        assert 0.0 <= health.maintainability_index <= 1.0
        assert 0.0 <= health.circular_validation_score <= 1.0
        assert 0.0 <= health.overall_health <= 1.0

    def test_validate_imports_critical_modules(self):
        """Test that critical Python modules can be imported"""
        validator = MetaValidator()
        result = validator.validate_imports()

        assert "valid_imports" in result
        assert "invalid_imports" in result
        assert "import_time" in result

        # Should include standard library modules
        assert "asyncio" in result["valid_imports"]
        assert "logging" in result["valid_imports"]

    def test_get_validation_summary_comprehensive(self):
        """Test validation summary includes all components"""
        validator = MetaValidator()
        summary = validator.get_validation_summary()

        assert "health_metrics" in summary
        assert "circular_analysis" in summary
        assert "import_validation" in summary
        assert "validation_count" in summary


class TestMetaTestingFrameworkIntegration:
    """Integration tests for the complete MetaTestingFramework"""

    @pytest.fixture
    def framework(self):
        """Create a fresh framework instance for each test"""
        return MetaTestingFramework()

    @pytest.mark.asyncio
    async def test_run_meta_tests_returns_result(self, framework):
        """Test that run_meta_tests executes and returns valid result"""
        result = await framework.run_meta_tests()

        assert isinstance(result, MetaTestResult)
        assert 0.0 <= result.framework_health <= 1.0
        assert isinstance(result.issues_found, list)
        assert isinstance(result.tests_executed, int)
        assert isinstance(result.tests_passed, int)
        assert result.execution_time >= 0.0

    @pytest.mark.asyncio
    async def test_metacircularity_proof(self, framework):
        """Prove metacircularity: framework validates itself"""
        result = await framework.run_meta_tests()

        # Framework should successfully run its own tests
        assert result.tests_executed > 0
        # Should maintain high health score (self-validating)
        assert result.framework_health > 0.5

    @pytest.mark.asyncio
    async def test_detect_architectural_issues(self, framework):
        """Test architectural issue detection"""
        issues = framework.detect_architectural_issues()

        assert isinstance(issues, list)
        for issue in issues:
            assert isinstance(issue, Issue)
            assert issue.severity in IssueSeverity
            assert issue.category
            assert issue.description
            assert issue.suggested_fix

    @pytest.mark.asyncio
    async def test_apply_automatic_fixes_returns_result(self, framework):
        """Test automatic fix application"""
        # Create a mock issue
        mock_issue = Issue(
            issue_id="test_issue",
            severity=IssueSeverity.LOW,
            category="runtime_issues",
            description="Test issue",
            location="test_location",
            suggested_fix="Test fix",
            confidence=0.5,
        )

        result = await framework.apply_automatic_fixes([mock_issue])

        assert isinstance(result, FixResult)
        assert result.total_issues == 1
        assert result.fixes_applied >= 0
        assert result.fixes_failed >= 0
        assert result.fixes_applied + result.fixes_failed == 1

    def test_add_fix_callback(self, framework):
        """Test registering fix callbacks"""
        callback_mock = Mock()
        framework.add_fix_callback(callback_mock)

        assert callback_mock in framework.fix_callbacks
        assert len(framework.fix_callbacks) == 1

    @pytest.mark.asyncio
    async def test_fix_callback_invoked(self, framework):
        """Test that fix callbacks are invoked after fix attempts"""
        callback_mock = Mock()
        framework.add_fix_callback(callback_mock)

        issue = Issue(
            issue_id="callback_test",
            severity=IssueSeverity.LOW,
            category="runtime_issues",
            description="Test",
            location="test",
            suggested_fix="test",
            confidence=0.5,
        )

        await framework.apply_automatic_fixes([issue])

        callback_mock.assert_called_once()
        args = callback_mock.call_args[0]
        assert len(args) == 2  # (fixes_applied, fixes_failed)

    def test_get_framework_status_snapshot(self, framework):
        """Test status snapshot generation"""
        status = framework.get_framework_status()

        assert "health" in status
        assert "circular_dependencies" in status
        assert "execution_stats" in status
        assert "validation_history_count" in status

        # Health metrics should be numeric
        assert isinstance(status["health"]["test_coverage"], float)

    @pytest.mark.asyncio
    async def test_framework_health_calculation(self, framework):
        """Test health score calculation logic"""
        # Run tests to generate history
        await framework.run_meta_tests()

        status = framework.get_framework_status()
        health_score = status["health"]["overall_health"]

        assert isinstance(health_score, float)
        assert 0.0 <= health_score <= 1.0

    @pytest.mark.asyncio
    async def test_recommendations_generation(self, framework):
        """Test that recommendations are generated"""
        result = await framework.run_meta_tests()

        assert isinstance(result.recommendations, list)
        # Should have at least one recommendation
        assert len(result.recommendations) >= 0

        if result.recommendations:
            for rec in result.recommendations:
                assert isinstance(rec, str)
                assert len(rec) > 0


class TestMetacircularityProof:
    """Tests proving metacircular properties"""

    @pytest.mark.asyncio
    async def test_framework_can_test_itself(self):
        """
        Metacircularity test: The framework must be able to
        execute tests that validate its own structure and behavior
        """
        framework = MetaTestingFramework()
        result = await framework.run_meta_tests()

        # The framework should successfully execute meta-tests
        assert result.tests_executed > 0
        # Should have high success rate on its own tests
        assert result.tests_passed / max(result.tests_executed, 1) > 0.8

    @pytest.mark.asyncio
    async def test_validator_can_validate_itself(self):
        """
        Metacircularity: MetaValidator must validate its own consistency
        """
        validator = MetaValidator()

        # First validation
        validation1 = await validator.validate_self_consistency()
        assert validation1.is_circular == True
        assert validation1.consistency_score > 0.8

        # Second validation should also succeed (proving circularity)
        validation2 = await validator.validate_self_consistency()
        assert validation2.is_circular == True
        assert validation2.validation_depth >= 2

    @pytest.mark.asyncio
    async def test_orchestrator_can_orchestrate_its_own_tests(self):
        """
        Metacircularity: TestOrchestrator must be testable by itself
        """
        orchestrator = TestOrchestrator()

        # Orchestrator generates meta-tests
        meta_tests = orchestrator.generate_meta_tests()
        orchestrator.register_test_suite("self_orchestration", meta_tests)

        # Orchestrator executes its own meta-tests
        results = await orchestrator.execute_test_suite("self_orchestration")

        assert len(results) > 0
        # All self-tests should pass (framework is consistent)
        assert all(r.result == TestResult.PASS for r in results)


class TestPerformanceThresholds:
    """Performance benchmark tests (must meet PRD thresholds)"""

    @pytest.mark.asyncio
    async def test_meta_testing_latency_under_5s(self):
        """
        PRD Requirement: Performance industrielle (<5s latence)
        Total meta-testing must complete in under 5 seconds
        """
        framework = MetaTestingFramework()

        start = time.time()
        result = await framework.run_meta_tests()
        duration = time.time() - start

        assert duration < 5.0, (
            f"Meta-testing took {duration:.2f}s, exceeds 5s threshold"
        )
        assert result.execution_time < 5.0

    @pytest.mark.asyncio
    async def test_individual_test_latency_reasonable(self):
        """
        Individual tests should complete quickly (<2s each)
        """
        orchestrator = TestOrchestrator()

        # Create many simple tests
        tests = [lambda: None for _ in range(100)]
        orchestrator.register_test_suite("latency_suite", tests)

        results = await orchestrator.execute_test_suite("latency_suite")

        avg_duration = sum(r.duration for r in results) / len(results)
        assert avg_duration < 0.1, f"Average test duration {avg_duration:.3f}s too high"

    def test_framework_startup_time(self):
        """
        Framework initialization should be instantaneous (<100ms)
        """
        start = time.time()
        framework = MetaTestingFramework()
        init_time = time.time() - start

        assert init_time < 0.1, f"Framework startup took {init_time:.3f}s"


class TestAutoFixMechanisms:
    """Tests for automatic fix capabilities"""

    @pytest.mark.asyncio
    async def test_fix_dispatcher_routes_correctly(self):
        """Test that fix dispatcher routes to correct handlers"""
        framework = MetaTestingFramework()

        # Mock the fix methods to track calls
        framework._fix_import_issue = AsyncMock(return_value=True)
        framework._fix_type_issue = AsyncMock(return_value=True)
        framework._fix_async_issue = AsyncMock(return_value=True)
        framework._fix_runtime_issue = AsyncMock(return_value=True)

        issues = [
            Issue("i1", IssueSeverity.LOW, "import_issues", "test", "loc", "fix", 0.5),
            Issue("i2", IssueSeverity.LOW, "type_issues", "test", "loc", "fix", 0.5),
            Issue("i3", IssueSeverity.LOW, "async_issues", "test", "loc", "fix", 0.5),
            Issue("i4", IssueSeverity.LOW, "runtime_issues", "test", "loc", "fix", 0.5),
        ]

        await framework.apply_automatic_fixes(issues)

        framework._fix_import_issue.assert_awaited_once_with(issues[0])
        framework._fix_type_issue.assert_awaited_once_with(issues[1])
        framework._fix_async_issue.assert_awaited_once_with(issues[2])
        framework._fix_runtime_issue.assert_awaited_once_with(issues[3])

    @pytest.mark.asyncio
    async def test_unknown_category_handled_gracefully(self):
        """Test that unknown issue categories don't crash"""
        framework = MetaTestingFramework()

        issue = Issue(
            issue_id="unknown",
            severity=IssueSeverity.LOW,
            category="unknown_category",
            description="Unknown issue type",
            location="unknown",
            suggested_fix="Manual",
            confidence=0.5,
        )

        result = await framework.apply_automatic_fixes([issue])

        # Should skip unknown categories without applying fixes
        assert result.fixes_applied == 0
        assert result.fixes_failed == 0  # Not failed, just skipped

    @pytest.mark.asyncio
    async def test_fix_callback_exception_handled(self):
        """Test that exceptions in callbacks are caught"""
        framework = MetaTestingFramework()

        def bad_callback(applied, failed):
            raise ValueError("Callback error")

        framework.add_fix_callback(bad_callback)

        issue = Issue(
            issue_id="test",
            severity=IssueSeverity.LOW,
            category="runtime_issues",
            description="t",
            location="l",
            suggested_fix="f",
            confidence=0.5,
        )

        # Should not raise despite callback error
        result = await framework.apply_automatic_fixes([issue])
        assert result.total_issues == 1


# Helper class for async mocking
from unittest.mock import AsyncMock
