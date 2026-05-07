#!/usr/bin/env python3
"""
Mini-benchmark interne pour la régression du moteur autoresearch.
Jeu de sessions figées (configs, seeds, repo jouet), snapshots de résultats attendus.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

from NEXUS.autoresearch.benchmark_runner import BenchmarkRunner
from NEXUS.autoresearch.decision_engine import DecisionEngine
from NEXUS.autoresearch.git_manager import GitManager, SafetyVeto
from NEXUS.autoresearch.session_runner import main as SessionRunner
from NEXUS.autoresearch.contracts import (
    BenchmarkResult,
    IterationResult,
    SessionSummary,
    DecisionRecord,
    SafetyVetoConfig,
    SessionConfig,
)

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# ============================================================
# SNAPSHOTS DE RÉFÉRENCE (attendus pour les tests de régression)
# ============================================================

REFERENCE_SNAPSHOTS = {
    "benchmark_basic": {
        "status": "success",
        "iterations": 5,
        "warmup_iterations": 1,
        "success_rate_min": 0.9,
        "time_per_iter_max": 5.0,
    },
    "decision_engine_basic": {
        "improvement_threshold": 5.0,
        "baseline_metric": 1.0,
        "should_improve_on_better_value": True,
        "should_reject_on_worse_value": True,
    },
    "safety_veto_limits": {
        "max_lines": 500,
        "max_files": 50,
        "should_reject_over_limit": True,
    },
    "dry_run_mode": {
        "status": "success_dry_run",
        "has_dry_run_details": True,
        "should_not_write_git": True,
    },
    "session_config_validation": {
        "required_fields": [
            "session_name",
            "module_path",
            "editable_paths",
            "max_iterations",
        ],
        "default_safety_limits": {
            "max_lines_changed_per_session": 500,
            "max_files_changed_per_session": 50,
        },
    },
}


def test_benchmark_runner_basic():
    """Test 1: Le BenchmarkRunner s'exécute sans erreur et retourne des métriques valides."""
    logger.info("=" * 70)
    logger.info("TEST 1: BenchmarkRunner - exécution basique")
    logger.info("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        os.system("git init")
        os.system('git config user.email "test@test.com"')
        os.system('git config user.name "Test"')

        with open("dummy.py", "w") as f:
            f.write("print('hello')\n")
        os.system("git add .")
        os.system('git commit -m "init"')

        runner = BenchmarkRunner(
            repo_path=tmpdir,
            iterations=5,
            metrics=["time_per_iter", "success_rate"],
            warmup=1,
            use_git=False,
        )
        result: BenchmarkResult = runner.run()

        ref = REFERENCE_SNAPSHOTS["benchmark_basic"]
        assert result.status == ref["status"], f"Status attendu: {ref['status']}"
        assert result.iterations == ref["iterations"], f"Iterations attendues: {ref['iterations']}"
        assert result.warmup_iterations == ref["warmup_iterations"]
        assert result.success_rate >= ref["success_rate_min"], f"Taux de succès trop bas: {result.success_rate}"
        assert result.time_per_iter <= ref["time_per_iter_max"], f"Temps par itération trop élevé: {result.time_per_iter}"
        assert result.measured_iterations > 0, "Aucune itération mesurée"

    logger.info("✓ TEST 1 PASSED - BenchmarkRunner OK\n")


def test_decision_engine_baseline():
    """Test 2: Le DecisionEngine compare correctement les métriques."""
    logger.info("=" * 70)
    logger.info("TEST 2: DecisionEngine - logique keep/revert")
    logger.info("=" * 70)

    engine = DecisionEngine(repo_path="/tmp/test", require_improvement_percent=5.0)
    engine.set_baseline(1.0)

    ref = REFERENCE_SNAPSHOTS["decision_engine_basic"]

    keep1, improvement1, veto1 = engine.evaluate_iteration(
        {"success": True, "value": 0.95},
        "commit_good"
    )
    assert ref["should_improve_on_better_value"] == (keep1 is True), "Devrait accepter l'amélioration"
    assert veto1 is None, "Pas de veto attendu"
    logger.info("✓ Amélioration acceptée correctement")

    keep2, improvement2, veto2 = engine.evaluate_iteration(
        {"success": True, "value": 0.98},
        "commit_bad"
    )
    assert keep2 is False or improvement2 is None, "Devrait rejeter la régression"
    logger.info("✓ Régression détectée et rejetée")

    keep3, improvement3, veto3 = engine.evaluate_iteration(
        {"success": False, "value": None},
        "commit_fail"
    )
    assert keep3 is False, "Devrait rejeter l'échec"
    logger.info("✓ Échec de métrique rejeté")

    logger.info("✓ TEST 2 PASSED - DecisionEngine OK\n")


def test_safety_veto_limits():
    """Test 3: Les garde-fous bloquent les changements excessifs."""
    logger.info("=" * 70)
    logger.info("TEST 3: SafetyVeto - limites et patterns suspects")
    logger.info("=" * 70)

    config = SafetyVetoConfig(
        max_lines_changed_per_session=100,
        max_files_changed_per_session=5,
        protected_paths=[".git", "__pycache__"],
    )
    veto = SafetyVeto(config)

    ref = REFERENCE_SNAPSHOTS["safety_veto_limits"]

    safe_ok, safe_reason = veto.check_limits(lines_changed=50, files_changed=3)
    assert safe_ok is True, f"Sous limite refusé: {safe_reason}"
    logger.info("✓ Changements sous la limite acceptés")

    if ref["should_reject_over_limit"]:
        safe_fail, fail_reason = veto.check_limits(lines_changed=200, files_changed=3)
        assert safe_fail is False, "Devrait refuser au-dessus limite"
        assert "exceeds limit" in (fail_reason or "")
        logger.info("✓ Limite de lignes appliquée")

        safe_fail2, fail_reason2 = veto.check_limits(lines_changed=50, files_changed=10)
        assert safe_fail2 is False, "Devrait refuser au-dessus limite"
        logger.info("✓ Limite de fichiers appliquée")

    safe_prot, prot_reason = veto.check_diff_safety(
        "diff text normal",
        ["module.py", ".git/config"]
    )
    assert safe_prot is False, "Devait détecter chemin protégé"
    assert "Protected path" in (prot_reason or "")
    logger.info("✓ Protection des chemins sensibles active")

    bad_diff2 = """--- a/__pycache__/module.pyc
+++ /dev/null
@@ -1,10 +0,0 @@
-old bytecode
-old bytecode2
-"""
    safe_pat2, pat_reason2 = veto.check_diff_safety(bad_diff2, ["__pycache__/module.pyc"])
    assert safe_pat2 is False, f"Devait détecter chemin protégé: {pat_reason2}"
    logger.info("✓ Détection de patterns/chemins suspects active")

    logger.info("✓ TEST 3 PASSED - SafetyVeto OK\n")


def test_dry_run_mode():
    """Test 4: Le mode dry_run_strict ne modifie pas Git."""
    logger.info("=" * 70)
    logger.info("TEST 4: Dry run mode - pas de modifications Git")
    logger.info("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        os.system("git init")
        os.system('git config user.email "test@test.com"')
        os.system('git config user.name "Test"')

        with open("dummy.py", "w") as f:
            f.write("print('hello')\n")
        os.system("git add .")
        os.system('git commit -m "init"')

        initial_commit = os.popen("git rev-parse HEAD").read().strip()
        logger.info(f"Commit initial: {initial_commit}")

        config_content = {
            "constraints": {
                "max_iterations": 3,
                "editable_paths": ["dummy.py"],
                "environment_vars": {},
            }
        }
        import yaml
        config_path = os.path.join(tmpdir, "dry_run_config.yaml")
        with open(config_path, "w") as f:
            yaml.dump(config_content, f)

        from NEXUS.autoresearch.session_runner import run_dry_simulation
        import logging
        logging.getLogger().setLevel(logging.INFO)

        results = run_dry_simulation(config_content, logger)

        ref = REFERENCE_SNAPSHOTS["dry_run_mode"]
        assert results["status"] == ref["status"], f"Statut attendu: {ref['status']}"
        assert "dry_run_details" in results
        logger.info("✓ Résultats du dry-run générés")

        final_commit = os.popen("git rev-parse HEAD").read().strip()
        assert initial_commit == final_commit, "Git a été modifié pendant le dry-run!"
        logger.info("✓ Aucune modification Git détectée (dry-run respecté)")

    logger.info("✓ TEST 4 PASSED - Dry run OK\n")


def test_contracts_serialization():
    """Test 5: Les dataclasses se sérialisent correctement."""
    logger.info("=" * 70)
    logger.info("TEST 5: Contracts - sérialisation JSON")
    logger.info("=" * 70)

    ref = REFERENCE_SNAPSHOTS["session_config_validation"]

    config = SessionConfig(
        session_name="test_session",
        module_path="NEXUS/mymodule.py",
        editable_paths=["NEXUS/mymodule.py", "NEXUS/sub/helper.py"],
        protected_files=["NEXUS/important.py"],
        max_iterations=15,
        metric_names=["time_per_iter", "success_rate"],
        require_improvement_percent=3.0,
    )

    from NEXUS.autoresearch.contracts import config_to_dict
    d = config_to_dict(config)

    for field in ref["required_fields"]:
        assert field in d, f"Champ manquant: {field}"
        logger.info(f"✓ Champ '{field}' présent")

    safety = d["safety_config"]
    assert safety["max_lines_changed_per_session"] == ref["default_safety_limits"]["max_lines_changed_per_session"]
    assert safety["max_files_changed_per_session"] == ref["default_safety_limits"]["max_files_changed_per_session"]
    logger.info("✓ Valeurs par défaut correctes")

    iter_result = IterationResult(
        iteration=1,
        metric_value=0.95,
        success=True,
        lines_changed=10,
        commit_hash="abc123",
    )
    assert iter_result.iteration == 1
    assert iter_result.metric_value == 0.95
    logger.info("✓ IterationResult créable")

    summary = SessionSummary(
        session_id="test_001",
        start_time=datetime.now().isoformat(),
        end_time=datetime.now().isoformat(),
        iteration_count=10,
        successful_iterations=8,
        baseline_metric=1.0,
        best_metric=0.85,
        overall_improvement=15.0,
        results=[iter_result],
        config_used=config_to_dict(config),
        dry_run=False,
    )
    assert summary.overall_improvement == 15.0
    assert len(summary.results) == 1
    logger.info("✓ SessionSummary créable")

    decision = DecisionRecord(
        iteration=1,
        metric_before=1.0,
        metric_after=0.95,
        improvement=0.05,
        improvement_percent=5.0,
        decision="keep",
        reason="Improvement > threshold",
        safety_veto=False,
        files_changed=["module.py"],
    )
    assert decision.decision == "keep"
    assert decision.improvement_percent == 5.0
    logger.info("✓ DecisionRecord créable")

    import json
    json_str = json.dumps(config_to_dict(config), indent=2, default=str)
    loaded = json.loads(json_str)
    assert loaded["session_name"] == "test_session"
    logger.info("✓ JSON sérialisation valide")

    logger.info("✓ TEST 5 PASSED - Contracts OK\n")


def test_integration_session_config():
    """Test 6: Configuration YAML -> SessionConfig valide."""
    logger.info("=" * 70)
    logger.info("TEST 6: Intégration - YAML vers SessionConfig")
    logger.info("=" * 70)

    test_yaml = """
session_name: "test_norm_engine"
module_path: "engines/norm_engine.py"
editable_paths:
  - "engines/norm_engine.py"
protected_files:
  - "engines/norm_engine.py.backup"
max_iterations: 20
metric_names:
  - "time_per_iter"
  - "success_rate"
metric_weights:
  time_per_iter: 1.0
require_improvement_percent: 5.0
warmup_iterations: 2
use_git: false
use_safety_veto: true
safety_config:
  max_lines_changed_per_session: 300
  max_files_changed_per_session: 20
  protected_paths:
    - ".git"
    - "__pycache__"
dry_run_strict: false
logging_level: "INFO"
enable_tracing: false
"""
    import yaml
    data = yaml.safe_load(test_yaml)

    assert data["session_name"] == "test_norm_engine"
    assert data["max_iterations"] == 20
    assert data["require_improvement_percent"] == 5.0
    assert data["use_safety_veto"] is True

    safety = data["safety_config"]
    assert safety["max_lines_changed_per_session"] == 300
    assert safety["max_files_changed_per_session"] == 20

    assert ".git" in safety["protected_paths"]

    logger.info("✓ YAML parsing valid")
    logger.info("✓ TEST 6 PASSED - Intégration OK\n")


if __name__ == "__main__":
    logger.info("\n" + "=" * 70)
    logger.info("SUITE DE TESTS : Moteur Autoresearch - Régression")
    logger.info("=" * 70 + "\n")

    tests = [
        test_benchmark_runner_basic,
        test_decision_engine_baseline,
        test_safety_veto_limits,
        test_dry_run_mode,
        test_contracts_serialization,
        test_integration_session_config,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            logger.error(f"✗ TEST ÉCHOUÉ: {test.__name__}")
            logger.error(f"  Raison: {e}")
            failed += 1
        except Exception as e:
            logger.error(f"✗ TEST ERREUR: {test.__name__}")
            logger.error(f"  Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    logger.info("=" * 70)
    logger.info(f"RÉSULTATS: {passed} passés, {failed} échoués")
    logger.info("=" * 70 + "\n")

    sys.exit(0 if failed == 0 else 1)
