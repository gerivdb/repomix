# tests/test_nexus_surface_gaps.py
# Repo: gerivdb/NEXUS | IntentHash: SURFGAPS_φ25.0
# Closes: #1 | IntentSource: direct

import os
from pathlib import Path

ROOT = Path(__file__).parent.parent

def test_managers_readme_exists():
    assert (ROOT / "managers" / "README.md").exists(), "managers/README.md manquant"

def test_skills_readme_exists():
    assert (ROOT / "skills" / "README.md").exists(), "skills/README.md manquant"

def test_readme_dashboard_markers():
    readme = (ROOT / "README.md").read_text()
    assert "NEXUS-REGISTRY-DASHBOARD:START" in readme, "Marqueur START absent du README"
    assert "NEXUS-REGISTRY-DASHBOARD:END" in readme, "Marqueur END absent du README"

def test_registry_changelog_has_content():
    changelog = (ROOT / "REGISTRY_CHANGELOG.md").read_text()
    assert len(changelog.strip()) > 100, "REGISTRY_CHANGELOG.md trop court (< 100 chars)"
    assert "2026-03-28" in changelog, "Entry initiale 2026-03-28 absente du changelog"

def test_test_sot_inversion_not_in_tools():
    assert not (ROOT / "tools" / "test_sot_inversion.py").exists(), "test_sot_inversion.py encore dans tools/ (doit être dans tests/)"

def test_labels_yml_exists():
    assert (ROOT / ".github" / "labels.yml").exists(), ".github/labels.yml manquant"

def test_labels_contains_registry_drift():
    labels = (ROOT / ".github" / "labels.yml").read_text()
    assert "registry-drift" in labels, "Label registry-drift absent de labels.yml"

def test_labels_contains_lifecycle_alert():
    labels = (ROOT / ".github" / "labels.yml").read_text()
    assert "lifecycle-alert" in labels, "Label lifecycle-alert absent de labels.yml"
