#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ TESTS TDD GOST ENGINE EPIC-1179
Conforme standard NEXUS TDD v3.0

Spécifications testées:
  👻 Invisibilité opérationnelle
  🧹 Effacement traces vérifiable
  📜 Preuves zéro-connaissance
  🎭 Masquage signature opérationnelle
"""
import sys
import pytest
import hashlib

# Ajout chemin engines
sys.path.insert(0, '.')
from engines.gost_engine import GostEngine


class TestGostEngineTDD:
    """
    Tests TDD unitaires GOST ENGINE
    Conforme: EPIC-1179 PERTURBATION LAYER
    """

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.gost = GostEngine()

    def test_initialization_activates_ghost_mode(self):
        """✅ TDD 1: Initialisation active mode fantôme"""
        status = self.gost.get_gost_status()
        assert status["ghost_mode_active"] is True
        assert status["current_visibility_level"] == 0.0

    def test_create_ghost_operation_zero_visibility(self):
        """✅ TDD 2: Opération fantôme a visibilité nulle"""
        op = self.gost.create_ghost_operation("test_op", visibility=0.0)

        assert op["visibility_level"] == 0.0
        assert op["ghost_mode_active"] is True
        assert op["auto_cleanup"] is True
        assert len(op["operation_id"]) == 36

    def test_erase_trace_returns_valid_hash(self):
        """✅ TDD 3: Effacement trace retourne hash vérification valide"""
        erasure = self.gost.erase_trace("/test/path", trace_type="log")

        assert erasure["erasure_complete"] is True
        assert erasure["no_trace_remaining"] is True
        assert len(erasure["verification_hash"]) == 64  # SHA256

    def test_zk_proof_absolute_deniability(self):
        """✅ TDD 4: Preuve ZK 0% révélation = déniabilité absolue"""
        proof = self.gost.generate_zk_proof("statement_valid", reveal_percentage=0.0)

        assert proof["proof_valid"] is True
        assert proof["revealed_information"] == 0.0
        assert proof["absolute_plausible_deniability"] is True

    def test_zk_proof_partial_revelation(self):
        """✅ TDD 5: Preuve ZK révélation partielle fonctionne"""
        proof = self.gost.generate_zk_proof("statement_valid", reveal_percentage=0.3)

        assert proof["revealed_information"] == 0.3
        assert proof["absolute_plausible_deniability"] is False

    def test_signature_masking_works(self):
        """✅ TDD 6: Masquage signature retourne masque valide"""
        mask = self.gost.mask_operational_signature("automated_script")

        assert mask["mask_applied"] == "automated_script"
        assert mask["original_signature_hidden"] is True
        assert mask["plausible_deniability"] == 0.98

    def test_status_returns_correct_metrics(self):
        """✅ TDD 7: État moteur retourne métriques correctes"""
        # Générer quelques opérations
        self.gost.create_ghost_operation("op1")
        self.gost.create_ghost_operation("op2")
        self.gost.erase_trace("/path1")

        status = self.gost.get_gost_status()

        assert status["ghost_operations_active"] == 2
        assert status["traces_permanently_erased"] == 1
        assert status["zk_proofs_generated"] == 0


if __name__ == "__main__":
    print("\n🧪 TESTS TDD GOST ENGINE")
    print("=" * 60)

    pytest.main([__file__, "-v", "-x"])