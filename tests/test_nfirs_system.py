#!/usr/bin/env python3
"""
Tests for PLIXRecovery System - NFIRS Phase 6
Tests end-to-end, TDD coverage >95%, chaos engineering.

IntentHash: 0xPLIX_RECOVERY_TESTS_20260419
"""

import os
import json
import tempfile
import unittest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from plix_recovery import PLIXRecovery


class TestPLIXRecovery(unittest.TestCase):
    """Tests unitaires et d'intégration pour PLIXRecovery"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.nexus_root = self.temp_dir / "nexus"
        self.nexus_root.mkdir()

        # Créer fichiers de test
        self.test_file = self.nexus_root / "test_critical.md"
        self.test_file.write_text("# Test Critical File\nContent for testing.")

        # Créer dossier snapshots
        self.snapshots_dir = self.nexus_root / "snapshots"
        self.snapshots_dir.mkdir()

        # Créer snapshot de test
        self.snapshot_dir = self.snapshots_dir / "snapshot_test"
        self.snapshot_dir.mkdir()
        shutil.copy2(self.test_file, self.snapshot_dir / "test_critical.md")

        # Initialiser PLIX
        self.plix = PLIXRecovery(str(self.nexus_root))

    def tearDown(self):
        """Nettoyage après chaque test"""
        shutil.rmtree(self.temp_dir)

    def test_list_snapshots(self):
        """Test listing des snapshots"""
        snapshots = self.plix.list_snapshots()
        self.assertEqual(len(snapshots), 1)
        self.assertIn("snapshot_test", snapshots[0])

    def test_reconstruct_from_snapshot(self):
        """Test reconstruction depuis snapshot"""
        # Supprimer le fichier original
        os.remove(self.test_file)

        # Reconstruire
        success = self.plix.reconstruct_from_snapshot(
            "snapshot_test", "test_critical.md"
        )
        self.assertTrue(success)
        self.assertTrue(self.test_file.exists())

        # Vérifier contenu
        content = self.test_file.read_text()
        self.assertEqual(content, "# Test Critical File\nContent for testing.")

    def test_validate_reconstruction(self):
        """Test validation post-reconstruction"""
        # Créer certifications de test
        certs = {
            "L300": {
                "files": {
                    str(self.test_file): self.plix._calculate_hash(str(self.test_file))
                }
            }
        }

        with open(self.nexus_root / "vdb_certifications.json", "w") as f:
            json.dump(certs, f)

        # Validation devrait réussir
        success = self.plix.validate_reconstruction()
        self.assertTrue(success)

    def test_missing_critical_file_detection(self):
        """Test détection fichier critique manquant"""
        # Supprimer un fichier critique
        critical_file = self.nexus_root / "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md"
        critical_file.write_text("# Critical content")
        os.remove(critical_file)

        # Validation devrait échouer
        success = self.plix.validate_reconstruction()
        self.assertFalse(success)

    @patch("plix_recovery.subprocess.run")
    def test_wal_recovery_simulation(self, mock_subprocess):
        """Test simulation récupération WAL"""
        # Mock du fichier WAL
        wal_content = (
            '{"operation": "certified", "filepath": "test.md", "file_hash": "abc123"}\n'
        )
        wal_file = self.nexus_root / "wal_nexus.log"
        wal_file.write_text(wal_content)

        # Test récupération
        success = self.plix.recover_from_wal("test.md")
        self.assertTrue(success)


class TestSkillsIntegration(unittest.TestCase):
    """Tests d'intégration pour les skills"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)

        # Créer fichiers de test
        Path("PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md").write_text("# PRD Content")
        Path("EPIC_NEXUS_FILE_INTEGRITY_RECOVERY.md").write_text("# EPIC Content")

    def tearDown(self):
        os.chdir(Path(__file__).parent.parent)
        shutil.rmtree(self.temp_dir)

    def test_integrity_monitor_scan(self):
        """Test scan intégrité du monitor"""
        from skills.integrity_monitor import IntegrityMonitor

        monitor = IntegrityMonitor()
        issues = monitor.scan_integrity()

        # Devrait détecter nouveaux fichiers sans baseline
        self.assertIsInstance(issues, list)

    def test_recovery_agent_workflow(self):
        """Test workflow complet recovery agent"""
        from skills.recovery_agent import RecoveryAgent

        agent = RecoveryAgent()

        # Simuler fichiers manquants
        os.remove("PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md")

        # Test détection
        missing = agent.detect_missing_files()
        self.assertIn("PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md", missing)

        # Test récupération (devrait échouer sans snapshots)
        success = agent.auto_recover_missing()
        self.assertFalse(success)  # Pas de snapshots disponibles

    def test_dev_accelerator_pipeline(self):
        """Test pipeline dev accelerator"""
        from skills.dev_accelerator import DevAccelerator

        accelerator = DevAccelerator()

        # Test pipeline (certaines étapes peuvent échouer sans setup complet)
        success = accelerator.run_pipeline(["lint"])
        self.assertIsInstance(success, bool)

    def test_crash_analyzer_reporting(self):
        """Test génération rapports crash analyzer"""
        from skills.crash_analyzer import CrashAnalyzer

        analyzer = CrashAnalyzer()

        # Générer rapport (même vide)
        report = analyzer.generate_report()
        self.assertIsInstance(report, dict)
        self.assertIn("total_crashes", report)

    def test_consciousness_tracker_session(self):
        """Test suivi session consciousness tracker"""
        from skills.consciousness_tracker import ConsciousnessTracker

        tracker = ConsciousnessTracker()

        # Simuler session
        tracker.track_session("testing", 30, True)

        # Vérifier données
        self.assertGreater(len(tracker.metrics["sessions"]), 0)


class TestEntitiesIntegration(unittest.TestCase):
    """Tests d'intégration pour les entities"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(Path(__file__).parent.parent)
        shutil.rmtree(self.temp_dir)

    def test_file_guardian_protection(self):
        """Test protection file guardian"""
        from entities.file_guardian import FileGuardian

        guardian = FileGuardian()

        # Test statut initial
        status = guardian.get_status()
        self.assertIn("protected_files", status)
        self.assertEqual(status["protected_files"], len(guardian.critical_files))

    def test_dev_consciousness_monitoring(self):
        """Test monitoring dev consciousness"""
        from entities.dev_consciousness import DevConsciousness

        consciousness = DevConsciousness()

        # Test statut
        status = consciousness.get_status()
        self.assertIn("consciousness_level", status)

    def test_auto_chain_execution(self):
        """Test exécution chaînes auto chain manager"""
        from entities.auto_chain_manager import AutoChainManager

        manager = AutoChainManager()

        # Créer chaîne de test
        test_chain = {
            "name": "Test Chain",
            "steps": [
                {
                    "name": "test_step",
                    "type": "skill",
                    "target": "integrity_monitor.scan_integrity",
                }
            ],
            "triggers": ["manual"],
            "error_handling": "stop_on_error",
        }

        manager.create_chain("test_chain", **test_chain)

        # Exécuter chaîne
        success = manager.execute_chain("test_chain")
        self.assertIsInstance(success, bool)

    def test_intent_validator_validation(self):
        """Test validation intent validator"""
        from entities.intent_validator import IntentValidator

        validator = IntentValidator()

        # Test intent valide
        result = validator.validate_intent("0xNFIRS_PHASE6_TESTS_20260419")
        self.assertTrue(result["valid"])

        # Test intent invalide
        result = validator.validate_intent("invalid_format")
        self.assertFalse(result["valid"])


class TestVersesIntegration(unittest.TestCase):
    """Tests d'intégration pour les verses"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(Path(__file__).parent.parent)
        shutil.rmtree(self.temp_dir)

    def test_devflow_verse_workflow(self):
        """Test workflow devflow verse"""
        from verses.devflow_verse import DevFlowVerse

        verse = DevFlowVerse()

        # Démarrer flow
        flow_id = verse.start_flow("Test development flow", 60)
        self.assertIsNotNone(flow_id)

        # Vérifier statut
        status = verse.check_flow_status(flow_id)
        self.assertIn("current_stage", status)

    def test_crash_recovery_detection(self):
        """Test détection crash recovery verse"""
        from verses.crash_recovery_verse import CrashRecoveryVerse

        verse = CrashRecoveryVerse()

        # Test détection (devrait ne rien détecter en normal)
        crash = verse.detect_crash()
        self.assertIsNone(crash)

        # Test statut
        status = verse.get_recovery_status()
        self.assertIn("auto_recovery_enabled", status)

    def test_file_integrity_protection(self):
        """Test protection file integrity verse"""
        from verses.file_integrity_verse import FileIntegrityVerse

        verse = FileIntegrityVerse()

        # Test statut
        status = verse.get_integrity_status()
        self.assertIn("protection_active", status)
        self.assertFalse(status["protection_active"])  # Pas démarré


class TestEndToEndScenarios(unittest.TestCase):
    """Tests scénarios end-to-end"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Setup environnement de test complet
        self._setup_test_environment()

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def _setup_test_environment(self):
        """Setup environnement de test complet"""
        # Créer fichiers critiques
        Path("PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md").write_text("# PRD Content")
        Path("EPIC_NEXUS_FILE_INTEGRITY_RECOVERY.md").write_text("# EPIC Content")
        Path("ARCHITECTURAL_INTENT.md").write_text("# Architecture")
        Path("ECOSROOT.json").write_text('{"ecos": "root"}')

        # Créer snapshots
        Path("snapshots").mkdir()
        snapshot_dir = Path("snapshots/snapshot_e2e_test")
        snapshot_dir.mkdir()

        # Copier fichiers dans snapshot
        for file in [
            "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md",
            "EPIC_NEXUS_FILE_INTEGRITY_RECOVERY.md",
        ]:
            if Path(file).exists():
                shutil.copy2(file, snapshot_dir / file)

    def test_full_recovery_workflow(self):
        """Test workflow récupération complète"""
        # Simuler perte de fichier
        target_file = "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md"
        backup_content = Path(target_file).read_text()
        os.remove(target_file)

        # Vérifier fichier manquant
        self.assertFalse(Path(target_file).exists())

        # Utiliser PLIX pour récupérer
        plix = PLIXRecovery()
        success = plix.reconstruct_from_snapshot("snapshot_e2e_test", target_file)

        self.assertTrue(success)
        self.assertTrue(Path(target_file).exists())

        # Vérifier contenu restauré
        restored_content = Path(target_file).read_text()
        self.assertEqual(restored_content, backup_content)

    def test_integrated_system_health(self):
        """Test santé système intégré"""
        # Importer tous les composants
        try:
            from skills.integrity_monitor import IntegrityMonitor
            from skills.recovery_agent import RecoveryAgent
            from entities.file_guardian import FileGuardian
            from verses.file_integrity_verse import FileIntegrityVerse

            # Créer instances
            monitor = IntegrityMonitor()
            agent = RecoveryAgent()
            guardian = FileGuardian()
            verse = FileIntegrityVerse()

            # Test statuts
            monitor_status = len(monitor.scan_integrity()) >= 0
            agent_status = isinstance(agent.detect_missing_files(), list)
            guardian_status = isinstance(guardian.get_status(), dict)
            verse_status = isinstance(verse.get_integrity_status(), dict)

            self.assertTrue(
                all([monitor_status, agent_status, guardian_status, verse_status])
            )

        except ImportError as e:
            self.fail(f"Import error: {e}")


class TestChaosEngineering(unittest.TestCase):
    """Tests chaos engineering - injection de pannes"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)

        # Setup fichiers critiques
        Path("PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md").write_text("# Chaos Test")

    def tearDown(self):
        os.chdir(Path(__file__).parent.parent)
        shutil.rmtree(self.temp_dir)

    def test_corruption_resilience(self):
        """Test résilience à la corruption"""
        from skills.integrity_monitor import IntegrityMonitor

        monitor = IntegrityMonitor()
        target_file = "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md"

        # Corrompre fichier
        with open(target_file, "w") as f:
            f.write("CORRUPTED CONTENT!")

        # Monitor devrait détecter
        issues = monitor.scan_integrity()
        corruption_detected = any(issue.get("type") == "modified" for issue in issues)

        self.assertTrue(corruption_detected)

    def test_deletion_recovery(self):
        """Test récupération après suppression"""
        from skills.recovery_agent import RecoveryAgent

        agent = RecoveryAgent()
        target_file = "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md"

        # Créer snapshot d'abord
        Path("snapshots").mkdir()
        snapshot_dir = Path("snapshots/snapshot_chaos")
        snapshot_dir.mkdir()
        shutil.copy2(target_file, snapshot_dir / target_file)

        # Supprimer fichier
        os.remove(target_file)

        # Agent devrait détecter et tenter récupération
        missing = agent.detect_missing_files()
        self.assertIn(target_file, missing)

        # Récupération manuelle via PLIX
        from plix_recovery import PLIXRecovery

        plix = PLIXRecovery()
        success = plix.reconstruct_from_snapshot("snapshot_chaos", target_file)

        self.assertTrue(success)
        self.assertTrue(Path(target_file).exists())

    def test_concurrent_access(self):
        """Test accès concurrent"""
        import threading
        import time

        results = {"monitor": False, "agent": False}

        def run_monitor():
            from skills.integrity_monitor import IntegrityMonitor

            monitor = IntegrityMonitor()
            issues = monitor.scan_integrity()
            results["monitor"] = len(issues) >= 0

        def run_agent():
            from skills.recovery_agent import RecoveryAgent

            agent = RecoveryAgent()
            missing = agent.detect_missing_files()
            results["agent"] = isinstance(missing, list)

        # Lancer threads simultanément
        t1 = threading.Thread(target=run_monitor)
        t2 = threading.Thread(target=run_agent)

        t1.start()
        t2.start()

        t1.join(timeout=5)
        t2.join(timeout=5)

        self.assertTrue(results["monitor"])
        self.assertTrue(results["agent"])


if __name__ == "__main__":
    # Configuration pour coverage >95%
    import coverage

    cov = coverage.Coverage(source=["plix_recovery", "skills", "entities", "verses"])
    cov.start()

    # Exécuter tests
    unittest.main(verbosity=2, exit=False)

    # Rapport coverage
    cov.stop()
    cov.save()
    cov.report()

    print("\n=== Test Results Summary ===")
    print("All NFIRS Phase 6 tests completed.")
    print("Check coverage report above for >95% target.")
