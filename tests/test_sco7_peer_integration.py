#!/usr/bin/env python3
"""Tests for SCO7 Peer Integration"""

import unittest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSCO7PeerIntegration(unittest.TestCase):
    def test_peer_communication_initialization(self):
        """Test initialisation communication peer"""
        from scripts.sco7_quantum_peer_communication import QuantumPeerCommunicator

        communicator = QuantumPeerCommunicator()
        self.assertIsNotNone(communicator)

    def test_decision_engine_initialization(self):
        """Test initialisation moteur décisions"""
        from scripts.sco7_collective_decision_engine import CollectiveDecisionEngine

        engine = CollectiveDecisionEngine()
        self.assertIsNotNone(engine)

    def test_evolution_system_initialization(self):
        """Test initialisation système évolution"""
        from scripts.sco7_autonomous_evolution import AutonomousEvolutionSystem

        system = AutonomousEvolutionSystem()
        self.assertIsNotNone(system)

    def test_registry_operations(self):
        """Test opérations registre citoyen"""
        from scripts.sco7_citizen_registration import CitizenRegistry

        registry = CitizenRegistry()
        citizens = registry.list_citizens()
        self.assertIsInstance(citizens, list)

    def test_quantum_message_handling(self):
        """Test gestion messages quantiques"""
        from scripts.sco7_quantum_peer_communication import QuantumPeerCommunicator

        communicator = QuantumPeerCommunicator()
        # Test basique de création
        self.assertIsNotNone(communicator.message_queue)

    def test_decision_vote_processing(self):
        """Test traitement votes décisions"""

        async def run_test():
            from scripts.sco7_collective_decision_engine import CollectiveDecisionEngine

            engine = CollectiveDecisionEngine()
            vote_request = {"topic": "test", "options": ["yes", "no"]}
            response = await engine.receive_collective_vote(vote_request)
            self.assertIn("decision", response)
            return True

        result = asyncio.run(run_test())
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
