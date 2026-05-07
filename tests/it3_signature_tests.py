#!/usr/bin/env python3
"""
Wazaa Bus Integration Tests - IT-3: Sécurité & Signatures JWS/ECDSA
Tests de signatures cryptographiques et validation d'autorité

IntentHash: 0xWAZAA_IT3_SIGNATURE_TESTS_20260425
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import logging
from typing import Dict, Any, List

# Imports locaux
from wazaa_bus.signature_manager import (
    JWSSignatureManager,
    sign_response,
    verify_signature,
    validate_agent_authority,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignatureSecurityTestSuite:
    """Suite de tests pour signatures et sécurité"""

    def __init__(self):
        self.signature_manager = JWSSignatureManager("test_agent_keys.json")
        self.results = {
            "signature_valide": {"passed": False, "metrics": {}},
            "signature_invalide": {"passed": False, "metrics": {}},
            "autorite_mismatch": {"passed": False, "metrics": {}},
            "performance_signature": {"passed": False, "metrics": {}},
            "cle_corrompue": {"passed": False, "metrics": {}},
        }

    def _create_test_response(
        self, agent_id: str, action: str, authority: int
    ) -> Dict[str, Any]:
        """Crée une réponse de test"""
        return {
            "responder": agent_id,
            "intent_id": f"test_intent_{int(time.time())}",
            "action": action,
            "confidence": 0.9,
            "authority_level": authority,
            "timestamp": time.time(),
        }

    def test_signature_valide(self) -> bool:
        """IT-3.1: Signature valide acceptée"""
        logger.info("Starting signature valide test...")

        # Générer clé pour agent test
        key_id = self.signature_manager.generate_key_pair("test_agent")

        # Créer réponse
        response = self._create_test_response("test_agent", "test action", 5)

        # Signer
        signed_jws = sign_response("test_agent", response)

        # Vérifier
        verified_payload = verify_signature(signed_jws)
        print(f"DEBUG: signed_jws = {signed_jws[:100]}...")
        print(f"DEBUG: verified_payload = {verified_payload}")
        print(f"DEBUG: original response = {response}")

        # Valider
        passed = (
            verified_payload is not None
            and verified_payload["responder"] == "test_agent"
            and verified_payload["action"] == "test action"
        )

        self.results["signature_valide"] = {
            "passed": passed,
            "metrics": {
                "signature_generated": signed_jws is not None and len(signed_jws) > 0,
                "payload_verified": verified_payload is not None,
                "payload_integrity": verified_payload == response
                if verified_payload
                else False,
            },
        }

        logger.info(f"Signature valide test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def test_signature_invalide(self) -> bool:
        """IT-3.2: Signature invalide rejetée"""
        logger.info("Starting signature invalide test...")

        # Générer clé valide
        key_id = self.signature_manager.generate_key_pair("test_agent_invalid")

        # Créer réponse valide
        response = self._create_test_response("test_agent_invalid", "valid action", 5)
        signed_jws = sign_response("test_agent_invalid", response)

        # Altérer la signature (modifier dernier caractère)
        tampered_jws = signed_jws[:-1] + ("B" if signed_jws[-1] == "A" else "A")

        # Tenter vérification
        verified_payload = verify_signature(tampered_jws)

        # Valider rejet
        passed = verified_payload is None

        # Test avec signature complètement invalide
        invalid_jws = "invalid.jwt.signature"
        verified_invalid = verify_signature(invalid_jws)
        passed = passed and verified_invalid is None

        self.results["signature_invalide"] = {
            "passed": passed,
            "metrics": {
                "tampered_signature_rejected": verified_payload is None,
                "invalid_signature_rejected": verified_invalid is None,
                "tampered_jws_length": len(tampered_jws),
                "original_jws_length": len(signed_jws),
            },
        }

        logger.info(f"Signature invalide test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def test_autorite_mismatch(self) -> bool:
        """IT-3.3: Mismatch d'autorité détecté"""
        logger.info("Starting autorite mismatch test...")

        # Générer clé pour agent niveau 5
        key_id = self.signature_manager.generate_key_pair("agent_niveau5")

        # Créer réponse avec autorité 5
        response = self._create_test_response("agent_niveau5", "action niveau5", 5)
        signed_jws = sign_response("agent_niveau5", response)

        # Tenter validation avec autorité revendiquée 10 (mismatch)
        validation_result = validate_agent_authority("agent_niveau5", 10, signed_jws)

        # Devrait échouer
        passed = validation_result is False

        # Test validation correcte
        correct_validation = validate_agent_authority("agent_niveau5", 5, signed_jws)
        passed = passed and correct_validation is True

        self.results["autorite_mismatch"] = {
            "passed": passed,
            "metrics": {
                "mismatch_detected": not validation_result,
                "correct_validation": correct_validation,
                "claimed_authority": 10,
                "actual_authority": 5,
            },
        }

        logger.info(f"Autorite mismatch test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def test_performance_signature(self) -> bool:
        """IT-3.4: Performance validation sous charge"""
        logger.info("Starting performance signature test...")

        # Générer clé
        key_id = self.signature_manager.generate_key_pair("perf_agent")

        # Créer 100 réponses
        responses = []
        for i in range(100):
            responses.append(self._create_test_response("perf_agent", f"action {i}", 5))

        # Mesurer temps signature
        start_time = time.time()
        signatures = []
        for response in responses:
            sig = sign_response("perf_agent", response)
            signatures.append(sig)
        sign_time = time.time() - start_time

        # Mesurer temps vérification
        start_time = time.time()
        verified_count = 0
        for sig in signatures:
            if verify_signature(sig):
                verified_count += 1
        verify_time = time.time() - start_time

        # Calculs
        avg_sign_time = sign_time / len(responses) * 1000  # ms
        avg_verify_time = verify_time / len(responses) * 1000  # ms

        passed = (
            avg_sign_time < 50  # <50ms par signature
            and avg_verify_time < 10  # <10ms par vérification
            and verified_count == len(signatures)  # Toutes vérifiées
        )

        self.results["performance_signature"] = {
            "passed": passed,
            "metrics": {
                "total_signatures": len(signatures),
                "total_sign_time": sign_time,
                "avg_sign_time_ms": avg_sign_time,
                "total_verify_time": verify_time,
                "avg_verify_time_ms": avg_verify_time,
                "verified_count": verified_count,
                "verification_success_rate": verified_count / len(signatures),
            },
        }

        logger.info(".1f")
        return passed

    def test_cle_corrompue(self) -> bool:
        """IT-3.5: Gestion clé corrompue"""
        logger.info("Starting cle corrompue test...")

        # Générer clé valide
        key_id = self.signature_manager.generate_key_pair("corrupt_agent")

        # Créer et signer réponse
        response = self._create_test_response("corrupt_agent", "corrupt action", 5)
        signed_jws = sign_response("corrupt_agent", response)

        # Vérifier que ça marche avant corruption
        valid_before = validate_agent_authority("corrupt_agent", 5, signed_jws)

        # Corrompre la clé privée (simuler compromission)
        if key_id in self.signature_manager.key_store:
            original_key = self.signature_manager.key_store[key_id]["private_key"]
            # Corrompre en modifiant quelques caractères
            corrupted_key = original_key[:-10] + "CORRUPTED"
            self.signature_manager.key_store[key_id]["private_key"] = corrupted_key

        # Tenter nouvelle signature (devrait échouer)
        try:
            new_signed = sign_response("corrupt_agent", response)
            sign_after_corrupt = new_signed is not None
        except Exception:
            sign_after_corrupt = False

        # Restaurer clé pour test validation
        if key_id in self.signature_manager.key_store:
            self.signature_manager.key_store[key_id]["private_key"] = original_key

        # Vérifier validation avec ancienne signature (devrait encore marcher)
        valid_after_restore = validate_agent_authority("corrupt_agent", 5, signed_jws)

        passed = (
            valid_before  # Fonctionnait avant
            and not sign_after_corrupt  # Impossible de signer après corruption
            and valid_after_restore  # Remarche après restauration
        )

        self.results["cle_corrompue"] = {
            "passed": passed,
            "metrics": {
                "valid_before_corruption": valid_before,
                "sign_failed_after_corruption": not sign_after_corrupt,
                "valid_after_restore": valid_after_restore,
                "key_id": key_id,
            },
        }

        logger.info(f"Clé corrompue test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def run_all_tests(self) -> Dict[str, Any]:
        """Exécute tous les tests de sécurité/signature"""
        logger.info("Starting IT-3 Sécurité/Signature Test Suite...")

        self.test_signature_valide()
        self.test_signature_invalide()
        self.test_autorite_mismatch()
        self.test_performance_signature()
        self.test_cle_corrompue()

        # Calcul résumé
        passed_tests = sum(1 for result in self.results.values() if result["passed"])
        total_tests = len(self.results)

        summary = {
            "test_suite": "IT-3 Sécurité/Signature",
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": passed_tests / total_tests,
            "overall_passed": passed_tests == total_tests,
            "results": self.results,
        }

        logger.info(
            f"IT-3 Sécurité/Signature Test Suite: {passed_tests}/{total_tests} tests passed"
        )
        return summary

    def cleanup(self):
        """Nettoie les fichiers de test"""
        try:
            if os.path.exists("test_agent_keys.json"):
                os.remove("test_agent_keys.json")
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")


# Test standalone
if __name__ == "__main__":
    suite = SignatureSecurityTestSuite()
    try:
        results = suite.run_all_tests()

        print("\n=== IT-3 SÉCURITÉ/SIGNATURE TEST RESULTS ===")
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

    finally:
        suite.cleanup()
