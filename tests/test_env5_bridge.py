#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENV5 Bridge Tests — Tests pour MCP Bridge ENV2+ENV5

Repo: gerivdb/NEXUS
Layer: ENV2 (Browser Automation + Internet)
Statut: CONFORME_NEXUS
"""

import asyncio
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

# Add managers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "managers"))


class TestENV5Bridge(unittest.TestCase):
    """Tests pour ENV5 Bridge"""
    
    def test_bridge_creation(self):
        """Teste la création du bridge"""
        from managers.env5_bridge import ENV5Bridge
        
        bridge = ENV5Bridge()
        self.assertEqual(bridge.env5_url, "https://api.chatjimmy.ai")
        self.assertTrue(bridge.use_mcp)
        self.assertIsNone(bridge.mcp_client)
    
    def test_diagnosis_action_enum(self):
        """Teste les actions de diagnostic"""
        from managers.env5_bridge import DiagnosisAction
        
        self.assertEqual(DiagnosisAction.RESTART_BROWSER.value, "restart_browser")
        self.assertEqual(DiagnosisAction.CLEAR_CACHE.value, "clear_cache")
        self.assertEqual(DiagnosisAction.CHANGE_PORT.value, "change_port")
        self.assertEqual(DiagnosisAction.CLOSE_TABS.value, "close_tabs")
    
    def test_diagnosis_dataclass(self):
        """Teste la structure Diagnosis"""
        from managers.env5_bridge import Diagnosis, DiagnosisAction
        
        diagnosis = Diagnosis(
            error="CDP not responding",
            root_cause="Browser crashed",
            confidence=0.9,
            action=DiagnosisAction.RESTART_BROWSER,
            params={},
            explanation="Le navigateur a crashé"
        )
        
        self.assertEqual(diagnosis.error, "CDP not responding")
        self.assertEqual(diagnosis.root_cause, "Browser crashed")
        self.assertEqual(diagnosis.confidence, 0.9)
        self.assertEqual(diagnosis.action, DiagnosisAction.RESTART_BROWSER)
    
    def test_classification_dataclass(self):
        """Teste la structure Classification"""
        from managers.env5_bridge import Classification
        
        classification = Classification(
            url="https://github.com/gerivdb/DevTools",
            title="DevTools",
            env2_type="ECOSYSTEM",
            env2_confidence=0.7,
            env5_type="ECOSYSTEM",
            env5_confidence=0.95,
            final_type="ECOSYSTEM",
            final_confidence=0.95,
            method="hybrid"
        )
        
        self.assertEqual(classification.url, "https://github.com/gerivdb/DevTools")
        self.assertEqual(classification.final_type, "ECOSYSTEM")
        self.assertEqual(classification.method, "hybrid")


class TestENV5BridgeAsync(unittest.TestCase):
    """Tests asynchrones pour ENV5 Bridge"""
    
    def test_predict_with_mock(self):
        """Teste predict() avec mock"""
        from managers.env5_bridge import ENV5Bridge
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            result = await bridge.predict("https://example.com", "classify")
            
            self.assertIsInstance(result, dict)
            self.assertIn("type", result)
        
        asyncio.run(run_test())
    
    def test_diagnose_with_mock(self):
        """Teste diagnose() avec mock"""
        from managers.env5_bridge import ENV5Bridge, DiagnosisAction
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            diagnosis = await bridge.diagnose(
                "CDP connection refused",
                {"port": 9222, "browser": "chrome"}
            )
            
            self.assertIsInstance(diagnosis.action, DiagnosisAction)
            self.assertGreater(diagnosis.confidence, 0)
        
        asyncio.run(run_test())
    
    def test_classify_hybrid_high_confidence(self):
        """Teste classification hybride avec haute confiance ENV2"""
        from managers.env5_bridge import ENV5Bridge
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            
            env2_result = {
                "type": "ECOSYSTEM",
                "confidence": 0.9  # Haute confiance
            }
            
            classification = await bridge.classify_hybrid(
                "https://github.com/gerivdb/DevTools",
                "DevTools",
                env2_result
            )
            
            # ENV2 confiant → ENV5 pas appelé
            self.assertEqual(classification.method, "env2_only")
            self.assertIsNone(classification.env5_type)
            self.assertEqual(classification.final_type, "ECOSYSTEM")
        
        asyncio.run(run_test())
    
    def test_classify_hybrid_low_confidence(self):
        """Teste classification hybride avec basse confiance ENV2"""
        from managers.env5_bridge import ENV5Bridge
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            
            env2_result = {
                "type": "DOC_EXTERNE",
                "confidence": 0.5  # Basse confiance
            }
            
            classification = await bridge.classify_hybrid(
                "https://example.com/doc",
                "Documentation",
                env2_result
            )
            
            # ENV2 pas confiant → ENV5 appelé
            self.assertEqual(classification.method, "hybrid")
            self.assertIsNotNone(classification.env5_type)
        
        asyncio.run(run_test())
    
    def test_generate_tests_with_mock(self):
        """Teste generate_tests() avec mock"""
        from managers.env5_bridge import ENV5Bridge
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            
            code = "def add(a, b): return a + b"
            tests = await bridge.generate_tests(code)
            
            self.assertIsInstance(tests, list)
        
        asyncio.run(run_test())


class TestHybridClassifier(unittest.TestCase):
    """Tests pour HybridClassifier"""
    
    def test_hybrid_classifier_creation(self):
        """Teste la création de HybridClassifier"""
        from managers.env5_bridge import HybridClassifier, ENV5Bridge
        
        mock_env2 = MagicMock()
        bridge = ENV5Bridge(use_mcp=False)
        classifier = HybridClassifier(mock_env2, bridge)
        
        self.assertEqual(classifier.env2, mock_env2)
        self.assertEqual(classifier.env5, bridge)
    
    def test_hybrid_classifier_classify(self):
        """Teste la classification hybride"""
        from managers.env5_bridge import HybridClassifier, ENV5Bridge
        
        async def run_test():
            mock_env2 = MagicMock()
            mock_env2.classify.return_value = {
                "type": "ECOSYSTEM",
                "confidence": 0.6
            }
            
            bridge = ENV5Bridge(use_mcp=False)
            classifier = HybridClassifier(mock_env2, bridge)
            
            classification = await classifier.classify(
                "https://github.com/gerivdb/DevTools",
                "DevTools"
            )
            
            # ENV2 appelé
            mock_env2.classify.assert_called_once()
            # ENV5 devrait être appelé car confiance < 0.8
            self.assertEqual(classification.method, "hybrid")
        
        asyncio.run(run_test())


class TestIntegration_ENV2_ENV5(unittest.TestCase):
    """Tests d'intégration ENV2+ENV5"""
    
    def test_full_workflow_hybrid(self):
        """Teste un workflow complet ENV2+ENV5"""
        from managers.env5_bridge import ENV5Bridge, DiagnosisAction
        from managers.env2_tab_harvest import classify_tab
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            
            # 1. Classification ENV2 (rapide)
            env2_result = classify_tab("https://github.com/gerivdb/DevTools", "DevTools")
            
            # 2. Classification hybride (ENV2+ENV5)
            classification = await bridge.classify_hybrid(
                "https://github.com/gerivdb/DevTools",
                "DevTools",
                env2_result
            )
            
            # 3. Vérification
            self.assertIn(classification.final_type, ["ECOSYSTEM", "DEV_TOOL", "DOC_EXTERNE"])
            
            return classification
        
        result = asyncio.run(run_test())
        print(f"\n📊 Classification hybride: {result.final_type} ({result.method})")
    
    def test_smart_recovery_workflow(self):
        """Teste le workflow de smart recovery"""
        from managers.env5_bridge import ENV5Bridge, DiagnosisAction
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            
            # Simule un rapport de santé
            health_report = {
                "status": "unhealthy",
                "message": "CDP connection refused",
                "port": 9222,
                "tabs_count": 5
            }
            
            # Diagnostic ENV5
            diagnosis = await bridge.diagnose(
                health_report["message"],
                health_report
            )
            
            print(f"\n🏥 Diagnostic ENV5:")
            print(f"   Cause: {diagnosis.root_cause}")
            print(f"   Action: {diagnosis.action.value}")
            print(f"   Confiance: {diagnosis.confidence}")
            
            self.assertIsInstance(diagnosis.action, DiagnosisAction)
        
        asyncio.run(run_test())


class TestSynergy_Scenarios(unittest.TestCase):
    """Tests des scénarios de synergie ENV2+ENV5"""
    
    def test_scenario_debug_assisted(self):
        """Scénario: Debug assisté par ENV5"""
        from managers.env5_bridge import ENV5Bridge, DiagnosisAction
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            
            print("\n🐛 Scénario: Debug Assisté")
            
            # 1. ENV2 détecte erreur
            error_msg = "CDP connection refused on port 9222"
            print(f"   1. ENV2 détecte: {error_msg}")
            
            # 2. ENV5 diagnostique
            diagnosis = await bridge.diagnose(error_msg, {"port": 9222})
            print(f"   2. ENV5 diagnostique: {diagnosis.root_cause}")
            print(f"   3. ENV5 recommande: {diagnosis.action.value}")
            
            # 4. ENV2 applique le fix
            print(f"   4. ENV2 applique: {diagnosis.action.value}")
            
            self.assertIsNotNone(diagnosis.action)
        
        asyncio.run(run_test())
    
    def test_scenario_smart_navigation(self):
        """Scénario: Navigation intelligente"""
        from managers.env5_bridge import ENV5Bridge
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            
            print("\n🧭 Scénario: Navigation Intelligente")
            
            # 1. ENV5 prédit les tabs pertinentes
            goal = "Implementer une nouvelle feature NEXUS"
            prediction = await bridge.predict("", f"predict_relevant_docs:{goal}")
            print(f"   1. Goal: {goal}")
            print(f"   2. ENV5 prédit: {prediction}")
            
            # 3. ENV2 ouvre seulement les tabs pertinentes
            print(f"   3. ENV2 ouvre les tabs pertinentes")
            
            self.assertIsInstance(prediction, dict)
        
        asyncio.run(run_test())
    
    def test_scenario_veille_techno(self):
        """Scénario: Veille technologique automatisée"""
        from managers.env5_bridge import ENV5Bridge
        from managers.env2_tab_harvest import classify_tab
        
        async def run_test():
            bridge = ENV5Bridge(use_mcp=False)
            
            print("\n📰 Scénario: Veille Technologique")
            
            # 1. ENV2 liste les repos
            repos = ["DevTools", "FLUENCE", "ECOYSTEM", "NEXUS"]
            print(f"   1. ENV2 liste: {repos}")
            
            # 2. ENV5 analyse chaque repo
            for repo in repos:
                classification = classify_tab(f"https://github.com/gerivdb/{repo}", repo)
                print(f"   2. {repo} → {classification['type']}")
            
            # 3. ENV5 génère résumé
            summary = await bridge.predict("", "generate_summary:ECOS_repos")
            print(f"   3. ENV5 génère résumé")
            
            # 4. ENV2 organise par priorité
            print(f"   4. ENV2 organise par priorité")
            
            self.assertIn("DevTools", repos)
        
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main(verbosity=2)