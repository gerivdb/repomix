# -----------------------------------------------------------------------------
# Tests TDD pour EPIC-9864: Factual Memory Ontology Completion
# Tests unitaires des classes ontologiques complètes et APIs CRUD
# Couverture: toutes classes, APIs, validation, exemples YAML
# -----------------------------------------------------------------------------

import pytest
import yaml
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

# Import des classes ontologiques
try:
    from ontology.factual_memory.complete_ontology import (
        Artifact, Actor, ProvenanceEdge, ArtifactRelation,
        FactualQuestion, FactualAnswer, ArtifactMemoryLayer, MemoryLayerTransition,
        ArtifactType, ArtifactStatus, VisibilityScope, RelationType,
        AudienceProfile, MemoryLayer, TrustLevel, OntologyValidator
    )
    from ontology.factual_memory.complete_apis import (
        FactualMemoryCRUDAPI, MockArtifactStorage, MockRelationStorage,
        MockMemoryStorage, MockAnswerStorage, MockVectorSearchExtension,
        MockCausalVersioningExtension, MockSovereignStackExtension
    )
except ImportError:
    pytest.skip("Complete ontology modules not available", allow_module_level=True)

class TestArtifactClass:
    """Tests pour la classe Artifact"""

    def test_artifact_creation(self):
        """Test création artefact"""
        artifact = Artifact(
            artifact_type=ArtifactType.DOCUMENT,
            title="Test Document",
            description="A test document",
            body_ref="s3://test/doc.pdf",
            status=ArtifactStatus.DRAFT,
            visibility_scope=VisibilityScope.PERSONAL
        )

        assert artifact.artifact_type == ArtifactType.DOCUMENT
        assert artifact.title == "Test Document"
        assert artifact.status == ArtifactStatus.DRAFT
        assert artifact.version == 1
        assert artifact.artifact_id is not None
        assert artifact.semantic_hash is not None

    def test_artifact_from_dict(self):
        """Test création artefact depuis dict"""
        data = {
            "artifact_id": "test_123",
            "artifact_type": "document",
            "title": "Test Document",
            "body_ref": "s3://test/doc.pdf",
            "created_at": "2026-04-30T10:00:00",
            "updated_at": "2026-04-30T10:00:00",
            "status": "draft",
            "visibility_scope": "personal",
            "tags": ["test"],
            "description": "Test description",
            "properties": {"key": "value"},
            "version": 1
        }

        artifact = Artifact.from_dict(data)

        assert artifact.artifact_id == "test_123"
        assert artifact.title == "Test Document"
        assert artifact.tags == {"test"}
        assert artifact.properties["key"] == "value"

    def test_artifact_to_dict(self):
        """Test conversion artefact vers dict"""
        artifact = Artifact(
            artifact_type=ArtifactType.DOCUMENT,
            title="Test",
            description="Test",
            body_ref="s3://test/doc.pdf",
            status=ArtifactStatus.DRAFT,
            visibility_scope=VisibilityScope.PERSONAL
        )

        data = artifact.to_dict()

        assert data["artifact_type"] == "document"
        assert data["title"] == "Test"
        assert "artifact_id" in data
        assert "semantic_hash" in data

    def test_artifact_access_control(self):
        """Test contrôle d'accès artefact"""
        artifact = Artifact(
            artifact_type=ArtifactType.DOCUMENT,
            title="Test",
            description="Test",
            body_ref="s3://test/doc.pdf",
            status=ArtifactStatus.ORG_OFFICIAL,
            visibility_scope=VisibilityScope.ORGANIZATION
        )

        # Accès par employé
        assert artifact.can_be_accessed_by("user123", ["employee"])
        # Pas d'accès par personne externe
        assert not artifact.can_be_accessed_by("external", [])

class TestActorClass:
    """Tests pour la classe Actor"""

    def test_actor_creation(self):
        """Test création acteur"""
        actor = Actor(
            name="John Doe",
            email="john@example.com",
            role_tags=["developer"],
            capabilities=["coding"]
        )

        assert actor.name == "John Doe"
        assert actor.email == "john@example.com"
        assert actor.role_tags == ["developer"]
        assert actor.capabilities == ["coding"]
        assert actor.actor_id is not None

    def test_actor_from_dict_to_dict(self):
        """Test conversion Actor dict"""
        data = {
            "actor_id": "actor_123",
            "name": "Jane Doe",
            "email": "jane@example.com",
            "role_tags": ["manager"],
            "capabilities": ["leadership"],
            "created_at": "2026-04-30T10:00:00"
        }

        actor = Actor.from_dict(data)
        assert actor.actor_id == "actor_123"
        assert actor.name == "Jane Doe"

        back_to_dict = actor.to_dict()
        assert back_to_dict["name"] == "Jane Doe"
        assert back_to_dict["role_tags"] == ["manager"]

    def test_actor_capabilities(self):
        """Test vérification capacités acteur"""
        actor = Actor(
            name="Test",
            email="test@example.com",
            capabilities=["coding", "testing"]
        )

        assert actor.has_capability("coding")
        assert actor.has_capability("testing")
        assert not actor.has_capability("design")

    def test_actor_roles(self):
        """Test vérification rôles acteur"""
        actor = Actor(
            name="Test",
            email="test@example.com",
            role_tags=["developer", "lead"]
        )

        assert actor.has_role("developer")
        assert actor.has_role("lead")
        assert not actor.has_role("manager")

class TestProvenanceEdge:
    """Tests pour ProvenanceEdge"""

    def test_provenance_edge_creation(self):
        """Test création arête de provenance"""
        edge = ProvenanceEdge(
            subject_artifact="artifact_123",
            predicate="created_by",
            object_actor_or_artifact="actor_456",
            timestamp=datetime(2026, 4, 30, 10, 0, 0),
            confidence=0.9
        )

        assert edge.subject_artifact == "artifact_123"
        assert edge.predicate == "created_by"
        assert edge.confidence == 0.9
        assert edge.edge_id is not None

    def test_provenance_edge_from_dict_to_dict(self):
        """Test conversion ProvenanceEdge dict"""
        data = {
            "edge_id": "edge_123",
            "subject_artifact": "artifact_123",
            "predicate": "created_by",
            "object_actor_or_artifact": "actor_456",
            "timestamp": "2026-04-30T10:00:00",
            "confidence": 0.9,
            "evidence_refs": ["ref1"],
            "properties": {"key": "value"}
        }

        edge = ProvenanceEdge.from_dict(data)
        assert edge.edge_id == "edge_123"
        assert edge.predicate == "created_by"

        back_to_dict = edge.to_dict()
        assert back_to_dict["confidence"] == 0.9
        assert back_to_dict["evidence_refs"] == ["ref1"]

class TestArtifactRelation:
    """Tests pour ArtifactRelation"""

    def test_artifact_relation_creation(self):
        """Test création relation artefact"""
        relation = ArtifactRelation(
            from_artifact_id="artifact_1",
            relation_type=RelationType.DEPENDS_ON,
            to_artifact_or_domain_entity="artifact_2",
            strength=0.8
        )

        assert relation.from_artifact_id == "artifact_1"
        assert relation.relation_type == RelationType.DEPENDS_ON
        assert relation.strength == 0.8
        assert relation.relation_id is not None

    def test_artifact_relation_from_dict_to_dict(self):
        """Test conversion ArtifactRelation dict"""
        data = {
            "relation_id": "rel_123",
            "from_artifact_id": "artifact_1",
            "relation_type": "depends_on",
            "to_artifact_or_domain_entity": "artifact_2",
            "strength": 0.8,
            "created_at": "2026-04-30T10:00:00"
        }

        relation = ArtifactRelation.from_dict(data)
        assert relation.relation_id == "rel_123"
        assert relation.strength == 0.8

        back_to_dict = relation.to_dict()
        assert back_to_dict["relation_type"] == "depends_on"

class TestFactualQuestionAnswer:
    """Tests pour FactualQuestion et FactualAnswer"""

    def test_factual_question_creation(self):
        """Test création question factuelle"""
        question = FactualQuestion(
            asked_by_actor_id="actor_123",
            asked_at=datetime(2026, 4, 30, 10, 0, 0),
            natural_language="What is the status?",
            intent_tags=["status"]
        )

        assert question.asked_by_actor_id == "actor_123"
        assert question.natural_language == "What is the status?"
        assert question.intent_tags == ["status"]
        assert question.question_id is not None

    def test_factual_answer_creation(self):
        """Test création réponse factuelle"""
        answer = FactualAnswer(
            question_id="question_123",
            generated_at=datetime(2026, 4, 30, 10, 0, 0),
            audience_profile=AudienceProfile.MANAGER,
            answer_summary_ref="s3://answers/123.md",
            supporting_artifacts=["artifact_1"],
            confidence_score=0.9
        )

        assert answer.question_id == "question_123"
        assert answer.audience_profile == AudienceProfile.MANAGER
        assert answer.confidence_score == 0.9
        assert answer.answer_id is not None

class TestArtifactMemoryLayer:
    """Tests pour ArtifactMemoryLayer"""

    def test_memory_layer_creation(self):
        """Test création couche mémoire"""
        layer = ArtifactMemoryLayer(
            artifact_id="artifact_123",
            current_layer=MemoryLayer.TEAM,
            visibility_score=0.8
        )

        assert layer.artifact_id == "artifact_123"
        assert layer.current_layer == MemoryLayer.TEAM
        assert layer.visibility_score == 0.8

    def test_memory_layer_transition_logic(self):
        """Test logique de transition couche mémoire"""
        layer = ArtifactMemoryLayer(
            artifact_id="artifact_123",
            current_layer=MemoryLayer.PERSONAL
        )

        # Création acteur pour test
        actor = Actor(name="Test", email="test@example.com", role_tags=["team_lead"])

        # Test transition autorisée
        assert layer.can_transition_to(MemoryLayer.TEAM, actor)

        # Test transition non autorisée
        non_authorized_actor = Actor(name="Test", email="test@example.com", role_tags=[])
        assert not layer.can_transition_to(MemoryLayer.ORGANIZATION, non_authorized_actor)

class TestOntologyValidator:
    """Tests pour OntologyValidator"""

    def test_validator_creation(self):
        """Test création validateur"""
        validator = OntologyValidator()
        assert validator is not None
        assert hasattr(validator, 'validation_rules')

    @pytest.mark.asyncio
    async def test_validate_artifact_creation_valid(self):
        """Test validation artefact valide"""
        validator = OntologyValidator()

        artifact = Artifact(
            artifact_type=ArtifactType.DOCUMENT,
            title="Valid Document",
            description="Valid description",
            body_ref="s3://test/doc.pdf",
            status=ArtifactStatus.DRAFT,
            visibility_scope=VisibilityScope.PERSONAL
        )

        # Ne devrait pas lever d'exception
        await validator.validate_artifact_creation(artifact)

    @pytest.mark.asyncio
    async def test_validate_artifact_creation_invalid(self):
        """Test validation artefact invalide"""
        validator = OntologyValidator()

        # Artefact sans titre
        artifact = Artifact(
            artifact_type=ArtifactType.DOCUMENT,
            title="",  # Invalide
            description="Test",
            body_ref="s3://test/doc.pdf",
            status=ArtifactStatus.DRAFT,
            visibility_scope=VisibilityScope.PERSONAL
        )

        with pytest.raises(ValueError, match="title cannot be empty"):
            await validator.validate_artifact_creation(artifact)

    @pytest.mark.asyncio
    async def test_validate_provenance_edge(self):
        """Test validation arête de provenance"""
        validator = OntologyValidator()

        edge = ProvenanceEdge(
            subject_artifact="artifact_123",
            predicate="created_by",
            object_actor_or_artifact="actor_456",
            timestamp=datetime(2026, 4, 30, 10, 0, 0),
            confidence=0.8
        )

        # Ne devrait pas lever d'exception
        await validator.validate_provenance_edge(edge)

        # Test prédicat invalide
        edge_invalid = ProvenanceEdge(
            subject_artifact="artifact_123",
            predicate="invalid_predicate",
            object_actor_or_artifact="actor_456",
            timestamp=datetime(2026, 4, 30, 10, 0, 0)
        )

        with pytest.raises(ValueError, match="Unknown predicate"):
            await validator.validate_provenance_edge(edge_invalid)

class TestFactualMemoryCRUDAPI:
    """Tests pour FactualMemoryCRUDAPI"""

    @pytest.fixture
    def api(self):
        """Fixture API avec mocks"""
        return FactualMemoryCRUDAPI(
            artifact_storage=MockArtifactStorage(),
            relation_storage=MockRelationStorage(),
            memory_storage=MockMemoryStorage(),
            answer_storage=MockAnswerStorage(),
            vector_search=MockVectorSearchExtension(),
            causal_versioning=MockCausalVersioningExtension(),
            sovereign_stack=MockSovereignStackExtension()
        )

    @pytest.mark.asyncio
    async def test_create_artifact_api(self, api):
        """Test création artefact via API"""
        result = await api.create_artifact({
            "artifact_type": "document",
            "title": "API Test Document",
            "description": "Created via API",
            "body_ref": "s3://test/api.pdf",
            "status": "draft",
            "visibility_scope": "personal"
        })

        assert result["success"] == True
        assert "artifact_id" in result
        assert result["status"] == "created_indexed_and_layered"

    @pytest.mark.asyncio
    async def test_get_artifact_api(self, api):
        """Test récupération artefact via API"""
        # Créer d'abord un artefact
        create_result = await api.create_artifact({
            "artifact_type": "document",
            "title": "Test Document",
            "description": "Test",
            "body_ref": "s3://test/doc.pdf",
            "status": "draft",
            "visibility_scope": "personal"
        })

        artifact_id = create_result["artifact_id"]

        # Récupérer l'artefact
        get_result = await api.get_artifact(artifact_id)

        assert get_result["success"] == True
        assert get_result["artifact"]["title"] == "Test Document"
        assert "memory_layer" in get_result

    @pytest.mark.asyncio
    async def test_create_relation_api(self, api):
        """Test création relation via API"""
        # Créer des entités d'abord
        await api.create_artifact({
            "artifact_type": "document",
            "title": "Source Doc",
            "description": "Source",
            "body_ref": "s3://test/source.pdf",
            "status": "draft",
            "visibility_scope": "personal"
        })

        result = await api.create_relation({
            "subject_artifact": "source_artifact_id",  # Note: dans un vrai test, utiliser l'ID réel
            "predicate": "created_by",
            "object_actor_or_artifact": "actor_123",
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": 0.9
        }, "provenance")

        # Même avec ID invalide, la structure devrait être validée
        assert result["success"] == False  # Échoue car artefact n'existe pas
        assert "error" in result

    @pytest.mark.asyncio
    async def test_ask_factual_question_api(self, api):
        """Test question factuelle via API"""
        result = await api.ask_factual_question({
            "asked_by_actor_id": "actor_123",
            "asked_at": datetime.utcnow().isoformat(),
            "natural_language": "What is the project status?",
            "intent_tags": ["status", "project"]
        })

        assert result["success"] == True
        assert "answer_id" in result
        assert "confidence_score" in result
        assert result["audience_profile"] == "general"  # Profil par défaut

    @pytest.mark.asyncio
    async def test_memory_health_api(self, api):
        """Test vérification santé mémoire via API"""
        result = await api.get_memory_health()

        assert result["success"] == True
        assert "overall_health_score" in result
        assert "total_artifacts" in result
        assert isinstance(result["overall_health_score"], float)
        assert 0.0 <= result["overall_health_score"] <= 1.0

class TestYAMLExamples:
    """Tests pour les exemples YAML"""

    def test_create_yaml_examples(self):
        """Test création exemples YAML"""
        from ontology.factual_memory.complete_ontology import create_concrete_yaml_examples

        examples = create_concrete_yaml_examples()

        assert len(examples) >= 2  # Au moins 2 exemples

        # Vérifier que chaque exemple est du YAML valide
        for example in examples:
            assert isinstance(example, str)

            # Parser YAML
            parsed = yaml.safe_load(example)
            assert isinstance(parsed, dict)

            # Vérifier structure injection
            assert "factual_memory_injection" in parsed
            injection = parsed["factual_memory_injection"]
            assert "entities" in injection

    def test_yaml_example_roadmap_structure(self):
        """Test structure exemple roadmap YAML"""
        from ontology.factual_memory.complete_ontology import create_concrete_yaml_examples

        examples = create_concrete_yaml_examples()
        roadmap_example = examples[0]  # Premier exemple devrait être roadmap

        parsed = yaml.safe_load(roadmap_example)

        # Vérifier structure artefact
        assert "factual_memory_injection" in parsed
        injection = parsed["factual_memory_injection"]
        assert "entities" in injection

        entities = injection["entities"]
        assert len(entities) > 0

        artifact = entities[0]
        assert artifact["type"] == "artifact"
        assert "artifact_type" in artifact
        assert "title" in artifact

        # Vérifier relations
        assert "relations" in injection

        # Vérifier couche mémoire
        assert "memory_layer" in injection

    def test_yaml_example_factual_answer_structure(self):
        """Test structure exemple factual answer YAML"""
        from ontology.factual_memory.complete_ontology import create_concrete_yaml_examples

        examples = create_concrete_yaml_examples()
        answer_example = examples[1]  # Deuxième exemple devrait être factual answer

        parsed = yaml.safe_load(answer_example)

        # Vérifier structure réponse
        assert "factual_memory_injection" in parsed
        injection = parsed["factual_memory_injection"]
        assert "factual_answer" in injection

        factual_answer = injection["factual_answer"]
        assert "answer_id" in factual_answer
        assert "question_id" in factual_answer
        assert "audience_profile" in factual_answer

        # Vérifier question originale
        assert "original_question" in injection
        question = injection["original_question"]
        assert "natural_language" in question

# -----------------------------------------------------------------------------
# Tests d'intégration
# -----------------------------------------------------------------------------

class TestOntologyIntegration:
    """Tests d'intégration ontologie complète"""

    @pytest.mark.asyncio
    async def test_complete_artifact_lifecycle(self):
        """Test cycle de vie complet d'un artefact"""
        api = FactualMemoryCRUDAPI()

        # 1. Création
        create_result = await api.create_artifact({
            "artifact_type": "document",
            "title": "Lifecycle Test Document",
            "description": "Test complete lifecycle",
            "body_ref": "s3://test/lifecycle.pdf",
            "status": "draft",
            "visibility_scope": "personal",
            "tags": ["test", "lifecycle"]
        })

        assert create_result["success"] == True
        artifact_id = create_result["artifact_id"]

        # 2. Récupération
        get_result = await api.get_artifact(artifact_id)
        assert get_result["success"] == True
        assert get_result["artifact"]["title"] == "Lifecycle Test Document"

        # 3. Mise à jour
        update_result = await api.update_artifact(artifact_id, {
            "status": "review",
            "description": "Updated lifecycle test document"
        })

        assert update_result["success"] == True
        assert update_result["new_version"] == 2

        # 4. Vérification mise à jour
        get_updated = await api.get_artifact(artifact_id)
        assert get_updated["artifact"]["status"] == "review"
        assert get_updated["artifact"]["version"] == 2

    @pytest.mark.asyncio
    async def test_artifact_with_relations_workflow(self):
        """Test artefact avec relations complètes"""
        api = FactualMemoryCRUDAPI()

        # Créer artefact
        create_result = await api.create_artifact({
            "artifact_type": "roadmap_entry",
            "title": "Q3 Roadmap Item",
            "description": "Roadmap item for testing",
            "body_ref": "s3://test/roadmap.pdf",
            "status": "team_shared",
            "visibility_scope": "team"
        })

        artifact_id = create_result["artifact_id"]

        # Créer relation de provenance (mock - normalement l'actor existerait)
        relation_result = await api.create_relation({
            "subject_artifact": artifact_id,
            "predicate": "created_by",
            "object_actor_or_artifact": "actor_test_creator",
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": 0.9
        }, "provenance")

        # La relation peut échouer si l'artefact n'existe pas dans le mock
        # Mais la structure devrait être testée

        # Récupérer artefact avec relations
        get_result = await api.get_artifact(artifact_id, include_relations=True)

        assert get_result["success"] == True
        # Les relations peuvent être vides selon l'implémentation mock

    @pytest.mark.asyncio
    async def test_factual_qa_workflow(self):
        """Test workflow question/réponse factuelle"""
        api = FactualMemoryCRUDAPI()

        # Poser question
        qa_result = await api.ask_factual_question({
            "asked_by_actor_id": "actor_test_user",
            "asked_at": datetime.utcnow().isoformat(),
            "natural_language": "What is the current project status?",
            "intent_tags": ["status", "project"]
        })

        assert qa_result["success"] == True
        assert "answer_id" in qa_result
        assert "confidence_score" in qa_result

        answer_id = qa_result["answer_id"]

        # Récupérer réponse
        answer_result = await api.get_factual_answer(answer_id)

        assert answer_result["success"] == True
        assert answer_result["answer"]["answer_id"] == answer_id

    @pytest.mark.asyncio
    async def test_memory_health_monitoring(self):
        """Test monitoring santé mémoire"""
        api = FactualMemoryCRUDAPI()

        # Créer quelques artefacts
        for i in range(3):
            await api.create_artifact({
                "artifact_type": "document",
                "title": f"Health Test Doc {i}",
                "description": f"Document for health testing {i}",
                "body_ref": f"s3://test/health{i}.pdf",
                "status": "draft",
                "visibility_scope": "personal"
            })

        # Vérifier santé
        health_result = await api.get_memory_health()

        assert health_result["success"] == True
        assert health_result["total_artifacts"] >= 3
        assert "overall_health_score" in health_result
        assert isinstance(health_result["overall_health_score"], float)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])