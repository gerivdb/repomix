# tests/test_repos_json_generated.py
# Repo: gerivdb/NEXUS | IntentHash: 0xNEXUS_SUB2_φ100.0
# Closes: #3 | IntentSource: from-intent:0xNEXUS_SUB2

import json, sys
import pytest
from pathlib import Path

try:
    from tools.nexus_repos_gen import generate_repos_json
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.nexus_repos_gen import generate_repos_json  # type: ignore

ECOS_ROOT = Path("ecosystem/registry/ECOS_ROOT.json")
REPOS_JSON = Path("ecosystem/registry/repos.json")

@pytest.fixture
def generated():
    return generate_repos_json()

@pytest.fixture
def ecos_root():
    with open(ECOS_ROOT) as f:
        return json.load(f)

def test_generated_flag(generated):
    assert generated["_generated"] is True

def test_do_not_edit_present(generated):
    assert "_do_not_edit" in generated
    assert "ECOS_ROOT" in generated["_do_not_edit"]

def test_generated_from_field(generated):
    assert generated["_generated_from"] == "ECOS_ROOT.json"

def test_repos_count_matches_ecos_root(generated, ecos_root):
    assert len(generated["repos"]) == len(ecos_root["repos"])

def test_all_repos_have_name(generated):
    for repo in generated["repos"]:
        assert "name" in repo and repo["name"]

def test_repos_names_match_ecos_root(generated, ecos_root):
    gen_names = {r["name"] for r in generated["repos"]}
    ecos_names = set(ecos_root["repos"].keys())
    assert gen_names == ecos_names

def test_repos_json_file_has_generated_flag():
    if not REPOS_JSON.exists():
        pytest.skip("repos.json not yet generated — run nexus_repos_gen.py first")
    with open(REPOS_JSON) as f:
        data = json.load(f)
    assert data.get("_generated") is True
