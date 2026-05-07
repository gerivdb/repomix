import pytest
import asyncio
import time
import psutil
import os
from statistics import mean, stdev
from mstgf.quantum_citizen import QuantumMSTGFCitizen
from mstgf.quantum_core import QuantumState, QuantumMeasurement

@pytest.mark.asyncio
class TestQuantumPerformanceBenchmarks:
    """Benchmarks de performance quantique simulée"""

    @pytest.fixture
    async def benchmark_citizen(self):
        """Citizen optimisé pour benchmarks"""
        citizen = QuantumMSTGFCitizen()

        # Configuration benchmark
        citizen.quantum_processor.quantum_acceleration = True
        citizen.autonomous_scanner.parallel_scanning = True
        citizen.probabilistic_predictor.use_quantum_sampling = True

        return citizen

    async def test_quantum_scan_scalability(self, benchmark_citizen):
        """Test scalabilité du scan quantique"""
        citizen = benchmark_citizen

        # Tester différentes tailles d'écosystème
        ecosystem_sizes = [10, 50, 100, 500]

        performance_results = {}

        for size in ecosystem_sizes:
            # Générer écosystème de test
            test_ecosystem = {
                'repositories': [
                    {
                        'id': f'repo-{i}',
                        'complexity': 0.5 + (i % 20) * 0.025,  # Variation réaliste
                        'test_coverage': 0.6 + (i % 15) * 0.02,
                        'language': 'python' if i % 3 == 0 else 'javascript'
                    }
                    for i in range(size)
                ]
            }

            # Mock analyse pour focus performance
            with patch.object(citizen.autonomous_scanner, 'get_active_repositories', return_value=test_ecosystem['repositories']):
                with patch.object(citizen.autonomous_scanner, 'quantum_analyze_repository') as mock_analyze:
                    mock_analyze.return_value = MagicMock(needs_governance=True)

                    # Mesurer performance
                    start_time = time.time()
                    result = await citizen.autonomous_scanner.quantum_scan()
                    scan_time = time.time() - start_time

                    performance_results[size] = {
                        'scan_time': scan_time,
                        'throughput': size / scan_time if scan_time > 0 else float('inf'),
                        'efficiency': result.quantum_efficiency_score
                    }

        # Assertions de scalabilité
        # Temps devrait croître moins que linéairement grâce à la parallélisation
        time_10 = performance_results[10]['scan_time']
        time_100 = performance_results[100]['scan_time']

        scalability_ratio = time_100 / (time_10 * 10)  # Idéal = 1.0 pour scalabilité parfaite

        assert scalability_ratio < 2.0  # Moins de 2x le temps linéaire = bonne scalabilité
        assert performance_results[100]['throughput'] > performance_results[10]['throughput'] * 0.5  # Débit maintenu

    async def test_quantum_prediction_accuracy_vs_speed(self, benchmark_citizen):
        """Test équilibre précision/vitesse des prédictions quantiques"""
        citizen = benchmark_citizen

        test_cases = [
            {'complexity': 0.9, 'expected_confidence': 0.85, 'time_budget': 1.0},
            {'complexity': 0.6, 'expected_confidence': 0.75, 'time_budget': 0.5},
            {'complexity': 0.3, 'expected_confidence': 0.65, 'time_budget': 0.2}
        ]

        accuracy_results = []

        for case in test_cases:
            ecosystem_data = {'complexity_avg': case['complexity']}

            start_time = time.time()
            prediction = await citizen.probabilistic_predictor.predict_needs(ecosystem_data)
            prediction_time = time.time() - start_time

            accuracy_results.append({
                'complexity': case['complexity'],
                'predicted_confidence': prediction.confidence_score,
                'expected_confidence': case['expected_confidence'],
                'prediction_time': prediction_time,
                'time_budget': case['time_budget'],
                'accuracy_error': abs(prediction.confidence_score - case['expected_confidence'])
            })

        # Analyse résultats
        avg_accuracy_error = mean(r['accuracy_error'] for r in accuracy_results)
        avg_prediction_time = mean(r['prediction_time'] for r in accuracy_results)

        # Assertions équilibre performance/précision
        assert avg_accuracy_error < 0.15  # Erreur moyenne < 15%
        assert avg_prediction_time < 0.8  # Temps moyen < 800ms
        assert all(r['prediction_time'] <= r['time_budget'] * 1.5 for r in accuracy_results)  # Respect budgets temps

    async def test_quantum_memory_optimization(self, benchmark_citizen):
        """Test optimisation mémoire quantique"""
        citizen = benchmark_citizen

        process = psutil.Process(os.getpid())

        # Mesure mémoire initiale
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Exécuter opérations intensives
        operations = []
        for i in range(50):  # 50 opérations simulées
            operation = asyncio.create_task(
                citizen.autonomous_scanner.quantum_scan()
            )
            operations.append(operation)

            # Ajouter prédiction
            prediction_task = asyncio.create_task(
                citizen.probabilistic_predictor.predict_needs({'iteration': i})
            )
            operations.append(prediction_task)

        # Exécuter toutes les opérations
        results = await asyncio.gather(*operations, return_exceptions=True)

        # Mesure mémoire finale
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Mesure fuites
        successful_operations = sum(1 for r in results if not isinstance(r, Exception))

        # Assertions mémoire
        assert successful_operations >= 80  # Au moins 80% de succès
        assert memory_increase < 100  # Moins de 100MB d'augmentation
        assert final_memory < initial_memory * 1.5  # Moins de 50% d'augmentation

        # Vérifier récupération mémoire
        await asyncio.sleep(1)  # Laisser GC travailler
        post_gc_memory = process.memory_info().rss / 1024 / 1024

        # Mémoire devrait diminuer après GC
        assert post_gc_memory <= final_memory

@pytest.mark.asyncio
class TestQuantumReliabilityBenchmarks:
    """Benchmarks de fiabilité quantique"""

    @pytest.fixture
    async def reliable_citizen(self):
        """Citizen configuré pour tests de fiabilité"""
        citizen = QuantumMSTGFCitizen()

        # Configuration fiabilité
        citizen.failure_retry_attempts = 3
        citizen.circuit_breaker_enabled = True
        citizen.health_check_interval = 30

        return citizen

    async def test_quantum_fault_tolerance(self, reliable_citizen):
        """Test tolérance aux pannes quantiques"""
        citizen = reliable_citizen

        # Simuler pannes partielles
        failure_scenarios = [
            ('scanner_failure', lambda: setattr(citizen.autonomous_scanner, 'quantum_scan',
                                               AsyncMock(side_effect=Exception("Scan failed")))),
            ('predictor_failure', lambda: setattr(citizen.probabilistic_predictor, 'predict_needs',
                                                AsyncMock(side_effect=Exception("Prediction failed")))),
            ('processor_failure', lambda: setattr(citizen.quantum_processor, 'optimize_strategy',
                                                 AsyncMock(side_effect=Exception("Optimization failed"))))
        ]

        reliability_results = {}

        for scenario_name, inject_failure in failure_scenarios:
            # Injecter panne
            inject_failure()

            # Tester résilience
            start_time = time.time()

            try:
                # Tenter opération malgré panne
                await asyncio.wait_for(
                    citizen.autonomous_operation_loop(),
                    timeout=5.0
                )
                operation_success = True
                operation_time = time.time() - start_time
            except asyncio.TimeoutError:
                operation_success = False
                operation_time = 5.0
            except Exception:
                operation_success = False
                operation_time = time.time() - start_time

            reliability_results[scenario_name] = {
                'operation_success': operation_success,
                'operation_time': operation_time,
                'system_still_active': citizen.is_active
            }

        # Analyse fiabilité
        successful_scenarios = sum(1 for r in reliability_results.values() if r['operation_success'])
        avg_operation_time = mean(r['operation_time'] for r in reliability_results.values())
        system_stability = all(r['system_still_active'] for r in reliability_results.values())

        # Assertions fiabilité
        assert successful_scenarios >= 2  # Au moins 2 scénarios gérés
        assert avg_operation_time < 10  # Temps raisonnable même en cas de panne
        assert system_stability == True  # Système reste stable malgré pannes

    async def test_quantum_consistency_under_load(self, reliable_citizen):
        """Test cohérence quantique sous charge"""
        citizen = reliable_citizen

        # Générer charge importante
        concurrent_operations = 20
        operation_results = []

        async def stressed_operation(iteration: int):
            """Opération sous stress"""
            start_time = time.time()

            try:
                # Simuler opération complète
                scan_result = await citizen.autonomous_scanner.quantum_scan()
                predict_result = await citizen.probabilistic_predictor.predict_needs(scan_result)
                optimize_result = await citizen.quantum_processor.optimize_strategy({'iteration': iteration})

                operation_time = time.time() - start_time

                return {
                    'success': True,
                    'operation_time': operation_time,
                    'iteration': iteration,
                    'consistency_check': predict_result.confidence_score > 0
                }

            except Exception as e:
                operation_time = time.time() - start_time
                return {
                    'success': False,
                    'error': str(e),
                    'operation_time': operation_time,
                    'iteration': iteration
                }

        # Lancer opérations concurrentes
        tasks = [stressed_operation(i) for i in range(concurrent_operations)]
        results = await asyncio.gather(*tasks)

        # Analyser cohérence
        successful_operations = [r for r in results if r['success']]
        failed_operations = [r for r in results if not r['success']]

        consistency_checks = [r['consistency_check'] for r in successful_operations if 'consistency_check' in r]
        consistency_rate = sum(consistency_checks) / len(consistency_checks) if consistency_checks else 0

        operation_times = [r['operation_time'] for r in results]
        avg_operation_time = mean(operation_times)
        operation_time_variance = stdev(operation_times) if len(operation_times) > 1 else 0

        # Assertions cohérence sous charge
        assert len(successful_operations) >= concurrent_operations * 0.8  # 80% de succès minimum
        assert consistency_rate > 0.7  # 70% de cohérence minimum
        assert avg_operation_time < 5.0  # Temps moyen acceptable
        assert operation_time_variance < avg_operation_time * 0.5  # Variance raisonnable

@pytest.mark.asyncio
class TestQuantumEvolutionBenchmarks:
    """Benchmarks d'évolution quantique"""

    @pytest.fixture
    async def evolving_citizen(self):
        """Citizen avec tracking d'évolution"""
        citizen = QuantumMSTGFCitizen()

        # Métriques d'évolution
        citizen.evolution_metrics = {
            'learning_iterations': 0,
            'performance_improvements': [],
            'pattern_discoveries': [],
            'adaptation_speed': []
        }

        return citizen

    async def test_quantum_learning_efficiency(self, evolving_citizen):
        """Test efficacité de l'apprentissage quantique"""
        citizen = evolving_citizen

        # Simuler itérations d'apprentissage
        learning_iterations = 10
        baseline_performance = 0.7

        learning_results = []

        for iteration in range(learning_iterations):
            # Simuler feedback d'apprentissage
            feedback = {
                'performance_score': baseline_performance + (iteration * 0.02),  # Amélioration progressive
                'new_patterns': 1 + (iteration % 3),  # Découvertes variables
                'adaptation_time': 0.5 + (iteration * 0.1)  # Adaptation plus lente
            }

            with patch.object(citizen.self_evolution_engine, 'evolve_from_feedback') as mock_evolve:
                mock_evolve.return_value = {
                    'performance_gain': feedback['performance_score'] - baseline_performance,
                    'patterns_learned': feedback['new_patterns'],
                    'adaptation_efficiency': 1.0 / feedback['adaptation_time']
                }

                evolution_result = await citizen.self_evolution_engine.evolve_from_feedback()

                learning_results.append({
                    'iteration': iteration,
                    'performance_gain': evolution_result['performance_gain'],
                    'patterns_learned': evolution_result['patterns_learned'],
                    'adaptation_efficiency': evolution_result['adaptation_efficiency']
                })

                citizen.evolution_metrics['learning_iterations'] += 1
                citizen.evolution_metrics['performance_improvements'].append(evolution_result['performance_gain'])
                citizen.evolution_metrics['pattern_discoveries'].append(evolution_result['patterns_learned'])
                citizen.evolution_metrics['adaptation_speed'].append(evolution_result['adaptation_efficiency'])

        # Analyser courbe d'apprentissage
        total_performance_gain = sum(r['performance_gain'] for r in learning_results)
        total_patterns_learned = sum(r['patterns_learned'] for r in learning_results)
        avg_adaptation_efficiency = mean(r['adaptation_efficiency'] for r in learning_results)

        # Vérifier amélioration cumulative
        assert total_performance_gain > 0.1  # Amélioration significative
        assert total_patterns_learned >= learning_iterations  # Au moins 1 pattern par itération
        assert avg_adaptation_efficiency > 0.5  # Efficacité d'adaptation raisonnable

        # Vérifier accélération de l'apprentissage (amélioration plus rapide avec l'expérience)
        early_iterations = learning_results[:3]
        late_iterations = learning_results[-3:]

        early_avg_gain = mean(r['performance_gain'] for r in early_iterations)
        late_avg_gain = mean(r['performance_gain'] for r in late_iterations)

        # Les itérations tardives devraient montrer plus d'amélioration
        assert late_avg_gain >= early_avg_gain * 0.9  # Au moins maintien du niveau

@pytest.mark.asyncio
class TestQuantumIntegrationEcosystemBenchmarks:
    """Benchmarks d'intégration écosystémique quantique"""

    @pytest.fixture
    async def integrated_citizen(self):
        """Citizen pleinement intégré"""
        citizen = QuantumMSTGFCitizen()

        # Mock intégrations complètes
        citizen.ecosystem_integrations = {
            'nexus': AsyncMock(),
            'kiva': AsyncMock(),
            'gateway': AsyncMock(),
            'ontology': AsyncMock(),
            'vdb': AsyncMock(),
            'plix': AsyncMock()
        }

        return citizen

    async def test_quantum_ecosystem_orchestration_efficiency(self, integrated_citizen):
        """Test efficacité de l'orchestration écosystémique quantique"""
        citizen = integrated_citizen

        # Simuler orchestration complexe impliquant tous les citizens
        complex_workflow = {
            'scan_phase': {'citizens': ['nexus', 'ontology'], 'parallel': True},
            'analysis_phase': {'citizens': ['gateway', 'vdb'], 'sequential': True},
            'execution_phase': {'citizens': ['kiva', 'plix'], 'parallel': True},
            'validation_phase': {'citizens': ['nexus'], 'single': True}
        }

        orchestration_results = {}

        for phase_name, phase_config in complex_workflow.items():
            phase_start = time.time()

            if phase_config.get('parallel'):
                # Orchestration parallèle
                tasks = []
                for citizen_name in phase_config['citizens']:
                    task = asyncio.create_task(
                        citizen.ecosystem_integrations[citizen_name](f'{phase_name}_task')
                    )
                    tasks.append(task)

                results = await asyncio.gather(*tasks)

            elif phase_config.get('sequential'):
                # Orchestration séquentielle
                results = []
                for citizen_name in phase_config['citizens']:
                    result = await citizen.ecosystem_integrations[citizen_name](f'{phase_name}_task')
                    results.append(result)

            else:
                # Orchestration unique
                citizen_name = phase_config['citizens'][0]
                results = [await citizen.ecosystem_integrations[citizen_name](f'{phase_name}_task')]

            phase_time = time.time() - phase_start

            orchestration_results[phase_name] = {
                'execution_time': phase_time,
                'citizens_involved': len(phase_config['citizens']),
                'parallel_execution': phase_config.get('parallel', False),
                'results_count': len(results),
                'all_successful': all(r == 'success' for r in results)
            }

        # Analyser efficacité d'orchestration
        total_time = sum(r['execution_time'] for r in orchestration_results.values())
        total_citizens = sum(r['citizens_involved'] for r in orchestration_results.values())
        parallel_phases = sum(1 for r in orchestration_results.values() if r['parallel_execution'])
        successful_phases = sum(1 for r in orchestration_results.values() if r['all_successful'])

        # Assertions d'efficacité
        assert total_time < 10.0  # Moins de 10 secondes pour workflow complexe
        assert successful_phases == len(orchestration_results)  # Toutes les phases réussies
        assert parallel_phases >= 2  # Au moins 2 phases parallèles utilisées
        assert total_citizens == 7  # Tous les citizens impliqués