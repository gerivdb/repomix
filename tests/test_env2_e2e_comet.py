#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENV2 E2E Test — Test réel avec Comet/Chrome

Repo: gerivdb/NEXUS
Layer: ENV2 (Browser Automation + Internet)
Statut: CONFORME_NEXUS

Ce test vérifie que le middleware ENV2 fonctionne réellement avec un navigateur.
Il nécessite qu'un navigateur soit lancé avec --remote-debugging-port=9222.

Usage:
    # 1. Lancer Comet/Chrome avec CDP
    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
    
    # 2. Exécuter le test
    python tests/test_env2_e2e_comet.py
"""

import json
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Optional

# Add managers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "managers"))


class TestE2E_CometLauncher(unittest.TestCase):
    """Test E2E du Comet Launcher"""
    
    def test_launcher_check_cdp_available(self):
        """Teste la vérification de disponibilité CDP"""
        from managers.comet_launcher import check_cdp_available
        
        # Ce test peut échouer si aucun navigateur n'est lancé
        result = check_cdp_available("localhost", 9222)
        
        if result:
            print(f"\n✅ CDP disponible: {result.get('Browser', 'Unknown')}")
            self.assertIsInstance(result, dict)
            self.assertIn("Browser", result)
        else:
            print("\n⚠️ CDP non disponible - Lancez Chrome/Comet avec --remote-debugging-port=9222")
            self.skipTest("Aucun navigateur CDP disponible")
    
    def test_launcher_find_exe(self):
        """Teste la recherche d'exécutable"""
        from managers.comet_launcher import find_exe, CHROME_PATHS, COMET_PATHS
        
        # Tester Chrome
        chrome_path = find_exe(CHROME_PATHS)
        if chrome_path:
            print(f"\n✅ Chrome trouvé: {chrome_path}")
        else:
            print("\n⚠️ Chrome non trouvé")
        
        # Tester Comet
        comet_path = find_exe(COMET_PATHS)
        if comet_path:
            print(f"✅ Comet trouvé: {comet_path}")
        else:
            print("⚠️ Comet non trouvé (normal si non installé)")


class TestE2E_CDPClient(unittest.TestCase):
    """Test E2E du CDP Client"""
    
    def setUp(self):
        """Vérifie que CDP est disponible avant chaque test"""
        from managers.cdp_client import CDPClient
        
        self.client = CDPClient(host="localhost", port=9222)
        
        if not self.client.is_available():
            self.skipTest("Aucun navigateur CDP disponible sur localhost:9222")
    
    def test_cdp_list_targets(self):
        """Teste la liste des tabs"""
        targets = self.client.list_targets()
        
        print(f"\n📋 Tabs trouvées: {len(targets)}")
        for i, tab in enumerate(targets[:5]):  # Afficher les 5 premières
            print(f"  {i+1}. {tab.title[:50]} - {tab.url[:60]}")
        
        self.assertIsInstance(targets, list)
    
    def test_cdp_get_version(self):
        """Teste la récupération de la version"""
        version = self.client.get_version()
        
        if version:
            print(f"\n🌐 Browser: {version.get('Browser', 'Unknown')}")
            print(f"   Protocol: {version.get('Protocol-Version', 'Unknown')}")
            self.assertIsInstance(version, dict)
        else:
            print("\n⚠️ Version non disponible")
    
    def test_cdp_create_target(self):
        """Teste la création d'une nouvelle tab"""
        test_url = "https://example.com"
        
        print(f"\n🔗 Ouverture de: {test_url}")
        target_id = self.client.create_target(test_url)
        
        if target_id:
            print(f"✅ Tab créée avec ID: {target_id}")
            self.assertIsInstance(target_id, str)
        else:
            print("⚠️ Échec création tab")
    
    def test_cdp_activate_target(self):
        """Teste l'activation d'une tab"""
        targets = self.client.list_targets()
        
        if targets:
            target = targets[0]
            print(f"\n🎯 Activation de: {target.title[:50]}")
            
            success = self.client.activate_target(target.id)
            if success:
                print("✅ Tab activée")
            else:
                print("⚠️ Échec activation")


class TestE2E_TabHarvest(unittest.TestCase):
    """Test E2E de TabHarvest avec classification"""
    
    def test_classification_reelle(self):
        """Teste la classification sur des tabs réelles"""
        from managers.cdp_client import CDPClient
        from managers.env2_tab_harvest import classify_tab
        
        client = CDPClient(host="localhost", port=9222)
        
        if not client.is_available():
            self.skipTest("Aucun navigateur CDP disponible")
        
        targets = client.list_targets()
        
        print(f"\n📊 Classification de {len(targets)} tabs:")
        
        for tab in targets[:5]:  # Classifier les 5 premières tabs
            classification = classify_tab(tab.url, tab.title)
            print(f"  {tab.title[:30]} → {classification['type']}")
            
            self.assertIn("type", classification)
            self.assertIn("nexus_status", classification)


class TestE2E_AutoHeal(unittest.TestCase):
    """Test E2E de l'auto-healing"""
    
    def test_health_check(self):
        """Teste la vérification de santé"""
        from managers.auto_heal import BrowserHealthChecker, HealthStatus
        
        checker = BrowserHealthChecker(host="localhost", port=9222)
        report = checker.check()
        
        print(f"\n🏥 Health Report:")
        print(f"  Status: {report.status.value}")
        print(f"  Browser: {report.browser}")
        print(f"  Tabs: {report.tabs_count}")
        
        if report.status == HealthStatus.HEALTHY:
            print("  ✅ Browser is healthy")
        else:
            print("  ⚠️ Browser health issues detected")


class TestE2E_Integration(unittest.TestCase):
    """Test d'intégration complète"""
    
    def test_full_workflow(self):
        """Teste un workflow complet"""
        from managers.cdp_client import CDPClient, SessionManager
        from managers.env2_tab_harvest import classify_tab, extract_intent
        from managers.auto_heal import BrowserHealthChecker, HealthStatus
        
        # 1. Vérifier santé
        checker = BrowserHealthChecker(host="localhost", port=9222)
        health = checker.check()
        
        if health.status != HealthStatus.HEALTHY:
            self.skipTest("Browser not healthy")
        
        print(f"\n🔄 Full Workflow Test:")
        print(f"  1. Health: {health.status.value} ✅")
        
        # 2. Lister les tabs
        client = CDPClient(host="localhost", port=9222)
        targets = client.list_targets()
        print(f"  2. Tabs: {len(targets)} ✅")
        
        # 3. Classifier
        if targets:
            tab = targets[0]
            classification = classify_tab(tab.url, tab.title)
            print(f"  3. Classification: {classification['type']} ✅")
        
        # 4. Sauvegarder session
        manager = SessionManager()
        session_path = manager.save_session(
            name="test-e2e",
            tabs=targets,
            context="E2E Test"
        )
        print(f"  4. Session saved: {session_path} ✅")
        
        # 5. Nettoyer
        manager.delete_session("test-e2e")
        print(f"  5. Session cleaned ✅")


def run_manual_test():
    """Exécute un test manuel interactif"""
    print("=" * 60)
    print("ENV2 Middleware — Test Manuel avec Comet/Chrome")
    print("=" * 60)
    
    from managers.comet_launcher import ensure_cdp_with_fallback
    
    print("\n1. Vérification/Lancement du navigateur...")
    result = ensure_cdp_with_fallback(port=9222, dry_run=False)
    
    if result.returncode == 0:
        print(f"   ✅ Navigateur disponible: {result.browser}")
        print(f"   Port: {result.port}")
        print(f"   CDP URL: {result.cdp_url}")
    else:
        print(f"   ❌ Échec: {result.message}")
        print("\n   Instructions:")
        print("   1. Fermez tous les navigateurs")
        print("   2. Lancez Chrome avec:")
        print('      "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
        return False
    
    from managers.cdp_client import CDPClient
    
    print("\n2. Liste des tabs...")
    client = CDPClient(host="localhost", port=9222)
    targets = client.list_targets()
    print(f"   {len(targets)} tabs trouvées")
    
    for i, tab in enumerate(targets[:5]):
        print(f"   - {tab.title[:50]}")
    
    print("\n3. Version du navigateur...")
    version = client.get_version()
    if version:
        print(f"   {version.get('Browser', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("✅ Tests manuels complétés avec succès!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    # Mode interactif
    if len(sys.argv) == 1:
        print("\nChoix du mode de test:")
        print("  1. Tests unitaires (nécessite navigateur lancé)")
        print("  2. Test manuel interactif")
        print("  3. Tous les tests")
        
        choice = input("\nVotre choix [1-3]: ").strip()
        
        if choice == "2":
            success = run_manual_test()
            sys.exit(0 if success else 1)
        elif choice == "3":
            sys.argv.append("-v")
        else:
            sys.argv.append("-v")
    
    # Exécuter les tests
    unittest.main(verbosity=2)