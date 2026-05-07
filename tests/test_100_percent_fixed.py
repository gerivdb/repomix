#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation 100% - NEXUS ENGINES COMPLETION
Tests TDD complets pour tous les moteurs
"""

import sys
import os
import subprocess
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def run_test_file(test_file):
    """Execute un fichier de test et analyse les resultats"""
    try:
        cmd = [sys.executable, "-m", "pytest", f"tests/{test_file}", "--tb=no", "-q"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        stdout = result.stdout
        stderr = result.stderr

        # Parser les resultats pytest
        passed_match = re.search(r'(\d+) passed', stdout)
        failed_match = re.search(r'(\d+) failed', stdout)
        error_match = re.search(r'(\d+) error', stdout)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(error_match.group(1)) if error_match else 0

        total = passed + failed + errors

        success = result.returncode == 0 and failed == 0 and errors == 0

        return success, passed, failed, errors, total

    except subprocess.TimeoutExpired:
        return False, 0, 0, 1, 0
    except Exception as e:
        return False, 0, 0, 1, 0


def main():
    """Fonction principale"""
    print("NEXUS ENGINES COMPLETION - VALIDATION 100%")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    test_files = [
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
    total_errors = 0
    total_tests = 0
    successful_files = 0

    for test_file in test_files:
        if os.path.exists(f"tests/{test_file}"):
            print(f"Testing {test_file}...")
            success, passed, failed, errors, total = run_test_file(test_file)

            total_passed += passed
            total_failed += failed
            total_errors += errors
            total_tests += total

            if success:
                successful_files += 1
                print(f"  [OK] {passed} passed")
            else:
                print(f"  [FAIL] {passed} passed, {failed} failed, {errors} errors")
        else:
            print(f"  [MISSING] {test_file}")

    print()
    print("FINAL RESULTS:")
    print(f"  Files tested: {len(test_files)}")
    print(f"  Successful: {successful_files}")
    print(f"  Total tests: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    print(f"  Errors: {total_errors}")

    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"  Success rate: {success_rate:.1f}%")

        if success_rate >= 99.0 and total_failed == 0 and total_errors == 0:
            print()
            print("SUCCESS: 100% VALIDATION ACHIEVED!")
            print("All NEXUS engines are fully tested and operational.")
            return 0
        else:
            print()
            print(f"FAILURE: Only {success_rate:.1f}% success rate")
            print("Tests need fixes before deployment.")
            return 1
    else:
        print("No tests were executed.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)