"""
Tests unitaires nexus_kfe_interface.py
IntentHash: 0xNEXUS_SYNC_FINAL_φ1.0
"""
import json
from pathlib import Path
import pytest
from tools.nexus_kfe_interface import get_active_repos, get_dispatch_matrix, get_gap_harvest_entities


class TestNexusKFEInterface:
    def test_get_active_repos_returns_list(self):
        repos = get_active_repos()
        assert isinstance(repos, list)
        assert len(repos) >= 42
        assert all(isinstance(r, dict) for r in repos)
        assert all("name" in r for r in repos)

    def test_get_active_repos_excludes_archived(self):
        repos = get_active_repos()
        for repo in repos:
            assert repo.get("lifecycle") != "ARCHIVED"

    def test_appflowy_mcp_server_present(self):
        repos = get_active_repos()
        names = [r["name"] for r in repos]
        assert "appflowy-mcp-server" in names
        appflowy = next(r for r in repos if r["name"] == "appflowy-mcp-server")
        assert appflowy["lifecycle"] == "ACTIVE"
        assert appflowy["criticality"] == "P2_SUPPORT"
        assert "mcp_server" in appflowy["flags"]

    def test_get_dispatch_matrix_structure(self):
        matrix = get_dispatch_matrix()
        assert isinstance(matrix, dict)
        assert "ECOYSTEM" in matrix
        assert "NEXUS" in matrix
        assert "appflowy-mcp-server" in matrix
        for entry in matrix.values():
            assert "layer" in entry
            assert "criticality" in entry

    def test_get_gap_harvest_entities(self):
        gap = get_gap_harvest_entities()
        assert isinstance(gap, dict)
        assert "entities" in gap
        assert len(gap["entities"]) > 0
        assert "citizens" in gap["entities"]
        assert "daemons" in gap["entities"]
        assert "pipelines" in gap["entities"]
        assert "skills" in gap["entities"]

    def test_validate_kfe_schema_returns_empty_list_when_all_good(self):
        gaps = validate_kfe_schema()
        assert isinstance(gaps, list)
        assert len(gaps) == 0

    def test_validate_kfe_schema_detects_missing_fields(self, monkeypatch):
        from tools import nexus_kfe_interface
        original = nexus_kfe_interface.get_active_repos

        def mock_bad_repos():
            repos = original()
            repos[0].pop("layer")
            return repos

        monkeypatch.setattr(nexus_kfe_interface, "get_active_repos", mock_bad_repos)
        gaps = validate_kfe_schema()
        assert len(gaps) >= 1
        assert "layer" in gaps[0]["missing"]

    def test_validate_kfe_schema_checks_all_required_fields(self):
        gaps = validate_kfe_schema()
        # Le schema est valide
        assert len(gaps) == 0
        # Vérifier que les champs sont bien présents sur tous les repos
        for repo in get_active_repos():
            assert "layer" in repo
            assert "criticality" in repo
            assert "lifecycle" in repo
            assert "tier" in repo
