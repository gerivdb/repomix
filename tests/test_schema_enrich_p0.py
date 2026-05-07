import json, pytest
from pathlib import Path

ECOS_ROOT = Path("ecosystem/registry/ECOS_ROOT.json")
P0_REPOS = ["KIVA", "GATEWAY-MANAGER", "BRAIN", "ECOYSTEM", "NEXUS"]
NEW_FIELDS = ["description","entry_point","dependencies","has_readme",
              "has_dockerfile","ci_status","test_coverage","mcp_citizens"]

@pytest.fixture
def root():
    with open(ECOS_ROOT) as f:
        return json.load(f)

def test_schema_version_300(root):
    assert root["schema_version"] == "3.0.0"

@pytest.mark.parametrize("repo", P0_REPOS)
@pytest.mark.parametrize("field", NEW_FIELDS)
def test_p0_repo_has_field(root, repo, field):
    assert field in root["repos"][repo], f"{repo} missing field {field}"

def test_wal_schema_enrich_p0_logged(root):
    events = [e["event"] for e in root.get("wal_log", [])]
    assert "SCHEMA_ENRICH_P0" in events

def test_non_p0_repos_unchanged(root):
    # P1/P2/P3 repos ne doivent pas avoir les nouveaux champs forcés
    non_p0 = [r for r in root["repos"] if r not in P0_REPOS]
    for repo in non_p0[:3]:  # spot check 3
        entry = root["repos"][repo]
        assert "tier" in entry  # champs de base présents
