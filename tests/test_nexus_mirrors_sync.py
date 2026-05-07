# tests/test_nexus_mirrors_sync.py
# Repo: gerivdb/NEXUS | IntentHash: 0xNEXUS_SYNC_E2_φ95.0
# Closes: #1256 | IntentSource: direct

import json
import sys
import pytest
from pathlib import Path

# DUAL-PATH IMPORTS (R2)
try:
    from tools.nexus_reciprocity_check import (
        check_ecoystem, check_ontology, patch_ecoystem, patch_ontology
    )
    from tools.nexus_mirror_trigger import trigger
except ImportError:
    from nexus_reciprocity_check import (  # type: ignore
        check_ecoystem, check_ontology, patch_ecoystem, patch_ontology
    )
    from nexus_mirror_trigger import trigger  # type: ignore

# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sot_minimal():
    return {
        "source_of_truth": "gerivdb/NEXUS@ecosystem/registry/ECOS_ROOT.json",
        "repos": {"core": ["NEXUS", "KIVA"]},
        "layers": {"L1_CAUSALITY": ["NEXUS", "KIVA"]},
        "criticality": {"P0_CONSTITUTIONAL": ["NEXUS", "KIVA"]},
    }

@pytest.fixture
def mirror_ecos_sync(sot_minimal):
    """Mirror parfaitement en sync avec le SOT."""
    # Deep copy to avoid shared object issues in tests
    return json.loads(json.dumps({
        "source_of_truth": sot_minimal["source_of_truth"],
        "repos": sot_minimal["repos"],
        "layers": sot_minimal["layers"],
        "criticality": sot_minimal["criticality"],
        "version": "3.3.0",
    }))

@pytest.fixture
def mirror_ecos_drift(sot_minimal):
    """Mirror avec drift: repo manquant dans BLO."""
    return json.loads(json.dumps({
        "source_of_truth": sot_minimal["source_of_truth"],
        "repos": {"core": ["KIVA"]},  # NEXUS manquant
        "layers": sot_minimal["layers"],
        "criticality": sot_minimal["criticality"],
        "version": "3.3.0",
    }))

@pytest.fixture
def mirror_onto_sync():
    """ONTOLOGY mirror avec NEXUS ACTIVE SOT."""
    return {
        "source_of_truth": "gerivdb/NEXUS@ecosystem/registry/ECOS_ROOT.json",
        "repos_connected": [{
            "name": "NEXUS",
            "bridge_status": "ACTIVE",
            "role": "source_of_truth",
            "layer": "L1_CAUSALITY",
            "criticality": "P0_CONSTITUTIONAL",
        }],
    }

@pytest.fixture
def mirror_onto_drift():
    """ONTOLOGY mirror sans NEXUS."""
    return {
        "repos_connected": [],
    }

# ── Tests check_ecoystem ────────────────────────────────────────────────────

def test_ecoystem_no_drift(sot_minimal, mirror_ecos_sync):
    r = check_ecoystem(sot_minimal, mirror_ecos_sync)
    assert r["has_drift"] is False
    assert r["drift_count"] == 0
    assert r["severity"] == "CRITICAL"
    assert r["mirror"] == "ecoystem"

def test_ecoystem_missing_repo(sot_minimal, mirror_ecos_drift):
    r = check_ecoystem(sot_minimal, mirror_ecos_drift)
    assert r["has_drift"] is True
    assert r["severity"] == "CRITICAL"
    fields = [d["field"] for d in r["drifts"]]
    assert "repos.core" in fields

def test_ecoystem_source_of_truth_mismatch(sot_minimal, mirror_ecos_sync):
    mirror_ecos_sync["source_of_truth"] = "wrong/repo"
    r = check_ecoystem(sot_minimal, mirror_ecos_sync)
    assert r["has_drift"] is True
    types = [d["type"] for d in r["drifts"]]
    assert "value_mismatch" in types

def test_ecoystem_extra_repo_in_mirror(sot_minimal, mirror_ecos_sync):
    mirror_ecos_sync["repos"]["core"].append("UNKNOWN_REPO")
    r = check_ecoystem(sot_minimal, mirror_ecos_sync)
    assert r["has_drift"] is True
    types = [d["type"] for d in r["drifts"]]
    assert "extra_in_mirror" in types

# ── Tests check_ontology ────────────────────────────────────────────────────

def test_ontology_no_drift(sot_minimal, mirror_onto_sync):
    r = check_ontology(sot_minimal, mirror_onto_sync)
    assert r["has_drift"] is False
    assert r["severity"] == "WARNING"
    assert r["mirror"] == "ontology"

def test_ontology_missing_nexus(sot_minimal, mirror_onto_drift):
    r = check_ontology(sot_minimal, mirror_onto_drift)
    assert r["has_drift"] is True
    fields = [d["field"] for d in r["drifts"]]
    assert "repos_connected[NEXUS]" in fields

def test_ontology_wrong_bridge_status(sot_minimal, mirror_onto_sync):
    mirror_onto_sync["repos_connected"][0]["bridge_status"] = "INACTIVE"
    r = check_ontology(sot_minimal, mirror_onto_sync)
    assert r["has_drift"] is True

def test_ontology_wrong_role(sot_minimal, mirror_onto_sync):
    mirror_onto_sync["repos_connected"][0]["role"] = "observer"
    r = check_ontology(sot_minimal, mirror_onto_sync)
    assert r["has_drift"] is True

# ── Tests patch_ecoystem ────────────────────────────────────────────────────

def test_patch_ecoystem_fixes_drift(sot_minimal, mirror_ecos_drift):
    patched = patch_ecoystem(sot_minimal, mirror_ecos_drift)
    r = check_ecoystem(sot_minimal, patched)
    assert r["has_drift"] is False

def test_patch_ecoystem_bumps_version(sot_minimal, mirror_ecos_drift):
    patched = patch_ecoystem(sot_minimal, mirror_ecos_drift)
    assert patched["version"] == "3.3.1"

def test_patch_ecoystem_wal_entry(sot_minimal, mirror_ecos_drift):
    patched = patch_ecoystem(sot_minimal, mirror_ecos_drift)
    assert len(patched.get("WAL", [])) > 0
    assert patched["WAL"][-1]["event"] == "NEXUS_AUTO_SYNC"

# ── Tests patch_ontology ────────────────────────────────────────────────────

def test_patch_ontology_adds_nexus(sot_minimal, mirror_onto_drift):
    patched = patch_ontology(sot_minimal, mirror_onto_drift)
    nexus_entries = [r for r in patched["repos_connected"] if r["name"] == "NEXUS"]
    assert len(nexus_entries) == 1
    assert nexus_entries[0]["bridge_status"] == "ACTIVE"
    assert nexus_entries[0]["role"] == "source_of_truth"

def test_patch_ontology_no_drift_after_patch(sot_minimal, mirror_onto_drift):
    patched = patch_ontology(sot_minimal, mirror_onto_drift)
    r = check_ontology(sot_minimal, patched)
    assert r["has_drift"] is False

# ── Tests trigger (intégration) ─────────────────────────────────────────────

def test_trigger_no_mirrors(tmp_path, monkeypatch):
    """trigger() sans miroirs disponibles → doit retourner 0 (non bloquant)."""
    monkeypatch.chdir(tmp_path)
    # Create required directory structure and file
    sot_dir = tmp_path / "ecosystem/registry"
    sot_dir.mkdir(parents=True)
    sot_file = sot_dir / "ECOS_ROOT.json"
    sot_file.write_text(json.dumps({"repos": {}}))

    rc = trigger(dry_run=True, mirror="all", fail_on_critical=True)
    assert rc == 0  # pas de miroirs → pas de CRITICAL détecté

# ── Acceptance Criteria ─────────────────────────────────────────────────────

def test_ac7_no_placeholders():
    """AC7: aucun placeholder {{ }} dans les fichiers livrés."""
    targets = [
        Path("tools/nexus_mirror_trigger.py"),
        Path("tools/nexus_reciprocity_check.py"),
        Path(".github/workflows/nexus-sync.yml"),
        Path("docs/nexus_sync_architecture.md"),
    ]
    for t in targets:
        if t.exists():
            content = t.read_text()
            # Ignore GitHub Actions expressions like ${{ ... }}
            content_clean = content.replace("${{", "")
            assert "{{" not in content_clean, f"Placeholder non résolu dans {t}"

def test_ac6_dual_path_imports():
    """AC6: dual-path imports présents dans les nouveaux fichiers Python."""
    trigger_file = Path("tools/nexus_mirror_trigger.py")
    if trigger_file.exists():
        content = trigger_file.read_text()
        assert "except ImportError" in content

def test_ac3_scope_check():
    """AC3: fichiers cibles déclarés existent."""
    expected = [
        Path(".github/workflows/nexus-sync.yml"),
        Path("tools/nexus_reciprocity_check.py"),
        Path("tools/nexus_mirror_trigger.py"),
        Path("docs/nexus_sync_architecture.md"),
    ]
    for p in expected:
        assert p.exists(), f"Fichier cible manquant: {p}"
