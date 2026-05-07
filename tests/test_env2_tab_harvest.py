#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour ENV2 TabHarvest Manager

Repo: gerivdb/NEXUS
Statut: CONFORME_NEXUS
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.env2_tab_harvest import classify_tab, extract_intent, find_gerivdb_repos


def test_classification_ecosystem():
    """Test: URL contient repo gerivdb → ECOSYSTEM"""
    result = classify_tab('https://github.com/gerivdb/DevTools', 'DevTools documentation')
    assert result['type'] == 'ECOSYSTEM', f"Expected ECOSYSTEM, got {result['type']}"
    assert result['nexus_status'] == 'CONFORME_NEXUS'
    assert result['priority'] == 'HIGH'
    assert result['skip'] == False
    print("✓ test_classification_ecosystem passed")


def test_classification_perso():
    """Test: Contenu personnel → SKIP"""
    result = classify_tab('https://example.com', 'whatsapp message')
    assert result['type'] == 'PERSO', f"Expected PERSO, got {result['type']}"
    assert result['nexus_status'] == 'SKIP'
    assert result['priority'] == 'LOW'
    assert result['skip'] == True
    print("✓ test_classification_perso passed")


def test_classification_doc_externe():
    """Test: URL documentation technique → DOC_EXTERNE"""
    result = classify_tab('https://docs.github.com/api', 'API documentation')
    assert result['type'] == 'DOC_EXTERNE', f"Expected DOC_EXTERNE, got {result['type']}"
    assert result['nexus_status'] == 'À_VALIDER_NEXUS'
    assert result['priority'] == 'MED'
    assert result['skip'] == False
    print("✓ test_classification_doc_externe passed")


def test_intent_create():
    """Test: Intent CREATE"""
    result = extract_intent('I want to create a new feature')
    assert result == 'CREATE:feature', f"Expected CREATE:feature, got {result}"
    print("✓ test_intent_create passed")


def test_intent_howto():
    """Test: Intent HOWTO"""
    result = extract_intent('how to setup Python')
    assert result == 'HOWTO:setup', f"Expected HOWTO:setup, got {result}"
    print("✓ test_intent_howto passed")


def test_intent_debug():
    """Test: Intent DEBUG"""
    result = extract_intent('fix the bug in module')
    assert result == 'DEBUG:bug', f"Expected DEBUG:bug, got {result}"
    print("✓ test_intent_debug passed")


def test_find_repos():
    """Test: Find gerivdb repos in content"""
    repos = find_gerivdb_repos('DevTools and ECOYSTEM integration')
    assert 'DevTools' in repos, f"Expected DevTools in {repos}"
    assert 'ECOYSTEM' in repos, f"Expected ECOYSTEM in {repos}"
    print(f"✓ test_find_repos passed: {repos}")


def run_all_tests():
    """Exécute tous les tests"""
    print("=" * 50)
    print("ENV2 TabHarvest - Tests Unitaires")
    print("=" * 50)
    
    tests = [
        test_classification_ecosystem,
        test_classification_perso,
        test_classification_doc_externe,
        test_intent_create,
        test_intent_howto,
        test_intent_debug,
        test_find_repos,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)