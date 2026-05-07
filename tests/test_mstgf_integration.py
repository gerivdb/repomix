import pytest
import asyncio
from unittest.mock import patch
from mstgf import MSTGFConfig, PatternRecognizer, TestOrchestrator, EvolutionAnalyzer, PythonAdapter

@pytest.mark.asyncio
async def test_tpre_uto_integration():
    """Test intégration TPRE + UTO"""
    config = MSTGFConfig()
    config.evaluation_timeout = 5

    # TPRE analyse
    recognizer = PatternRecognizer(config)
    entity_data = {
        'id': 'integration-test',
        'name': 'Integration Test',
        'type': 'service',
        'url': 'https://github.com/gerivdb/integration-test',
        'language': 'python',
        'dependencies': ['nexus', 'kiva'],
        'description': 'Test d\'intégration TPRE-UTO'
    }

    analysis = await recognizer.analyze_entity(entity_data)
    assert analysis.overall_success == True
    assert len(analysis.recommendations) > 0

    # UTO exécution basée sur recommandations
    orchestrator = TestOrchestrator(config)
    await orchestrator.start()

    # Créer job basé sur première recommandation
    rec = analysis.recommendations[0]
    exec_request = {
        'entity_id': entity_data['id'],
        'test_type': rec.test_type,
        'framework': 'pytest',  # Assumption
        'environment': {},
        'timeout': 30,
        'priority': 'medium'
    }

    job_id = await orchestrator.submit_test_request(exec_request)
    assert job_id is not None

    # Attendre un peu pour traitement
    await asyncio.sleep(1)

    # Vérifier statut
    job = await orchestrator.get_job_status(job_id)
    assert job is not None
    assert job.status in ['pending', 'running', 'completed']

    await orchestrator.stop()

@pytest.mark.asyncio
async def test_full_mstgf_pipeline_integration():
    """Test pipeline complet MSTGF"""
    config = MSTGFConfig()
    config.evaluation_timeout = 5
    config.sce_timeout = 10

    from mstgf import Orchestrator

    orchestrator = Orchestrator(config)

    entity_data = {
        'id': 'full-pipeline-test',
        'name': 'Full Pipeline Test',
        'type': 'api',
        'url': 'https://github.com/gerivdb/full-pipeline-test',
        'language': 'python',
        'dependencies': ['nexus', 'kiva', 'ontology'],
        'description': 'Test pipeline complet MSTGF'
    }

    # Exécuter orchestration complète
    result = await orchestrator.orchestrate_entity(entity_data)

    # Vérifications d'intégration
    assert result.overall_success == True

    # Vérifier que tous les composants ont été utilisés
    system_status = await orchestrator.get_system_status()
    assert system_status['evaluator_metrics']['evaluations_performed'] >= 1
    assert system_status['sce_metrics']['pipelines_executed'] >= 1
    assert system_status['lifecycle_metrics']['entities_managed'] >= 1
    assert system_status['orchestrator_metrics']['orchestrations_completed'] >= 1

@pytest.mark.asyncio
async def test_taal_adaptation_integration():
    """Test intégration TAAL avec différents langages"""
    config = MSTGFConfig()

    # Tester adaptateur Python
    python_adapter = PythonAdapter(config)

    from mstgf.taal.adapter_base import EnvironmentConfig
    env_config = EnvironmentConfig(
        language='python',
        version='3.8',
        dependencies=['pytest', 'fastapi'],
        test_framework='pytest',
        working_directory='/tmp/test',
        environment_variables={'PYTHONPATH': '/tmp'}
    )

    # Validation environnement
    env_valid = await python_adapter.validate_environment(env_config)
    assert isinstance(env_valid, bool)  # Peut être True ou False selon environnement

    # Installation dépendances (simulation)
    deps_installed = await python_adapter.install_dependencies(env_config)
    assert isinstance(deps_installed, bool)

    # Commandes de test
    unit_commands = python_adapter.get_test_commands('unit')
    assert isinstance(unit_commands, list)
    assert len(unit_commands) > 0

@pytest.mark.asyncio
async def test_msee_evolution_integration():
    """Test intégration MSEE avec métriques historiques"""
    config = MSTGFConfig()

    analyzer = EvolutionAnalyzer(config)

    # Analyser performance historique
    analysis = await analyzer.analyze_historical_performance(days=7)
    assert isinstance(analysis, dict)
    assert 'total_tests_analyzed' in analysis
    assert 'success_rate_trend' in analysis

    # Générer suggestions d'amélioration
    suggestions = await analyzer.generate_improvement_suggestions(analysis)
    assert isinstance(suggestions, list)

    # Vérifier structure suggestions
    if suggestions:
        suggestion = suggestions[0]
        required_keys = ['category', 'title', 'description', 'impact_estimate', 'effort_estimate', 'confidence']
        for key in required_keys:
            assert key in suggestion

@pytest.mark.asyncio
async def test_error_handling_integration():
    """Test gestion d'erreurs à travers tous les composants"""
    config = MSTGFConfig()

    from mstgf import Orchestrator

    orchestrator = Orchestrator(config)

    # Entité avec erreurs potentielles
    problematic_entity = {
        'id': 'error-handling-test',
        'name': 'Error Handling Test',
        'type': 'service',
        'url': 'https://github.com/gerivdb/error-test',
        'language': 'python',
        'dependencies': ['nonexistent_dep'],  # Dépendance inexistante
        'description': 'Test de gestion d\'erreurs'
    }

    # Le système doit gérer l'erreur proprement
    result = await orchestrator.orchestrate_entity(problematic_entity)

    # Vérifications de robustesse
    assert isinstance(result.overall_success, bool)  # Ne doit pas planter
    assert isinstance(result.errors, list)  # Doit collecter les erreurs
    assert result.execution_time >= 0  # Temps mesuré

    # Système doit rester fonctionnel
    status = await orchestrator.get_system_status()
    assert 'system_health' in status

@pytest.mark.asyncio
async def test_performance_under_load_integration():
    """Test performance sous charge"""
    config = MSTGFConfig()
    config.max_concurrent_tests = 2  # Limiter pour test

    from mstgf import Orchestrator

    orchestrator = Orchestrator(config)

    # Créer plusieurs entités pour test de charge
    entities = [
        {
            'id': f'load-test-{i}',
            'name': f'Load Test {i}',
            'type': 'service',
            'url': f'https://github.com/gerivdb/load-test-{i}',
            'language': 'python',
            'dependencies': ['nexus'],
            'description': f'Test de charge {i}'
        }
        for i in range(3)
    ]

    import time
    start_time = time.time()

    # Traitement parallèle
    results = await orchestrator.run_batch_orchestration(entities)

    end_time = time.time()
    total_time = end_time - start_time

    # Vérifications performance
    assert len(results) == 3
    assert total_time < 60  # Moins d'1 minute pour 3 entités

    successful = sum(1 for r in results if r.overall_success)
    assert successful >= 2  # Au moins 2 succès

    # Métriques système mises à jour
    status = await orchestrator.get_system_status()
    assert status['orchestrator_metrics']['orchestrations_completed'] >= 3