#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests pour CDP Capabilities — Détection automatique des capacités CDP

Repo: gerivdb/NEXUS
Layer: ENV2 (Browser Automation + Internet)
Statut: CONFORME_NEXUS
OPS: OPS3_BREAKTHROUGH
"""

import json
import socket
import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import sys

# Add managers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "managers"))

from managers.cdp_capabilities import (
    BrowserType,
    CDPMode,
    CDPMethodNotSupported,
    CDPCapabilities,
    CDPCapabilityDetector,
    detect_cdp_capabilities,
)


class TestBrowserType(unittest.TestCase):
    """Tests pour BrowserType enum"""
    
    def test_browser_types(self):
        """Teste les types de navigateurs"""
        self.assertEqual(BrowserType.CHROME.value, "chrome")
        self.assertEqual(BrowserType.CHROMIUM.value, "chromium")
        self.assertEqual(BrowserType.EDGE.value, "edge")
        self.assertEqual(BrowserType.BRAVE.value, "brave")
        self.assertEqual(BrowserType.COMET.value, "comet")
        self.assertEqual(BrowserType.UNKNOWN.value, "unknown")


class TestCDPMode(unittest.TestCase):
    """Tests pour CDPMode enum"""
    
    def test_cdp_modes(self):
        """Teste les modes CDP"""
        self.assertEqual(CDPMode.FULL.value, "full")
        self.assertEqual(CDPMode.PARTIAL.value, "partial")
        self.assertEqual(CDPMode.NONE.value, "none")


class TestCDPMethodNotSupported(unittest.TestCase):
    """Tests pour l'exception CDPMethodNotSupported"""
    
    def test_exception_creation(self):
        """Teste la création de l'exception"""
        exc = CDPMethodNotSupported(
            method="Target.createTarget",
            browser_type=BrowserType.COMET,
            details="HTTP 405"
        )
        
        self.assertEqual(exc.method, "Target.createTarget")
        self.assertEqual(exc.browser_type, BrowserType.COMET)
        self.assertEqual(exc.details, "HTTP 405")
        self.assertIn("Target.createTarget", str(exc))
        self.assertIn("comet", str(exc))
    
    def test_exception_inheritance(self):
        """Teste que l'exception hérite de Exception"""
        exc = CDPMethodNotSupported("test", BrowserType.COMET)
        self.assertIsInstance(exc, Exception)


class TestCDPCapabilities(unittest.TestCase):
    """Tests pour CDPCapabilities dataclass"""
    
    def test_default_values(self):
        """Teste les valeurs par défaut"""
        caps = CDPCapabilities()
        
        self.assertEqual(caps.browser_type, BrowserType.UNKNOWN)
        self.assertEqual(caps.cdp_mode, CDPMode.NONE)
        self.assertFalse(caps.target_create)
        self.assertFalse(caps.target_close)
        self.assertTrue(caps.target_attach)  # Toujours supporté
        self.assertTrue(caps.page_navigate)  # Supporté sur tabs existants
        self.assertTrue(caps.page_reload)
        self.assertTrue(caps.runtime_evaluate)
        self.assertTrue(caps.dom_inspect)
        self.assertFalse(caps.network_intercept)
        self.assertEqual(caps.error_message, "")
    
    def test_to_dict(self):
        """Teste la conversion en dictionnaire"""
        caps = CDPCapabilities(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL,
            target_create=False,
        )
        
        d = caps.to_dict()
        
        self.assertEqual(d["browser_type"], "comet")
        self.assertEqual(d["cdp_mode"], "partial")
        self.assertFalse(d["capabilities"]["target_create"])
        self.assertTrue(d["capabilities"]["target_attach"])
    
    def test_to_dict_includes_all(self):
        """Teste que to_dict inclut toutes les capacités"""
        caps = CDPCapabilities()
        d = caps.to_dict()
        
        expected_keys = [
            "target_create", "target_close", "target_attach",
            "page_navigate", "page_reload", "runtime_evaluate",
            "dom_inspect", "network_intercept"
        ]
        
        for key in expected_keys:
            self.assertIn(key, d["capabilities"])


class TestCDPCapabilityDetector(unittest.TestCase):
    """Tests pour CDPCapabilityDetector"""
    
    def test_init(self):
        """Teste l'initialisation"""
        detector = CDPCapabilityDetector(host="127.0.0.1", port=9223)
        
        self.assertEqual(detector.host, "127.0.0.1")
        self.assertEqual(detector.port, 9223)
    
    @patch('socket.socket')
    def test_check_port_open_success(self, mock_socket):
        """Teste la détection de port ouvert"""
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock
        
        detector = CDPCapabilityDetector()
        result = detector.check_port_open()
        
        self.assertTrue(result)
        mock_sock.close.assert_called_once()
    
    @patch('socket.socket')
    def test_check_port_open_closed(self, mock_socket):
        """Teste la détection de port fermé"""
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 1  # Connection refused
        mock_socket.return_value = mock_sock
        
        detector = CDPCapabilityDetector()
        result = detector.check_port_open()
        
        self.assertFalse(result)
    
    @patch('socket.socket')
    def test_check_port_open_timeout(self, mock_socket):
        """Teste la gestion du timeout"""
        mock_sock = MagicMock()
        mock_sock.connect_ex.side_effect = socket.timeout()
        mock_socket.return_value = mock_sock
        
        detector = CDPCapabilityDetector()
        result = detector.check_port_open()
        
        self.assertFalse(result)
    
    def test_detect_browser_type_chrome(self):
        """Teste la détection de Chrome"""
        detector = CDPCapabilityDetector()
        
        version_info = {"Browser": "Chrome/120.0.0.0"}
        result = detector.detect_browser_type(version_info)
        
        self.assertEqual(result, BrowserType.CHROME)
    
    def test_detect_browser_type_comet(self):
        """Teste la détection de Comet"""
        detector = CDPCapabilityDetector()
        
        version_info = {"Browser": "Comet/1.0.0"}
        result = detector.detect_browser_type(version_info)
        
        self.assertEqual(result, BrowserType.COMET)
    
    def test_detect_browser_type_edge(self):
        """Teste la détection de Edge"""
        detector = CDPCapabilityDetector()
        
        version_info = {"Browser": "Edge/120.0.0.0"}
        result = detector.detect_browser_type(version_info)
        
        self.assertEqual(result, BrowserType.EDGE)
    
    def test_detect_browser_type_unknown(self):
        """Teste la détection d'un browser inconnu"""
        detector = CDPCapabilityDetector()
        
        version_info = {"Browser": "Firefox/120.0"}
        result = detector.detect_browser_type(version_info)
        
        self.assertEqual(result, BrowserType.UNKNOWN)
    
    @patch('urllib.request.urlopen')
    def test_test_create_target_supported(self, mock_urlopen):
        """Teste la détection de Target.createTarget supporté"""
        # Créer un mock de réponse qui retourne un JSON valide
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"targetId": "abc123", "type": "page"}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        detector = CDPCapabilityDetector()
        result = detector.test_create_target()
        
        self.assertTrue(result)
    
    @patch('urllib.request.urlopen')
    def test_test_create_target_http_405(self, mock_urlopen):
        """Teste la détection de Target.createTarget non supporté (HTTP 405)"""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "url", 405, "Method Not Allowed", {}, None
        )
        
        detector = CDPCapabilityDetector()
        result = detector.test_create_target()
        
        self.assertFalse(result)
    
    @patch('urllib.request.urlopen')
    def test_test_create_target_http_404(self, mock_urlopen):
        """Teste la détection de Target.createTarget non supporté (HTTP 404)"""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "url", 404, "Not Found", {}, None
        )
        
        detector = CDPCapabilityDetector()
        result = detector.test_create_target()
        
        self.assertFalse(result)


class TestDetectCDPCapabilities(unittest.TestCase):
    """Tests pour la fonction utilitaire detect_cdp_capabilities"""
    
    @patch('managers.cdp_capabilities.CDPCapabilityDetector')
    def test_detect_cdp_capabilities(self, mock_detector_class):
        """Teste la fonction utilitaire"""
        mock_detector = MagicMock()
        mock_detector_class.return_value = mock_detector
        
        expected_caps = CDPCapabilities(
            browser_type=BrowserType.COMET,
            cdp_mode=CDPMode.PARTIAL,
        )
        mock_detector.detect_capabilities.return_value = expected_caps
        
        result = detect_cdp_capabilities("localhost", 9222)
        
        self.assertEqual(result, expected_caps)
        mock_detector_class.assert_called_once_with("localhost", 9222)


if __name__ == "__main__":
    unittest.main(verbosity=2)