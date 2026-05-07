#!/usr/bin/env python3
"""
Unit tests for SCO7 Ecosystem Integration
EPIC_SCO7_ECOSYSTEM_INTEGRATION_9041 Tests
"""

import unittest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sco7_engine.ecosystem_integration import (
    EcosystemKnowledgeExtractor,
    EcosystemIntegrationOrchestrator,
)


class TestSCO7EcosystemIntegration(unittest.TestCase):
    def setUp(self):
        self.test_epic = {"id": "test_epic", "type": "api"}

    def test_extractor_initialization(self):
        """Test ecosystem extractor initialization"""
        extractor = EcosystemKnowledgeExtractor()
        self.assertIsNotNone(extractor)
        self.assertIsInstance(extractor.repositories, list)
        self.assertEqual(len(extractor.repositories), 5)

    def test_integration_orchestrator_creation(self):
        """Test integration orchestrator creation"""
        integrator = EcosystemIntegrationOrchestrator()
        self.assertIsNotNone(integrator)

    def test_knowledge_extraction_structure(self):
        """Test knowledge extraction returns proper structure"""

        async def run_test():
            extractor = EcosystemKnowledgeExtractor()
            knowledge = await extractor.extract_ecosystem_knowledge()

            self.assertIn("ontological_terms", knowledge)
            self.assertIn("architectural_patterns", knowledge)
            self.assertIn("security_patterns", knowledge)
            self.assertIn("performance_benchmarks", knowledge)
            self.assertIn("summary", knowledge)
            return True

        result = asyncio.run(run_test())
        self.assertTrue(result)

    def test_ecosystem_integration_enhancement(self):
        """Test EPIC enhancement with ecosystem knowledge"""

        async def run_test():
            integrator = EcosystemIntegrationOrchestrator()
            result = await integrator.integrate_ecosystem(self.test_epic)

            enhanced_epic = result["enhanced_epic"]
            self.assertIn("ontological_context", enhanced_epic)
            self.assertIn("architectural_patterns", enhanced_epic)
            self.assertIn("security_requirements", enhanced_epic)
            return True

        result = asyncio.run(run_test())
        self.assertTrue(result)

    def test_integration_patterns_generation(self):
        """Test integration patterns are generated"""

        async def run_test():
            integrator = EcosystemIntegrationOrchestrator()
            result = await integrator.integrate_ecosystem(self.test_epic)

            patterns = result["integration_patterns"]
            self.assertIsInstance(patterns, list)
            self.assertGreater(len(patterns), 0)
            return True

        result = asyncio.run(run_test())
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
