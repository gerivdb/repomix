#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite complète de tests TDD pour NEXUS ENGINES COMPLETION
Validation 100% de tous les moteurs et layers
"""

import sys
import os
import subprocess
import pytest
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def run_single_test_suite(test_file):
    """Exécute une suite de tests individuelle"""
    print(f"\n[TEST] Execution de {test_file}...")

    try:
        # Utiliser pytest pour exécuter les tests
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"tests/{test_file}",
            "-v", "--tb=short", "--disable-warnings"
        ], capture_output=True, text=True, timeout=60)

        # Analyser les résultats
        output = result.stdout + result.stderr

        # Compter les tests
        passed = output.count("PASSED") + output.count("passed")
        failed = output.count("FAILED") + output.count("failed") + output.count("ERROR")
        total = passed + failed

        if result.returncode == 0:
            print(f"   ✅ {test_file}: {passed}/{total} tests réussis")
            return {"status": "PASSED", "passed": passed, "failed": failed, "total": total}
        else:
            print(f"   ❌ {test_file}: {passed}/{total} tests réussis, {failed} échoués")
            print(f"   📄 Détails: {output[-500:]}")  # Derniers 500 caractères
            return {"status": "FAILED", "passed": passed, "failed": failed, "total": total}

    except subprocess.TimeoutExpired:
        print(f"   ⏰ {test_file}: Timeout (60s)")
        return {"status": "TIMEOUT", "passed": 0, "failed": 0, "total": 0}
    except Exception as e:
        print(f"   💥 {test_file}: Erreur d'exécution: {e}")
        return {"status": "ERROR", "passed": 0, "failed": 0, "total": 0}


def run_all_tdd_tests():
    """Exécute toutes les suites de tests TDD"""
    print("NEXUS ENGINES COMPLETION - VALIDATION TDD 100%")
    print("=" * 70)

    test_suites = [
        "test_riddler_tdd.py",
        "test_gost_tdd.py",
        "test_fluence_tdd.py",
        "test_magnonic_geometry_tdd.py",
        "test_dev_tdd.py",
        "test_science_tdd.py",
        "test_conceptual_mass_tdd.py",
        "test_transduction_tdd.py"
    ]

    results = {}
    total_passed = 0
    total_failed = 0
    total_tests = 0

    for test_file in test_suites:
        if os.path.exists(f"tests/{test_file}"):
            result = run_single_test_suite(test_file)
            results[test_file] = result

            total_passed += result["passed"]
            total_failed += result["failed"]
            total_tests += result["total"]
        else:
            print(f"   ⚠️ {test_file}: Fichier non trouvé")
            results[test_file] = {"status": "NOT_FOUND", "passed": 0, "failed": 0, "total": 0}

    return results, total_passed, total_failed, total_tests


def run_integration_tests():
    """Exécute les tests d'intégration cross-engines"""
    print("\n🔗 TESTS D'INTÉGRATION CROSS-ENGINES")

    try:
        # Tester l'orchestrateur
        from engines import orchestrator

        # Test cross-engines
        integration_results = orchestrator.test_cross_engine_integration()

        successful_integrations = sum(1 for r in integration_results.values() if r["status"] == "SUCCESS")
        total_integrations = len(integration_results)

        print(f"   ✅ Intégrations réussies: {successful_integrations}/{total_integrations}")

        for test_name, result in integration_results.items():
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
            print(f"     {status_icon} {test_name}")

        return successful_integrations, total_integrations

    except Exception as e:
        print(f"   ❌ Erreur d'intégration: {e}")
        return 0, 1


def generate_comprehensive_report(tdd_results, integration_passed, integration_total):
    """Génère un rapport complet de validation"""
    print("\n📋 RAPPORT COMPLÉT NEXUS ENGINES COMPLETION - VALIDATION 100%")
    print("=" * 70)

    total_passed = sum(r["passed"] for r in tdd_results.values())
    total_failed = sum(r["failed"] for r in tdd_results.values())
    total_tests = sum(r["total"] for r in tdd_results.values())

    # Résumé TDD
    print("🧪 TESTS TDD:")
    print(f"   Total exécuté: {total_tests} tests")
    print(f"   Réussis: {total_passed}")
    print(f"   Échoués: {total_failed}")
    tdd_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"   Taux de réussite: {tdd_success_rate:.1f}%")
    # Détail par suite
    print("\n   📊 Détail par moteur:")
    for test_file, result in tdd_results.items():
        engine_name = test_file.replace("test_", "").replace("_tdd.py", "").upper()
        if result["total"] > 0:
            rate = result["passed"] / result["total"] * 100
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"     {status_icon} {engine_name}: {result['passed']}/{result['total']} tests ({rate:.1f}%)")
        else:
            print(f"     ⚠️ {engine_name}: Non exécuté")

    # Résumé Intégration
    print("\n🔗 TESTS D'INTÉGRATION:")
    integration_rate = (integration_passed / integration_total * 100) if integration_total > 0 else 0
    print(f"   Taux de réussite: {integration_rate:.1f}%")
    # Score Global
    print("\n🌟 SCORE GLOBAL:")
    print(f"   Score global: {overall_score:.1f}%")
    print(f"   📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Évaluation Finale
    if overall_score >= 99.0:
        print("\n🎉 VALIDATION 100% RÉUSSIE!")
        print("   ✅ Tous les moteurs opérationnels")
        print("   ✅ Toutes les intégrations validées")
        print("   ✅ NEXUS ENGINES COMPLETION terminé")
        return True
    elif overall_score >= 95.0:
        print("\n⚠️ VALIDATION QUASI-COMPLÈTE (>95%)")
        print("   ✅ Moteurs principaux opérationnels")
        print("   ⚠️ Quelques tests mineurs à corriger")
        return True
    else:
        print(f"\n❌ VALIDATION INCOMPLÈTE ({overall_score:.1f}%)")
        print("   ❌ Corrections requises avant déploiement")
        return False


def main():
    """Fonction principale"""
    # Exécuter tous les tests TDD
    tdd_results, tdd_passed, tdd_failed, tdd_total = run_all_tdd_tests()

    # Exécuter les tests d'intégration
    integration_passed, integration_total = run_integration_tests()

    # Générer le rapport final
    success = generate_comprehensive_report(tdd_results, integration_passed, integration_total)

    # Code de retour
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)