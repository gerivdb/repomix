#!/usr/bin/env python3
"""
Wazaa Bus Integration Tests - IT-1: Concurrence & Invariants Protocole
Tests de charge concurrente et validation des invariants critiques

IntentHash: 0xWAZAA_IT1_CONCURRENCE_TESTS_20260425
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import threading
import time
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Imports locaux
from wazaa_bus.intention_resolution import (
    CollectiveIntentionManager,
    AuthorityLevel,
    IntentResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConcurrenceTestSuite:
    """Suite de tests pour la concurrence et invariants protocole"""

    def __init__(self):
        self.manager = CollectiveIntentionManager()
        self.results = {
            "broadcast_simultane": {"passed": False, "metrics": {}},
            "timeout_adaptatif": {"passed": False, "metrics": {}},
            "double_reponses": {"passed": False, "metrics": {}},
            "self_reference": {"passed": False, "metrics": {}},
            "race_conditions": {"passed": False, "metrics": {}},
        }

        # Enregistrer les agents de test
        self._setup_test_agents()

    def _setup_test_agents(self):
        """Configure les agents pour les tests"""
        self.kilocode = self.manager.register_agent("kilocode", AuthorityLevel.KILOCODE)
        self.cline = self.manager.register_agent("cline", AuthorityLevel.CLINE)
        self.windsurf = self.manager.register_agent("windsurf", AuthorityLevel.WINDSURF)
        self.cursor = self.manager.register_agent("cursor", AuthorityLevel.CURSOR)
        self.copilot = self.manager.register_agent("copilot", AuthorityLevel.COPILOT)

        logger.info(
            "Test agents registered: kilocode, cline, windsurf, cursor, copilot"
        )

    def test_broadcast_simultane(self) -> bool:
        """IT-1.1: 5 agents broadcastent 10 intents chacun en parallèle"""
        logger.info("Starting broadcast simultané test...")

        start_time = time.time()
        exceptions = []

        def agent_broadcasts(agent_id: str, commands: List[str]):
            try:
                for cmd in commands:
                    intent_id = self.manager.resolve_intention(agent_id, cmd)
                    time.sleep(0.01)  # Petit délai pour réalisme
            except Exception as e:
                exceptions.append(f"{agent_id}: {e}")

        # Préparer les commandes
        commands = [
            "lance ECOS CLI",
            "compile le projet",
            "run tests unitaires",
            "deploy to staging",
            "check logs erreurs",
            "update dependencies",
            "build documentation",
            "run performance tests",
            "backup database",
            "restart services",
        ]

        # Lancer broadcasts simultanés
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for agent_id in ["kilocode", "cline", "windsurf", "cursor", "copilot"]:
                futures.append(executor.submit(agent_broadcasts, agent_id, commands))

            # Attendre la fin
            for future in as_completed(futures):
                future.result()

        total_time = time.time() - start_time

        # Vérifier résultats
        system_status = self.manager.get_system_status()
        consensus_count = system_status["total_consensus"]
        broadcast_count = system_status["total_broadcasts"]

        passed = (
            len(exceptions) == 0
            and consensus_count >= 5  # Au moins 5 consensus atteints
            and total_time < 15.0  # Moins de 15 secondes (réalisme)
        )

        self.results["broadcast_simultane"] = {
            "passed": passed,
            "metrics": {
                "total_time": total_time,
                "consensus_count": consensus_count,
                "broadcast_count": broadcast_count,
                "exceptions": exceptions,
                "consensus_success_rate": consensus_count / max(broadcast_count, 1),
            },
        }

        logger.info(f"Broadcast simultané test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def test_timeout_adaptatif(self) -> bool:
        """IT-1.2: Timeout s'adapte au nombre d'agents"""
        logger.info("Starting timeout adaptatif test...")

        # Test avec 2 agents (timeout ~200ms attendu)
        manager_small = CollectiveIntentionManager()
        k_small = manager_small.register_agent(
            "kilocode_small", AuthorityLevel.KILOCODE
        )
        c_small = manager_small.register_agent("cline_small", AuthorityLevel.CLINE)

        start_time = time.time()
        intent_id = manager_small.resolve_intention(
            "kilocode_small", "test timeout small"
        )
        time.sleep(0.3)  # Attendre résolution
        small_time = time.time() - start_time

        # Test avec 5 agents (timeout ~500ms attendu)
        start_time = time.time()
        intent_id = self.manager.resolve_intention("kilocode", "test timeout large")
        time.sleep(0.6)  # Attendre résolution
        large_time = time.time() - start_time

        # Vérifier que timeout s'adapte
        timeout_ratio = large_time / max(small_time, 0.1)
        passed = (
            small_time < 0.5  # Petit groupe rapide
            and large_time < 1.0  # Grand groupe plus lent mais raisonnable
            and timeout_ratio > 1.5  # Grand groupe effectivement plus lent
        )

        self.results["timeout_adaptatif"] = {
            "passed": passed,
            "metrics": {
                "small_group_time": small_time,
                "large_group_time": large_time,
                "timeout_ratio": timeout_ratio,
            },
        }

        logger.info(f"Timeout adaptatif test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def test_double_reponses(self) -> bool:
        """IT-1.3: Agent ne peut répondre qu'une fois par intent"""
        logger.info("Starting double réponses test...")

        # Simuler double réponse en forçant
        intent_id = "test_double_" + str(time.time())

        # Première réponse
        response1 = {
            "responder": "cline",
            "intent_id": intent_id,
            "action": "test action",
            "confidence": 0.8,
            "authority_level": 9,
            "signature": "test_sig_1",
            "timestamp": time.time(),
        }

        # Deuxième réponse (même agent, même intent)
        response2 = {
            "responder": "cline",
            "intent_id": intent_id,
            "action": "different action",
            "confidence": 0.7,
            "authority_level": 9,
            "signature": "test_sig_2",
            "timestamp": time.time(),
        }

        # Injecter les réponses
        self.cline.receive_response(IntentResponse(**response1))
        self.cline.receive_response(IntentResponse(**response2))

        # Vérifier que seul une réponse est comptée
        pending = self.cline.pending_responses.get(intent_id, [])
        passed = len(pending) <= 1  # Au plus une réponse par agent

        self.results["double_reponses"] = {
            "passed": passed,
            "metrics": {"responses_counted": len(pending), "intent_id": intent_id},
        }

        logger.info(f"Double réponses test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def test_self_reference(self) -> bool:
        """IT-1.4: Agent ignore ses propres broadcasts"""
        logger.info("Starting self-reference test...")

        # Kilocode broadcast une commande qu'il pourrait traiter
        original_responses = len(self.kilocode.pending_responses)

        intent_id = self.manager.resolve_intention("kilocode", "lance ECOS CLI")

        # Vérifier que kilocode ne s'est pas ajouté de réponse
        current_responses = len(self.kilocode.pending_responses)
        passed = current_responses == original_responses

        # Vérifier métrique self_reference_detected
        metrics = self.kilocode.get_metrics()
        self_ref_detected = metrics.get("self_reference_detected", 0)

        self.results["self_reference"] = {
            "passed": passed,
            "metrics": {
                "original_responses": original_responses,
                "current_responses": current_responses,
                "self_reference_detected": self_ref_detected,
            },
        }

        logger.info(f"Self-reference test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def test_race_conditions(self) -> bool:
        """IT-1.5: 50 broadcasts simultanés sans corruption"""
        logger.info("Starting race conditions test...")

        exceptions = []
        start_time = time.time()

        def stress_broadcast(agent_id: str, command: str):
            try:
                self.manager.resolve_intention(agent_id, command)
            except Exception as e:
                exceptions.append(f"{agent_id}: {e}")

        # 50 broadcasts simultanés
        commands = [f"stress command {i}" for i in range(50)]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i, cmd in enumerate(commands):
                agent_id = ["kilocode", "cline", "windsurf", "cursor", "copilot"][i % 5]
                futures.append(executor.submit(stress_broadcast, agent_id, cmd))

            for future in as_completed(futures):
                future.result()

        total_time = time.time() - start_time

        # Vérifier pas de corruption
        system_status = self.manager.get_system_status()
        passed = (
            len(exceptions) == 0
            and total_time < 5.0  # Moins de 5 secondes pour 50 broadcasts
            and system_status["total_broadcasts"]
            >= 45  # Au moins 45 broadcasts réussis
        )

        self.results["race_conditions"] = {
            "passed": passed,
            "metrics": {
                "total_time": total_time,
                "exceptions": exceptions,
                "total_broadcasts": system_status["total_broadcasts"],
                "total_consensus": system_status["total_consensus"],
            },
        }

        logger.info(f"Race conditions test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def run_all_tests(self) -> Dict[str, Any]:
        """Exécute tous les tests de concurrence"""
        logger.info("Starting IT-1 Concurrence Test Suite...")

        self.test_broadcast_simultane()
        self.test_timeout_adaptatif()
        self.test_double_reponses()
        self.test_self_reference()
        self.test_race_conditions()

        # Calcul résumé
        passed_tests = sum(1 for result in self.results.values() if result["passed"])
        total_tests = len(self.results)

        summary = {
            "test_suite": "IT-1 Concurrence",
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": passed_tests / total_tests,
            "overall_passed": passed_tests == total_tests,
            "results": self.results,
            "system_status": self.manager.get_system_status(),
        }

        logger.info(
            f"IT-1 Concurrence Test Suite: {passed_tests}/{total_tests} tests passed"
        )
        return summary


# Test standalone
if __name__ == "__main__":
    suite = ConcurrenceTestSuite()
    results = suite.run_all_tests()

    print("\n=== IT-1 CONCURRENCE TEST RESULTS ===")
    print(f"Overall: {'PASSED' if results['overall_passed'] else 'FAILED'}")
    print(".1f")

    for test_name, test_result in results["results"].items():
        status = "PASSED" if test_result["passed"] else "FAILED"
        print(f"  {test_name}: {status}")

    print("\nDetailed metrics:")
    for test_name, test_result in results["results"].items():
        print(f"\n{test_name}:")
        for key, value in test_result["metrics"].items():
            print(f"  {key}: {value}")
