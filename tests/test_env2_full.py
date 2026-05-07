#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENV2 Browser Middleware — Full Integration Tests (E2E)

Tests unitaires + integration pour toutes les phases (1-9)
Executable sans HITL — utilise mocks pour CDP

Repo: gerivdb/NEXUS
Date: 2026-04-08
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Add managers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "managers"))


class TestPhase1_TabHarvest(unittest.TestCase):
    """Tests Phase 1: TabHarvest + Classification NEXUS"""
    
    def test_classification_ecosystem(self):
        from env2_tab_harvest import classify_tab
        result = classify_tab("https://github.com/gerivdb/DevTools", "DevTools documentation")
        self.assertEqual(result["type"], "ECOSYSTEM")
    
    def test_classification_perso(self):
        from env2_tab_harvest import classify_tab
        result = classify_tab("https://example.com", "whatsapp message")
        self.assertEqual(result["type"], "PERSO")
    
    def test_classification_doc_externe(self):
        from env2_tab_harvest import classify_tab
        result = classify_tab("https://docs.github.com/api", "API documentation")
        self.assertEqual(result["type"], "DOC_EXTERNE")
    
    def test_intent_create(self):
        from env2_tab_harvest import extract_intent
        intent = extract_intent("I want to create a new feature")
        self.assertTrue(intent.startswith("CREATE"))
    
    def test_intent_howto(self):
        from env2_tab_harvest import extract_intent
        intent = extract_intent("how to setup Python")
        self.assertTrue(intent.startswith("HOWTO"))
    
    def test_intent_debug(self):
        from env2_tab_harvest import extract_intent
        intent = extract_intent("fix the bug in module")
        self.assertTrue(intent.startswith("DEBUG"))
    
    def test_find_repos(self):
        from env2_tab_harvest import find_gerivdb_repos
        repos = find_gerivdb_repos("DevTools and ECOYSTEM integration")
        self.assertIn("DevTools", repos)
        self.assertIn("ECOYSTEM", repos)


class TestPhase2_CDPClient(unittest.TestCase):
    """Tests Phase 2: CDP Client (mocked)"""
    
    @patch("managers.cdp_client.urllib.request.urlopen")
    def test_cdp_is_available(self, mock_urlopen):
        from managers.cdp_client import CDPClient
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([{"id": "1", "title": "Test"}]).encode()
        mock_urlopen.return_value = mock_response
        
        client = CDPClient()
        self.assertTrue(client.is_available())
    
    @patch("managers.cdp_client.urllib.request.urlopen")
    def test_cdp_list_targets(self, mock_urlopen):
        from managers.cdp_client import CDPClient
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([
            {"id": "1", "title": "Tab 1", "url": "https://example.com", "type": "page"}
        ]).encode()
        mock_urlopen.return_value = mock_response
        
        client = CDPClient()
        targets = client.list_targets()
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0].title, "Tab 1")


class TestPhase6_CometLauncher(unittest.TestCase):
    """Tests Phase 6: Comet Launcher (mocked)"""
    
    @patch("managers.comet_launcher.check_cdp_available")
    def test_launcher_cdp_already_available(self, mock_check):
        from managers.comet_launcher import ensure_cdp, LauncherResult
        mock_check.return_value = {"Browser": "Comet/120.0"}
        
        result = ensure_cdp(port=9222)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.status, "ok")
        self.assertFalse(result.launched)
    
    @patch("managers.comet_launcher.find_exe")
    @patch("managers.comet_launcher.check_cdp_available")
    def test_launcher_exe_not_found(self, mock_check, mock_find):
        from managers.comet_launcher import ensure_cdp
        mock_check.return_value = None
        mock_find.return_value = None
        
        result = ensure_cdp(port=9222, browser="comet")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.status, "error")


class TestPhase7_TabGroups(unittest.TestCase):
    """Tests Phase 7: Tab Groups"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def test_create_group(self):
        from managers.tab_groups import TabGroupManager
        manager = TabGroupManager(self.test_dir)
        group = manager.create_group("Test Group", {"repo": "DevTools"})
        
        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.context["repo"], "DevTools")
    
    def test_list_groups(self):
        from managers.tab_groups import TabGroupManager
        manager = TabGroupManager(self.test_dir)
        manager.create_group("Group 1")
        manager.create_group("Group 2")
        
        groups = manager.list_groups()
        self.assertEqual(len(groups), 2)
    
    def test_add_tab_to_group(self):
        from managers.tab_groups import TabGroupManager
        manager = TabGroupManager(self.test_dir)
        group = manager.create_group("Test")
        
        result = manager.add_tab_to_group(group.id, "https://github.com", "GitHub")
        self.assertTrue(result)
        
        updated_group = manager.get_group(group.id)
        self.assertEqual(len(updated_group.tabs), 1)
    
    def test_export_group_json(self):
        from managers.tab_groups import TabGroupManager
        manager = TabGroupManager(self.test_dir)
        group = manager.create_group("Export Test")
        manager.add_tab_to_group(group.id, "https://example.com", "Example")
        
        output = manager.export_group(group.id, "json")
        data = json.loads(output)
        self.assertEqual(data["name"], "Export Test")
        self.assertEqual(len(data["tabs"]), 1)


class TestPhase8_AutoHeal(unittest.TestCase):
    """Tests Phase 8: Auto-Healing"""
    
    @patch("managers.auto_heal.BrowserHealthChecker.check_cdp")
    def test_health_healthy(self, mock_check):
        from managers.auto_heal import BrowserHealthChecker, HealthStatus
        mock_check.return_value = True
        
        checker = BrowserHealthChecker()
        report = checker.check()
        
        self.assertEqual(report.status, HealthStatus.HEALTHY)
    
    @patch("managers.auto_heal.BrowserHealthChecker.check_cdp")
    def test_health_unhealthy(self, mock_check):
        from managers.auto_heal import BrowserHealthChecker, HealthStatus
        mock_check.return_value = False
        
        checker = BrowserHealthChecker()
        report = checker.check()
        
        self.assertEqual(report.status, HealthStatus.UNHEALTHY)


class TestPhase9_WorkflowEngine(unittest.TestCase):
    """Tests Phase 9: Workflow Engine"""
    
    def test_workflow_definition(self):
        from managers.workflow_engine import WorkflowDefinition, WorkflowStep, WorkflowStatus
        
        step = WorkflowStep(name="Open Tab", action="open", params={"url": "https://example.com"})
        workflow = WorkflowDefinition(name="Test Workflow", steps=[step])
        
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(len(workflow.steps), 1)
    
    def test_workflow_executor_mock(self):
        from managers.workflow_engine import WorkflowExecutor, WorkflowDefinition, WorkflowStep, WorkflowStatus
        
        # Mock CDP client
        mock_cdp = MagicMock()
        mock_cdp.create_target.return_value = "target_123"
        
        executor = WorkflowExecutor(mock_cdp)
        workflow = WorkflowDefinition(
            name="Test",
            steps=[
                WorkflowStep(name="Open", action="open", params={"url": "https://example.com"})
            ]
        )
        
        result = executor.execute(workflow, dry_run=True)
        
        self.assertEqual(result.status, WorkflowStatus.COMPLETED)
        self.assertEqual(result.steps_completed, 1)


class TestIntegration_FullFlow(unittest.TestCase):
    """Tests d'integration: Full flow from launcher to workflow"""
    
    @patch("managers.comet_launcher.check_cdp_available")
    @patch("managers.cdp_client.urllib.request.urlopen")
    def test_full_flow_mocked(self, mock_urlopen, mock_check):
        """Teste le flux complet avec mocks"""
        # Simuler CDP disponible
        mock_check.return_value = {"Browser": "Comet/120.0"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([
            {"id": "1", "title": "Test Tab", "url": "https://github.com/gerivdb/DevTools", "type": "page"}
        ]).encode()
        mock_urlopen.return_value = mock_response
        
        # Phase 2: CDP Client
        from managers.cdp_client import CDPClient
        client = CDPClient()
        self.assertTrue(client.is_available())
        
        targets = client.list_targets()
        self.assertEqual(len(targets), 1)
        
        # Phase 1: Classification
        from env2_tab_harvest import classify_tab
        result = classify_tab(targets[0].url, targets[0].title)
        self.assertEqual(result["type"], "ECOSYSTEM")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)