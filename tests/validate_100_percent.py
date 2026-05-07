#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite complete de tests TDD pour NEXUS ENGINES COMPLETION
Validation 100% de tous les moteurs et layers
"""

import sys
import os
import subprocess
from datetime import datetime

# Ajouter le repertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def run_pytest_suite(test_file):
    """Execute une suite de tests avec pytest"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"tests/{test_file}",
            "-v", "--tb=line", "--disable-warnings", "--quiet"
        ], capture_output=True, text=True, timeout=30)

        # Analyser les resultats
        passed = result.stdout.count("PASSED") + result.stdout.count("passed")
        failed = result.stdout.count("FAILED") + result.stdout.count("failed")

        return result.returncode == 0, passed, failed
    except:
        return False, 0, 1


def main():
    """Fonction principale"""
    print("NEXUS ENGINES COMPLETION - VALIDATION COMPLETE 100%")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

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

    total_passed = 0
    total_failed = 0
    successful_suites = 0

    for test_file in test_suites:
        if os.path.exists(f"tests/{test_file}"):
            print(f"Testing {test_file}...")
            success, passed, failed = run_pytest_suite(test_file)

            if success:
                print(f"  [OK] {passed} tests passed")
                successful_suites += 1
                total_passed += passed
            else:
                print(f"  [FAIL] {passed} passed, {failed} failed")
                total_failed += failed
        else:
            print(f"  [MISSING] {test_file} not found")

    print()
    print("RESULTS SUMMARY:")
    print(f"  Suites executed: {len(test_suites)}")
    print(f"  Successful suites: {successful_suites}")
    print(f"  Total tests passed: {total_passed}")
    print(f"  Total tests failed: {total_failed}")

    success_rate = (successful_suites / len(test_suites) * 100) if test_suites else 0
    print(f"  Success rate: {success_rate:.1f}%")

    if success_rate >= 99.0:
        print()
        print("SUCCESS: 100% VALIDATION ACHIEVED!")
        print("All engines are fully tested and operational.")
        return 0
    else:
        print()
        print(f"FAILURE: Only {success_rate:.1f}% success rate")
        print("Some tests need to be fixed.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)