import pytest
import asyncio
from cli_anything_engine import (
    CLIAnythingConfig, Orchestrator, EntityEvaluator,
    SCEPipeline, LifecycleManager
)
from . import assert_eligibility_score, assert_sce_validation, assert_orchestration_result

class TestE2EOrchestration:
    """Tests End-to-End pour orchestration complète"""

    @pytest.fixture
    def config(self):
        """Configuration optimisée pour E2E"""
        config = CLIAnythingConfig()
        # Paramètres pour tests E2E rapides
        config.evaluation_timeout = 10
        config.sce_timeout = 20
        config.cache_ttl = 5
        return config

    @pytest.fixture
    async def orchestrator(self, config):
        """Orchestrateur configuré pour E2E"""
        return Orchestrator(config)

    @pytest.mark.asyncio
    async def test_full_orchestration_workflow(self, orchestrator):
        """Test workflow complet d'orchestration E2E"""
        entity_data = {
            'id': 'e2e-test-entity',
            'name': 'E2ETestEntity',
            'type': 'service',
            'url': 'https://github.com/gerivdb/e2e-test-entity',
            'language': 'python',
            'dependencies': ['nexus', 'kiva', 'ontology'],
            'description': 'Entité de test E2E pour validation complète CLI-ANYTHING'
        }

        # Exécuter orchestration complète
        result = await orchestrator.orchestrate_entity(entity_data)

        # Assertions complètes
        assert_orchestration_result(result, expected_success=True)

        # Vérifications supplémentaires E2E
        assert result.entity_id == entity_data['id']
        assert result.execution_time < 60  # Moins de 1 minute pour E2E

        # Vérifier que l'entité est enregistrée dans lifecycle
        entity_status = orchestrator.lifecycle_manager.get_entity_status(entity_data['id'])
        assert entity_status is not None
        assert entity_status.status == 'active'
        assert entity_status.usage_count == 0  # Première utilisation

        # Vérifier métriques système mises à jour
        system_status = await orchestrator.get_system_status()
        assert system_status['orchestrator_metrics']['orchestrations_completed'] >= 1
        assert system_status['system_health'] in ['operational', 'degraded']

    @pytest.mark.asyncio
    async def test_batch_orchestration_e2e(self, orchestrator):
        """Test orchestration par lot E2E"""
        entities = [
            {
                'id': 'e2e-batch-1',
                'name': 'E2EBatch1',
                'type': 'service',
                'url': 'https://github.com/gerivdb/e2e-batch-1',
                'language': 'python',
                'dependencies': ['nexus'],
                'description': 'Première entité batch E2E'
            },
            {
                'id': 'e2e-batch-2',
                'name': 'E2EBatch2',
                'type': 'library',
                'url': 'https://github.com/gerivdb/e2e-batch-2',
                'language': 'javascript',
                'dependencies': ['kiva', 'ontology'],
                'description': 'Deuxième entité batch E2E'
            },
            {
                'id': 'e2e-batch-3',
                'name': 'E2EBatch3',
                'type': 'api',
                'url': 'https://github.com/gerivdb/e2e-batch-3',
                'language': 'python',
                'dependencies': ['nexus', 'kiva', 'ontology', 'gateway-manager'],
                'description': 'Troisième entité batch E2E avec toutes dépendances'
            }
        ]

        # Orchestration par lot
        results = await orchestrator.run_batch_orchestration(entities)

        # Vérifications batch
        assert len(results) == 3

        successful_results = [r for r in results if r.overall_success]
        assert len(successful_results) >= 2  # Au moins 2 réussites

        # Vérifier que toutes les entités sont enregistrées
        for entity_data in entities:
            entity_status = orchestrator.lifecycle_manager.get_entity_status(entity_data['id'])
            assert entity_status is not None
            assert entity_status.status == 'active'

        # Vérifier métriques globales
        system_status = await orchestrator.get_system_status()
        assert system_status['orchestrator_metrics']['orchestrations_completed'] >= 3

        # Calculer métriques batch
        total_time = sum(r.execution_time for r in results)
        avg_time = total_time / len(results)
        success_rate = len(successful_results) / len(results)

        assert avg_time < 45  # Temps moyen acceptable
        assert success_rate >= 0.66  # Au moins 2/3 de succès

    @pytest.mark.asyncio
    async def test_error_recovery_e2e(self, orchestrator):
        """Test récupération d'erreurs E2E"""
        # Entité qui va échouer
        failing_entity = {
            'id': 'e2e-error-test',
            'name': 'E2EErrorTest',
            'type': 'service',
            'url': 'https://github.com/gerivdb/e2e-error-test',
            'language': 'unsupported_lang',  # Langage non supporté
            'dependencies': [],
            'description': 'Entité de test pour erreurs E2E'
        }

        # Orchestration qui va échouer
        result = await orchestrator.orchestrate_entity(failing_entity)

        # Vérifier échec propre
        assert_orchestration_result(result, expected_success=False)
        assert len(result.errors) > 0
        assert 'non supporté' in str(result.errors).lower()

        # Vérifier que le système continue de fonctionner
        system_status = await orchestrator.get_system_status()
        assert 'system_health' in system_status

        # Tester orchestration réussie après échec
        successful_entity = {
            'id': 'e2e-recovery-test',
            'name': 'E2ERecoveryTest',
            'type': 'service',
            'url': 'https://github.com/gerivdb/e2e-recovery-test',
            'language': 'python',
            'dependencies': ['nexus'],
            'description': 'Test récupération après erreur'
        }

        recovery_result = await orchestrator.orchestrate_entity(successful_entity)
        assert_orchestration_result(recovery_result, expected_success=True)

class TestComponentIntegration:
    """Tests d'intégration entre composants"""

    @pytest.fixture
    def config(self):
        config = CLIAnythingConfig()
        config.evaluation_timeout = 5
        config.sce_timeout = 10
        return config

    @pytest.mark.asyncio
    async def test_entity_evaluator_sce_integration(self, config):
        """Test intégration EntityEvaluator + SCE"""
        evaluator = EntityEvaluator(config)
        sce_pipeline = SCEPipeline(config)

        entity_data = {
            'id': 'integration-test',
            'name': 'IntegrationTest',
            'type': 'service',
            'url': 'https://github.com/gerivdb/integration-test',
            'language': 'python',
            'dependencies': ['nexus', 'kiva']
        }

        # Créer entité
        entity = evaluator._EntityEvaluator__class__(
            id=entity_data['id'],
            name=entity_data['name'],
            type=entity_data['type'],
            url=entity_data['url'],
            language=entity_data['language'],
            dependencies=entity_data['dependencies'],
            description='Test intégration'
        )

        # Évaluation
        eligibility = await evaluator.evaluate_eligibility(entity)
        assert_eligibility_score(eligibility, expected_recommended=True)

        # SCE si éligible
        if eligibility.recommended:
            sce_result = await sce_pipeline.run_full_sce(entity_data)
            assert_sce_validation(sce_result, expected_passed=True)

    @pytest.mark.asyncio
    async def test_full_pipeline_integration(self, config):
        """Test pipeline complète intégrée"""
        orchestrator = Orchestrator(config)

        entity_data = {
            'id': 'full-pipeline-test',
            'name': 'FullPipelineTest',
            'type': 'api',
            'url': 'https://github.com/gerivdb/full-pipeline-test',
            'language': 'python',
            'dependencies': ['nexus', 'kiva', 'ontology', 'gateway-manager'],
            'description': 'Test pipeline complète intégrée'
        }

        # Exécuter orchestration
        result = await orchestrator.orchestrate_entity(entity_data)
        assert_orchestration_result(result, expected_success=True)

        # Vérifier intégration composants
        assert orchestrator.evaluator.get_metrics()['evaluations_performed'] >= 1
        assert orchestrator.sce_pipeline.get_metrics()['pipelines_executed'] >= 1
        assert orchestrator.lifecycle_manager.get_metrics()['entities_managed'] >= 1

        # Vérifier cohérence métriques
        system_status = await orchestrator.get_system_status()
        assert system_status['orchestrator_metrics']['orchestrations_completed'] >= 1
        assert system_status['evaluator_metrics']['evaluations_performed'] >= 1
        assert system_status['sce_metrics']['pipelines_executed'] >= 1
        assert system_status['lifecycle_metrics']['entities_managed'] >= 1

class TestPerformanceBenchmarks:
    """Tests de performance et benchmarks"""

    @pytest.fixture
    def config(self):
        config = CLIAnythingConfig()
        # Paramètres performance
        config.evaluation_timeout = 30
        config.sce_timeout = 120
        return config

    @pytest.fixture
    async def orchestrator(self, config):
        return Orchestrator(config)

    @pytest.mark.asyncio
    async def test_orchestration_performance(self, orchestrator):
        """Test performance orchestration"""
        import time

        entity_data = {
            'id': 'perf-test-entity',
            'name': 'PerfTestEntity',
            'type': 'service',
            'url': 'https://github.com/gerivdb/perf-test',
            'language': 'python',
            'dependencies': ['nexus'],
            'description': 'Test performance orchestration'
        }

        start_time = time.time()
        result = await orchestrator.orchestrate_entity(entity_data)
        end_time = time.time()

        execution_time = end_time - start_time

        # Assertions performance
        assert result.execution_time < 60  # Moins de 1 minute
        assert execution_time < 65  # Marge pour mesure
        assert abs(result.execution_time - execution_time) < 5  # Cohérence

        # Vérifier succès
        assert_orchestration_result(result, expected_success=True)

    @pytest.mark.asyncio
    async def test_concurrent_orchestration_performance(self, orchestrator):
        """Test performance orchestration concurrente"""
        import time

        entities = [
            {
                'id': f'concurrent-test-{i}',
                'name': f'ConcurrentTest{i}',
                'type': 'service',
                'url': f'https://github.com/gerivdb/concurrent-test-{i}',
                'language': 'python',
                'dependencies': ['nexus'],
                'description': f'Test concurrent {i}'
            }
            for i in range(5)  # 5 entités concurrentes
        ]

        start_time = time.time()
        results = await orchestrator.run_batch_orchestration(entities)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_entity = total_time / len(entities)

        # Assertions performance concurrente
        assert len(results) == 5
        assert total_time < 120  # Moins de 2 minutes pour 5 entités
        assert avg_time_per_entity < 30  # Moins de 30s par entité

        # Au moins 4 succès
        successful = sum(1 for r in results if r.overall_success)
        assert successful >= 4

    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, orchestrator):
        """Test stabilité utilisation mémoire"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Exécuter plusieurs orchestrations
        for i in range(3):
            entity_data = {
                'id': f'memory-test-{i}',
                'name': f'MemoryTest{i}',
                'type': 'service',
                'url': f'https://github.com/gerivdb/memory-test-{i}',
                'language': 'python',
                'dependencies': ['nexus'],
                'description': f'Test mémoire {i}'
            }

            result = await orchestrator.orchestrate_entity(entity_data)
            assert_orchestration_result(result, expected_success=True)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Vérifier pas de fuite mémoire majeure
        assert memory_increase < 50  # Moins de 50MB d'augmentation

    @pytest.mark.asyncio
    async def test_scalability_test(self, orchestrator):
        """Test scalabilité"""
        # Test avec entité complexe
        complex_entity = {
            'id': 'scalability-test',
            'name': 'ScalabilityTest',
            'type': 'platform',
            'url': 'https://github.com/gerivdb/scalability-test',
            'language': 'python',
            'dependencies': ['nexus', 'kiva', 'ontology', 'gateway-manager', 'brain', 'fluence'],
            'description': 'Test scalabilité avec nombreuses dépendances'
        }

        result = await orchestrator.orchestrate_entity(complex_entity)
        assert_orchestration_result(result, expected_success=True)

        # Vérifier que le système gère la complexité
        assert len(complex_entity['dependencies']) == 6
        assert result.execution_time < 90  # Gère complexité raisonnablement