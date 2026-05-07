#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline V6 Full E2E Tests — Tests complets pour Pipeline V6 + ENV2

Repo: gerivdb/NEXUS
Layer: ENV2 (Browser Automation + Internet)
Statut: CONFORME_NEXUS
OPS: OPS3_BREAKTHROUGH
"""

import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

# Add managers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "managers"))


class TestPipelineV6Executor(unittest.TestCase):
    """Tests pour Pipeline V6 Executor"""
    
    def test_executor_creation(self):
        """Teste la création de l'executor"""
        from managers.pipeline_v6_executor import PipelineV6Executor
        
        executor = PipelineV6Executor()
        self.assertIsNotNone(executor.cdp)
        self.assertIsNotNone(executor.env5)
    
    def test_detect_arxiv_papers(self):
        """Teste la détection de papiers arXiv"""
        from managers.pipeline_v6_executor import PipelineV6Executor
        import asyncio
        
        executor = PipelineV6Executor()
        
        content = """
        Cet article parle de l'architecture Transformer (Vaswani et al., 2017).
        Voir arXiv:1706.03762 pour plus de détails.
        Aussi intéressant: arXiv:2301.12345 sur les LLM.
        """
        
        papers = asyncio.run(executor.detect_arxiv_papers(content))
        self.assertEqual(len(papers), 2)
        self.assertIn("1706.03762", papers[0])
        self.assertIn("2301.12345", papers[1])
    
    def test_paper_result_dataclass(self):
        """Teste la structure PaperResult"""
        from managers.pipeline_v6_executor import PaperResult
        
        result = PaperResult(
            arxiv_id="2301.12345",
            url="https://arxiv.org/abs/2301.12345",
            title="Test Paper",
            target_id="tab-123",
            classification={"type": "ECOSYSTEM"},
            opened_at=datetime.now().isoformat()
        )
        
        self.assertEqual(result.arxiv_id, "2301.12345")
        self.assertEqual(result.title, "Test Paper")


class TestPipelineV6Events(unittest.TestCase):
    """Tests pour Pipeline V6 Events"""
    
    def test_events_creation(self):
        """Teste la création de l'émetteur d'events"""
        from managers.pipeline_v6_events import PipelineV6Events
        
        events = PipelineV6Events()
        self.assertIsNotNone(events.server)
        self.assertEqual(len(events._event_queue), 0)
    
    def test_emit_paper_detected(self):
        """Teste l'émission d'event paper_detected"""
        from managers.pipeline_v6_events import PipelineV6Events
        
        events = PipelineV6Events()
        events.emit_paper_detected("2301.12345", "note")
        
        self.assertEqual(len(events._event_queue), 1)
        event = events._event_queue[0]
        self.assertEqual(event["type"], "pipeline:paper:detected")
        self.assertEqual(event["data"]["arxiv_id"], "2301.12345")
    
    def test_emit_paper_opened(self):
        """Teste l'émission d'event paper_opened"""
        from managers.pipeline_v6_events import PipelineV6Events
        
        events = PipelineV6Events()
        events.emit_paper_opened("2301.12345", "Test Paper", "https://arxiv.org/abs/2301.12345")
        
        self.assertEqual(len(events._event_queue), 1)
        event = events._event_queue[0]
        self.assertEqual(event["type"], "pipeline:paper:opened")
        self.assertEqual(event["data"]["title"], "Test Paper")


class TestArxivClassifier(unittest.TestCase):
    """Tests pour arXiv Classifier"""
    
    def test_classifier_creation(self):
        """Teste la création du classifier"""
        from managers.arxiv_classifier import ArxivClassifier
        
        classifier = ArxivClassifier()
        self.assertIsNotNone(classifier.env5)
        self.assertEqual(len(classifier.ecosystem_repos), 8)
    
    def test_arxiv_categories(self):
        """Teste les catégories arXiv"""
        from managers.arxiv_classifier import ARXIV_CATEGORIES
        
        self.assertIn("cs.AI", ARXIV_CATEGORIES)
        self.assertIn("cs.LG", ARXIV_CATEGORIES)
        self.assertEqual(ARXIV_CATEGORIES["cs.AI"], "Artificial Intelligence")
    
    def test_arxiv_classification_dataclass(self):
        """Teste la structure ArxivClassification"""
        from managers.arxiv_classifier import ArxivClassification
        
        classification = ArxivClassification(
            arxiv_id="2301.12345",
            title="Test Paper",
            abstract="Test abstract",
            category="cs.LG",
            category_name="Machine Learning",
            confidence=0.95,
            keywords=["transformer", "attention"],
            related_repos=["NEXUS", "DevTools"],
            is_ecosystem=True
        )
        
        self.assertEqual(classification.arxiv_id, "2301.12345")
        self.assertTrue(classification.is_ecosystem)


class TestENV1Orchestrator(unittest.TestCase):
    """Tests pour ENV1 Orchestrator"""
    
    def test_orchestrator_creation(self):
        """Teste la création de l'orchestrator"""
        from managers.env1_orchestrator import ENV1Orchestrator
        
        orchestrator = ENV1Orchestrator()
        self.assertIsNotNone(orchestrator.executor)
        self.assertIsNotNone(orchestrator.classifier)
    
    def test_detect_arxiv_papers_in_note(self):
        """Teste la détection de papiers dans une note"""
        from managers.env1_orchestrator import ENV1Orchestrator
        import asyncio
        
        orchestrator = ENV1Orchestrator()
        
        content = """
        # Ma Note de Recherche
        
        J'ai lu l'article sur Attention is All You Need (arXiv:1706.03762).
        Très intéressant pour NEXUS.
        
        Aussi: arXiv:2301.00001 sur les LLM.
        """
        
        papers = asyncio.run(orchestrator.detect_arxiv_papers(content))
        self.assertEqual(len(papers), 2)
    
    def test_processing_result_dataclass(self):
        """Teste la structure ProcessingResult"""
        from managers.env1_orchestrator import ProcessingResult
        
        result = ProcessingResult(
            note_path="/path/to/note.md",
            papers_detected=["arXiv:2301.12345"],
            classifications=[],
            processed_at=datetime.now().isoformat(),
            duration_ms=1234.5
        )
        
        self.assertEqual(result.note_path, "/path/to/note.md")
        self.assertEqual(len(result.papers_detected), 1)


class TestAutoImprovement(unittest.TestCase):
    """Tests pour Auto-Improvement"""
    
    def test_auto_improvement_creation(self):
        """Teste la création de l'auto-improvement"""
        from managers.auto_improvement import AutoImprovement
        
        ai = AutoImprovement()
        self.assertIsNotNone(ai.env5)
        self.assertIsNotNone(ai.metrics_dir)
    
    def test_detect_patterns(self):
        """Teste la détection de patterns"""
        from managers.auto_improvement import AutoImprovement
        
        ai = AutoImprovement()
        
        logs = [
            {"duration_ms": 1000, "success": True},
            {"duration_ms": 2000, "success": True},
            {"duration_ms": 500, "success": False},
        ]
        
        metrics = ai.detect_patterns(logs)
        
        self.assertAlmostEqual(metrics.avg_execution_time_ms, 1166.67, places=2)
        self.assertAlmostEqual(metrics.success_rate, 0.667, places=3)
        self.assertEqual(metrics.papers_processed, 3)
    
    def test_performance_metrics_dataclass(self):
        """Teste la structure PerformanceMetrics"""
        from managers.auto_improvement import PerformanceMetrics
        
        metrics = PerformanceMetrics(
            avg_execution_time_ms=1000.0,
            success_rate=0.95,
            papers_processed=10,
            bottlenecks=["Slow CDP"],
            timestamp=datetime.now().isoformat()
        )
        
        self.assertEqual(metrics.avg_execution_time_ms, 1000.0)
        self.assertEqual(metrics.success_rate, 0.95)
    
    def test_optimization_dataclass(self):
        """Teste la structure Optimization"""
        from managers.auto_improvement import Optimization
        
        opt = Optimization(
            target="cache_optimization",
            description="Enable caching for arXiv requests",
            expected_gain_percent=25.0,
            implementation="Add Redis cache layer",
            priority=1
        )
        
        self.assertEqual(opt.target, "cache_optimization")
        self.assertEqual(opt.priority, 1)


class TestIntegration_PipelineV6(unittest.TestCase):
    """Tests d'intégration Pipeline V6 complet"""
    
    def test_full_pipeline_structure(self):
        """Teste la structure complète du pipeline"""
        from managers.pipeline_v6_executor import PipelineV6Executor
        from managers.pipeline_v6_events import PipelineV6Events
        from managers.arxiv_classifier import ArxivClassifier
        from managers.env1_orchestrator import ENV1Orchestrator
        from managers.auto_improvement import AutoImprovement
        
        # Vérifier que tous les composants existent
        executor = PipelineV6Executor()
        events = PipelineV6Events()
        classifier = ArxivClassifier()
        orchestrator = ENV1Orchestrator()
        ai = AutoImprovement()
        
        self.assertIsNotNone(executor)
        self.assertIsNotNone(events)
        self.assertIsNotNone(classifier)
        self.assertIsNotNone(orchestrator)
        self.assertIsNotNone(ai)
    
    def test_pipeline_workflow(self):
        """Teste le workflow complet du pipeline"""
        from managers.env1_orchestrator import ENV1Orchestrator
        import asyncio
        
        # Créer une note de test
        test_note = """
        # Test Note
        
        arXiv:2301.12345 - Test paper 1
        arXiv:2302.67890 - Test paper 2
        """
        
        orchestrator = ENV1Orchestrator()
        papers = asyncio.run(orchestrator.detect_arxiv_papers(test_note))
        
        self.assertEqual(len(papers), 2)
        self.assertIn("arXiv:2301.12345", papers)
        self.assertIn("arXiv:2302.67890", papers)


class TestOPS_Compliance(unittest.TestCase):
    """Tests de conformité OPS"""
    
    def test_ops_metrics_present(self):
        """Teste que les composants ont leurs métriques OPS"""
        import inspect
        from managers import pipeline_v6_executor, pipeline_v6_events
        from managers import arxiv_classifier, env1_orchestrator, auto_improvement
        
        modules = [
            pipeline_v6_executor,
            pipeline_v6_events,
            arxiv_classifier,
            env1_orchestrator,
            auto_improvement,
        ]
        
        for module in modules:
            docstring = module.__doc__ or ""
            self.assertIn("OPS3_BREAKTHROUGH", docstring,
                         f"{module.__name__} doit avoir OPS3_BREAKTHROUGH dans docstring")


if __name__ == "__main__":
    unittest.main(verbosity=2)