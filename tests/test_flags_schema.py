import pytest
import json
import os
from pathlib import Path
from tools.nexus_validate import check_schema, check_orphans

@pytest.fixture
def base_registry():
    return {
        "schema_version": "3.0.0",
        "ecosystem_id": "test-ecosystem",
        "repos": {
            "TEST-REPO": {
                "tier": "T1-CORE",
                "lifecycle": "ACTIVE",
                "lang": "Python",
                "criticality": "P0",
                "layer": "L1",
                "url": "https://github.com/test/repo"
            }
        }
    }

def test_schema_v3_valid(base_registry):
    errors = check_schema(base_registry)
    assert not errors

def test_schema_v3_invalid_version(base_registry):
    base_registry["schema_version"] = "2.2.0"
    errors = check_schema(base_registry)
    assert any("schema_version" in e.lower() for e in errors)

def test_schema_v3_invalid_flag(base_registry):
    base_registry["repos"]["TEST-REPO"]["flags"] = ["INVALID_FLAG"]
    errors = check_schema(base_registry)
    assert any("flags" in e.lower() for e in errors)

def test_check_orphans_with_flag(base_registry):
    base_registry["repos"]["TEST-REPO"]["flags"] = ["ORPHAN_PENDING_REVIEW"]
    errors = check_orphans(base_registry)
    assert len(errors) == 1
    assert "ORPHAN: TEST-REPO" in errors[0]

def test_check_orphans_no_flag(base_registry):
    base_registry["repos"]["TEST-REPO"]["note"] = "this is an orphan_pending_review in note"
    errors = check_orphans(base_registry)
    assert not errors

def test_check_orphans_multiple_repos(base_registry):
    base_registry["repos"]["ORPHAN-1"] = {
        "tier": "T1", "lifecycle": "ACTIVE", "lang": "Go", "criticality": "P1", "layer": "L2",
        "url": "https://github.com/o1", "flags": ["ORPHAN_PENDING_REVIEW"]
    }
    base_registry["repos"]["ACTIVE-1"] = {
        "tier": "T1", "lifecycle": "ACTIVE", "lang": "Go", "criticality": "P1", "layer": "L2",
        "url": "https://github.com/a1", "flags": ["EXTERNAL_DEPENDENCY"]
    }
    errors = check_orphans(base_registry)
    assert len(errors) == 1
    assert "ORPHAN: ORPHAN-1" in errors[0]
