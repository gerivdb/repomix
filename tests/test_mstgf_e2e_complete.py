import pytest
import asyncio
import time
from mstgf import MSTGFConfig, Orchestrator

@pytest.mark.asyncio
async def test_mstgf_full_e2e_workflow():
    """Test E2E complet du workflow MSTGF"""
    # Configuration
    config = MSTGFConfig()
    config.evaluation_timeout = 5
    config.sce_timeout = 10

    # Orchestrateur
    orchestrator = Orchestrator(config)

    # Entité de test réaliste
    entity_data = {
        'id': 'e2e-mstgf-test-entity',
        'name': 'E2E MSTGF Test Entity',
        'type': 'service',
        'url': 'https://github.com/gerivdb/e2e-mstgf-test',
        'language': 'python',
        'dependencies': ['nexus', 'kiva', 'ontology', 'fastapi'],
        'description': 'Entité de test E2E pour validation complète MSTGF'
    }

    # Mesurer le temps d'exécution
    start_time = time.time()

    # Exécuter orchestration complète
    result = await orchestrator.orchestrate_entity(entity_data)

    execution_time = time.time() - start_time

    # Assertions E2E
    assert result.overall_success == True
    assert result.evaluation_completed == True
    assert result.sce_completed == True
    assert result.cli_generated == True
    assert result.lifecycle_registered == True
    assert result.execution_time < 30  # Moins de 30 secondes
    assert len(result.errors) == 0

    # Vérifier composants internes
    assert len(orchestrator.lifecycle_manager.entities) >= 1
    entity = orchestrator.lifecycle_manager.get_entity_status(entity_data['id'])
    assert entity is not None
    assert entity.status == 'active'

    print(f'E2E test passed in {execution_time:.2f}s')

@pytest.mark.asyncio
async def test_mstgf_error_recovery_e2e():
    """Test récupération d'erreurs E2E"""
    config = MSTGFConfig()
    orchestrator = Orchestrator(config)

    # Entité qui va échouer
    failing_entity = {
        'id': 'e2e-error-test',
        'name': 'E2E Error Test',
        'type': 'service',
        'url': 'https://github.com/gerivdb/error-test',
        'language': 'nonexistent_lang',  # Langage non supporté
        'dependencies': [],
        'description': 'Test de récupération d\'erreurs'
    }

    # Orchestration doit échouer proprement
    result = await orchestrator.orchestrate_entity(failing_entity)

    assert result.overall_success == False
    assert result.evaluation_completed == False
    assert len(result.errors) > 0
    assert 'non supporté' in str(result.errors).lower()

    # Système doit rester fonctionnel
    status = await orchestrator.get_system_status()
    assert 'system_health' in status

@pytest.mark.asyncio
async def test_mstgf_batch_processing_e2e():
    """Test traitement par lot E2E"""
    config = MSTGFConfig()
    orchestrator = Orchestrator(config)

    # Lot d'entités
    entities = [
        {
            'id': f'batch-test-{i}',
            'name': f'Batch Test {i}',
            'type': 'service',
            'url': f'https://github.com/gerivdb/batch-test-{i}',
            'language': 'python',
            'dependencies': ['nexus'],
            'description': f'Entité batch {i}'
        }
        for i in range(3)
    ]

    start_time = time.time()
    results = await orchestrator.run_batch_orchestration(entities)
    batch_time = time.time() - start_time

    # Vérifications batch
    assert len(results) == 3
    successful = sum(1 for r in results if r.overall_success)
    assert successful >= 2  # Au moins 2 succès

    avg_time = batch_time / len(results)
    assert avg_time < 20  # Performance acceptable

    # Vérifier métriques système
    status = await orchestrator.get_system_status()
    assert status['orchestrator_metrics']['orchestrations_completed'] >= 3

@pytest.mark.asyncio
async def test_mstgf_system_health_e2e():
    """Test santé système E2E"""
    config = MSTGFConfig()
    orchestrator = Orchestrator(config)

    # Test sans charge
    status = await orchestrator.get_system_status()

    required_keys = [
        'orchestrator_metrics', 'evaluator_metrics',
        'sce_metrics', 'lifecycle_metrics', 'system_health'
    ]

    for key in required_keys:
        assert key in status

    assert status['system_health'] in ['operational', 'degraded', 'critical']

    # Test après traitement
    entity_data = {
        'id': 'health-test-entity',
        'name': 'Health Test Entity',
        'type': 'service',
        'url': 'https://github.com/gerivdb/health-test',
        'language': 'python',
        'dependencies': ['nexus'],
        'description': 'Test santé système'
    }

    result = await orchestrator.orchestrate_entity(entity_data)
    assert result.overall_success == True

    # Santé après traitement
    status_after = await orchestrator.get_system_status()
    assert status_after['orchestrator_metrics']['orchestrations_completed'] > status['orchestrator_metrics']['orchestrations_completed']