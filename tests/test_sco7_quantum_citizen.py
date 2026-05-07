#!/usr/bin/env python3
"""
Unit tests for SCO7 Quantum Citizen
EPIC_SCO7_QUANTUM_CITIZEN_ACTIVATION_9047 Tests
"""

import unittest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.sco7_citizen_registration import CitizenRegistry
from scripts.sco7_quantum_peer_communication import QuantumPeerCommunicator
from scripts.sco7_collective_decision_engine import CollectiveDecisionEngine
from scripts.sco7_autonomous_evolution import AutonomousEvolutionSystem


class TestSCO7QuantumCitizen(unittest.TestCase):
    def setUp(self):
        self.citizen_id = "SCO7_INDUSTRIALISATION_ENGINE"

    def test_citizen_registry_creation(self):
        """Test création du registre citoyen"""
        registry = CitizenRegistry()
        self.assertIsNotNone(registry)
        self.assertIsInstance(registry.citizens, dict)

    def test_citizen_registration(self):
        """Test enregistrement d'un citoyen"""
        registry = CitizenRegistry()

        citizen_profile = {
            "citizen_id": "test_citizen",
            "type": "quantum_citizen",
            "capabilities": ["test"],
        }

        result = registry.register_citizen(citizen_profile)
        self.assertEqual(result["citizen_id"], "test_citizen")

        # Vérifier l'enregistrement
        retrieved = registry.get_citizen("test_citizen")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["type"], "quantum_citizen")

    def test_quantum_peer_communicator_creation(self):
        """Test création du communicateur peer quantique"""
        communicator = QuantumPeerCommunicator(self.citizen_id)
        self.assertIsNotNone(communicator)
        self.assertEqual(communicator.citizen_id, self.citizen_id)

    def test_communication_status(self):
        """Test obtention du statut de communication"""
        communicator = QuantumPeerCommunicator(self.citizen_id)
        status = communicator.get_communication_status()

        self.assertIn("citizen_id", status)
        self.assertIn("is_listening", status)
        self.assertIn("connected_peers", status)
        self.assertEqual(status["citizen_id"], self.citizen_id)

    def test_collective_decision_engine_creation(self):
        """Test création du moteur de décisions collectives"""
        engine = CollectiveDecisionEngine(self.citizen_id)
        self.assertIsNotNone(engine)
        self.assertEqual(engine.citizen_id, self.citizen_id)

    def test_decision_proposal(self):
        """Test proposition de décision collective"""

        async def run_test():
            engine = CollectiveDecisionEngine(self.citizen_id)
            proposal_id = await engine.propose_collective_decision(
                "test_topic", "Test decision"
            )
            self.assertIsInstance(proposal_id, str)
            self.assertIn("sco7_proposal", proposal_id)
            return True

        result = asyncio.run(run_test())
        self.assertTrue(result)

    def test_autonomous_evolution_system_creation(self):
        """Test création du système d'évolution autonome"""
        system = AutonomousEvolutionSystem(self.citizen_id)
        self.assertIsNotNone(system)
        self.assertEqual(system.citizen_id, self.citizen_id)

    def test_evolution_status(self):
        """Test obtention du statut d'évolution"""
        system = AutonomousEvolutionSystem(self.citizen_id)
        status = system.get_evolution_status()

        self.assertIn("citizen_id", status)
        self.assertIn("current_version", status)
        self.assertIn("quantum_level", status)
        self.assertEqual(status["citizen_id"], self.citizen_id)

    def test_collective_stats(self):
        """Test statistiques collectives"""
        engine = CollectiveDecisionEngine(self.citizen_id)
        stats = engine.get_collective_stats()

        self.assertIn("decisions_participated", stats)
        self.assertIsInstance(stats["decisions_participated"], int)


if __name__ == "__main__":
    unittest.main()
