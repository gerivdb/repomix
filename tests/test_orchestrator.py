import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from cli_anything_engine.orchestrator import (
    Orchestrator, OrchestrationResult, NEXUSIntegrator,
    KIVACoordinator, GatewayRouter
)
from . import assert_orchestration_result

class TestNEXUSIntegrator:
    """Tests pour NEXUSIntegrator"""

    @pytest.fixture
    def nexus_config(self):
        return {
            "url": "http://localhost:8000",
            "timeout": 30,
            "retry_attempts": 3
        }

    @pytest.fixture
    def integrator(self, nexus_config):
        return NEXUSIntegrator(nexus_config)

    @pytest.mark.asyncio
    async def test_register_entity(self, integrator):
        """Test enregistrement entité dans NEXUS"""
        entity_data = {
            'id': 'test-entity',
            'name': 'TestEntity',
            'type': 'service'
        }

        success = await integrator.register_entity(entity_data)

        assert success is True

    @pytest.mark.asyncio
    async def test_update_entity_status(self, integrator):
        """Test mise à jour statut entité"""
        status = {'cli_ready': True, 'evaluation_score': 0.85}

        success = await integrator.update_entity_status('test-entity', status)

        assert success is True

class TestKIVACoordinator:
    """Tests pour KIVACoordinator"""

    @pytest.fixture
    def kiva_config(self):
        return {
            "url": "http://localhost:8001",
            "max_concurrent_tests": 10,
            "test_timeout": 600
        }

    @pytest.fixture
    def coordinator(self, kiva_config):
        return KIVACoordinator(kiva_config)

    @pytest.mark.asyncio
    async def test_coordinate_sce_tests(self, coordinator):
        """Test coordination tests SCE"""
        test_plan = {
            'tests': [
                {'type': 'functional', 'name': 'test1'},
                {'type': 'load', 'name': 'test2'}
            ]
        }

        result = await coordinator.coordinate_sce_tests('test-entity', test_plan)

        assert isinstance(result, dict)
        assert 'coordination_success' in result
        assert 'tests_scheduled' in result
        assert 'estimated_duration' in result

        assert result['coordination_success'] is True
        assert result['tests_scheduled'] == 2
        assert result['estimated_duration'] > 0

class TestGatewayRouter:
    """Tests pour GatewayRouter"""

    @pytest.fixture
    def gateway_config(self):
        return {
            "url": "http://localhost:8002",
            "default_model": "claude-3-sonnet",
            "max_tokens": 4000
        }

    @pytest.fixture
    def router(self, gateway_config):
        return GatewayRouter(gateway_config)

    @pytest.mark.asyncio
    async def test_request_evaluation_llm(self, router):
        """Test requête LLM pour évaluation"""
        prompt = "Evaluate this entity for CLI-ANYTHING eligibility"

        response = await router.request_evaluation_llm(prompt)

        assert isinstance(response, dict)
        assert 'response' in response
        assert 'confidence' in response
        assert 'tokens_used' in response

        assert isinstance(response['response'], str)
        assert isinstance(response['confidence'], float)
        assert isinstance(response['tokens_used'], int)

class TestOrchestrator:
    """Tests pour Orchestrator"""

    @pytest.fixture
    def config(self):
        from cli_anything_engine.config import CLIAnythingConfig
        config = CLIAnythingConfig()
        # Override pour tests rapides
        config.evaluation_timeout = 5
        config.sce_timeout = 10
        return config

    @pytest.fixture
    def orchestrator(self, config):
        return Orchestrator(config)

    @pytest.mark.asyncio
    async def test_orchestrate_entity_success(self, orchestrator, sample_entity_data):
        """Test orchestration complète réussie"""
        result = await orchestrator.orchestrate_entity(sample_entity_data)

        assert_orchestration_result(result, expected_success=True)

        assert result.entity_id == sample_entity_data['id']
        assert result.evaluation_completed is True
        assert result.sce_completed is True
        assert result.cli_generated is True
        assert result.lifecycle_registered is True
        assert result.overall_success is True
        assert result.execution_time > 0
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_orchestrate_entity_evaluation_failure(self, orchestrator):
        """Test orchestration avec échec évaluation"""
        entity_data = {
            'id': 'test-fail-eval',
            'name': 'TestFailEval',
            'type': 'service',
            'url': 'https://github.com/gerivdb/fail-eval',
            'language': 'unknown',  # Langage non supporté
            'dependencies': [],
            'description': 'Test failure'
        }

        result = await orchestrator.orchestrate_entity(entity_data)

        assert_orchestration_result(result, expected_success=False)

        assert result.evaluation_completed is False
        assert result.sce_completed is False
        assert result.cli_generated is False
        assert result.lifecycle_registered is False
        assert result.overall_success is False
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_orchestrate_entity_sce_failure(self, orchestrator):
        """Test orchestration avec échec SCE"""
        entity_data = {
            'id': 'test-fail-sce',
            'name': 'TestFailSce',
            'type': 'service',
            'url': 'https://github.com/gerivdb/fail-sce',
            'language': 'python',
            'dependencies': [],  # Pas de dépendances = échec SCE simulé
            'description': 'Test SCE failure'
        }

        result = await orchestrator.orchestrate_entity(entity_data)

        assert_orchestration_result(result, expected_success=False)

        assert result.evaluation_completed is True
        assert result.sce_completed is False
        assert result.cli_generated is False
        assert result.lifecycle_registered is False
        assert len(result.errors) > 0

    def test_create_entity_from_data(self, orchestrator, sample_entity_data):
        """Test création objet Entity"""
        entity = orchestrator._create_entity_from_data(sample_entity_data)

        from cli_anything_engine.entity_evaluator import Entity
        assert isinstance(entity, Entity)
        assert entity.id == sample_entity_data['id']
        assert entity.name == sample_entity_data['name']
        assert entity.language == sample_entity_data['language']
        assert entity.dependencies == sample_entity_data['dependencies']

    @pytest.mark.asyncio
    async def test_generate_cli_anything(self, orchestrator, sample_entity_data):
        """Test génération CLI-ANYTHING"""
        success = await orchestrator._generate_cli_anything(sample_entity_data)

        assert success is True

    @pytest.mark.asyncio
    async def test_register_lifecycle(self, orchestrator, sample_entity_data):
        """Test enregistrement lifecycle"""
        success = await orchestrator._register_lifecycle(sample_entity_data)

        assert success is True

        # Vérifier entité enregistrée
        entity = orchestrator.lifecycle_manager.get_entity_status(sample_entity_data['id'])
        assert entity is not None
        assert entity.id == sample_entity_data['id']

    @pytest.mark.asyncio
    async def test_run_batch_orchestration(self, orchestrator, sample_entity_data):
        """Test orchestration par lot"""
        entities = [sample_entity_data, sample_entity_data.copy()]
        entities[1]['id'] = 'test-batch-2'
        entities[1]['name'] = 'TestBatch2'

        results = await orchestrator.run_batch_orchestration(entities)

        assert isinstance(results, list)
        assert len(results) == 2

        for result in results:
            assert_orchestration_result(result, expected_success=True)

    @pytest.mark.asyncio
    async def test_get_system_status(self, orchestrator):
        """Test récupération statut système"""
        status = await orchestrator.get_system_status()

        assert isinstance(status, dict)
        assert 'orchestrator_metrics' in status
        assert 'evaluator_metrics' in status
        assert 'sce_metrics' in status
        assert 'lifecycle_metrics' in status
        assert 'system_health' in status

        # Vérifier métriques
        orch_metrics = status['orchestrator_metrics']
        assert 'orchestrations_completed' in orch_metrics
        assert 'success_rate' in orch_metrics
        assert 'avg_execution_time' in orch_metrics

    @pytest.mark.asyncio
    @patch('cli_anything_engine.orchestrator.Orchestrator._generate_cli_anything')
    async def test_error_handling_orchestration(self, mock_generate, orchestrator, sample_entity_data):
        """Test gestion d'erreurs dans orchestration"""
        mock_generate.side_effect = Exception("CLI generation failed")

        result = await orchestrator.orchestrate_entity(sample_entity_data)

        assert_orchestration_result(result, expected_success=False)
        assert len(result.errors) > 0
        assert "CLI generation failed" in str(result.errors)

    def test_update_metrics(self, orchestrator):
        """Test mise à jour métriques"""
        initial_metrics = orchestrator.metrics.copy()

        result = OrchestrationResult(
            entity_id='test',
            evaluation_completed=True,
            sce_completed=True,
            cli_generated=True,
            lifecycle_registered=True,
            overall_success=True,
            execution_time=10.5,
            errors=[]
        )

        orchestrator._update_metrics(result)

        assert orchestrator.metrics['orchestrations_completed'] == initial_metrics['orchestrations_completed'] + 1
        assert orchestrator.metrics['success_rate'] >= 0.0
        assert orchestrator.metrics['avg_execution_time'] > 0