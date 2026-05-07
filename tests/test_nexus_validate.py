import json, sys
import pytest
from pathlib import Path

try:
    from tools.nexus_validate import check_schema, check_consistency, check_orphans, check_sot
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.nexus_validate import check_schema, check_consistency, check_orphans, check_sot  # type: ignore

ECOS_ROOT = Path("ecosystem/registry/ECOS_ROOT.json")

@pytest.fixture
def root():
    with open(ECOS_ROOT) as f:
        return json.load(f)

def test_check_sot_passes_on_current_main(root):
    errors = check_sot(root)
    assert errors == [], f"SOT check failed: {errors}"

def test_check_schema_required_fields(root):
    errors = check_schema(root)
    schema_errors = [e for e in errors if "missing" in e or "required" in e.lower() or "is a required property" in e.lower()]
    assert schema_errors == [], f"Schema errors: {schema_errors}"

def test_check_sot_detects_wrong_sot():
    fake = {"source_of_truth": "gerivdb/ECOYSTEM@wrong", "repos": {}}
    errors = check_sot(fake)
    assert len(errors) == 1

def test_check_orphans_detects_orphan():
    # Orphans check returns list of error strings.
    # We test flags-based detection.
    fake = {
        "repos": {
            "REPO_FLAG": {
                "lifecycle": "ACTIVE",
                "tier": "T1",
                "flags": ["ORPHAN_PENDING_REVIEW"]
            },
            "REPO_NOTE": {
                "lifecycle": "ACTIVE",
                "tier": "T1",
                "note": "flags as orphan_pending_review"
            }
        }
    }
    errors = check_orphans(fake)
    assert len(errors) == 1
    assert any("REPO_FLAG" in e for e in errors)
    assert not any("REPO_NOTE" in e for e in errors)

def test_check_schema_detects_missing_field():
    fake = {"repos": {"TEST": {"tier": "T1"}}}
    errors = check_schema(fake)
    assert any("missing" in e or "required" in e.lower() or "is a required property" in e.lower() for e in errors)
