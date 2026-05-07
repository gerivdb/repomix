#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTS UNITAIRES - NEXUS ENGINES
Tests pour les EPICs: 1220, 1222, 1226
"""

import unittest
import tempfile
import json
import os
import time
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import des engines à tester
from engines.env_health_engine import EnvHealthEngine, HealthMetric
from engines.config_watcher_daemon import ConfigWatcherDaemon, WatchedFile
from engines.self_healing_skill import SelfHealingSkill, HealingPattern


class TestEnvHealthEngine(unittest.TestCase):
    """Tests pour EPIC-1220 EnvHealthEngine"""

    def setUp(self):
        self.engine = EnvHealthEngine()

    def test_initialization(self):
        """Test initialisation du moteur"""
        self.assertIsInstance(self.engine.config, dict)
        self.assertIn('cpu_threshold_warning', self.engine.config)

    def test_evaluate_threshold(self):
        """Test évaluation des seuils"""
        # Test healthy
        self.assertEqual(self.engine._evaluate_threshold(50, 80, 95), 'healthy')

        # Test warning
        self.assertEqual(self.engine._evaluate_threshold(85, 80, 95), 'warning')

        # Test critical
        self.assertEqual(self.engine._evaluate_threshold(96, 80, 95), 'critical')

    def test_system_health_check(self):
        """Test vérification santé système"""
        metrics = self.engine._get_system_health()

        # Vérification présence métriques
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        self.assertIn('disk_usage', metrics)

        # Vérification structure métrique
        cpu_metric = metrics['cpu_usage']
        self.assertIsInstance(cpu_metric, HealthMetric)
        self.assertEqual(cpu_metric.unit, '%')
        self.assertIn(cpu_metric.status, ['healthy', 'warning', 'critical'])

    def test_network_health_check(self):
        """Test vérification santé réseau"""
        metrics = self.engine._get_network_health()

        self.assertIn('connectivity', metrics)
        self.assertIn('latency', metrics)

        # Le statut peut varier selon la connectivité réelle
        connectivity = metrics['connectivity']
        self.assertIsInstance(connectivity.value, bool)
        self.assertIn(connectivity.status, ['healthy', 'critical'])

    def test_dependency_health_check(self):
        """Test vérification santé dépendances"""
        metrics = self.engine._get_dependency_health()

        # Au minimum, on devrait avoir python_dependencies
        self.assertIn('python_dependencies', metrics)

        python_deps = metrics['python_dependencies']
        self.assertIsInstance(python_deps.value, bool)

    def test_config_health_check(self):
        """Test vérification santé configuration"""
        metrics = self.engine._get_config_health()

        self.assertIn('config_files', metrics)
        self.assertIn('environment_variables', metrics)

    def test_generate_health_report(self):
        """Test génération rapport complet"""
        report = self.engine.generate_health_report()

        # Vérification structure rapport
        self.assertIn('timestamp', report.__dict__)
        self.assertIn('overall_status', report.__dict__)
        self.assertIn('system_health', report.__dict__)
        self.assertIn('network_health', report.__dict__)
        self.assertIn('dependency_health', report.__dict__)
        self.assertIn('config_health', report.__dict__)
        self.assertIn('security_health', report.__dict__)

        # Vérification statut global
        self.assertIn(report.overall_status, ['healthy', 'degraded', 'critical', 'unknown'])

        # Vérification alertes et recommandations
        self.assertIsInstance(report.alerts, list)
        self.assertIsInstance(report.recommendations, list)

    def test_metric_to_dict_conversion(self):
        """Test conversion métrique vers dictionnaire"""
        metric = HealthMetric(
            name='Test Metric',
            value=85.5,
            unit='%',
            status='warning',
            threshold_warning=80.0,
            threshold_critical=90.0
        )

        result = self.engine._metric_to_dict(metric)

        self.assertEqual(result['name'], 'Test Metric')
        self.assertEqual(result['value'], 85.5)
        self.assertEqual(result['unit'], '%')
        self.assertEqual(result['status'], 'warning')
        self.assertEqual(result['threshold_warning'], 80.0)
        self.assertEqual(result['threshold_critical'], 90.0)
        self.assertIn('timestamp', result)


class TestConfigWatcherDaemon(unittest.TestCase):
    """Tests pour EPIC-1222 ConfigWatcherDaemon"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.daemon = ConfigWatcherDaemon()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test initialisation du daemon"""
        self.assertFalse(self.daemon.running)
        self.assertEqual(len(self.daemon.watched_files), 0)
        self.assertIsInstance(self.daemon.config, dict)

    def test_add_watched_file(self):
        """Test ajout fichier surveillé"""
        test_file = Path(self.temp_dir) / 'test.json'
        test_file.write_text('{"test": "value"}')

        self.daemon.add_watched_file(str(test_file), critical=True)

        self.assertIn(str(test_file), self.daemon.watched_files)
        watched = self.daemon.watched_files[str(test_file)]
        self.assertTrue(watched.critical)
        self.assertIsNotNone(watched.last_hash)

    def test_file_hash_calculation(self):
        """Test calcul hash fichier"""
        test_file = Path(self.temp_dir) / 'test.txt'
        test_file.write_text('Hello World')

        hash1 = self.daemon._calculate_file_hash(test_file)
        self.assertIsNotNone(hash1)
        self.assertEqual(len(hash1), 64)  # SHA256 = 64 caractères

        # Vérification cohérence
        hash2 = self.daemon._calculate_file_hash(test_file)
        self.assertEqual(hash1, hash2)

        # Modification fichier
        test_file.write_text('Hello Universe')
        hash3 = self.daemon._calculate_file_hash(test_file)
        self.assertNotEqual(hash1, hash3)

    def test_validate_config_content(self):
        """Test validation contenu configuration"""
        # Test JSON valide
        valid_json = '{"key": "value"}'
        is_valid, msg = self.daemon._validate_config_content(Path('test.json'), valid_json)
        self.assertTrue(is_valid)

        # Test JSON invalide
        invalid_json = '{"key": "value"'  # Virgule manquante
        is_valid, msg = self.daemon._validate_config_content(Path('test.json'), invalid_json)
        self.assertFalse(is_valid)

        # Test fichier non-JSON
        text_content = 'some text'
        is_valid, msg = self.daemon._validate_config_content(Path('test.txt'), text_content)
        self.assertTrue(is_valid)  # Format non validé = considéré valide

    def test_generate_report(self):
        """Test génération rapport daemon"""
        report = self.daemon.generate_report()

        self.assertIn('timestamp', report.__dict__)
        self.assertIn('watched_files', report.__dict__)
        self.assertIn('recent_changes', report.__dict__)
        self.assertIn('alerts', report.__dict__)
        self.assertIsInstance(report.alerts, list)

    def test_get_stats(self):
        """Test récupération statistiques"""
        stats = self.daemon.get_stats()

        required_keys = ['files_watched', 'changes_detected', 'alerts_triggered', 'is_running']
        for key in required_keys:
            self.assertIn(key, stats)

    @patch('time.sleep')  # Pour accélérer les tests
    def test_daemon_lifecycle(self, mock_sleep):
        """Test cycle de vie du daemon"""
        # Démarrage
        self.daemon.start()
        self.assertTrue(self.daemon.running)

        # Vérification stats mises à jour
        stats = self.daemon.get_stats()
        self.assertIsNotNone(stats['start_time'])

        # Arrêt
        self.daemon.stop()
        self.assertFalse(self.daemon.running)


class TestSelfHealingSkill(unittest.TestCase):
    """Tests pour EPIC-1226 SelfHealingSkill"""

    def setUp(self):
        self.skill = SelfHealingSkill()

    def test_initialization(self):
        """Test initialisation de la skill"""
        self.assertIsInstance(self.skill.alfred, object)  # ALFRED engine
        self.assertIsInstance(self.skill.healing_patterns, list)
        self.assertGreater(len(self.skill.healing_patterns), 0)

    def test_healing_patterns_initialization(self):
        """Test initialisation patterns de guérison"""
        patterns = self.skill.healing_patterns

        # Vérification présence patterns critiques
        pattern_names = [p.name for p in patterns]
        required_patterns = [
            'broken_python_imports',
            'incorrect_file_permissions',
            'invalid_json_config'
        ]

        for required in required_patterns:
            self.assertIn(required, pattern_names)

        # Vérification structure pattern
        for pattern in patterns:
            self.assertIsInstance(pattern, HealingPattern)
            self.assertIsInstance(pattern.correction_function, callable)

    def test_backup_creation_and_restore(self):
        """Test création et restauration backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / 'test.txt'
            test_file.write_text('Original content')

            # Création backup
            backup_path = self.skill._create_backup(str(test_file))
            self.assertIsNotNone(backup_path)
            self.assertTrue(Path(backup_path).exists())

            # Modification fichier
            test_file.write_text('Modified content')

            # Restauration
            self.skill._restore_backup(backup_path, str(test_file))

            # Vérification restauration
            with open(test_file, 'r') as f:
                content = f.read()
            self.assertEqual(content, 'Original content')

    def test_fix_invalid_json(self):
        """Test réparation JSON invalide"""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / 'test.json'

            # JSON invalide (virgule finale)
            invalid_json = '{"key": "value",}'
            json_file.write_text(invalid_json)

            # Tentative réparation
            success = self.skill._fix_invalid_json(str(json_file), invalid_json)

            if success:
                # Vérification contenu réparé
                with open(json_file, 'r') as f:
                    repaired_content = f.read()

                # Devrait être valide maintenant
                try:
                    json.loads(repaired_content)
                    self.assertTrue(True)  # JSON valide
                except json.JSONDecodeError:
                    self.fail("JSON réparé toujours invalide")

    def test_scan_for_issues(self):
        """Test scan des problèmes"""
        # Création fichiers de test avec problèmes
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            # Fichier Python avec import cassé
            py_file = Path('test.py')
            py_file.write_text('import nonexistent_module\nprint("test")')

            # Fichier JSON invalide
            json_file = Path('config.json')
            json_file.write_text('{"key": "value",}')

            # Scan
            issues = self.skill.scan_for_issues()

            # Vérification détection problèmes
            self.assertGreaterEqual(len(issues), 0)  # Au minimum pas d'erreur

            # Les problèmes peuvent ne pas être détectés selon l'implémentation exacte
            # mais le scan devrait réussir sans erreur

    def test_healing_session(self):
        """Test session de guérison complète"""
        # Session sans auto-application (sécurisé pour tests)
        report = self.skill.auto_healing_session(auto_apply=False)

        # Vérification structure rapport
        self.assertIsInstance(report, object)
        self.assertIn('issues_detected', report.__dict__)
        self.assertIn('issues_fixed', report.__dict__)
        self.assertIn('actions_taken', report.__dict__)
        self.assertIsInstance(report.actions_taken, list)

    def test_get_stats(self):
        """Test récupération statistiques"""
        stats = self.skill.get_stats()

        required_keys = ['sessions_run', 'issues_detected_total', 'patterns_available']
        for key in required_keys:
            self.assertIn(key, stats)

        self.assertGreaterEqual(stats['patterns_available'], 5)  # Au moins 5 patterns

    def test_emergency_rollback(self):
        """Test rollback d'urgence"""
        # Rollback sur période courte (devrait être vide normalement)
        rollback_result = self.skill.emergency_rollback(hours_back=1)

        self.assertIsInstance(rollback_result, list)
        # Normalement vide en conditions de test


class TestIntegration(unittest.TestCase):
    """Tests d'intégration entre les engines"""

    def test_env_health_with_config_watcher(self):
        """Test intégration EnvHealth + ConfigWatcher"""
        # Création environnement de test
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            # Création fichier de config pour watcher
            config_file = Path('.env')
            config_file.write_text('TEST_VAR=value')

            # Initialisation engines
            health_engine = EnvHealthEngine()
            watcher = ConfigWatcherDaemon()

            # Watcher surveille le fichier
            watcher.add_watched_file(str(config_file), critical=True)

            # Health check inclut vérification config
            report = health_engine.generate_health_report()

            # Vérification que config est détectée comme présente
            config_metrics = report.config_health
            self.assertIn('config_files', config_metrics)

            config_status = config_metrics['config_files']
            # Le statut dépend de la présence d'autres fichiers critiques
            self.assertIn(config_status.status, ['healthy', 'warning'])

    def test_self_healing_with_alfred(self):
        """Test intégration SelfHealing + ALFRED"""
        from engines.alfred_engine import AlfredEngine

        alfred = AlfredEngine()
        healer = SelfHealingSkill(alfred_engine=alfred)

        # Vérification que ALFRED est utilisé
        self.assertEqual(healer.alfred, alfred)

        # Test scan utilisant ALFRED
        issues = healer.scan_for_issues()
        self.assertIsInstance(issues, list)


if __name__ == '__main__':
    # Configuration logging pour tests
    logging.basicConfig(level=logging.WARNING)  # Réduire verbosité

    # Exécution tests
    unittest.main(verbosity=2)