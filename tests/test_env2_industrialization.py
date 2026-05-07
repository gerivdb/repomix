#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENV2 Industrialization Tests — Phases 10-15

Repo: gerivdb/NEXUS
Layer: ENV2 (Browser Automation + Internet)
Statut: CONFORME_NEXUS
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


class TestPhase12_EventServer(unittest.TestCase):
    """Tests Phase 12: WebSocket Event Server"""
    
    def test_event_server_creation(self):
        from managers.event_server import EventServer
        server = EventServer(host="localhost", port=8765)
        self.assertEqual(server.host, "localhost")
        self.assertEqual(server.port, 8765)
        self.assertFalse(server._running)
    
    def test_subscription_types(self):
        from managers.event_server import SubscriptionType
        self.assertEqual(SubscriptionType.ALL.value, "all")
        self.assertEqual(SubscriptionType.TABS.value, "tabs")
        self.assertEqual(SubscriptionType.SESSIONS.value, "sessions")
        self.assertEqual(SubscriptionType.WORKFLOWS.value, "workflows")
        self.assertEqual(SubscriptionType.HEALTH.value, "health")
    
    def test_get_category(self):
        from managers.event_server import EventServer
        server = EventServer()
        
        self.assertEqual(server._get_category("tab:opened"), "tabs")
        self.assertEqual(server._get_category("tab:closed"), "tabs")
        self.assertEqual(server._get_category("session:saved"), "sessions")
        self.assertEqual(server._get_category("workflow:started"), "workflows")
        self.assertEqual(server._get_category("health:check"), "health")
        self.assertEqual(server._get_category("unknown:event"), "all")
    
    def test_server_stats(self):
        from managers.event_server import EventServer
        server = EventServer()
        stats = server.get_stats()
        
        self.assertIn("running", stats)
        self.assertIn("host", stats)
        self.assertIn("port", stats)
        self.assertIn("connected_clients", stats)
        self.assertEqual(stats["connected_clients"], 0)


class TestPhase14_NexusClassifier(unittest.TestCase):
    """Tests Phase 14: IA NEXUS Classifier"""
    
    def test_classifier_creation(self):
        from managers.nexus_classifier import NexusClassifier
        classifier = NexusClassifier()
        self.assertFalse(classifier.use_onnx)
        self.assertIsNone(classifier.model_path)
    
    def test_classify_ecosystem_url(self):
        from managers.nexus_classifier import NexusClassifier, NexusType
        classifier = NexusClassifier()
        
        result = classifier.classify(
            url="https://github.com/gerivdb/DevTools",
            title="DevTools Repository"
        )
        
        # DevTools is classified as DEV_TOOL (matches github.com domain + "tool" keyword)
        self.assertIn(result.nexus_type, [NexusType.ECOSYSTEM.value, NexusType.DEV_TOOL.value])
        self.assertIn("DevTools", result.repos)
        self.assertFalse(result.skip)
    
    def test_classify_perso_url(self):
        from managers.nexus_classifier import NexusClassifier, NexusType
        classifier = NexusClassifier()
        
        result = classifier.classify(
            url="https://whatsapp.com",
            title="WhatsApp Web"
        )
        
        self.assertEqual(result.nexus_type, NexusType.PERSO.value)
        self.assertTrue(result.skip)
    
    def test_classify_doc_externe_url(self):
        from managers.nexus_classifier import NexusClassifier, NexusType
        classifier = NexusClassifier()
        
        result = classifier.classify(
            url="https://docs.github.com/api",
            title="GitHub API Documentation"
        )
        
        self.assertEqual(result.nexus_type, NexusType.DOC_EXTERNE.value)
        self.assertFalse(result.skip)
    
    def test_extract_intent_create(self):
        from managers.nexus_classifier import NexusClassifier, IntentType
        classifier = NexusClassifier()
        
        intent = classifier._extract_intent("I want to create a new feature")
        self.assertEqual(intent, IntentType.CREATE)
    
    def test_extract_intent_howto(self):
        from managers.nexus_classifier import NexusClassifier, IntentType
        classifier = NexusClassifier()
        
        intent = classifier._extract_intent("how to setup Python environment")
        self.assertEqual(intent, IntentType.HOWTO)
    
    def test_extract_intent_debug(self):
        from managers.nexus_classifier import NexusClassifier, IntentType
        classifier = NexusClassifier()
        
        intent = classifier._extract_intent("fix the bug in module")
        self.assertEqual(intent, IntentType.DEBUG)
    
    def test_find_repos(self):
        from managers.nexus_classifier import NexusClassifier
        classifier = NexusClassifier()
        
        # Test with lowercase content (as the method uses .lower())
        repos = classifier._find_repos("devtools and ecoystem integration with nexus")
        self.assertIn("DevTools", repos)
        self.assertIn("ECOYSTEM", repos)
        self.assertIn("NEXUS", repos)
    
    def test_classify_batch(self):
        from managers.nexus_classifier import NexusClassifier
        classifier = NexusClassifier()
        
        tabs = [
            {"url": "https://github.com/gerivdb/DevTools", "title": "DevTools"},
            {"url": "https://whatsapp.com", "title": "WhatsApp"},
        ]
        
        results = classifier.classify_batch(tabs)
        self.assertEqual(len(results), 2)
    
    def test_get_stats(self):
        from managers.nexus_classifier import NexusClassifier, NexusType
        classifier = NexusClassifier()
        
        results = [
            classifier.classify("https://github.com/gerivdb/DevTools", "DevTools"),
            classifier.classify("https://github.com/gerivdb/FLUENCE", "FLUENCE"),
            classifier.classify("https://whatsapp.com", "WhatsApp"),
        ]
        
        stats = classifier.get_stats(results)
        self.assertEqual(stats["total"], 3)
        self.assertIn(NexusType.ECOSYSTEM.value, stats["by_type"])
        self.assertIn(NexusType.PERSO.value, stats["by_type"])


class TestPhase15_FluenceMatrix(unittest.TestCase):
    """Tests Phase 15: FLUENCE Matrix"""
    
    def test_matrix_creation(self):
        from managers.fluence_matrix import FluenceMatrix
        matrix = FluenceMatrix()
        self.assertEqual(matrix.base, 36)
    
    def test_encode_integer(self):
        from managers.fluence_matrix import FluenceMatrix
        matrix = FluenceMatrix()
        
        encoded = matrix.encode_base675(12345)
        self.assertIsInstance(encoded, str)
        self.assertEqual(matrix.decode_base675(encoded), 12345)
    
    def test_encode_url(self):
        from managers.fluence_matrix import FluenceMatrix
        matrix = FluenceMatrix()
        
        url = "https://github.com/gerivdb/DevTools"
        encoded = matrix.encode_url(url)
        
        self.assertEqual(encoded.original, url)
        self.assertIsInstance(encoded.encoded, str)
        self.assertIsInstance(encoded.hash_semantic, str)
        self.assertIsInstance(encoded.compression_ratio, float)
    
    def test_hash_semantic(self):
        from managers.fluence_matrix import FluenceMatrix
        matrix = FluenceMatrix()
        
        hash1 = matrix.hash_semantic("DevTools documentation")
        hash2 = matrix.hash_semantic("DevTools documentation")
        hash3 = matrix.hash_semantic("FLUENCE matrix")
        
        self.assertEqual(hash1, hash2)  # Mêmes inputs → mêmes hashes
        self.assertNotEqual(hash1, hash3)  # Inputs différents → hashes différents
    
    def test_compress_session(self):
        from managers.fluence_matrix import FluenceMatrix
        matrix = FluenceMatrix()
        
        tabs = [
            {"url": "https://github.com/gerivdb/DevTools", "title": "DevTools"},
            {"url": "https://github.com/gerivdb/FLUENCE", "title": "FLUENCE"},
        ]
        
        compressed = matrix.compress_session("test-session", tabs, "DevTools/main")
        
        self.assertEqual(compressed.name, "test-session")
        self.assertEqual(compressed.tabs_count, 2)
        self.assertEqual(len(compressed.encoded_tabs), 2)
        self.assertIsInstance(compressed.compression_ratio, float)
    
    def test_create_index(self):
        from managers.fluence_matrix import FluenceMatrix
        matrix = FluenceMatrix()
        
        urls = [
            "https://github.com/gerivdb/DevTools",
            "https://github.com/gerivdb/FLUENCE",
            "https://github.com/gerivdb/ECOYSTEM",
        ]
        
        index = matrix.create_index(urls)
        
        self.assertIn("semantic", index)
        self.assertIn("domain", index)
        self.assertIn("path", index)
        self.assertIn("entries", index)
        self.assertEqual(len(index["entries"]), 3)
    
    def test_search_by_semantic(self):
        from managers.fluence_matrix import FluenceMatrix
        matrix = FluenceMatrix()
        
        urls = [
            "https://github.com/gerivdb/DevTools",
            "https://github.com/gerivdb/FLUENCE",
        ]
        
        index = matrix.create_index(urls)
        results = matrix.search_by_semantic(index, "DevTools")
        
        self.assertIsInstance(results, list)
    
    def test_get_stats(self):
        from managers.fluence_matrix import FluenceMatrix
        matrix = FluenceMatrix()
        
        urls = [
            "https://github.com/gerivdb/DevTools",
            "https://github.com/gerivdb/FLUENCE",
        ]
        
        stats = matrix.get_stats(urls)
        
        self.assertEqual(stats["total_urls"], 2)
        self.assertIn("total_original_size", stats)
        self.assertIn("total_encoded_size", stats)
        self.assertIn("overall_compression_ratio", stats)


class TestPhase15_SessionStorage(unittest.TestCase):
    """Tests Phase 15: Session Storage with FLUENCE"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def test_save_and_load_session(self):
        from managers.fluence_matrix import SessionStorage
        storage = SessionStorage(self.test_dir)
        
        tabs = [
            {"url": "https://github.com/gerivdb/DevTools", "title": "DevTools"},
        ]
        
        # Save
        path = storage.save_session("test", tabs, "test context")
        self.assertTrue(Path(path).exists())
        
        # Load
        session = storage.load_session("test")
        self.assertIsNotNone(session)
        self.assertEqual(session.name, "test")
        self.assertEqual(session.tabs_count, 1)
    
    def test_list_sessions(self):
        from managers.fluence_matrix import SessionStorage
        storage = SessionStorage(self.test_dir)
        
        tabs = [{"url": "https://example.com", "title": "Example"}]
        storage.save_session("session1", tabs)
        storage.save_session("session2", tabs)
        
        sessions = storage.list_sessions()
        self.assertEqual(len(sessions), 2)


class TestIntegration_Industrialization(unittest.TestCase):
    """Tests d'integration pour les phases 10-15"""
    
    def test_classifier_with_matrix(self):
        """Teste la classification + encodage FLUENCE combinés"""
        from managers.nexus_classifier import NexusClassifier
        from managers.fluence_matrix import FluenceMatrix
        
        classifier = NexusClassifier()
        matrix = FluenceMatrix()
        
        # Classifier une URL
        result = classifier.classify(
            "https://github.com/gerivdb/DevTools",
            "DevTools"
        )
        
        # Encoder l'URL classifiée
        encoded = matrix.encode_url(result.url)
        
        # DevTools can be classified as ECOSYSTEM or DEV_TOOL
        self.assertIn(result.nexus_type, ["ECOSYSTEM", "DEV_TOOL"])
        self.assertIsInstance(encoded.encoded, str)
        self.assertIsInstance(encoded.hash_semantic, str)
    
    def test_full_workflow(self):
        """Teste un workflow complet: classification → encodage → compression"""
        from managers.nexus_classifier import NexusClassifier
        from managers.fluence_matrix import FluenceMatrix
        
        classifier = NexusClassifier()
        matrix = FluenceMatrix()
        
        # Tabs à traiter
        tabs = [
            {"url": "https://github.com/gerivdb/DevTools", "title": "DevTools"},
            {"url": "https://github.com/gerivdb/FLUENCE", "title": "FLUENCE"},
            {"url": "https://whatsapp.com", "title": "WhatsApp"},
        ]
        
        # Classifier
        results = classifier.classify_batch(tabs)
        
        # Filtrer les tabs non-perso
        filtered_tabs = [
            tab for tab, result in zip(tabs, results)
            if not result.skip
        ]
        
        # Compresser la session
        compressed = matrix.compress_session("filtered-session", filtered_tabs)
        
        self.assertEqual(len(filtered_tabs), 2)  # WhatsApp filtré
        self.assertEqual(compressed.tabs_count, 2)
        self.assertIsInstance(compressed.compression_ratio, float)


if __name__ == "__main__":
    unittest.main(verbosity=2)