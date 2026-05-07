# tests/test_nexus_sync.py
# Repo: gerivdb/NEXUS | IntentHash: 0xNEXUS_SUB4_φ100.0
# Closes: #5 | IntentSource: from-intent:0xNEXUS_SUB4

import json, sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

try:
    from tools.nexus_sync import fetch_repo_meta, sync
    from tools.nexus_repos_gen import generate_repos_json
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.nexus_sync import fetch_repo_meta, sync  # type: ignore
    from tools.nexus_repos_gen import generate_repos_json # type: ignore

ECOS_ROOT = Path("ecosystem/registry/ECOS_ROOT.json")

@pytest.fixture
def root():
    with open(ECOS_ROOT) as f:
        return json.load(f)

def test_generate_repos_json_structure(root, tmp_path):
    import tools.nexus_repos_gen as nrg
    original_path = nrg.REPOS_JSON
    nrg.REPOS_JSON = tmp_path / "repos.json"
    data = generate_repos_json()
    assert data["_generated"] is True
    assert len(data["repos"]) == len(root["repos"])
    nrg.REPOS_JSON = original_path

def test_fetch_repo_meta_no_token():
    result = fetch_repo_meta("NEXUS", {})
    assert result == {}

def test_fetch_repo_meta_mock():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "open_issues_count": 5,
        "pushed_at": "2026-03-28T10:00:00Z",
        "language": "Python"
    }
    with patch("tools.nexus_sync.requests") as mock_req:
        mock_req.get.return_value = mock_resp
        result = fetch_repo_meta("NEXUS", {"Authorization": "Bearer test"})
    assert result["open_issues"] == 5
    assert result["last_pushed"] == "2026-03-28"
    assert result["lang"] == "Python"

def test_sync_dry_run_no_write(root, tmp_path):
    # dry_run ne doit pas modifier ECOS_ROOT
    import tools.nexus_sync as ns
    original_path = ns.ECOS_ROOT_PATH
    ns.ECOS_ROOT_PATH = tmp_path / "ECOS_ROOT.json"
    with open(ns.ECOS_ROOT_PATH, "w") as f:
        json.dump(root, f)
    mtime_before = ns.ECOS_ROOT_PATH.stat().st_mtime
    with patch("tools.nexus_sync.fetch_repo_meta", return_value={}):
        sync(dry_run=True)
    mtime_after = ns.ECOS_ROOT_PATH.stat().st_mtime
    assert mtime_before == mtime_after
    ns.ECOS_ROOT_PATH = original_path
