# Tests CLI-ANYTHING Engine v2.0
# IntentHash: 0xCLI_ANYTHING_ENGINE_V2_20260428

import pytest
import asyncio
from typing import Dict, Any

# Fixtures communes pour tous les tests
@pytest.fixture
def sample_entity_data() -> Dict[str, Any]:
    """Données d'entité de test"""
    return {
        'id': 'test-entity-001',
        'name': 'TestEntity',
        'type': 'repository',
        'url': 'https://github.com/gerivdb/test-entity',
        'language': 'python',
        'dependencies': ['nexus', 'kiva'],
        'description': 'Test entity for CLI-ANYTHING Engine validation'
    }

@pytest.fixture
def mock_config():
    """Configuration de test mockée"""
    from cli_anything_engine.config import CLIAnythingConfig
    
    config = CLIAnythingConfig()
    # Override pour tests
    config.evaluation_timeout = 5  # secondes pour tests rapides
    config.sce_timeout = 10
    config.cache_ttl = 1  # cache court pour tests
    
    return config

@pytest.fixture
def event_loop():
    """Event loop pour tests async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Utilitaires de test
def assert_eligibility_score(score, expected_recommended: bool = True, min_score: float = 0.5):
    """Assertion pour scores d'éligibilité"""
    assert isinstance(score.overall_score, float)
    assert 0.0 <= score.overall_score <= 1.0
    assert score.recommended == expected_recommended
    if expected_recommended:
        assert score.overall_score >= min_score
    
    # Vérifier composants
    assert isinstance(score.api_complexity, float)
    assert isinstance(score.agent_utility, float)
    assert isinstance(score.code_maturity, float)
    assert isinstance(score.ecosystem_impact, float)
    assert isinstance(score.reasoning, str)
    assert len(score.reasoning) > 0

def assert_sce_validation(validation, expected_passed: bool = True):
    """Assertion pour validation SCE"""
    assert validation.entity_id is not None
    assert isinstance(validation.canonical_analysis_complete, bool)
    assert isinstance(validation.swarm_tests_generated, int)
    assert isinstance(validation.load_tests_passed, bool)
    assert isinstance(validation.failure_injection_passed, bool)
    assert isinstance(validation.security_audit_passed, bool)
    assert isinstance(validation.performance_score, float)
    assert isinstance(validation.coverage_percentage, float)
    assert isinstance(validation.overall_passed, bool)
    assert validation.execution_time > 0
    assert isinstance(validation.report, dict)
    
    if expected_passed:
        assert validation.overall_passed
        assert validation.coverage_percentage >= 80.0

def assert_orchestration_result(result, expected_success: bool = True):
    """Assertion pour résultat d'orchestration"""
    assert result.entity_id is not None
    assert isinstance(result.evaluation_completed, bool)
    assert isinstance(result.sce_completed, bool)
    assert isinstance(result.cli_generated, bool)
    assert isinstance(result.lifecycle_registered, bool)
    assert isinstance(result.overall_success, bool)
    assert result.execution_time > 0
    assert isinstance(result.errors, list)
    
    if expected_success:
        assert result.overall_success
        assert result.evaluation_completed
        assert result.sce_completed
        assert result.cli_generated
        assert result.lifecycle_registered
        assert len(result.errors) == 0