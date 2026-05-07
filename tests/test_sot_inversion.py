# ecosystem/registry/ECOS_ROOT.json
# Repo: gerivdb/NEXUS | IntentHash: 0xNEXUS_SUB1_φ100.0
# Closes: #2 | IntentSource: from-intent:0xNEXUS_SUB1

import json, pytest
from pathlib import Path

ECOS_ROOT = Path("ecosystem/registry/ECOS_ROOT.json")

@pytest.fixture
def root():
    with open(ECOS_ROOT) as f:
        return json.load(f)

def test_source_of_truth_points_to_nexus(root):
    sot = root["source_of_truth"]
    assert "gerivdb/NEXUS" in sot, f"Expected NEXUS in source_of_truth, got: {sot}"

def test_mirrors_field_exists(root):
    assert "mirrors" in root, "Field 'mirrors' missing from ECOS_ROOT.json"
    assert isinstance(root["mirrors"], list), "'mirrors' must be a list"
    assert len(root["mirrors"]) >= 1, "'mirrors' must contain at least ECOYSTEM ref"

def test_mirrors_contains_ecoystem(root):
    mirrors = root["mirrors"]
    assert any("ECOYSTEM" in m for m in mirrors), \
        f"ECOYSTEM not found in mirrors: {mirrors}"

def test_schema_version_bumped(root):
    # Updated to expect 3.0.0 as established in Sync v3.0.0
    assert root["schema_version"] == "3.0.0", \
        f"Expected schema_version=3.0.0, got: {root['schema_version']}"

def test_wal_sot_inversion_logged(root):
    events = [e["event"] for e in root.get("wal_log", [])]
    assert "SOT_INVERSION" in events, "WAL entry SOT_INVERSION not found"

def test_repos_unchanged(root):
    """Vérifier que le périmètre protégé n'a pas été altéré"""
    repos = root["repos"]
    assert "KIVA" in repos
    assert "NEXUS" in repos
    assert "BRAIN" in repos
    assert len(repos) >= 23, f"Repos count regressed: {len(repos)}"

def test_sot_not_ecoystem_anymore(root):
    sot = root["source_of_truth"]
    assert "ECOYSTEM" not in sot, \
        f"ECOYSTEM must not be primary source_of_truth anymore, got: {sot}"
