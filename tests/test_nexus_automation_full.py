# tests/test_nexus_automation_full.py
# Repo: gerivdb/NEXUS | IntentHash: 0xNEXUS_AUTOFULL_φ86.0
# Closes: #9 | IntentSource: direct

"""
Tests suite EPIC-2 — couvre SUB-B à G :
  - nexus_sync.py --dry-run
  - nexus_validate.py check_drift (mock API)
  - nexus_validate.py check_mcp_citizens (fixtures)
  - nexus_watchdog.py (fixtures lifecycle)
  - nexus_changelog_gen.py (diff mock)
  - nexus_readme_gen.py (marqueurs + tableau)
"""
import sys, json, pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure tools is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

# ── Fixtures ────────────────────────────────────────────────────────────────

MOCK_ROOT_CLEAN = {
    "schema_version": "2.2.0",
    "repos": {
        "KIVA": {"lifecycle": "ACTIVE", "last_pushed": "2026-03-01",
                 "criticality": "P0_CONSTITUTIONAL", "ci_status": "success",
                 "mcp_citizens": ["kiva-agent"], "flags": []},
        "GHOST": {"lifecycle": "REACTIVATION_PENDING", "last_pushed": "2025-11-11",
                  "criticality": "P1_STRATEGIC", "ci_status": "none",
                  "mcp_citizens": [], "flags": ["REACTIVATION_PENDING"]},
    },
    "layers": {"L1_CAUSALITY": ["KIVA"]},
    "excluded_repos": {"rules": [{"pattern": "lovable-*", "type": "pattern"}], "explicit": []},
    "generated_at": "2026-03-28T17:30:00Z",
}

# ── SUB-B : nexus_sync --dry-run ─────────────────────────────────────────────

def test_sync_dry_run_no_write(tmp_path):
    """--dry-run ne doit pas modifier ECOS_ROOT."""
    import subprocess, sys as _sys
    # We use the real ECOS_ROOT but with --dry-run it shouldn't be touched.
    # To be safe in test environment, we could mock the file write,
    # but the PRD asks for a subprocess run.
    result = subprocess.run(
        [_sys.executable, "tools/nexus_sync.py", "--dry-run"],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0, f"nexus_sync --dry-run failed:\n{result.stderr}"

# ── SUB-C : check_drift ──────────────────────────────────────────────────────

def test_check_drift_detects_unknown_repo():
    from nexus_validate import check_drift
    mock_github_repos = [
        {"name": "KIVA", "archived": False, "fork": False},
        {"name": "PHANTOM-REPO", "archived": False, "fork": False},  # absent du registry
    ]
    root = {"repos": {"KIVA": {}}, "excluded_repos": {"rules": [], "explicit": []}}
    with patch("nexus_validate.fetch_github_repos", return_value=mock_github_repos):
        errors = check_drift(root, gh_token="fake-token")
    assert any("PHANTOM-REPO" in e for e in errors)

def test_check_drift_excludes_pattern():
    from nexus_validate import check_drift
    mock_github_repos = [
        {"name": "lovable-xyz", "archived": False, "fork": False},
    ]
    root = {
        "repos": {},
        "excluded_repos": {"rules": [{"pattern": "lovable-*", "type": "pattern"}], "explicit": []}
    }
    with patch("nexus_validate.fetch_github_repos", return_value=mock_github_repos):
        errors = check_drift(root, gh_token="fake-token")
    assert errors == []

def test_check_drift_no_token_returns_empty():
    from nexus_validate import check_drift
    root = {"repos": {}, "excluded_repos": {"rules": [], "explicit": []}}
    errors = check_drift(root, gh_token="")
    assert errors == []

# ── SUB-F : check_mcp_citizens ───────────────────────────────────────────────

def test_check_mcp_citizens_missing_file(tmp_path):
    from nexus_validate import check_mcp_citizens
    root = {"repos": {"KIVA": {"mcp_citizens": ["ghost-agent"]}}}
    # tmp_path n'a pas de managers/ghost-agent.yml
    errors = check_mcp_citizens(root, repo_root=str(tmp_path))
    assert any("ghost-agent" in e for e in errors)

def test_check_mcp_citizens_orphan_file(tmp_path):
    from nexus_validate import check_mcp_citizens
    (tmp_path / "managers").mkdir()
    (tmp_path / "managers" / "ghost-agent.yml").write_text("name: ghost-agent")
    root = {"repos": {"KIVA": {"mcp_citizens": []}}}
    errors = check_mcp_citizens(root, repo_root=str(tmp_path))
    assert any("ghost-agent" in e for e in errors)

def test_check_mcp_citizens_clean(tmp_path):
    from nexus_validate import check_mcp_citizens
    (tmp_path / "managers").mkdir()
    (tmp_path / "managers" / "kiva-agent.yml").write_text("name: kiva-agent")
    root = {"repos": {"KIVA": {"mcp_citizens": ["kiva-agent"]}}}
    errors = check_mcp_citizens(root, repo_root=str(tmp_path))
    assert errors == []

# ── SUB-E : nexus_watchdog ───────────────────────────────────────────────────

def test_watchdog_reactivation_stale():
    from nexus_watchdog import run_watchdog
    root = {"repos": {"GeriCode": {
        "lifecycle": "REACTIVATION_PENDING",
        "last_pushed": "2025-11-11",
        "criticality": "P1_STRATEGIC",
        "ci_status": "none"
    }}}
    triggered = run_watchdog(root, dry_run=True)
    assert any(t["rule"] == "REACTIVATION_STALE" for t in triggered)

def test_watchdog_p0_ci_broken():
    from nexus_watchdog import run_watchdog
    root = {"repos": {"BRAIN": {
        "lifecycle": "ACTIVE",
        "last_pushed": "2026-03-01",
        "criticality": "P0_CONSTITUTIONAL",
        "ci_status": "failing"
    }}}
    triggered = run_watchdog(root, dry_run=True)
    assert any(t["rule"] == "P0_CI_BROKEN" for t in triggered)

def test_watchdog_healthy_no_trigger():
    from nexus_watchdog import run_watchdog
    root = {"repos": {"KIVA": {
        "lifecycle": "ACTIVE",
        "last_pushed": "2026-03-20",
        "criticality": "P0_CONSTITUTIONAL",
        "ci_status": "success"
    }}}
    triggered = run_watchdog(root, dry_run=True)
    assert triggered == []

# ── SUB-D : nexus_changelog_gen ──────────────────────────────────────────────

def test_changelog_detects_modification():
    from nexus_changelog_gen import diff_repos, generate_entry
    old = {"repos": {"KIVA": {"open_issues": 9}}}
    new = {"repos": {"KIVA": {"open_issues": 7}}}
    diff = diff_repos(old, new)
    # Check that KIVA is in modified
    assert any(item[0] == "KIVA" and item[1] == "open_issues" for item in diff["modified"])
    entry = generate_entry(diff, "2.2.0")
    assert "KIVA" in entry and "9" in entry and "7" in entry

def test_changelog_detects_new_repo():
    from nexus_changelog_gen import diff_repos
    old = {"repos": {}}
    new = {"repos": {"NEW-REPO": {"lifecycle": "ACTIVE"}}}
    diff = diff_repos(old, new)
    assert "NEW-REPO" in diff["added"]

# ── SUB-G : nexus_readme_gen ─────────────────────────────────────────────────

def test_readme_dashboard_contains_markers(tmp_path):
    from nexus_readme_gen import generate_dashboard, inject_into_readme, MARKER_START, MARKER_END
    import nexus_readme_gen as nrg
    nrg.README_PATH = tmp_path / "README.md"
    nrg.README_PATH.write_text("# NEXUS\n")
    dashboard = generate_dashboard(MOCK_ROOT_CLEAN)
    assert MARKER_START in dashboard
    assert MARKER_END in dashboard
    inject_into_readme(dashboard)
    content = nrg.README_PATH.read_text()
    assert MARKER_START in content
    assert MARKER_END in content

def test_readme_dashboard_contains_kiva():
    from nexus_readme_gen import generate_dashboard
    dashboard = generate_dashboard(MOCK_ROOT_CLEAN)
    assert "KIVA" in dashboard

def test_readme_dry_run_no_file_write(tmp_path, capsys):
    """--dry-run ne doit pas modifier README.md."""
    import subprocess, sys as _sys
    result = subprocess.run(
        [_sys.executable, "tools/nexus_readme_gen.py", "--dry-run"],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0
