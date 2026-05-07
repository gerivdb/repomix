# tests/test_prd_env3_parser.py
# Repo: gerivdb/NEXUS | IntentHash: 0xPRD_ENV3_v2.4_φ100.0
# Ref: ISE-20260329-PRD-ENV3

try:
    from tools.prd_env3_parser import PRDContext, parse_direct, parse_from_intent, validate_template_placeholders
except ImportError:
    from prd_env3_parser import PRDContext, parse_direct, parse_from_intent, validate_template_placeholders  # type: ignore

import pytest
from pathlib import Path


# ── Fixtures ─────────────────────────────────────────────────────────────────

VALID_DIRECT_ARGS = ["ECOYSTEM", "phi_guard", "1042", "95.0"]

INTENT_BLOCK = """Repo : gerivdb/BRAIN
Feature : memory_router
Closes #88
φ-CPS budget restant: 87.5%
Branche : main
IntentHash : 0xBRAIN_ROUTE_φ90"""


# ── Tests parse_direct ────────────────────────────────────────────────────────

class TestParseDirect:
    def test_basic(self):
        ctx = parse_direct(VALID_DIRECT_ARGS)
        assert ctx.repo_name == "ECOYSTEM"
        assert ctx.feature_name == "phi_guard"
        assert ctx.issue_number == 1042
        assert ctx.phi_budget == 95.0
        assert ctx.intent_source == "direct"

    def test_phi_default(self):
        ctx = parse_direct(["NEXUS", "nexus_sync", "1256"])
        assert ctx.phi_budget == 100.0

    def test_phi_with_prefix(self):
        ctx = parse_direct(["NEXUS", "nexus_sync", "1256", "phi_budget=80.0"])
        assert ctx.phi_budget == 80.0

    def test_hash8_generated(self):
        ctx = parse_direct(VALID_DIRECT_ARGS)
        assert len(ctx.hash8) >= 8
        assert ctx.hash8.startswith("ECOY")

    def test_missing_args_exits(self):
        with pytest.raises(SystemExit):
            parse_direct(["ECOYSTEM", "phi_guard"])  # issue_number manquant

    def test_invalid_issue_number_exits(self):
        with pytest.raises(SystemExit):
            parse_direct(["ECOYSTEM", "phi_guard", "not_a_number"])


# ── Tests parse_from_intent ───────────────────────────────────────────────────

class TestParseFromIntent:
    def test_basic(self):
        ctx = parse_from_intent(INTENT_BLOCK)
        assert ctx.repo_name == "BRAIN"
        assert ctx.feature_name == "memory_router"
        assert ctx.issue_number == 88
        assert ctx.phi_budget == 87.5
        assert ctx.base_branch == "main"
        assert ctx.hash8 == "BRAIN_RO"
        assert ctx.intent_source == "from-intent:BRAIN_RO"

    def test_missing_fields_produce_empty(self):
        ctx = parse_from_intent("Repo : gerivdb/CANDIDATOR")
        assert ctx.repo_name == "CANDIDATOR"
        assert ctx.feature_name == ""
        assert ctx.issue_number == 0


# ── Tests PRDContext.validate ─────────────────────────────────────────────────

class TestPRDContextValidate:
    def test_valid(self):
        ctx = PRDContext(repo_name="ECOYSTEM", feature_name="phi_guard", issue_number=1042)
        assert ctx.validate() == []

    def test_invalid_repo(self):
        ctx = PRDContext(repo_name="UNKNOWN_REPO", feature_name="foo", issue_number=1)
        errors = ctx.validate()
        assert any("inconnu" in e for e in errors)

    def test_placeholder_repo(self):
        ctx = PRDContext(repo_name="{{repo_name}}", feature_name="foo", issue_number=1)
        errors = ctx.validate()
        assert any("R9" in e for e in errors)

    def test_zero_issue(self):
        ctx = PRDContext(repo_name="NEXUS", feature_name="sync", issue_number=0)
        errors = ctx.validate()
        assert any("issue_number" in e for e in errors)


# ── Tests to_dict ─────────────────────────────────────────────────────────────

class TestPRDContextToDict:
    def test_keys(self):
        ctx = PRDContext(repo_name="NEXUS", feature_name="sync", issue_number=42)
        d = ctx.to_dict()
        for key in ["repo_name", "feature_name", "issue_number", "phi_budget",
                    "sha_env0", "base_branch", "intent_source", "hash8"]:
            assert key in d


# ── Tests validate_template_placeholders ────────────────────────────────────

class TestValidateTemplatePlaceholders:
    def test_template_exists(self):
        p = Path("tools/prd_env3.md")
        assert p.exists(), "tools/prd_env3.md introuvable — vérifier le path"

    def test_no_critical_placeholders_after_render(self):
        p = Path("tools/prd_env3.md")
        if not p.exists():
            pytest.skip("template absent")
        ctx = PRDContext(
            repo_name="ECOYSTEM",
            feature_name="phi_guard",
            issue_number=1042,
            phi_budget=95.0,
            sha_env0="abc1234",
            base_branch="main",
            intent_source="direct",
            hash8="ECOS2603",
            src_root="src",
            pkg="ecos",
            module="phi_guard",
            test_dir="tests",
        )
        rc = validate_template_placeholders(p, ctx)
        # On accepte des placeholders volontairement non résolus (ex: {{delta_phi}})
        assert rc == 0
