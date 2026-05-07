# tests/test_nexus_autodiscover.py
# Repo: gerivdb/NEXUS | IntentHash: 0xNEXUS_AUTODISCO_E3_φ92.0
# Closes: #1257 | IntentSource: direct

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# DUAL-PATH IMPORTS (R2)
try:
    from tools.nexus_autodiscover import (
        matches_excluded, fetch_all_repos, discover, DEFAULT_ENTRY
    )
except ImportError:
    from nexus_autodiscover import (  # type: ignore
        matches_excluded, fetch_all_repos, discover, DEFAULT_ENTRY
    )

# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def excluded_rules():
    return [
        {"pattern": "lovable-*",     "type": "pattern", "reason": "Lovable.dev"},
        {"pattern": "test-*-tmp",    "type": "pattern", "reason": "throwaway"},
        {"pattern": "*.lovable",     "type": "pattern", "reason": "Lovable.dev"},
        {"pattern": "exact-excluded","type": "exact",   "reason": "explicit exact"},
    ]

@pytest.fixture
def minimal_ecos_root(tmp_path):
    root = {
        "repos": {"NEXUS": {}, "KIVA": {}},
        "archived": ["old-repo"],
        "excluded_repos": {
            "rules": [
                {"pattern": "lovable-*", "type": "pattern", "reason": "Lovable.dev"},
                {"pattern": "test-*-tmp","type": "pattern", "reason": "throwaway"},
            ],
            "explicit": [],
        },
        "wal_log": [],
        "generated_at": "2026-03-29T00:00:00Z",
    }
    p = tmp_path / "ECOS_ROOT.json"
    p.write_text(json.dumps(root, indent=2))
    return tmp_path, root

@pytest.fixture
def mock_gh_repos():
    return [
        {"name": "NEXUS",           "archived": False, "private": True,
         "language": "Python",      "pushed_at": "2026-03-29", "open_issues_count": 0,
         "html_url": "https://github.com/gerivdb/NEXUS", "description": "SOT"},
        {"name": "KIVA",            "archived": False, "private": True,
         "language": "Python",      "pushed_at": "2026-03-08", "open_issues_count": 9,
         "html_url": "https://github.com/gerivdb/KIVA",  "description": "Runtime"},
        {"name": "NEW-REPO-1",      "archived": False, "private": True,
         "language": "TypeScript",  "pushed_at": "2026-03-20", "open_issues_count": 2,
         "html_url": "https://github.com/gerivdb/NEW-REPO-1", "description": "new"},
        {"name": "lovable-test",    "archived": False, "private": True,
         "language": None,          "pushed_at": "2026-01-01", "open_issues_count": 0,
         "html_url": "https://github.com/gerivdb/lovable-test", "description": None},
        {"name": "test-abc-tmp",    "archived": False, "private": True,
         "language": None,          "pushed_at": "2026-02-01", "open_issues_count": 0,
         "html_url": "https://github.com/gerivdb/test-abc-tmp", "description": None},
        {"name": "old-repo",        "archived": True,  "private": True,
         "language": None,          "pushed_at": "2025-01-01", "open_issues_count": 0,
         "html_url": "https://github.com/gerivdb/old-repo", "description": None},
    ]

# ── Tests matches_excluded ───────────────────────────────────────────────────

def test_excluded_lovable_pattern(excluded_rules):
    assert matches_excluded("lovable-myapp", excluded_rules) == "Lovable.dev"

def test_excluded_tmp_pattern(excluded_rules):
    assert matches_excluded("test-myfeature-tmp", excluded_rules) == "throwaway"

def test_excluded_dotlovable(excluded_rules):
    assert matches_excluded("myapp.lovable", excluded_rules) == "Lovable.dev"

def test_excluded_exact_match(excluded_rules):
    assert matches_excluded("exact-excluded", excluded_rules) == "explicit exact"

def test_not_excluded_normal_repo(excluded_rules):
    assert matches_excluded("NEXUS", excluded_rules) is None

def test_not_excluded_partial_match(excluded_rules):
    # "test-abc" sans "-tmp" ne doit pas matcher "test-*-tmp"
    assert matches_excluded("test-abc", excluded_rules) is None

# ── Tests discover (intégration mocked) ─────────────────────────────────────

def test_discover_finds_new_repo(tmp_path, minimal_ecos_root, mock_gh_repos, monkeypatch):
    ecos_dir, _ = minimal_ecos_root
    ecos_path = ecos_dir / "ECOS_ROOT.json"
    report_path = ecos_dir / "autodiscover_report.json"

    monkeypatch.setattr("tools.nexus_autodiscover.ECOS_ROOT_PATH", ecos_path)
    monkeypatch.setattr("tools.nexus_autodiscover.AUTODISCOVER_REPORT_PATH", report_path)
    monkeypatch.setattr("tools.nexus_autodiscover.fetch_all_repos",
                        lambda headers: mock_gh_repos)

    with patch("tools.nexus_autodiscover.get_headers", return_value={"Authorization": "token x"}):
        report = discover(dry_run=True, patch=False)

    assert report["candidate_count"] == 1
    assert report["candidates"][0]["name"] == "NEW-REPO-1"

def test_discover_excludes_lovable(tmp_path, minimal_ecos_root, mock_gh_repos, monkeypatch):
    ecos_dir, _ = minimal_ecos_root
    ecos_path = ecos_dir / "ECOS_ROOT.json"
    report_path = ecos_dir / "autodiscover_report.json"

    monkeypatch.setattr("tools.nexus_autodiscover.ECOS_ROOT_PATH", ecos_path)
    monkeypatch.setattr("tools.nexus_autodiscover.AUTODISCOVER_REPORT_PATH", report_path)
    monkeypatch.setattr("tools.nexus_autodiscover.fetch_all_repos",
                        lambda headers: mock_gh_repos)

    with patch("tools.nexus_autodiscover.get_headers", return_value={"Authorization": "token x"}):
        report = discover(dry_run=True, patch=False)

    excluded_names = [e["name"] for e in report["excluded_matched"]]
    assert "lovable-test" in excluded_names
    assert "test-abc-tmp" in excluded_names

def test_discover_skips_registered(tmp_path, minimal_ecos_root, mock_gh_repos, monkeypatch):
    ecos_dir, _ = minimal_ecos_root
    ecos_path = ecos_dir / "ECOS_ROOT.json"
    report_path = ecos_dir / "autodiscover_report.json"

    monkeypatch.setattr("tools.nexus_autodiscover.ECOS_ROOT_PATH", ecos_path)
    monkeypatch.setattr("tools.nexus_autodiscover.AUTODISCOVER_REPORT_PATH", report_path)
    monkeypatch.setattr("tools.nexus_autodiscover.fetch_all_repos",
                        lambda headers: mock_gh_repos)

    with patch("tools.nexus_autodiscover.get_headers", return_value={"Authorization": "token x"}):
        report = discover(dry_run=True, patch=False)

    candidate_names = [c["name"] for c in report["candidates"]]
    assert "NEXUS" not in candidate_names
    assert "KIVA" not in candidate_names

def test_discover_patch_updates_ecos_root(tmp_path, minimal_ecos_root, mock_gh_repos, monkeypatch):
    ecos_dir, _ = minimal_ecos_root
    ecos_path = ecos_dir / "ECOS_ROOT.json"
    report_path = ecos_dir / "autodiscover_report.json"

    monkeypatch.setattr("tools.nexus_autodiscover.ECOS_ROOT_PATH", ecos_path)
    monkeypatch.setattr("tools.nexus_autodiscover.AUTODISCOVER_REPORT_PATH", report_path)
    monkeypatch.setattr("tools.nexus_autodiscover.fetch_all_repos",
                        lambda headers: mock_gh_repos)

    with patch("tools.nexus_autodiscover.get_headers", return_value={"Authorization": "token x"}):
        report = discover(dry_run=False, patch=True)

    updated = json.loads(ecos_path.read_text())
    assert "NEW-REPO-1" in updated["repos"]
    assert updated["repos"]["NEW-REPO-1"]["flags"] == ["autodiscovered"]
    # WAL entry ajouté
    events = [w["event"] for w in updated.get("wal_log", [])]
    assert "AUTODISCOVER_PATCH" in events

def test_discover_dry_run_no_write(tmp_path, minimal_ecos_root, mock_gh_repos, monkeypatch):
    ecos_dir, original = minimal_ecos_root
    ecos_path = ecos_dir / "ECOS_ROOT.json"
    report_path = ecos_dir / "autodiscover_report.json"

    monkeypatch.setattr("tools.nexus_autodiscover.ECOS_ROOT_PATH", ecos_path)
    monkeypatch.setattr("tools.nexus_autodiscover.AUTODISCOVER_REPORT_PATH", report_path)
    monkeypatch.setattr("tools.nexus_autodiscover.fetch_all_repos",
                        lambda headers: mock_gh_repos)

    with patch("tools.nexus_autodiscover.get_headers", return_value={"Authorization": "token x"}):
        discover(dry_run=True, patch=True)  # dry_run prime sur patch

    after = json.loads(ecos_path.read_text())
    assert set(after["repos"].keys()) == {"NEXUS", "KIVA"}  # inchangé

def test_discover_no_api_token(tmp_path, minimal_ecos_root, monkeypatch):
    ecos_dir, _ = minimal_ecos_root
    ecos_path = ecos_dir / "ECOS_ROOT.json"
    report_path = ecos_dir / "autodiscover_report.json"

    monkeypatch.setattr("tools.nexus_autodiscover.ECOS_ROOT_PATH", ecos_path)
    monkeypatch.setattr("tools.nexus_autodiscover.AUTODISCOVER_REPORT_PATH", report_path)
    monkeypatch.setattr("tools.nexus_autodiscover.fetch_all_repos", lambda h: [])

    with patch("tools.nexus_autodiscover.get_headers", return_value={}):
        report = discover(dry_run=True, patch=False)

    assert report["gh_repos_scanned"] == 0
    assert report["candidate_count"] == 0

# ── Acceptance Criteria ─────────────────────────────────────────────────────

def test_ac7_no_placeholders():
    """AC7: aucun placeholder {{ }} dans les fichiers livrés."""
    targets = [
        Path("tools/nexus_autodiscover.py"),
        # .github/workflows/nexus-autodiscover.yml contient des {{ }} légitimes pour GitHub Actions
    ]
    for t in targets:
        if t.exists():
            content = t.read_text()
            assert "{{" not in content, f"Placeholder non résolu dans {t}"

def test_ac6_dual_path_imports():
    """AC6: dual-path imports présents."""
    f = Path("tools/nexus_autodiscover.py")
    if f.exists():
        assert "except ImportError" in f.read_text()

def test_ac3_scope_check():
    """AC3: fichiers cibles déclarés existent."""
    expected = [
        Path("tools/nexus_autodiscover.py"),
        Path(".github/workflows/nexus-autodiscover.yml"),
    ]
    for p in expected:
        assert p.exists(), f"Fichier cible manquant: {p}"
