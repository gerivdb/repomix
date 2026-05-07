# -----------------------------------------------------------------------------
# Tests TDD pour EPIC-9860: Factual Memory Ontology
# Tests unitaires du système de mémoire factuelle avec APIs CRUD sémantiques
# Couverture: entités, relations, requêtes, QA system, YAML injections
# -----------------------------------------------------------------------------

import pytest
import yaml
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import des modules de mémoire factuelle
try:
    from ontology.factual_memory import (
        FactualMemory, SemanticEntity, SemanticRelation,
        MemoryQuery, QueryResult, MemoryQASystem,
        MemoryType, SemanticRelation as RelType, ConfidenceLevel
    )
    from ontology.factual_memory.api import FactualMemoryAPI, AdvancedQASystem
    from ontology.factual_memory.yaml_examples import generate_brain_docs_injection_examples
except ImportError:
    pytest.skip("Factual memory modules not available", allow_module_level=True)

class TestSemanticEntity:
    """Tests pour SemanticEntity"""

    def test_semantic_entity_creation(self):
        """Test création d'entité sémantique"""
        entity = SemanticEntity(
            id="test_entity",
            type=MemoryType.ARTIFACT,
            name="Test Entity",
            description="A test entity"
        )

        assert entity.id == "test_entity"
        assert entity.type == MemoryType.ARTIFACT
        assert entity.name == "Test Entity"
        assert entity.description == "A test entity"
        assert entity.confidence == ConfidenceLevel.MEDIUM
        assert isinstance(entity.created_at, datetime)

    def test_semantic_entity_auto_id(self):
        """Test génération automatique d'ID"""
        entity = SemanticEntity(
            type=MemoryType.ARTIFACT,
            name="Test Entity",
            description="A test entity"
        )

        assert entity.id is not None
        assert len(entity.id) > 0

    def test_semantic_entity_semantic_hash(self):
        """Test calcul du hash sémantique"""
        entity = SemanticEntity(
            type=MemoryType.ARTIFACT,
            name="Test Entity",
            description="A test entity"
        )

        semantic_hash = entity.semantic_hash
        assert isinstance(semantic_hash, str)
        assert len(semantic_hash) == 16  # 16 caractères hex

        # Hash devrait être déterministe
        hash2 = entity.semantic_hash
        assert semantic_hash == hash2

class TestSemanticRelation:
    """Tests pour SemanticRelation"""

    def test_semantic_relation_creation(self):
        """Test création de relation sémantique"""
        relation = SemanticRelation(
            source_id="source",
            target_id="target",
            relation_type=RelType.CREATES
        )

        assert relation.source_id == "source"
        assert relation.target_id == "target"
        assert relation.relation_type == RelType.CREATES
        assert relation.strength == 1.0
        assert relation.bidirectional == False

    def test_semantic_relation_auto_id(self):
        """Test génération automatique d'ID de relation"""
        relation = SemanticRelation(
            source_id="source",
            target_id="target",
            relation_type=RelType.CREATES
        )

        expected_id = "source_creates_target"
        assert relation.id == expected_id

class TestFactualMemory:
    """Tests pour FactualMemory"""

    def test_factual_memory_creation(self):
        """Test création de la mémoire factuelle"""
        memory = FactualMemory()

        assert len(memory.entities) == 0
        assert len(memory.relations) == 0
        assert len(memory.memory_stats) > 0

    def test_create_and_read_entity(self):
        """Test création et lecture d'entité"""
        memory = FactualMemory()

        entity = SemanticEntity(
            type=MemoryType.ARTIFACT,
            name="Test Artifact",
            description="Test description"
        )

        # Création
        entity_id = memory.create_entity(entity)
        assert entity_id is not None

        # Lecture
        retrieved = memory.read_entity(entity_id)
        assert retrieved is not None
        assert retrieved.name == "Test Artifact"
        assert retrieved.type == MemoryType.ARTIFACT

    def test_update_entity(self):
        """Test mise à jour d'entité"""
        memory = FactualMemory()

        entity = SemanticEntity(
            type=MemoryType.ARTIFACT,
            name="Original Name",
            description="Original description"
        )

        entity_id = memory.create_entity(entity)

        # Mise à jour
        success = memory.update_entity(entity_id, {"name": "Updated Name"})
        assert success == True

        # Vérification
        updated = memory.read_entity(entity_id)
        assert updated.name == "Updated Name"
        assert updated.description == "Original description"  # Non modifié
        assert updated.version == 2

    def test_delete_entity(self):
        """Test suppression d'entité"""
        memory = FactualMemory()

        entity = SemanticEntity(
            type=MemoryType.ARTIFACT,
            name="Test",
            description="Test"
        )

        entity_id = memory.create_entity(entity)
        assert memory.read_entity(entity_id) is not None

        # Suppression
        success = memory.delete_entity(entity_id)
        assert success == True

        # Vérification
        assert memory.read_entity(entity_id) is None

    def test_create_and_read_relation(self):
        """Test création et lecture de relation"""
        memory = FactualMemory()

        # Créer les entités d'abord
        entity1 = SemanticEntity(type=MemoryType.ARTOR, name="Entity1", description="Test")
        entity2 = SemanticEntity(type=MemoryType.ARTIFACT, name="Entity2", description="Test")

        id1 = memory.create_entity(entity1)
        id2 = memory.create_entity(entity2)

        # Créer la relation
        relation = SemanticRelation(
            source_id=id1,
            target_id=id2,
            relation_type=RelType.CREATES
        )

        relation_id = memory.create_relation(relation)
        assert relation_id is not None

        # Lecture
        retrieved = memory.read_relation(relation_id)
        assert retrieved is not None
        assert retrieved.source_id == id1
        assert retrieved.target_id == id2

    def test_relation_validation(self):
        """Test validation des relations (entités doivent exister)"""
        memory = FactualMemory()

        relation = SemanticRelation(
            source_id="nonexistent",
            target_id="also_nonexistent",
            relation_type=RelType.CREATES
        )

        with pytest.raises(ValueError, match="Source entity.*does not exist"):
            memory.create_relation(relation)

    def test_memory_query_entities(self):
        """Test requête d'entités"""
        memory = FactualMemory()

        # Créer des entités
        entity1 = SemanticEntity(type=MemoryType.ARTIFACT, name="Python Script", description="A script")
        entity2 = SemanticEntity(type=MemoryType.ACTOR, name="Developer", description="A person")

        memory.create_entity(entity1)
        memory.create_entity(entity2)

        # Requête par type
        query = MemoryQuery(query_type="entity", filters={"type": "artifact"})
        result = memory.query(query)

        assert len(result.entities) == 1
        assert result.entities[0].type == MemoryType.ARTIFACT

    def test_memory_query_relations(self):
        """Test requête de relations"""
        memory = FactualMemory()

        # Créer entités et relation
        entity1 = SemanticEntity(type=MemoryType.ACTOR, name="Creator", description="Test")
        entity2 = SemanticEntity(type=MemoryType.ARTIFACT, name="Creation", description="Test")

        id1 = memory.create_entity(entity1)
        id2 = memory.create_entity(entity2)

        relation = SemanticRelation(source_id=id1, target_id=id2, relation_type=RelType.CREATES)
        memory.create_relation(relation)

        # Requête de relations
        query = MemoryQuery(query_type="relation", filters={"relation_type": "creates"})
        result = memory.query(query)

        assert len(result.relations) == 1
        assert result.relations[0].relation_type == RelType.CREATES

    def test_memory_stats(self):
        """Test statistiques de mémoire"""
        memory = FactualMemory()

        # Créer quelques entités
        for i in range(3):
            entity = SemanticEntity(type=MemoryType.ARTIFACT, name=f"Entity{i}", description="Test")
            memory.create_entity(entity)

        stats = memory.get_memory_stats()

        assert stats["total_entities"] == 3
        assert stats["total_relations"] == 0
        assert "entity_types" in stats
        assert stats["entity_types"]["artifact"] == 3

class TestFactualMemoryAPI:
    """Tests pour FactualMemoryAPI"""

    def test_api_creation(self):
        """Test création de l'API"""
        api = FactualMemoryAPI()
        assert api.memory is not None

    def test_create_artifact_api(self):
        """Test création d'artefact via API"""
        api = FactualMemoryAPI()

        artifact_id = api.create_artifact(
            name="Test Artifact",
            description="Test description",
            properties={"version": "1.0"},
            tags=["test", "api"]
        )

        assert artifact_id is not None

        # Vérifier que l'entité existe
        entity = api.memory.read_entity(artifact_id)
        assert entity is not None
        assert entity.name == "Test Artifact"
        assert "test" in entity.tags
        assert entity.properties["version"] == "1.0"

    def test_create_actor_api(self):
        """Test création d'acteur via API"""
        api = FactualMemoryAPI()

        actor_id = api.create_actor(
            name="Test Actor",
            description="Test actor",
            actor_type="ai",
            capabilities=["testing", "analysis"]
        )

        entity = api.memory.read_entity(actor_id)
        assert entity.type == MemoryType.ACTOR
        assert entity.properties["actor_type"] == "ai"
        assert "testing" in entity.properties["capabilities"]

    def test_create_relation_api(self):
        """Test création de relation via API"""
        api = FactualMemoryAPI()

        # Créer des entités
        entity1_id = api.create_artifact("Entity1", "Test")
        entity2_id = api.create_artifact("Entity2", "Test")

        # Créer relation
        relation_id = api.create_relation(
            source_id=entity1_id,
            target_id=entity2_id,
            relation_type="depends_on",
            strength=0.8
        )

        relation = api.memory.read_relation(relation_id)
        assert relation.relation_type == RelType.DEPENDS_ON
        assert relation.strength == 0.8

    def test_link_creator_api(self):
        """Test liaison créateur via API"""
        api = FactualMemoryAPI()

        creator_id = api.create_actor("Creator", "Test creator")
        artifact_id = api.create_artifact("Artifact", "Test artifact")

        relation_id = api.link_creator(creator_id, artifact_id, "development")

        relation = api.memory.read_relation(relation_id)
        assert relation.relation_type == RelType.CREATES
        assert relation.properties["creation_context"] == "development"

    def test_find_artifacts_api(self):
        """Test recherche d'artefacts via API"""
        api = FactualMemoryAPI()

        # Créer des artefacts
        api.create_artifact("Python Script", "A script", tags=["python", "script"])
        api.create_artifact("Java Class", "A class", tags=["java", "class"])
        api.create_artifact("Python Module", "A module", tags=["python", "module"])

        # Recherche par tags
        artifacts = api.find_artifacts(tags=["python"])
        assert len(artifacts) == 2

        # Recherche par nom
        scripts = api.find_artifacts(name_pattern="Script")
        assert len(scripts) == 1
        assert scripts[0].name == "Python Script"

    def test_find_created_by_api(self):
        """Test recherche d'artefacts créés par un acteur"""
        api = FactualMemoryAPI()

        creator_id = api.create_actor("Creator", "Test creator")

        # Créer plusieurs artefacts
        artifact1_id = api.create_artifact("Artifact1", "Test")
        artifact2_id = api.create_artifact("Artifact2", "Test")

        # Lier le créateur
        api.link_creator(creator_id, artifact1_id)
        api.link_creator(creator_id, artifact2_id)

        # Recherche
        created_artifacts = api.find_created_by(creator_id)
        assert len(created_artifacts) == 2

    def test_analyze_connectivity_api(self):
        """Test analyse de connectivité via API"""
        api = FactualMemoryAPI()

        # Créer un réseau d'entités connectées
        center_id = api.create_artifact("Center", "Central entity")

        # Créer des connexions
        connected_ids = []
        for i in range(3):
            connected_id = api.create_artifact(f"Connected{i}", f"Connected entity {i}")
            connected_ids.append(connected_id)
            api.create_relation(center_id, connected_id, "uses")

        # Analyser la connectivité
        connectivity = api.analyze_connectivity(center_id)

        assert connectivity["entity_id"] == center_id
        assert connectivity["outgoing_relations"] == 3
        assert connectivity["connected_entities"] == 3

class TestMemoryQASystem:
    """Tests pour MemoryQASystem"""

    def test_qa_system_creation(self):
        """Test création du système QA"""
        from ontology.factual_memory import factual_memory
        qa = MemoryQASystem(factual_memory)

        assert qa.memory is factual_memory
        assert len(qa.qa_templates) > 0

    def test_qa_simple_question(self):
        """Test question simple via QA system"""
        from ontology.factual_memory import factual_memory
        qa = MemoryQASystem(factual_memory)

        # Question simple (devrait retourner réponse par défaut car peu de données)
        response = qa.ask("What is NEXUS?")

        assert "answer" in response
        assert "confidence" in response
        assert response["confidence"] >= 0.0

    def test_qa_unsupported_question(self):
        """Test question non supportée"""
        from ontology.factual_memory import factual_memory
        qa = MemoryQASystem(factual_memory)

        response = qa.ask("How to cook spaghetti?")

        assert "answer" in response
        assert "I ne comprends pas" in response["answer"] or "understand" in response["answer"]

class TestYAMLExamples:
    """Tests pour les exemples YAML"""

    def test_generate_yaml_examples(self):
        """Test génération des exemples YAML"""
        examples = generate_brain_docs_injection_examples()

        assert len(examples) >= 5  # Au moins 5 exemples

        # Vérifier que chaque exemple est du YAML valide
        for example in examples:
            assert isinstance(example, str)
            assert len(example) > 0

            # Tester le parsing YAML
            parsed = yaml.safe_load(example)
            assert "factual_memory_injection" in parsed
            assert "entities" in parsed["factual_memory_injection"]

    def test_yaml_example_structure(self):
        """Test structure des exemples YAML"""
        examples = generate_brain_docs_injection_examples()

        first_example = yaml.safe_load(examples[0])

        injection = first_example["factual_memory_injection"]
        assert "version" in injection
        assert "timestamp" in injection
        assert "confidence" in injection
        assert "entities" in injection
        assert "injection_context" in injection

        # Vérifier structure d'entité
        if injection["entities"]:
            entity = injection["entities"][0]
            required_fields = ["id", "type", "name", "description", "properties", "tags"]
            for field in required_fields:
                assert field in entity

class TestMemoryPersistence:
    """Tests pour la persistance de la mémoire"""

    def test_memory_export_import(self):
        """Test export/import de la mémoire"""
        memory = FactualMemory()

        # Créer des données
        entity = SemanticEntity(type=MemoryType.ARTIFACT, name="Test", description="Test")
        entity_id = memory.create_entity(entity)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name

        try:
            # Export
            memory.export_to_json(export_file)

            # Créer nouvelle mémoire et importer
            new_memory = FactualMemory()
            new_memory.import_from_json(export_file)

            # Vérifier
            imported_entity = new_memory.read_entity(entity_id)
            assert imported_entity is not None
            assert imported_entity.name == "Test"

        finally:
            if os.path.exists(export_file):
                os.unlink(export_file)

class TestAdvancedQASystem:
    """Tests pour AdvancedQASystem"""

    def test_advanced_qa_creation(self):
        """Test création du système QA avancé"""
        api = FactualMemoryAPI()
        advanced_qa = AdvancedQASystem(api)

        assert advanced_qa.api == api

    def test_advanced_qa_complexity_analysis(self):
        """Test analyse de complexité des questions"""
        api = FactualMemoryAPI()
        advanced_qa = AdvancedQASystem(api)

        # Question simple
        complexity = advanced_qa._analyze_question_complexity("What is NEXUS?")
        assert complexity < 0.5

        # Question complexe
        complexity = advanced_qa._analyze_question_complexity(
            "How does the impact of SCE compliance affect the evolution of scientific engines?"
        )
        assert complexity > 0.7

    def test_advanced_qa_inference_handling(self):
        """Test gestion des questions avec inférence"""
        api = FactualMemoryAPI()
        advanced_qa = AdvancedQASystem(api)

        # Ajouter des données de test
        sce_id = api.create_artifact("SCE Framework", "Scientific compliance framework")
        engine_id = api.create_artifact("Scientific Engines", "Engine suite")
        api.link_dependency("Scientific Engines", "SCE Framework")

        # Question complexe
        response = advanced_qa.ask_advanced(
            "How does SCE compliance impact scientific engine development?",
            {"audience": "technical"}
        )

        assert "answer" in response
        assert response.get("inference_used", False)

# -----------------------------------------------------------------------------
# Tests d'intégration
# -----------------------------------------------------------------------------

class TestFactualMemoryIntegration:
    """Tests d'intégration de la mémoire factuelle"""

    def test_complete_workflow(self):
        """Test workflow complet de la mémoire factuelle"""
        api = FactualMemoryAPI()

        # 1. Créer des acteurs et artefacts
        kilo_id = api.create_actor("Kilo Assistant", "AI coding assistant",
                                  capabilities=["coding", "testing", "documentation"])

        sce_id = api.create_artifact("SCE Framework", "Compliance framework",
                                   properties={"compliance_score": 22.07})

        engine_id = api.create_artifact("Scientific Engines", "Engine suite",
                                      properties={"engines_count": 8})

        # 2. Créer des relations
        api.link_creator(kilo_id, sce_id, "implementation")
        api.link_creator(kilo_id, engine_id, "architecture")
        api.link_dependency(engine_id, sce_id, "functional")

        # 3. Effectuer des recherches
        artifacts = api.find_artifacts()
        assert len(artifacts) == 2

        created_by_kilo = api.find_created_by(kilo_id)
        assert len(created_by_kilo) == 2

        dependencies = api.find_dependencies(engine_id)
        assert len(dependencies) == 1

        # 4. Analyser la connectivité
        connectivity = api.analyze_connectivity(kilo_id)
        assert connectivity["outgoing_relations"] == 2

        # 5. Tester le QA system
        from ontology.factual_memory import memory_qa
        response = memory_qa.ask("What is SCE Framework?")
        assert response is not None

        print("Complete workflow test passed")

    def test_memory_scalability(self):
        """Test scalabilité de la mémoire"""
        memory = FactualMemory()

        # Créer beaucoup d'entités
        entity_ids = []
        for i in range(100):
            entity = SemanticEntity(
                type=MemoryType.ARTIFACT,
                name=f"Entity{i}",
                description=f"Test entity {i}"
            )
            entity_id = memory.create_entity(entity)
            entity_ids.append(entity_id)

        # Vérifier que toutes les entités sont accessibles
        for entity_id in entity_ids:
            entity = memory.read_entity(entity_id)
            assert entity is not None

        # Vérifier les statistiques
        stats = memory.get_memory_stats()
        assert stats["total_entities"] == 100

        # Test de recherche
        query = MemoryQuery(query_type="entity", filters={"type": "artifact"})
        result = memory.query(query)
        assert len(result.entities) == 100

if __name__ == "__main__":
    pytest.main([__file__, "-v"])