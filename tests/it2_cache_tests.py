#!/usr/bin/env python3
"""
Wazaa Bus Integration Tests - IT-2: Cache & Persistence
Tests de persistance cache, TTL, restart, corruption et performance

IntentHash: 0xWAZAA_IT2_CACHE_TESTS_20260425
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import threading
import time
import json
import tempfile
import shutil
import logging
from typing import List, Dict, Any

# Imports locaux
from wazaa_bus.cache_manager import (
    ConsensusCacheManager,
    store_consensus,
    get_consensus,
    get_cache_stats,
)
from wazaa_bus.wazaa_stubs import ConsensusResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CachePersistenceTestSuite:
    """Suite de tests pour cache et persistance"""

    def __init__(self):
        self.test_db_path = "test_wazaa_cache.duckdb"
        self.cache_manager = ConsensusCacheManager(self.test_db_path)
        self.results = {
            "hit_miss_rate": {"passed": False, "metrics": {}},
            "ttl_expiration": {"passed": False, "metrics": {}},
            "restart_persistence": {"passed": False, "metrics": {}},
            "duckdb_fallback": {"passed": False, "metrics": {}},
            "corruption_handling": {"passed": False, "metrics": {}},
        }

    def _create_test_consensus(
        self, intent_id: str, action: str, score: float = 0.95
    ) -> ConsensusResult:
        """Crée un consensus de test"""
        return ConsensusResult(
            intent_id=intent_id,
            official_action=action,
            consensus_score=score,
            votes=3,
            cache_ttl=2592000,  # 30 jours
            timestamp=time.time(),
        )

    def test_hit_miss_rate(self) -> bool:
        """IT-2.1: Mesure hit rate avec pattern réaliste"""
        logger.info("Starting hit/miss rate test...")

        # Créer 100 consensus de test
        test_consensus = []
        for i in range(100):
            consensus = self._create_test_consensus(
                f"test_intent_{i}",
                f"test action {i}",
                0.8 + (i % 20) * 0.01,  # Scores variés
            )
            test_consensus.append(consensus)
            store_consensus(consensus)

        # Pattern de consultation réaliste : 20% répétés, 80% nouveaux
        lookups = 0
        hits = 0

        # 20% hits attendus (répétitions)
        for i in range(20):
            intent_id = f"test_intent_{i % 20}"  # Répète les 20 premiers
            result = get_consensus(intent_id)
            lookups += 1
            if result:
                hits += 1

        # 80% misses attendus (nouveaux)
        for i in range(80):
            intent_id = f"new_intent_{i}"
            result = get_consensus(intent_id)
            lookups += 1
            if result:
                hits += 1

        hit_rate = hits / lookups if lookups > 0 else 0

        # Nettoyer
        self.cache_manager.clear_cache()

        passed = hit_rate >= 0.15  # Au moins 15% hits (léger en dessous de 20% attendu)

        self.results["hit_miss_rate"] = {
            "passed": passed,
            "metrics": {
                "total_lookups": lookups,
                "total_hits": hits,
                "hit_rate": hit_rate,
                "expected_hit_rate": 0.2,
                "cache_size_after": get_cache_stats()["total_entries"],
            },
        }

        logger.info(".1f")
        return passed

    def test_ttl_expiration(self) -> bool:
        """IT-2.2: Vérifie expiration automatique TTL"""
        logger.info("Starting TTL expiration test...")

        # Créer consensus avec TTL court (5 secondes)
        consensus = ConsensusResult(
            intent_id="ttl_test",
            official_action="ttl test action",
            consensus_score=0.9,
            votes=2,
            cache_ttl=5,  # 5 secondes
            timestamp=time.time(),
        )
        store_consensus(consensus)

        # Vérifier présent immédiatement
        result1 = get_consensus("ttl_test")
        present_before = result1 is not None

        # Attendre expiration + 1 seconde
        time.sleep(6)

        # Vérifier disparu
        result2 = get_consensus("ttl_test")
        expired_after = result2 is None

        # Vérifier nettoyage périodique
        initial_stats = get_cache_stats()
        self.cache_manager.cleanup_expired()
        final_stats = get_cache_stats()

        cleaned_entries = (
            initial_stats["expired_entries"] - final_stats["expired_entries"]
        )

        passed = present_before and expired_after and cleaned_entries >= 1

        self.results["ttl_expiration"] = {
            "passed": passed,
            "metrics": {
                "present_before_expiry": present_before,
                "expired_after_ttl": expired_after,
                "cleaned_entries": cleaned_entries,
                "ttl_seconds": 5,
            },
        }

        logger.info(f"TTL expiration test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def test_restart_persistence(self) -> bool:
        """IT-2.3: Test persistance après restart process"""
        logger.info("Starting restart persistence test...")

        # Créer plusieurs consensus
        test_data = []
        for i in range(10):
            consensus = self._create_test_consensus(
                f"restart_test_{i}", f"restart action {i}"
            )
            test_data.append((consensus.intent_id, consensus.official_action))
            store_consensus(consensus)

        # Forcer écriture disque
        self.cache_manager.cleanup_expired()

        # Simuler restart : créer nouveau manager sur même DB
        new_manager = ConsensusCacheManager(self.test_db_path)

        # Vérifier récupération
        recovered = 0
        for intent_id, expected_action in test_data:
            result = new_manager.get_consensus(intent_id)
            if result and result.official_action == expected_action:
                recovered += 1

        recovery_rate = recovered / len(test_data)

        # Nettoyer
        new_manager.close()
        self.cache_manager.clear_cache()

        passed = recovery_rate >= 0.95  # Au moins 95% récupérés

        self.results["restart_persistence"] = {
            "passed": passed,
            "metrics": {
                "total_stored": len(test_data),
                "total_recovered": recovered,
                "recovery_rate": recovery_rate,
                "expected_recovery": 1.0,
            },
        }

        logger.info(".1f")
        return passed

    def test_duckdb_fallback(self) -> bool:
        """IT-2.4: Test fallback JSON si DuckDB indisponible"""
        logger.info("Starting DuckDB fallback test...")

        # Sauvegarder état original
        original_duckdb_available = True
        try:
            import duckdb
        except ImportError:
            original_duckdb_available = False

        if original_duckdb_available:
            # Forcer fallback en renommant DuckDB temporairement
            temp_db_path = self.test_db_path + ".backup"
            if os.path.exists(self.test_db_path):
                os.rename(self.test_db_path, temp_db_path)

            try:
                # Créer manager qui devrait utiliser JSON fallback
                json_manager = ConsensusCacheManager("nonexistent.duckdb")

                # Test opérations basiques
                consensus = self._create_test_consensus(
                    "fallback_test", "fallback action"
                )
                stored = json_manager.store_consensus(consensus)
                retrieved = json_manager.get_consensus("fallback_test")

                passed = (
                    stored
                    and retrieved
                    and retrieved.official_action == "fallback action"
                )

                # Vérifier fichier JSON créé
                json_file_exists = os.path.exists("wazaa_cache.json")

                json_manager.close()

            finally:
                # Restaurer
                if os.path.exists(temp_db_path):
                    os.rename(temp_db_path, self.test_db_path)
                if os.path.exists("wazaa_cache.json"):
                    os.remove("wazaa_cache.json")

        else:
            # DuckDB déjà indisponible, test direct JSON
            json_manager = ConsensusCacheManager("test_json_only.duckdb")
            consensus = self._create_test_consensus("json_test", "json action")
            stored = json_manager.store_consensus(consensus)
            retrieved = json_manager.get_consensus("json_test")
            passed = stored and retrieved and retrieved.official_action == "json action"
            json_manager.close()

        self.results["duckdb_fallback"] = {
            "passed": passed,
            "metrics": {
                "duckdb_available": original_duckdb_available,
                "fallback_used": not original_duckdb_available,
                "json_file_created": os.path.exists("wazaa_cache.json")
                if not original_duckdb_available
                else False,
            },
        }

        logger.info(f"DuckDB fallback test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def test_corruption_handling(self) -> bool:
        """IT-2.5: Test gestion corruption fichiers"""
        logger.info("Starting corruption handling test...")

        # Créer données normales
        consensus = self._create_test_consensus("corruption_test", "corruption action")
        store_consensus(consensus)

        # Vérifier opération normale
        result1 = get_consensus("corruption_test")
        normal_operation = result1 is not None

        # Simuler corruption DuckDB (si disponible)
        if os.path.exists(self.test_db_path):
            # Sauvegarder original
            backup_path = self.test_db_path + ".corrupt_backup"
            shutil.copy2(self.test_db_path, backup_path)

            try:
                # Corrompre fichier (écrire données aléatoires)
                with open(self.test_db_path, "wb") as f:
                    f.write(b"CORRUPTED_DATA" * 1000)

                # Créer nouveau manager - devrait gérer corruption
                corrupt_manager = ConsensusCacheManager(self.test_db_path)

                # Tester qu'il ne crash pas
                test_consensus = self._create_test_consensus(
                    "post_corrupt_test", "post corrupt action"
                )
                stored_after_corrupt = corrupt_manager.store_consensus(test_consensus)

                # Vérifier récupération partielle possible
                recovered = corrupt_manager.get_consensus("post_corrupt_test")

                graceful_handling = (
                    not stored_after_corrupt or recovered
                )  # Soit échec propre, soit succès

                corrupt_manager.close()

            finally:
                # Restaurer
                if os.path.exists(backup_path):
                    os.replace(backup_path, self.test_db_path)

        else:
            # Test JSON corruption
            json_manager = ConsensusCacheManager("corrupt_test.duckdb")

            # Créer données
            json_manager.store_consensus(consensus)

            # Corrompre JSON
            json_file = "wazaa_cache.json"
            if os.path.exists(json_file):
                with open(json_file, "w") as f:
                    f.write("INVALID JSON {")

            # Tester récupération
            recovered = json_manager.get_consensus("corruption_test")
            graceful_handling = recovered is None  # Devrait retourner None proprement

            json_manager.close()
            if os.path.exists(json_file):
                os.remove(json_file)

        passed = normal_operation and graceful_handling

        self.results["corruption_handling"] = {
            "passed": passed,
            "metrics": {
                "normal_operation_before": normal_operation,
                "graceful_corruption_handling": graceful_handling,
                "tested_backend": "duckdb"
                if os.path.exists(self.test_db_path)
                else "json",
            },
        }

        logger.info(f"Corruption handling test: {'PASSED' if passed else 'FAILED'}")
        return passed

    def run_all_tests(self) -> Dict[str, Any]:
        """Exécute tous les tests de cache/persistance"""
        logger.info("Starting IT-2 Cache/Persistence Test Suite...")

        self.test_hit_miss_rate()
        self.test_ttl_expiration()
        self.test_restart_persistence()
        self.test_duckdb_fallback()
        self.test_corruption_handling()

        # Calcul résumé
        passed_tests = sum(1 for result in self.results.values() if result["passed"])
        total_tests = len(self.results)

        summary = {
            "test_suite": "IT-2 Cache/Persistence",
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": passed_tests / total_tests,
            "overall_passed": passed_tests == total_tests,
            "results": self.results,
            "final_cache_stats": get_cache_stats(),
        }

        logger.info(
            f"IT-2 Cache/Persistence Test Suite: {passed_tests}/{total_tests} tests passed"
        )
        return summary

    def cleanup(self):
        """Nettoie les fichiers de test"""
        try:
            if os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)
            if os.path.exists("wazaa_cache.json"):
                os.remove("wazaa_cache.json")
            if os.path.exists("nonexistent.duckdb"):
                os.remove("nonexistent.duckdb")
            self.cache_manager.close()
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")


# Test standalone
if __name__ == "__main__":
    suite = CachePersistenceTestSuite()
    try:
        results = suite.run_all_tests()

        print("\n=== IT-2 CACHE/PERSISTENCE TEST RESULTS ===")
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

        print("\nFinal cache stats:")
        for key, value in results["final_cache_stats"].items():
            print(f"  {key}: {value}")

    finally:
        suite.cleanup()
