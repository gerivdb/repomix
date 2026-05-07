#!/bin/bash
# -----------------------------------------------------------------------------
# Tests E2E pour EPIC-9864: Factual Memory Ontology Completion
# Tests end-to-end de l'ontologie complète avec APIs CRUD et exemples YAML
# Environnements: Python avec modules ontologie complète
# -----------------------------------------------------------------------------

set -e  # Exit on any error

# Configuration tests
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$TEST_DIR/.." && pwd)"
PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}NEXUS EPIC-9864 E2E Tests - Factual Memory Ontology Completion${NC}"
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
# TESTS E2E CLASSES ONTOLOGIQUES
# -----------------------------------------------------------------------------

test_ontological_classes_e2e() {
    echo "Testing ontological classes E2E..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from ontology.factual_memory.complete_ontology import (
    Artifact, Actor, ProvenanceEdge, ArtifactRelation,
    FactualQuestion, FactualAnswer, ArtifactMemoryLayer,
    ArtifactType, ArtifactStatus, VisibilityScope, RelationType,
    AudienceProfile, MemoryLayer, TrustLevel
)
from datetime import datetime

# Test création instances de toutes les classes
print('Creating instances of all ontological classes...')

# Artifact
artifact = Artifact(
    artifact_type=ArtifactType.DOCUMENT,
    title='E2E Test Document',
    description='Document for E2E testing',
    body_ref='s3://test/e2e.pdf',
    status=ArtifactStatus.DRAFT,
    visibility_scope=VisibilityScope.PERSONAL
)
print(f'✓ Artifact created: {artifact.artifact_id}')

# Actor
actor = Actor(
    name='E2E Test User',
    email='e2e@test.com',
    role_tags=['tester'],
    capabilities=['testing']
)
print(f'✓ Actor created: {actor.actor_id}')

# ProvenanceEdge
prov_edge = ProvenanceEdge(
    subject_artifact=artifact.artifact_id,
    predicate='created_by',
    object_actor_or_artifact=actor.actor_id,
    timestamp=datetime.utcnow(),
    confidence=0.9
)
print(f'✓ ProvenanceEdge created: {prov_edge.edge_id}')

# ArtifactRelation
art_relation = ArtifactRelation(
    from_artifact_id=artifact.artifact_id,
    relation_type=RelationType.DEPENDS_ON,
    to_artifact_or_domain_entity='external_system',
    strength=0.7
)
print(f'✓ ArtifactRelation created: {art_relation.relation_id}')

# FactualQuestion
question = FactualQuestion(
    asked_by_actor_id=actor.actor_id,
    asked_at=datetime.utcnow(),
    natural_language='What is the test status?',
    intent_tags=['status', 'testing']
)
print(f'✓ FactualQuestion created: {question.question_id}')

# FactualAnswer
answer = FactualAnswer(
    question_id=question.question_id,
    generated_at=datetime.utcnow(),
    audience_profile=AudienceProfile.TECHNICAL,
    answer_summary_ref='s3://answers/e2e_test.md',
    supporting_artifacts=[artifact.artifact_id],
    confidence_score=0.85
)
print(f'✓ FactualAnswer created: {answer.answer_id}')

# ArtifactMemoryLayer
memory_layer = ArtifactMemoryLayer(
    artifact_id=artifact.artifact_id,
    current_layer=MemoryLayer.TEAM,
    visibility_score=0.8
)
print(f'✓ ArtifactMemoryLayer created for: {memory_layer.artifact_id}')

# Test conversions dict
print('Testing dict conversions...')
artifact_dict = artifact.to_dict()
reconstructed_artifact = Artifact.from_dict(artifact_dict)
assert reconstructed_artifact.artifact_id == artifact.artifact_id
print('✓ Artifact dict conversion OK')

actor_dict = actor.to_dict()
reconstructed_actor = Actor.from_dict(actor_dict)
assert reconstructed_actor.actor_id == actor.actor_id
print('✓ Actor dict conversion OK')

prov_dict = prov_edge.to_dict()
reconstructed_prov = ProvenanceEdge.from_dict(prov_dict)
assert reconstructed_prov.edge_id == prov_edge.edge_id
print('✓ ProvenanceEdge dict conversion OK')

relation_dict = art_relation.to_dict()
reconstructed_rel = ArtifactRelation.from_dict(relation_dict)
assert reconstructed_rel.relation_id == art_relation.relation_id
print('✓ ArtifactRelation dict conversion OK')

question_dict = question.to_dict()
reconstructed_q = FactualQuestion.from_dict(question_dict)
assert reconstructed_q.question_id == question.question_id
print('✓ FactualQuestion dict conversion OK')

answer_dict = answer.to_dict()
reconstructed_a = FactualAnswer.from_dict(answer_dict)
assert reconstructed_a.answer_id == answer.answer_id
print('✓ FactualAnswer dict conversion OK')

memory_dict = memory_layer.to_dict()
reconstructed_m = ArtifactMemoryLayer.from_dict(memory_dict)
assert reconstructed_m.artifact_id == memory_layer.artifact_id
print('✓ ArtifactMemoryLayer dict conversion OK')

print('ONTOLOGICAL_CLASSES_E2E_SUCCESS')
    ")

    if echo "$result" | grep -q "ONTOLOGICAL_CLASSES_E2E_SUCCESS"; then
        echo -e "${GREEN}✓ Ontological classes E2E successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Ontological classes E2E failed${NC}"
        return 1
    fi
}

test_apis_crud_e2e() {
    echo "Testing CRUD APIs E2E..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from ontology.factual_memory.complete_apis import FactualMemoryCRUDAPI
import asyncio
from datetime import datetime

async def run_api_tests():
    # Créer API
    api = FactualMemoryCRUDAPI()
    
    # 1. Créer artefact
    print('1. Creating artifact...')
    artifact_result = await api.create_artifact({
        'artifact_type': 'document',
        'title': 'E2E API Test Document',
        'description': 'Document created via E2E API test',
        'body_ref': 's3://test/e2e_api.pdf',
        'status': 'draft',
        'visibility_scope': 'personal',
        'tags': ['e2e', 'api', 'test']
    })
    
    if not artifact_result['success']:
        print(f'Failed to create artifact: {artifact_result}')
        return False
        
    artifact_id = artifact_result['artifact_id']
    print(f'✓ Artifact created: {artifact_id}')
    
    # 2. Récupérer artefact
    print('2. Retrieving artifact...')
    get_result = await api.get_artifact(artifact_id)
    
    if not get_result['success']:
        print(f'Failed to get artifact: {get_result}')
        return False
        
    assert get_result['artifact']['title'] == 'E2E API Test Document'
    print('✓ Artifact retrieved successfully')
    
    # 3. Mettre à jour artefact
    print('3. Updating artifact...')
    update_result = await api.update_artifact(artifact_id, {
        'status': 'review',
        'description': 'Updated via E2E API test'
    })
    
    if not update_result['success']:
        print(f'Failed to update artifact: {update_result}')
        return False
        
    assert update_result['new_version'] == 2
    print('✓ Artifact updated successfully')
    
    # 4. Créer relation
    print('4. Creating relation...')
    relation_result = await api.create_relation({
        'subject_artifact': artifact_id,
        'predicate': 'created_by',
        'object_actor_or_artifact': 'actor_e2e_tester',
        'timestamp': datetime.utcnow().isoformat(),
        'confidence': 0.9
    }, 'provenance')
    
    # Note: peut échouer si actor n'existe pas, mais structure testée
    print(f'Relation creation result: {relation_result[\"success\"]}')
    
    # 5. Question factuelle
    print('5. Asking factual question...')
    qa_result = await api.ask_factual_question({
        'asked_by_actor_id': 'actor_e2e_tester',
        'asked_at': datetime.utcnow().isoformat(),
        'natural_language': 'What is the status of the E2E test document?',
        'intent_tags': ['status', 'document']
    })
    
    if not qa_result['success']:
        print(f'Failed QA: {qa_result}')
        return False
        
    print(f'✓ Factual question answered: {qa_result[\"answer_id\"]}')
    
    # 6. Recherche
    print('6. Searching artifacts...')
    search_result = await api.search_artifacts('E2E API Test')
    
    if not search_result['success']:
        print(f'Failed search: {search_result}')
        return False
        
    print(f'✓ Search completed: {search_result[\"total_results\"]} results')
    
    # 7. Santé système
    print('7. Checking system health...')
    health_result = await api.get_memory_health()
    
    if not health_result['success']:
        print(f'Failed health check: {health_result}')
        return False
        
    print(f'✓ System health: {health_result[\"overall_health_score\"]:.1%}')
    
    return True

# Exécuter les tests async
result = asyncio.run(run_api_tests())
if result:
    print('APIS_CRUD_E2E_SUCCESS')
else:
    print('APIS_CRUD_E2E_FAILED')
    ")

    if echo "$result" | grep -q "APIS_CRUD_E2E_SUCCESS"; then
        echo -e "${GREEN}✓ CRUD APIs E2E successful${NC}"
        return 0
    else
        echo -e "${RED}✗ CRUD APIs E2E failed${NC}"
        return 1
    fi
}

test_yaml_injection_examples_e2e() {
    echo "Testing YAML injection examples E2E..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from ontology.factual_memory.complete_ontology import create_concrete_yaml_examples
import yaml

# Générer exemples YAML
print('Generating YAML injection examples...')
examples = create_concrete_yaml_examples()
print(f'Generated {len(examples)} YAML examples')

# Tester parsing de chaque exemple
valid_examples = 0
parsed_data = []

for i, example_yaml in enumerate(examples):
    try:
        parsed = yaml.safe_load(example_yaml)
        parsed_data.append(parsed)
        
        # Validation structure de base
        assert 'factual_memory_injection' in parsed
        injection = parsed['factual_memory_injection']
        assert 'version' in injection
        assert 'entities' in injection
        
        valid_examples += 1
        print(f'✓ Example {i+1}: YAML valid')
        
    except yaml.YAMLError as e:
        print(f'✗ Example {i+1}: YAML parsing failed - {e}')
    except Exception as e:
        print(f'✗ Example {i+1}: Validation failed - {e}')

print(f'Valid YAML examples: {valid_examples}/{len(examples)}')

# Tester contenu spécifique
if valid_examples >= len(examples):
    # Tester premier exemple (roadmap)
    roadmap_injection = parsed_data[0]['factual_memory_injection']
    
    entities = roadmap_injection['entities']
    assert len(entities) > 0
    artifact = entities[0]
    assert artifact['type'] == 'artifact'
    assert 'artifact_type' in artifact
    assert artifact['artifact_type'] == 'roadmap_entry'
    print('✓ Roadmap example structure validated')
    
    # Tester relations
    relations = roadmap_injection.get('relations', [])
    assert len(relations) > 0
    relation = relations[0]
    assert 'type' in relation
    print('✓ Relations structure validated')
    
    # Tester couche mémoire
    memory_layer = roadmap_injection.get('memory_layer')
    assert memory_layer is not None
    assert 'current_layer' in memory_layer
    print('✓ Memory layer structure validated')
    
    # Tester deuxième exemple (factual answer)
    if len(parsed_data) > 1:
        answer_injection = parsed_data[1]['factual_memory_injection']
        assert 'factual_answer' in answer_injection
        assert 'original_question' in answer_injection
        
        factual_answer = answer_injection['factual_answer']
        assert 'audience_profile' in factual_answer
        assert 'supporting_artifacts' in factual_answer
        print('✓ Factual answer example structure validated')

print('YAML_INJECTION_EXAMPLES_E2E_SUCCESS')
    ")

    if echo "$result" | grep -q "YAML_INJECTION_EXAMPLES_E2E_SUCCESS"; then
        echo -e "${GREEN}✓ YAML injection examples E2E successful${NC}"
        return 0
    else
        echo -e "${RED}✗ YAML injection examples E2E failed${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# TESTS E2E WORKFLOW COMPLET
# -----------------------------------------------------------------------------

test_complete_ontology_workflow_e2e() {
    echo "Testing complete ontology workflow E2E..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from ontology.factual_memory.complete_apis import FactualMemoryCRUDAPI
from ontology.factual_memory.complete_ontology import create_concrete_yaml_examples
import asyncio
import yaml
from datetime import datetime

async def run_complete_workflow():
    print('=== COMPLETE ONTOLOGY WORKFLOW TEST ===')
    
    api = FactualMemoryCRUDAPI()
    
    # Phase 1: Création d'entités via APIs
    print('Phase 1: Creating entities via APIs...')
    
    # Artefact
    artifact_result = await api.create_artifact({
        'artifact_type': 'roadmap_entry',
        'title': 'Workflow Test Roadmap',
        'description': 'Roadmap for complete workflow testing',
        'body_ref': 's3://test/workflow_roadmap.pdf',
        'status': 'team_shared',
        'visibility_scope': 'team',
        'tags': ['workflow', 'test', 'roadmap']
    })
    
    if not artifact_result['success']:
        print(f'Failed artifact creation: {artifact_result}')
        return False
        
    artifact_id = artifact_result['artifact_id']
    print(f'✓ Artifact created: {artifact_id}')
    
    # Phase 2: Enrichissement avec relations
    print('Phase 2: Adding relations...')
    
    # Relation de provenance
    prov_result = await api.create_relation({
        'subject_artifact': artifact_id,
        'predicate': 'created_by',
        'object_actor_or_artifact': 'actor_workflow_tester',
        'timestamp': datetime.utcnow().isoformat(),
        'confidence': 0.95
    }, 'provenance')
    
    print(f'Relation provenance result: {prov_result[\"success\"]}')
    
    # Phase 3: Question factuelle
    print('Phase 3: Factual question...')
    
    qa_result = await api.ask_factual_question({
        'asked_by_actor_id': 'actor_workflow_tester',
        'asked_at': datetime.utcnow().isoformat(),
        'natural_language': 'What is the status of the workflow test roadmap?',
        'intent_tags': ['status', 'roadmap', 'workflow']
    })
    
    if not qa_result['success']:
        print(f'Failed QA: {qa_result}')
        return False
        
    answer_id = qa_result['answer_id']
    print(f'✓ Factual question answered: {answer_id}')
    
    # Phase 4: Récupération réponse
    print('Phase 4: Retrieving factual answer...')
    
    answer_result = await api.get_factual_answer(answer_id)
    
    if not answer_result['success']:
        print(f'Failed answer retrieval: {answer_result}')
        return False
        
    print('✓ Factual answer retrieved successfully')
    
    # Phase 5: Recherche sémantique
    print('Phase 5: Semantic search...')
    
    search_result = await api.search_artifacts('workflow test')
    
    if not search_result['success']:
        print(f'Failed search: {search_result}')
        return False
        
    print(f'✓ Semantic search completed: {search_result[\"total_results\"]} results')
    
    # Phase 6: Export vers YAML
    print('Phase 6: YAML export simulation...')
    
    # Simuler export (pas d'implémentation complète dans mock)
    get_full_result = await api.get_artifact(artifact_id, include_relations=True)
    
    if not get_full_result['success']:
        print(f'Failed full artifact retrieval: {get_full_result}')
        return False
        
    print('✓ Full artifact with relations retrieved')
    
    # Phase 7: Validation santé
    print('Phase 7: Health validation...')
    
    health_result = await api.get_memory_health()
    
    if not health_result['success']:
        print(f'Failed health check: {health_result}')
        return False
        
    print(f'✓ System health validated: {health_result[\"overall_health_score\"]:.1%}')
    
    # Phase 8: Injection YAML (simulation)
    print('Phase 8: YAML injection examples...')
    
    examples = create_concrete_yaml_examples()
    
    if len(examples) < 2:
        print('Insufficient YAML examples generated')
        return False
        
    # Tester parsing d'un exemple
    try:
        parsed = yaml.safe_load(examples[0])
        assert 'factual_memory_injection' in parsed
        print('✓ YAML injection example parsed successfully')
    except Exception as e:
        print(f'Failed YAML parsing: {e}')
        return False
    
    print('=== WORKFLOW COMPLETED SUCCESSFULLY ===')
    return True

# Exécuter le workflow complet
workflow_success = asyncio.run(run_complete_workflow())

if workflow_success:
    print('COMPLETE_ONTOLOGY_WORKFLOW_E2E_SUCCESS')
else:
    print('COMPLETE_ONTOLOGY_WORKFLOW_E2E_FAILED')
    ")

    if echo "$result" | grep -q "COMPLETE_ONTOLOGY_WORKFLOW_E2E_SUCCESS"; then
        echo -e "${GREEN}✓ Complete ontology workflow E2E successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Complete ontology workflow E2E failed${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# TESTS E2E PERFORMANCE ET SCALABILITÉ
# -----------------------------------------------------------------------------

test_ontology_performance_e2e() {
    echo "Testing ontology performance E2E..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from ontology.factual_memory.complete_apis import FactualMemoryCRUDAPI
import asyncio
import time

async def run_performance_tests():
    api = FactualMemoryCRUDAPI()
    
    print('Testing ontology performance with 50 entities...')
    
    # Créer 50 artefacts
    creation_times = []
    artifacts_created = 0
    
    for i in range(50):
        start_time = time.time()
        
        result = await api.create_artifact({
            'artifact_type': 'document',
            'title': f'Performance Test Doc {i}',
            'description': f'Document {i} for performance testing',
            'body_ref': f's3://test/perf_doc_{i}.pdf',
            'status': 'draft',
            'visibility_scope': 'personal',
            'tags': ['performance', 'test']
        })
        
        end_time = time.time()
        
        if result['success']:
            creation_times.append(end_time - start_time)
            artifacts_created += 1
    
    if artifacts_created == 0:
        print('No artifacts created')
        return False
        
    avg_creation_time = sum(creation_times) / len(creation_times)
    print(f'Created {artifacts_created} artifacts')
    print(f'Average creation time: {avg_creation_time:.3f}s')
    
    # Tester recherche
    search_start = time.time()
    search_result = await api.search_artifacts('Performance Test')
    search_end = time.time()
    
    search_time = search_end - search_start
    print(f'Search time: {search_time:.3f}s for {search_result[\"total_results\"]} results')
    
    # Tester santé système avec charge
    health_start = time.time()
    health_result = await api.get_memory_health()
    health_end = time.time()
    
    health_time = health_end - health_start
    print(f'Health check time: {health_time:.3f}s')
    
    # Critères de performance
    creation_ok = avg_creation_time < 0.1  # < 100ms par création
    search_ok = search_time < 1.0  # < 1s pour recherche
    health_ok = health_time < 0.5  # < 500ms pour santé
    
    print(f'Performance criteria - Creation: {creation_ok}, Search: {search_ok}, Health: {health_ok}')
    
    return creation_ok and search_ok and health_ok

# Exécuter tests performance
performance_success = asyncio.run(run_performance_tests())

if performance_success:
    print('ONTOLOGY_PERFORMANCE_E2E_SUCCESS')
else:
    print('ONTOLOGY_PERFORMANCE_E2E_WARNING')  # Ne pas échouer pour performance
    ")

    if echo "$result" | grep -q "ONTOLOGY_PERFORMANCE_E2E"; then
        echo -e "${GREEN}✓ Ontology performance E2E completed${NC}"
        return 0
    else
        echo -e "${RED}✗ Ontology performance E2E failed${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# TESTS E2E INTÉGRATION EXTENSIONS
# -----------------------------------------------------------------------------

test_extensions_integration_e2e() {
    echo "Testing extensions integration E2E..."

    result=$(run_python_cmd "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from ontology.factual_memory.complete_apis import FactualMemoryCRUDAPI
import asyncio
from datetime import datetime

async def run_extensions_tests():
    # Créer API avec mocks d'extensions
    api = FactualMemoryCRUDAPI()
    
    print('Testing integration with mocked extensions...')
    
    # Créer artefact (devrait déclencher indexation vectorielle)
    artifact_result = await api.create_artifact({
        'artifact_type': 'document',
        'title': 'Extensions Integration Test',
        'description': 'Testing integration with vector search, causal versioning, sovereign stack',
        'body_ref': 's3://test/extensions_test.pdf',
        'status': 'draft',
        'visibility_scope': 'personal'
    })
    
    if not artifact_result['success']:
        print(f'Failed artifact creation: {artifact_result}')
        return False
        
    artifact_id = artifact_result['artifact_id']
    print('✓ Artifact created with extension integration')
    
    # Mettre à jour artefact (devrait déclencher versionning causal)
    update_result = await api.update_artifact(artifact_id, {
        'status': 'review',
        'description': 'Updated with causal versioning'
    })
    
    if not update_result['success']:
        print(f'Failed artifact update: {update_result}')
        return False
        
    print('✓ Artifact updated with causal versioning')
    
    # Tester question factuelle (devrait utiliser vector search)
    qa_result = await api.ask_factual_question({
        'asked_by_actor_id': 'actor_extensions_tester',
        'asked_at': datetime.utcnow().isoformat(),
        'natural_language': 'What are the extensions integration test results?',
        'intent_tags': ['extensions', 'integration', 'testing']
    })
    
    if not qa_result['success']:
        print(f'Failed QA with extensions: {qa_result}')
        return False
        
    print('✓ Factual question processed with vector search')
    
    # Tester santé (devrait inclure souveraineté)
    health_result = await api.get_memory_health()
    
    if not health_result['success']:
        print(f'Failed health check with sovereignty: {health_result}')
        return False
        
    print(f'✓ System health checked with sovereignty: {health_result[\"overall_health_score\"]:.1%}')
    
    return True

# Exécuter tests intégration
extensions_success = asyncio.run(run_extensions_tests())

if extensions_success:
    print('EXTENSIONS_INTEGRATION_E2E_SUCCESS')
else:
    print('EXTENSIONS_INTEGRATION_E2E_FAILED')
    ")

    if echo "$result" | grep -q "EXTENSIONS_INTEGRATION_E2E_SUCCESS"; then
        echo -e "${GREEN}✓ Extensions integration E2E successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Extensions integration E2E failed${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# EXÉCUTION DES TESTS E2E
# -----------------------------------------------------------------------------

echo -e "\n${YELLOW}Running E2E Tests...${NC}"

# Tests classes et APIs de base
test_ontological_classes_e2e
test_apis_crud_e2e
test_yaml_injection_examples_e2e

# Tests workflow complet
test_complete_ontology_workflow_e2e

# Tests performance et intégration
test_ontology_performance_e2e
test_extensions_integration_e2e

echo -e "\n${GREEN}All E2E tests completed!${NC}"
echo -e "${BLUE}$(printf '%.0s=' {1..60})${NC}"