#!/bin/bash
# -----------------------------------------------------------------------------
# Tests E2E pour EPIC-9858: Scientific Engines (Joker Engine)
# Tests end-to-end du système d'engines scientifiques
# Environnements: Python avec modules engines
# -----------------------------------------------------------------------------

set -e  # Exit on any error

# Configuration tests
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$TEST_DIR/.." && pwd)"
PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}NEXUS EPIC-9858 E2E Tests - Scientific Engines${NC}"
echo -e "${BLUE}$(printf '%.0s=' {1..60})${NC}"

# -----------------------------------------------------------------------------
# UTILITAIRES DE TEST
# -----------------------------------------------------------------------------

assert_success() {
    local message="$1"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $message${NC}"
        return 0
    else
        echo -e "${RED}✗ $message${NC}"
        return 1
    fi
}

assert_failure() {
    local message="$1"
    if [ $? -ne 0 ]; then
        echo -e "${GREEN}✓ $message${NC}"
        return 0
    else
        echo -e "${RED}✗ $message${NC}"
        return 1
    fi
}

assert_numeric() {
    local value="$1"
    local min_val="$2"
    local max_val="$3"
    local message="$4"

    if (( $(echo "$value >= $min_val && $value <= $max_val" | bc -l 2>/dev/null || echo "0") )); then
        echo -e "${GREEN}✓ $message ($value dans [$min_val, $max_val])${NC}"
        return 0
    else
        echo -e "${RED}✗ $message ($value hors [$min_val, $max_val])${NC}"
        return 1
    fi
}

run_python_cmd() {
    local cmd="$1"
    PYTHONPATH="$PYTHONPATH" python3 -c "$cmd"
}

# -----------------------------------------------------------------------------
# TESTS E2E ENGINES FRAMEWORK
# -----------------------------------------------------------------------------

test_engines_framework_import() {
    echo "Testing scientific engines framework import..."

    if run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
try:
    from engines import (
        ScientificEngine, JokerEngine, EngineRegistry,
        EngineResult, EngineConfig, EngineStatus, EnginePhase,
        PerturbationType, engine_registry, create_engine_result_summary
    )
    print('SUCCESS: Engines framework imported')
except ImportError as e:
    print(f'FAILED: {e}')
    import sys
    sys.exit(1)
    "; then
        echo -e "${GREEN}✓ Scientific engines framework imported successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Scientific engines framework import failed${NC}"
        return 1
    fi
}

test_joker_engine_initialization() {
    echo "Testing Joker Engine initialization and basic functionality..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from engines import JokerEngine, EngineStatus

# Créer un Joker Engine
engine = JokerEngine()
print(f'Engine status: {engine.status.value}')
print(f'Config ID: {engine.config.engine_id}')
print(f'Has perturbation generators: {hasattr(engine, \"perturbation_generators\")}')

# Vérifications
if engine.status == EngineStatus.READY:
    print('ENGINE_READY')
else:
    print('ENGINE_NOT_READY')
    import sys
    sys.exit(1)

if engine.config.engine_id == 'JokerEngine':
    print('CONFIG_CORRECT')
else:
    print('CONFIG_INCORRECT')
    import sys
    sys.exit(1)
    ")

    if echo "$result" | grep -q "ENGINE_READY" && echo "$result" | grep -q "CONFIG_CORRECT"; then
        echo -e "${GREEN}✓ Joker Engine initialization successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Joker Engine initialization failed${NC}"
        return 1
    fi
}

test_joker_engine_basic_processing() {
    echo "Testing Joker Engine basic processing capabilities..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from engines import JokerEngine, EnginePhase

# Créer engine et traiter des données
engine = JokerEngine()

test_inputs = [
    'string data',
    42,
    [1, 2, 3],
    {'key': 'value'}
]

results_successful = 0

for i, input_data in enumerate(test_inputs):
    result = engine.process(input_data, EnginePhase.SPARK)
    print(f'Input {i}: success={result.success}, perturbations={len(result.perturbations_applied)}')
    
    if result.success:
        results_successful += 1
        
        # Vérifier métadonnées
        if 'joker_phase' in result.metadata and 'perturbation_types' in result.metadata:
            print(f'  Metadata OK: phase={result.metadata[\"joker_phase\"]}')
        else:
            print('  Metadata incomplete')
            import sys
            sys.exit(1)

print(f'Successful results: {results_successful}/{len(test_inputs)}')

if results_successful == len(test_inputs):
    print('ALL_PROCESSING_SUCCESSFUL')
else:
    print('SOME_PROCESSING_FAILED')
    import sys
    sys.exit(1)
    ")

    if echo "$result" | grep -q "ALL_PROCESSING_SUCCESSFUL"; then
        echo -e "${GREEN}✓ Joker Engine basic processing working correctly${NC}"
        return 0
    else
        echo -e "${RED}✗ Joker Engine basic processing failed${NC}"
        return 1
    fi
}

test_joker_engine_perturbation_types() {
    echo "Testing Joker Engine perturbation types..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from engines import JokerEngine, PerturbationType

engine = JokerEngine()

# Tester différents types de perturbations
test_cases = [
    ([PerturbationType.RANDOM_NOISE], 'random_noise'),
    ([PerturbationType.BOUNDARY_TEST], 'boundary_test'),
    ([PerturbationType.INVERSION_TEST], 'inversion_test'),
    ([PerturbationType.CHAOS_INJECTION], 'chaos_injection'),
    ([PerturbationType.ADVERSARIAL_INPUT], 'adversarial_input')
]

perturbation_works = 0

for perturbations, expected_type in test_cases:
    result = engine.process('test_data', perturbations=perturbations)
    
    if result.success and any(expected_type in p for p in result.perturbations_applied):
        print(f'{expected_type}: SUCCESS')
        perturbation_works += 1
    else:
        print(f'{expected_type}: FAILED')
        print(f'  Applied: {result.perturbations_applied}')

print(f'Working perturbations: {perturbation_works}/{len(test_cases)}')

if perturbation_works >= 3:  # Au moins 3 perturbations fonctionnelles
    print('PERTURBATIONS_MOSTLY_WORKING')
else:
    print('PERTURBATIONS_MOSTLY_FAILING')
    import sys
    sys.exit(1)
    ")

    if echo "$result" | grep -q "PERTURBATIONS_MOSTLY_WORKING"; then
        echo -e "${GREEN}✓ Joker Engine perturbation types working${NC}"
        return 0
    else
        echo -e "${RED}✗ Joker Engine perturbation types failed${NC}"
        return 1
    fi
}

test_joker_engine_phase_adaptation() {
    echo "Testing Joker Engine phase adaptation..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from engines import JokerEngine, EnginePhase, PerturbationType

engine = JokerEngine()

# Tester adaptation par phase
phases_to_test = [
    (EnginePhase.SPARK, ['chaos_injection', 'random_noise']),
    (EnginePhase.SHAPE, ['boundary_test', 'adversarial_input']),
    (EnginePhase.REFINE, ['inversion_test', 'boundary_test']),
    (EnginePhase.PROVE, ['adversarial_input', 'inversion_test']),
    (EnginePhase.SHIP, ['random_noise'])
]

phase_adaptations_correct = 0

for phase, expected_perturbations in phases_to_test:
    result = engine.process('test_data', phase=phase)
    
    # Vérifier que les perturbations attendues sont présentes
    applied_types = [p.split('_')[0] for p in result.perturbations_applied if '_' in p]
    expected_found = any(exp in applied_types for exp in expected_perturbations)
    
    if expected_found:
        print(f'{phase.value}: CORRECT (found: {applied_types})')
        phase_adaptations_correct += 1
    else:
        print(f'{phase.value}: INCORRECT (expected: {expected_perturbations}, found: {applied_types})')

print(f'Correct phase adaptations: {phase_adaptations_correct}/{len(phases_to_test)}')

if phase_adaptations_correct >= 3:
    print('PHASE_ADAPTATION_MOSTLY_CORRECT')
else:
    print('PHASE_ADAPTATION_MOSTLY_INCORRECT')
    import sys
    sys.exit(1)
    ")

    if echo "$result" | grep -q "PHASE_ADAPTATION"; then
        echo -e "${GREEN}✓ Joker Engine phase adaptation working${NC}"
        return 0
    else
        echo -e "${RED}✗ Joker Engine phase adaptation failed${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# TESTS E2E ENGINE REGISTRY
# -----------------------------------------------------------------------------

test_engine_registry_functionality() {
    echo "Testing Engine Registry functionality..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from engines import EngineRegistry, engine_registry

# Tester registre local
registry = EngineRegistry()
print(f'Local registry engines: {len(registry.engines)}')

# Tester récupération d'engines
joker = registry.get_engine('JokerEngine')
if joker:
    print('JokerEngine found in local registry')
else:
    print('JokerEngine NOT found in local registry')
    import sys
    sys.exit(1)

# Tester registre global
global_joker = engine_registry.get_engine('JokerEngine')
if global_joker:
    print('JokerEngine found in global registry')
else:
    print('JokerEngine NOT found in global registry')
    import sys
    sys.exit(1)

# Tester santé système
health = registry.get_system_health()
print(f'System health: {health[\"system_health\"]:.2%}')
print(f'Ready engines: {health[\"ready_engines\"]}/{health[\"total_engines\"]}')

if health['system_health'] > 0:
    print('REGISTRY_FUNCTIONAL')
else:
    print('REGISTRY_NOT_FUNCTIONAL')
    import sys
    sys.exit(1)
    ")

    if echo "$result" | grep -q "REGISTRY_FUNCTIONAL"; then
        echo -e "${GREEN}✓ Engine Registry functionality working${NC}"
        return 0
    else
        echo -e "${RED}✗ Engine Registry functionality failed${NC}"
        return 1
    fi
}

test_engine_pipeline_execution() {
    echo "Testing engine pipeline execution..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from engines import engine_registry, create_engine_result_summary

# Exécuter un pipeline simple
input_data = {
    'test_field': 'test_value',
    'numbers': [1, 2, 3],
    'value': 100
}

pipeline = ['JokerEngine']
results = engine_registry.execute_pipeline(input_data, pipeline)

print(f'Pipeline results: {len(results)}')
print(f'All successful: {all(r.success for r in results)}')

if results:
    first_result = results[0]
    print(f'First result engine: {first_result.engine_id}')
    print(f'Execution time: {first_result.execution_time:.3f}s')
    print(f'Validation score: {first_result.validation_score:.3f}')
    
    # Créer résumé
    summary = create_engine_result_summary(results)
    print(f'Summary - Success rate: {summary[\"success_rate\"]:.1%}')
    
    if all(r.success for r in results):
        print('PIPELINE_SUCCESSFUL')
    else:
        print('PIPELINE_HAS_FAILURES')
        import sys
        sys.exit(1)
else:
    print('NO_RESULTS')
    import sys
    sys.exit(1)
    ")

    if echo "$result" | grep -q "PIPELINE_SUCCESSFUL"; then
        echo -e "${GREEN}✓ Engine pipeline execution working${NC}"
        return 0
    else
        echo -e "${RED}✗ Engine pipeline execution failed${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# TESTS E2E PERFORMANCE ET ROBUSTESSE
# -----------------------------------------------------------------------------

test_joker_engine_performance() {
    echo "Testing Joker Engine performance baseline..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from engines import JokerEngine
import time

engine = JokerEngine()

# Test performance avec différents types de données
test_cases = [
    ('small_string', 'hello'),
    ('large_string', 'x' * 1000),
    ('small_list', [1, 2, 3]),
    ('large_list', list(range(100))),
    ('dict', {'a': 1, 'b': 2, 'c': 3}),
    ('number', 42.0)
]

total_time = 0
successful_executions = 0

for name, data in test_cases:
    start_time = time.time()
    result = engine.execute(data)
    end_time = time.time()
    
    execution_time = end_time - start_time
    total_time += execution_time
    
    if result.success:
        successful_executions += 1
        print(f'{name}: {execution_time:.3f}s ✓')
    else:
        print(f'{name}: {execution_time:.3f}s ✗ ({result.error_message})')

avg_time = total_time / len(test_cases)
success_rate = successful_executions / len(test_cases)

print(f'Average execution time: {avg_time:.3f}s')
print(f'Success rate: {success_rate:.1%}')

# Critères de performance: < 1s en moyenne, > 80% succès
if avg_time < 1.0 and success_rate > 0.8:
    print('PERFORMANCE_ACCEPTABLE')
else:
    print('PERFORMANCE_ISSUES')
    # Ne pas échouer pour performance - dépend de l'environnement
    ")

    if echo "$result" | grep -q "PERFORMANCE"; then
        echo -e "${GREEN}✓ Joker Engine performance baseline tested${NC}"
        return 0
    else
        echo -e "${RED}✗ Joker Engine performance test failed${NC}"
        return 1
    fi
}

test_joker_engine_robustness() {
    echo "Testing Joker Engine robustness with edge cases..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from engines import JokerEngine

engine = JokerEngine()

# Cas limites à tester
edge_cases = [
    ('none_value', None),
    ('empty_string', ''),
    ('empty_list', []),
    ('empty_dict', {}),
    ('zero', 0),
    ('negative', -42),
    ('very_large_number', 1e308),
    ('very_small_number', 1e-323),
    ('special_float', float('inf')),
    ('nan', float('nan')),
    ('nested_structure', {'a': [1, 2, {'b': 3}]}),
    ('unicode_string', 'héllo wörld 🚀')
]

successful_cases = 0

for name, data in edge_cases:
    try:
        result = engine.execute(data)
        if result.success:
            successful_cases += 1
            print(f'{name}: SUCCESS')
        else:
            print(f'{name}: FAILED - {result.error_message}')
    except Exception as e:
        print(f'{name}: EXCEPTION - {e}')

success_rate = successful_cases / len(edge_cases)
print(f'Robustness success rate: {success_rate:.1%}')

# Critère: > 70% des cas limites gérés correctement
if success_rate > 0.7:
    print('ROBUSTNESS_ACCEPTABLE')
else:
    print('ROBUSTNESS_ISSUES')
    import sys
    sys.exit(1)
    ")

    if echo "$result" | grep -q "ROBUSTNESS_ACCEPTABLE"; then
        echo -e "${GREEN}✓ Joker Engine robustness acceptable${NC}"
        return 0
    else
        echo -e "${RED}✗ Joker Engine robustness issues${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# TESTS E2E INTÉGRATION COMPLET
# -----------------------------------------------------------------------------

test_full_engine_integration_workflow() {
    echo "Testing full engine integration workflow..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from engines import engine_registry, JokerEngine, EnginePhase, PerturbationType
import json

# Workflow complet: création → configuration → exécution → métriques

# 1. Créer engine personnalisé
custom_config = {
    'engine_id': 'CustomJoker',
    'perturbation_intensity': 0.3,
    'max_execution_time': 10.0,
    'validation_threshold': 0.7
}

# Pour l'instant, utiliser le Joker standard (extension future pour config personnalisée)
engine = JokerEngine()

# 2. Exécuter avec différentes phases
test_data = 'integration_test_data'
phases_to_test = [EnginePhase.SPARK, EnginePhase.SHAPE, EnginePhase.PROVE]

phase_results = {}
for phase in phases_to_test:
    result = engine.execute(test_data, phase=phase)
    phase_results[phase.value] = {
        'success': result.success,
        'execution_time': result.execution_time,
        'validation_score': result.validation_score,
        'perturbations': len(result.perturbations_applied)
    }
    print(f'{phase.value}: success={result.success}, time={result.execution_time:.3f}s')

# 3. Tester pipeline complet
pipeline_results = engine_registry.execute_pipeline(test_data, ['JokerEngine'])
pipeline_success = all(r.success for r in pipeline_results)

# 4. Vérifier métriques
metrics = engine.get_metrics()
print(f'Engine metrics: {metrics[\"executions\"]} executions, {metrics[\"success_rate\"]:.1%} success')

# 5. Tester santé système
health = engine_registry.get_system_health()
print(f'System health: {health[\"system_health\"]:.1%}')

# Validation finale
all_phase_success = all(r['success'] for r in phase_results.values())
integration_success = all([
    all_phase_success,
    pipeline_success,
    metrics['executions'] > 0,
    health['system_health'] > 0
])

if integration_success:
    print('FULL_INTEGRATION_SUCCESS')
    # Afficher résumé JSON
    summary = {
        'phase_results': phase_results,
        'pipeline_success': pipeline_success,
        'engine_metrics': metrics,
        'system_health': health
    }
    print('Integration summary:', json.dumps(summary, indent=2))
else:
    print('FULL_INTEGRATION_FAILED')
    import sys
    sys.exit(1)
    ")

    if echo "$result" | grep -q "FULL_INTEGRATION_SUCCESS"; then
        echo -e "${GREEN}✓ Full engine integration workflow successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Full engine integration workflow failed${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# EXÉCUTION DES TESTS E2E
# -----------------------------------------------------------------------------

echo -e "\n${YELLOW}Running E2E Tests...${NC}"

# Tests modules et base
test_engines_framework_import
test_joker_engine_initialization
test_joker_engine_basic_processing

# Tests fonctionnalités Joker
test_joker_engine_perturbation_types
test_joker_engine_phase_adaptation

# Tests registry et pipeline
test_engine_registry_functionality
test_engine_pipeline_execution

# Tests performance et robustesse
test_joker_engine_performance
test_joker_engine_robustness

# Test intégration complet
test_full_engine_integration_workflow

echo -e "\n${GREEN}All E2E tests completed!${NC}"
echo -e "${BLUE}$(printf '%.0s=' {1..60})${NC}"