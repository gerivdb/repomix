#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests E2E pour Comet Degraded Mode — Pipeline V6 avec Comet CDP partiel

Repo: gerivdb/NEXUS
Layer: ENV2 (Browser Automation + Internet)
Statut: CONFORME_NEXUS
OPS: OPS3_BREAKTHROUGH
"""

import asyncio
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add managers to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.cdp_capabilities import BrowserType, CDPMode, CDPCapabilities
from managers.pipeline_v6_executor import PipelineV6Executor, PaperResult


class MockCDPCapabilities:
    """Mock pour CDPCapabilities"""
    def __init__(self, browser_type=BrowserType.COMET, cdp_mode=CDPMode.PARTIAL):
        self.browser_type = browser_type
        self.cdp_mode = cdp_mode
        self.target_create = (cdp_mode == CDPMode.FULL)
        self.target_close = (cdp_mode == CDPMode.FULL)
        self.target_attach = True
        self.page_navigate = True
        self.page_reload = True
        self.runtime_evaluate = True
        self.dom_inspect = True
        self.network_intercept = (cdp_mode == CDPMode.FULL)


class MockCDPClient:
    """Mock pour CDPClient avec support mode dégradé"""
    def __init__(self, browser_type=BrowserType.COMET, cdp_mode=CDPMode.PARTIAL):
        self.browser_type = browser_type
        self.cdp_mode = cdp_mode
        self.tabs = [
            MagicMock(id="tab1", title="Existing Tab", url="https://example.com"),
        ]
        self.create_target_called = False
        self.navigate_called = False
    
    def create_target(self, url):
        """Simule Target.createTarget"""
        self.create_target_called = True
        if self.cdp_mode == CDPMode.PARTIAL:
            # Comet: retourne None ou lève une exception
            return None
        else:
            # Chrome: retourne un targetId
            return "new_target_123"
    
    def list_targets(self):
        """Retourne la liste des tabs"""
        return self.tabs
    
    def navigate(self, target_id, url):
        """Navigue vers une URL"""
        self.navigate_called = True
        # Met à jour le tab
        for tab in self.tabs:
            if tab.id == target_id:
                tab.url = url
                tab.title = f"Navigated to {url}"
                break


class TestCometDegradedMode(unittest.TestCase):
    """Tests pour le mode dégradé Comet"""
    
    @patch('managers.pipeline_v6_executor.detect_cdp_capabilities')
    @patch('managers.pipeline_v6_executor.CDPClient')
    def test_degraded_mode_detection(self, mock_cdp_client, mock_detect):
        """Teste que le mode dégradé est détecté correctement"""
        # Configurer les mocks
        mock_detect.return_value = MockCDPCapabilities(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL
        )
        mock_cdp_client.return_value = MockCDPClient(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL
        )
        
        # Créer l'executor
        executor = PipelineV6Executor()
        
        # Vérifier détection
        self.assertEqual(executor.browser_type, BrowserType.COMET)
        self.assertEqual(executor.cdp_mode, CDPMode.PARTIAL)
    
    @patch('managers.pipeline_v6_executor.detect_cdp_capabilities')
    @patch('managers.pipeline_v6_executor.CDPClient')
    def test_normal_mode_detection(self, mock_cdp_client, mock_detect):
        """Teste que le mode normal est détecté correctement"""
        # Configurer les mocks
        mock_detect.return_value = MockCDPCapabilities(
            browser_type=BrowserType.CHROME,
            cdp_mode=CDPMode.FULL
        )
        mock_cdp_client.return_value = MockCDPClient(
            browser_type=BrowserType.CHROME,
            cdp_mode=CDPMode.FULL
        )
        
        # Créer l'executor
        executor = PipelineV6Executor()
        
        # Vérifier détection
        self.assertEqual(executor.browser_type, BrowserType.CHROME)
        self.assertEqual(executor.cdp_mode, CDPMode.FULL)
    
    @patch('managers.pipeline_v6_executor.detect_cdp_capabilities')
    @patch('managers.pipeline_v6_executor.CDPClient')
    async def test_open_arxiv_paper_degraded_with_tabs(self, mock_cdp_client, mock_detect):
        """Teste ouverture papier en mode dégradé avec tabs existants"""
        # Configurer les mocks
        mock_detect.return_value = MockCDPCapabilities(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL
        )
        mock_cdp = MockCDPClient(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL
        )
        mock_cdp_client.return_value = mock_cdp
        
        executor = PipelineV6Executor()
        
        # Tester ouverture papier
        result = await executor.open_arxiv_paper("1706.03762")
        
        # Vérifications
        self.assertIsNotNone(result)
        self.assertEqual(result.arxiv_id, "1706.03762")
        self.assertEqual(result.url, "https://arxiv.org/abs/1706.03762")
        self.assertIsNotNone(result.target_id)
        
        # create_target ne doit PAS être appelé en mode dégradé
        self.assertFalse(mock_cdp.create_target_called)
        
        # navigate doit être appelé
        self.assertTrue(mock_cdp.navigate_called)
    
    @patch('managers.pipeline_v6_executor.detect_cdp_capabilities')
    @patch('managers.pipeline_v6_executor.CDPClient')
    async def test_open_arxiv_paper_degraded_no_tabs(self, mock_cdp_client, mock_detect):
        """Teste ouverture papier en mode dégradé sans tabs existants"""
        # Configurer les mocks
        mock_detect.return_value = MockCDPCapabilities(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL
        )
        mock_cdp = MockCDPClient(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL
        )
        mock_cdp.tabs = []  # Pas de tabs
        mock_cdp_client.return_value = mock_cdp
        
        executor = PipelineV6Executor()
        
        # Tester ouverture papier
        result = await executor.open_arxiv_paper("1706.03762")
        
        # Vérifications
        self.assertIsNone(result)  # Doit retourner None
    
    @patch('managers.pipeline_v6_executor.detect_cdp_capabilities')
    @patch('managers.pipeline_v6_executor.CDPClient')
    async def test_open_arxiv_paper_normal_mode(self, mock_cdp_client, mock_detect):
        """Teste ouverture papier en mode normal (Chrome)"""
        # Configurer les mocks
        mock_detect.return_value = MockCDPCapabilities(
            browser_type=BrowserType.CHROME,
            cdp_mode=CDPMode.FULL
        )
        mock_cdp = MockCDPClient(
            browser_type=BrowserType.CHROME,
            cdp_mode=CDPMode.FULL
        )
        mock_cdp.tabs = [
            MagicMock(id="new_target_123", title="arXiv Paper", url="https://arxiv.org/abs/1706.03762"),
        ]
        mock_cdp_client.return_value = mock_cdp
        
        executor = PipelineV6Executor()
        
        # Tester ouverture papier
        result = await executor.open_arxiv_paper("1706.03762")
        
        # Vérifications
        self.assertIsNotNone(result)
        self.assertEqual(result.arxiv_id, "1706.03762")
        
        # create_target doit être appelé en mode normal
        self.assertTrue(mock_cdp.create_target_called)
    
    @patch('managers.pipeline_v6_executor.detect_cdp_capabilities')
    @patch('managers.pipeline_v6_executor.CDPClient')
    async def test_fallback_to_degraded_on_exception(self, mock_cdp_client, mock_detect):
        """Teste fallback vers mode dégradé si create_target échoue"""
        # Configurer pour simuler un browser full qui échoue sur create_target
        mock_detect.return_value = MockCDPCapabilities(
            browser_type=BrowserType.CHROME,
            cdp_mode=CDPMode.FULL
        )
        mock_cdp = MockCDPClient(
            browser_type=BrowserType.CHROME,
            cdp_mode=CDPMode.FULL
        )
        mock_cdp.create_target = MagicMock(return_value=None)  # Échec
        mock_cdp.tabs = [
            MagicMock(id="tab1", title="Existing Tab", url="https://example.com"),
        ]
        mock_cdp_client.return_value = mock_cdp
        
        executor = PipelineV6Executor()
        
        # Tester ouverture papier
        result = await executor.open_arxiv_paper("1706.03762")
        
        # Vérifications: doit fallback vers degraded mode
        self.assertIsNotNone(result)
        self.assertTrue(mock_cdp.navigate_called)  # navigate appelé en degraded mode


class TestCometDegradedModeE2E(unittest.TestCase):
    """Tests E2E complets pour Comet degraded mode"""
    
    @patch('managers.pipeline_v6_executor.detect_cdp_capabilities')
    @patch('managers.pipeline_v6_executor.CDPClient')
    async def test_full_workflow_comet_degraded(self, mock_cdp_client, mock_detect):
        """Test complet du workflow ENV2 avec Comet en mode dégradé"""
        # 1. Configurer Comet avec CDP partial
        mock_detect.return_value = MockCDPCapabilities(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL
        )
        mock_cdp = MockCDPClient(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL
        )
        mock_cdp.tabs = [
            MagicMock(id="tab1", title="Comet Tab", url="https://comet.perplexity.ai"),
        ]
        mock_cdp_client.return_value = mock_cdp
        
        # 2. Initialiser ENV2
        executor = PipelineV6Executor()
        
        # 3. Vérifier détection mode dégradé
        self.assertEqual(executor.browser_type, BrowserType.COMET)
        self.assertEqual(executor.cdp_mode, CDPMode.PARTIAL)
        
        # 4. Tester détection arXiv dans note
        note_content = "Voir arXiv:1706.03762 pour détails"
        papers = await executor.detect_arxiv_papers(note_content)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0], "1706.03762")
        
        # 5. Tester ouverture papier (mode dégradé)
        result = await executor.open_arxiv_paper("1706.03762")
        self.assertIsNotNone(result)
        self.assertEqual(result.arxiv_id, "1706.03762")
        
        # 6. Vérifier que create_target n'a pas été appelé
        self.assertFalse(mock_cdp.create_target_called)
        
        # 7. Vérifier que navigate a été appelé
        self.assertTrue(mock_cdp.navigate_called)


if __name__ == "__main__":
    unittest.main(verbosity=2)