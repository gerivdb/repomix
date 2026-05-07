"""
Tests TDD: Modèle Artefact
EPIC-9860 Factual Memory Ontology
"""
import pytest
from datetime import datetime
from src.ontological_memory.artifact_model import (
    Artifact,
    ArtifactType,
    VisibilityScope,
    ArtifactStatus
)


class TestArtifactModel:
    
    def test_artifact_creation_valid(self):
        """✅ Test création artefact valide"""
        artifact = Artifact(
            artifact_id="art_123",
            artifact_type=ArtifactType.DOCUMENT,
            title="Test Document",
            body_ref="s3://bucket/doc.txt",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status=ArtifactStatus.DRAFT,
            visibility_scope=VisibilityScope.PERSONAL
        )

        assert artifact.artifact_id == "art_123"
        assert artifact.artifact_type == ArtifactType.DOCUMENT
        assert artifact.status == ArtifactStatus.DRAFT
        assert artifact.visibility_scope == VisibilityScope.PERSONAL
    
    def test_artifact_from_dict_valid(self):
        """✅ Test création depuis dictionnaire"""
        data = {
            "artifact_id": "art_456",
            "artifact_type": "ticket",
            "title": "Bug Report",
            "body_ref": "firnflow://docs/bug.txt",
            "created_at": "2026-04-30T10:00:00Z",
            "updated_at": "2026-04-30T11:00:00Z",
            "status": "team_shared",
            "visibility_scope": "team",
            "tags": ["bug", "urgent"]
        }

        artifact = Artifact.from_dict(data)

        assert artifact.artifact_id == "art_456"
        assert artifact.artifact_type == ArtifactType.TICKET
        assert artifact.status == ArtifactStatus.TEAM_SHARED
        assert artifact.tags == ["bug", "urgent"]
    
    def test_artifact_from_dict_invalid_type(self):
        """❌ Test rejet type artefact invalide"""
        data = {
            "artifact_id": "art_789",
            "artifact_type": "invalid_type",
            "title": "Test",
            "body_ref": "s3://test",
            "created_at": "2026-04-30T10:00:00Z",
            "updated_at": "2026-04-30T11:00:00Z",
            "status": "draft",
            "visibility_scope": "personal"
        }

        with pytest.raises(ValueError):
            Artifact.from_dict(data)
    
    def test_artifact_from_dict_missing_required_field(self):
        """❌ Test rejet si champ obligatoire manquant"""
        data = {
            "artifact_id": "art_999",
            # artifact_type manquant
            "title": "Test Missing Field",
            "body_ref": "s3://test",
            "created_at": "2026-04-30T10:00:00Z",
            "updated_at": "2026-04-30T11:00:00Z",
            "status": "draft",
            "visibility_scope": "personal"
        }

        with pytest.raises(ValueError, match="Champ obligatoire manquant: artifact_type"):
            Artifact.from_dict(data)
    
    def test_artifact_is_official(self):
        """✅ Test vérification statut officiel"""
        artifact_official = Artifact(
            artifact_id="art_official",
            artifact_type=ArtifactType.DECISION_RECORD,
            title="Official Decision",
            body_ref="s3://docs/decision.pdf",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status=ArtifactStatus.ORG_OFFICIAL,
            visibility_scope=VisibilityScope.ORGANIZATION
        )
        
        artifact_draft = Artifact(
            artifact_id="art_draft",
            artifact_type=ArtifactType.DOCUMENT,
            title="Draft Document",
            body_ref="s3://docs/draft.txt",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status=ArtifactStatus.DRAFT,
            visibility_scope=VisibilityScope.PERSONAL
        )
        
        assert artifact_official.is_official() is True
        assert artifact_draft.is_official() is False
    
    def test_artifact_visibility_scope_hierarchy(self):
        """✅ Test hiérarchie des scopes de visibilité"""
        artifact_personal = Artifact(
            artifact_id="art_perso",
            artifact_type=ArtifactType.DOCUMENT,
            title="Personal Note",
            body_ref="s3://personal/note.txt",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status=ArtifactStatus.DRAFT,
            visibility_scope=VisibilityScope.PERSONAL
        )
        
        artifact_team = Artifact(
            artifact_id="art_team",
            artifact_type=ArtifactType.DOCUMENT,
            title="Team Document",
            body_ref="s3://team/doc.txt",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status=ArtifactStatus.TEAM_SHARED,
            visibility_scope=VisibilityScope.TEAM
        )
        
        artifact_org = Artifact(
            artifact_id="art_org",
            artifact_type=ArtifactType.DOCUMENT,
            title="Organization Policy",
            body_ref="s3://org/policy.pdf",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status=ArtifactStatus.ORG_OFFICIAL,
            visibility_scope=VisibilityScope.ORGANIZATION
        )
        
        # Artefact personnel visible par tout le monde
        assert artifact_personal.is_visible_for(VisibilityScope.PERSONAL) is True
        assert artifact_personal.is_visible_for(VisibilityScope.TEAM) is True
        assert artifact_personal.is_visible_for(VisibilityScope.ORGANIZATION) is True
        
        # Artefact équipe non visible personnellement
        assert artifact_team.is_visible_for(VisibilityScope.PERSONAL) is False
        assert artifact_team.is_visible_for(VisibilityScope.TEAM) is True
        assert artifact_team.is_visible_for(VisibilityScope.ORGANIZATION) is True
        
        # Artefact organisation uniquement visible au niveau organisation
        assert artifact_org.is_visible_for(VisibilityScope.PERSONAL) is False
        assert artifact_org.is_visible_for(VisibilityScope.TEAM) is False
        assert artifact_org.is_visible_for(VisibilityScope.ORGANIZATION) is True
    
    def test_artifact_serialization_roundtrip(self):
        """✅ Test sérialisation / désérialisation identique"""
        original = Artifact(
            artifact_id="art_roundtrip",
            artifact_type=ArtifactType.INCIDENT,
            title="Incident #789",
            body_ref="s3://incidents/789.json",
            created_at=datetime.fromisoformat("2026-04-30T12:00:00+00:00"),
            updated_at=datetime.fromisoformat("2026-04-30T13:30:00+00:00"),
            status=ArtifactStatus.TEAM_SHARED,
            visibility_scope=VisibilityScope.TEAM,
            tags=["incident", "critical", "network"],
            description="Network outage incident report"
        )
        
        serialized = original.to_dict()
        deserialized = Artifact.from_dict(serialized)
        
        assert deserialized == original