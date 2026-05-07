#!/usr/bin/env python3
"""
DEV ENGINE - Test Suite E2E TDD
EPIC-1176 | arXiv:2604.24658v2

Tests complets de la spécification ARA /src Layer
"""

import pytest
import hashlib
from datetime import datetime

from engines.dev_engine import DevEngine, Artifact, Lifecycle, ArtifactState
from engines.dev_engine import DependencyGraph, ArtifactDependency, DependencyStrength


class TestDevEngineEndToEnd:
    """
    Suite de tests E2E complète conforme aux standards NEXUS TDD
    """

    def test_engine_initialization(self):
        """✅ Test 1: Initialisation propre du moteur"""
        engine = DevEngine()
        assert engine is not None
        assert engine.total_count() == 0
        assert engine.executable_count() == 0
        assert engine.storage_path.exists()

    def test_artifact_lifecycle_complete(self):
        """✅ Test 2: Cycle de vie complet d'un artefact"""
        lifecycle = Lifecycle()
        
        assert lifecycle.state == ArtifactState.PROPOSED
        assert len(lifecycle.state_history) == 1
        
        lifecycle.transition(ArtifactState.VALIDATED)
        lifecycle.transition(ArtifactState.COMPILED)
        lifecycle.transition(ArtifactState.EXECUTABLE)
        
        assert lifecycle.is_executable == True
        assert len(lifecycle.state_history) == 4
        assert lifecycle.age >= 0

    def test_artifact_cryptographic_identity(self):
        """✅ Test 3: Identité cryptographique immuable"""
        artifact = Artifact(
            artifact_id="test-001",
            name="Test Artefact",
            version="1.0.0"
        )
        
        test_content = b"Native ARA executable artifact"
        hash_result = artifact.compute_hash(test_content)
        
        assert hash_result == hashlib.blake2b(test_content).hexdigest()
        assert artifact.content_hash == hash_result
        assert hash(artifact) == hash(("test-001", "1.0.0", hash_result))

    def test_dependency_graph_no_cycles(self):
        """✅ Test 4: Graphe de dépendances sans cycle"""
        graph = DependencyGraph()
        
        graph.add_dependency(ArtifactDependency("a", "b", DependencyStrength.HARD))
        graph.add_dependency(ArtifactDependency("b", "c", DependencyStrength.HARD))
        graph.add_dependency(ArtifactDependency("c", "d", DependencyStrength.HARD))
        
        assert graph.has_cycle() == False
        assert graph.validate_all() == True
        assert len(graph) == 4

    def test_dependency_graph_detect_cycles(self):
        """✅ Test 5: Détection automatique des cycles"""
        graph = DependencyGraph()
        
        graph.add_dependency(ArtifactDependency("a", "b", DependencyStrength.HARD))
        graph.add_dependency(ArtifactDependency("b", "c", DependencyStrength.HARD))
        graph.add_dependency(ArtifactDependency("c", "a", DependencyStrength.HARD))
        
        assert graph.has_cycle() == True
        assert graph.validate_all() == False

    def test_complete_integration_end_to_end(self):
        """✅ Test 6: Flux complet E2E ARA standard"""
        engine = DevEngine()
        
        # Créer un artefact
        artifact = Artifact(
            artifact_id="ara-demo-001",
            name="Premier artefact ARA natif NEXUS",
            version="0.1.0"
        )
        
        # Calculer son empreinte
        artifact.compute_hash(b"Executable content")
        
        # Ajouter des dépendances
        artifact.dependencies.add_dependency(
            ArtifactDependency("ara-demo-001", "prim-engine", DependencyStrength.HARD)
        )
        
        # Enregistrer
        engine.register(artifact)
        
        # Valider
        validation_result = engine.validate("ara-demo-001")
        
        assert validation_result == True
        assert engine.get("ara-demo-001").lifecycle.state == ArtifactState.VALIDATED
        assert engine.total_count() == 1

    def test_all_imports_and_interface(self):
        """✅ Test 7: Interface publique complète"""
        from engines.dev_engine import __all__ as public_interface
        
        required = ['DevEngine', 'Artifact', 'Lifecycle', 'ArtifactState', 'DependencyGraph']
        assert all(x in public_interface for x in required)
        assert len(public_interface) == 7


if __name__ == "__main__":
    print("🧪 DEV ENGINE TEST SUITE E2E")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "-x"])