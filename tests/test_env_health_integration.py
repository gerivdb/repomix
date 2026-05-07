#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 TESTS D'INTÉGRATION - ENVIRONNEMENT HEALTH
Tests complets pour EPIC-1220 EnvHealthEngine
"""

import unittest
import tempfile
import json
import os
import time
import psutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from engines.env_health_engine import EnvHealthEngine, HealthMetric


class TestEnvHealthIntegration(unittest.TestCase):
    """Tests d'intégration pour EnvHealthEngine"""

    def setUp(self):
        self.engine = EnvHealthEngine()

    def test_full_health_check_workflow(self):
        """Test workflow complet de vérification santé"""
        # Génération rapport
        report = self.engine.generate_health_report()

        # Vérifications structure
        self.assertIsNotNone(report.timestamp)
        self.assertIn(report.overall_status, ['healthy', 'degraded', 'critical'])

        # Vérification présence de toutes les catégories
        categories = ['system_health', 'network_health', 'dependency_health',
                     'config_health', 'security_health']

        for category in categories:
            self.assertTrue(hasattr(report, category))
            category_data = getattr(report, category)
            self.assertIsInstance(category_data, dict)

        # Vérification alertes et recommandations
        self.assertIsInstance(report.alerts, list)
        self.assertIsInstance(report.recommendations, list)

    def test_continuous_monitoring_simulation(self):
        """Test simulation surveillance continue"""
        reports = []

        # Simulation de quelques itérations
        for i in range(3):
            report = self.engine.generate_health_report()
            reports.append(report)
            time.sleep(0.1)  # Petit délai pour simuler le temps

        # Vérification cohérence des rapports
        self.assertEqual(len(reports), 3)

        for report in reports:
            self.assertIsNotNone(report.overall_status)
            self.assertGreater(len(report.system_health), 0)

        # Vérification timestamps croissants
        timestamps = [r.timestamp for r in reports]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_report_serialization(self):
        """Test sérialisation/désérialisation du rapport"""
        # Génération rapport
        original_report = self.engine.generate_health_report()

        # Sauvegarde
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            self.engine.save_report(original_report, temp_file)

            # Vérification fichier créé
            self.assertTrue(Path(temp_file).exists())

            # Lecture et désérialisation
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Vérification structure JSON
            required_keys = ['timestamp', 'overall_status', 'system_health',
                           'network_health', 'dependency_health', 'alerts', 'recommendations']
            for key in required_keys:
                self.assertIn(key, data)

            # Vérification statut
            self.assertIn(data['overall_status'], ['healthy', 'degraded', 'critical'])

        finally:
            # Nettoyage
            Path(temp_file).unlink(missing_ok=True)

    def test_threshold_based_alerts(self):
        """Test génération d'alertes basée sur seuils"""
        # Test avec métriques simulées critiques
        with patch.object(self.engine, '_get_system_health') as mock_system:
            # Simulation métriques critiques
            mock_system.return_value = {
                'cpu_usage': HealthMetric('CPU Usage', 98.0, '%', 'critical', 80.0, 95.0),
                'memory_usage': HealthMetric('Memory Usage', 97.0, '%', 'critical', 85.0, 95.0),
                'disk_usage': HealthMetric('Disk Usage', 96.0, '%', 'critical', 85.0, 95.0)
            }

            report = self.engine.generate_health_report()

            # Vérification statut critique
            self.assertEqual(report.overall_status, 'critical')

            # Vérification alertes générées
            self.assertGreater(len(report.alerts), 0)

            # Vérification recommandations
            self.assertGreater(len(report.recommendations), 0)

            # Vérification présence recommandations CPU/mémoire/disque
            rec_text = ' '.join(report.recommendations).lower()
            self.assertIn('cpu', rec_text)
            self.assertIn('mémoire', rec_text)
            self.assertIn('disque', rec_text)

    def test_network_connectivity_detection(self):
        """Test détection connectivité réseau"""
        metrics = self.engine._get_network_health()

        connectivity_metric = metrics['connectivity']
        self.assertIsInstance(connectivity_metric.value, bool)
        self.assertIn(connectivity_metric.status, ['healthy', 'critical'])

        latency_metric = metrics['latency']
        self.assertIsInstance(latency_metric.value, (int, float))
        self.assertEqual(latency_metric.unit, 'ms')

    def test_dependency_validation(self):
        """Test validation dépendances"""
        metrics = self.engine._get_dependency_health()

        # Python dependencies toujours présent
        self.assertIn('python_dependencies', metrics)
        python_deps = metrics['python_dependencies']
        self.assertIsInstance(python_deps.value, bool)

        # Node.js dependencies seulement si package.json existe
        has_package_json = Path('package.json').exists()
        has_npm_deps = 'npm_dependencies' in metrics

        if has_package_json:
            self.assertTrue(has_npm_deps)
        # Note: si pas de package.json, npm_dependencies peut ne pas être présent

    def test_config_file_validation(self):
        """Test validation fichiers de configuration"""
        metrics = self.engine._get_config_health()

        config_files_metric = metrics['config_files']
        self.assertIsInstance(config_files_metric.value, bool)

        env_vars_metric = metrics['environment_variables']
        self.assertIsInstance(env_vars_metric.value, bool)

    def test_security_permissions_check(self):
        """Test vérification permissions de sécurité"""
        metrics = self.engine._get_security_health()

        # Devrait avoir au moins file_permissions
        self.assertGreater(len(metrics), 0)

        if 'file_permissions' in metrics:
            perm_metric = metrics['file_permissions']
            self.assertIsInstance(perm_metric.value, bool)

    def test_performance_under_load(self):
        """Test performance sous charge"""
        import threading

        results = []
        errors = []

        def health_check_worker():
            try:
                start_time = time.time()
                report = self.engine.generate_health_report()
                duration = time.time() - start_time

                results.append({
                    'duration': duration,
                    'status': report.overall_status,
                    'metrics_count': sum(len(cat) for cat in [
                        report.system_health, report.network_health,
                        report.dependency_health, report.config_health,
                        report.security_health
                    ])
                })
            except Exception as e:
                errors.append(str(e))

        # Exécution parallèle
        threads = []
        num_threads = 3

        for i in range(num_threads):
            thread = threading.Thread(target=health_check_worker)
            threads.append(thread)
            thread.start()

        # Attente fin
        for thread in threads:
            thread.join(timeout=30)

        # Vérifications
        self.assertEqual(len(results), num_threads)
        self.assertEqual(len(errors), 0)

        for result in results:
            # Chaque check devrait prendre moins de 5 secondes
            self.assertLess(result['duration'], 5.0)
            # Devrait avoir des métriques
            self.assertGreater(result['metrics_count'], 0)

    def test_error_handling(self):
        """Test gestion d'erreurs"""
        # Test avec fichier de config corrompu
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / '.env.health.json'

            # Configuration JSON invalide
            config_file.write_text('{"invalid": json}')

            # Engine avec config corrompue
            engine = EnvHealthEngine(config_path=str(config_file))

            # Devrait quand même fonctionner avec config par défaut
            report = engine.generate_health_report()
            self.assertIsNotNone(report.overall_status)

    def test_real_system_interaction(self):
        """Test interaction avec le système réel"""
        # Vérification que les métriques correspondent au système réel
        report = self.engine.generate_health_report()

        # CPU usage devrait être entre 0 et 100
        cpu_metric = report.system_health.get('cpu_usage')
        if cpu_metric:
            self.assertGreaterEqual(cpu_metric.value, 0.0)
            self.assertLessEqual(cpu_metric.value, 100.0)

        # Memory usage devrait être entre 0 et 100
        mem_metric = report.system_health.get('memory_usage')
        if mem_metric:
            self.assertGreaterEqual(mem_metric.value, 0.0)
            self.assertLessEqual(mem_metric.value, 100.0)

        # Disk usage devrait être entre 0 et 100
        disk_metric = report.system_health.get('disk_usage')
        if disk_metric:
            self.assertGreaterEqual(disk_metric.value, 0.0)
            self.assertLessEqual(disk_metric.value, 100.0)

    def test_config_persistence(self):
        """Test persistance de la configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / 'test_config.json'

            # Configuration personnalisée
            custom_config = {
                "cpu_threshold_warning": 70.0,
                "cpu_threshold_critical": 90.0,
                "custom_param": "test_value"
            }

            with open(config_file, 'w') as f:
                json.dump(custom_config, f)

            # Engine avec config personnalisée
            engine = EnvHealthEngine(config_path=str(config_file))

            # Vérification chargement config
            self.assertEqual(engine.config['cpu_threshold_warning'], 70.0)
            self.assertEqual(engine.config['cpu_threshold_critical'], 90.0)
            self.assertEqual(engine.config['custom_param'], 'test_value')

            # Config par défaut toujours présente
            self.assertIn('memory_threshold_warning', engine.config)


if __name__ == '__main__':
    # Configuration pour tests d'intégration
    logging.basicConfig(level=logging.ERROR)  # Très silencieux pour tests

    # Exécution tests
    unittest.main(verbosity=2)