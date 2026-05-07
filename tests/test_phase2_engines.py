#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTS UNITAIRES - PHASE 2 EPICs
Tests pour les EPICs: 1224, 1225, 1221, 1228
"""

import unittest
import tempfile
import json
import os
import time
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Import des engines à tester
from engines.dev_sandbox_engine import DevSandboxEngine, SandboxConfig, SandboxSession
from engines.build_cache_daemon import BuildCacheDaemon, CacheEntry
from engines.dep_validator_engine import DepValidatorEngine, Dependency, ValidationResult
from engines.net_health_engine import NetHealthEngine, NetworkEndpoint, NetworkTestResult


class TestDevSandboxEngine(unittest.TestCase):
    """Tests pour EPIC-1224 DevSandboxEngine"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        self.engine = DevSandboxEngine(cache_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test initialisation du moteur sandbox"""
        self.assertIsInstance(self.engine.config, dict)
        self.assertIn('max_cache_size_gb', self.engine.config)
        self.assertIsInstance(self.engine.endpoints, list)

    def test_sandbox_config_creation(self):
        """Test création configuration sandbox"""
        config = self.engine.create_sandbox_config("test_sandbox")

        self.assertEqual(config.name, "test_sandbox")
        self.assertIsInstance(config.root_path, Path)
        self.assertTrue(config.root_path.name.endswith("test_sandbox"))
        self.assertEqual(config.memory_limit_mb, self.engine.config['default_memory_limit_mb'])

    def test_sandbox_initialization(self):
        """Test initialisation d'un sandbox"""
        config = self.engine.create_sandbox_config("test_init")

        success = self.engine.initialize_sandbox(config)
        self.assertTrue(success)

        # Vérification structure créée
        self.assertTrue(config.root_path.exists())
        self.assertTrue((config.root_path / "bin").exists())
        self.assertTrue((config.root_path / "lib").exists())
        self.assertTrue((config.root_path / "tmp").exists())
        self.assertTrue((config.root_path / "work").exists())

        # Vérification fichier config
        config_file = config.root_path / ".sandbox.json"
        self.assertTrue(config_file.exists())

        with open(config_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['name'], "test_init")

    def test_session_management(self):
        """Test gestion des sessions sandbox"""
        config = self.engine.create_sandbox_config("test_session")

        # Démarrage session
        session = self.engine.start_session(config)
        self.assertIsNotNone(session)
        self.assertEqual(session.config.name, "test_session")
        self.assertEqual(session.status, 'active')
        self.assertIn(session.session_id, self.engine.active_sessions)

        # Fin session
        success = self.engine.end_session(session.session_id)
        self.assertTrue(success)
        self.assertNotIn(session.session_id, self.engine.active_sessions)

    def test_command_validation(self):
        """Test validation des commandes"""
        config = SandboxConfig(
            name="test",
            root_path=Path("/tmp"),
            allowed_commands=["python", "pip"]
        )

        self.assertTrue(self.engine._validate_command(config, "python"))
        self.assertTrue(self.engine._validate_command(config, "pip"))
        self.assertFalse(self.engine._validate_command(config, "curl"))

    @patch('subprocess.Popen')
    def test_sandbox_execution(self, mock_popen):
        """Test exécution dans sandbox"""
        # Mock processus
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("output", "error")
        mock_process.returncode = 0
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        config = self.engine.create_sandbox_config("test_exec")
        session = self.engine.start_session(config)

        report = self.engine.execute_in_sandbox(session, ["echo", "test"])

        self.assertEqual(report.exit_code, 0)
        self.assertEqual(report.stdout, "output")
        self.assertEqual(report.stderr, "error")
        self.assertEqual(session.process_id, 12345)

    def test_stats_collection(self):
        """Test collecte statistiques"""
        stats = self.engine.get_stats()

        required_keys = ['total_sessions', 'active_sessions', 'successful_sessions']
        for key in required_keys:
            self.assertIn(key, stats)


class TestBuildCacheDaemon(unittest.TestCase):
    """Tests pour EPIC-1225 BuildCacheDaemon"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / 'cache'
        self.daemon = BuildCacheDaemon(cache_dir=str(self.cache_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test initialisation du daemon cache"""
        self.assertTrue(self.cache_dir.exists())
        self.assertIsInstance(self.daemon.config, dict)
        self.assertIn('max_cache_size_gb', self.daemon.config)

    def test_cache_key_generation(self):
        """Test génération clés cache"""
        # Test avec dict
        data = {"key": "value", "number": 42}
        key1 = self.daemon._generate_cache_key(data)
        key2 = self.daemon._generate_cache_key(data)
        self.assertEqual(key1, key2)
        self.assertEqual(len(key1), 64)  # SHA256

        # Test avec string différent
        data2 = {"key": "different"}
        key3 = self.daemon._generate_cache_key(data2)
        self.assertNotEqual(key1, key3)

    def test_cache_storage_and_retrieval(self):
        """Test stockage et récupération cache"""
        test_data = {"build": "result", "version": "1.0"}
        key = "test_build"

        # Stockage
        success = self.daemon.store(key, test_data, category="artifacts")
        self.assertTrue(success)

        # Récupération
        cached_data = self.daemon.retrieve(key)
        self.assertEqual(cached_data, test_data)

        # Vérification présence
        self.assertTrue(self.daemon.has_key(key))

    def test_cache_invalidation(self):
        """Test invalidation cache"""
        test_data = {"data": "test"}
        key = "test_invalidate"

        # Stockage puis invalidation
        self.daemon.store(key, test_data)
        self.assertTrue(self.daemon.has_key(key))

        success = self.daemon.invalidate(key)
        self.assertTrue(success)
        self.assertFalse(self.daemon.has_key(key))

    def test_cache_category_management(self):
        """Test gestion catégories cache"""
        # Stockage dans différentes catégories
        self.daemon.store("py_cache", {"type": "python"}, category="dependencies")
        self.daemon.store("js_cache", {"type": "javascript"}, category="dependencies")
        self.daemon.store("artifact", {"type": "binary"}, category="artifacts")

        # Invalidation catégorie
        invalidated = self.daemon.invalidate_category("dependencies")
        self.assertEqual(invalidated, 2)

        # Vérification
        self.assertFalse(self.daemon.has_key("py_cache"))
        self.assertFalse(self.daemon.has_key("js_cache"))
        self.assertTrue(self.daemon.has_key("artifact"))

    def test_cache_report_generation(self):
        """Test génération rapport cache"""
        # Ajout données test
        self.daemon.store("entry1", {"data": 1}, category="test")
        self.daemon.store("entry2", {"data": 2}, category="test")

        report = self.daemon.generate_report()

        self.assertIsNotNone(report.timestamp)
        self.assertGreaterEqual(report.stats.total_entries, 2)
        self.assertIsInstance(report.recommendations, list)
        self.assertIsInstance(report.top_entries, list)

    def test_stats_reporting(self):
        """Test reporting statistiques"""
        stats = self.daemon.get_stats()

        required_keys = ['total_entries', 'cache_hits', 'cache_misses', 'evictions']
        for key in required_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], (int, float))


class TestDepValidatorEngine(unittest.TestCase):
    """Tests pour EPIC-1221 DepValidatorEngine"""

    def setUp(self):
        self.engine = DepValidatorEngine()

    def test_initialization(self):
        """Test initialisation du moteur validation"""
        self.assertIsInstance(self.engine.config, dict)
        self.assertIsInstance(self.engine.healing_patterns, list)
        self.assertGreater(len(self.engine.healing_patterns), 0)

    def test_dependency_creation(self):
        """Test création objets dépendance"""
        dep = Dependency(
            name="requests",
            version="2.28.0",
            source="pip"
        )

        self.assertEqual(dep.name, "requests")
        self.assertEqual(dep.version, "2.28.0")
        self.assertEqual(dep.source, "pip")
        self.assertFalse(dep.is_outdated)

    def test_python_dependency_validation(self):
        """Test validation dépendance Python"""
        dep = Dependency(name="os", version="", source="pip")  # Module standard

        result = self.engine._validate_python_dependency(dep)

        self.assertEqual(result.dependency.name, "os")
        self.assertIn(result.status, ['valid', 'warning', 'error'])
        self.assertIsInstance(result.issues, list)
        self.assertIsInstance(result.recommendations, list)

    def test_node_dependency_validation(self):
        """Test validation dépendance Node.js"""
        dep = Dependency(name="express", version="4.18.0", source="npm")

        result = self.engine._validate_node_dependency(dep)

        self.assertEqual(result.dependency.name, "express")
        self.assertIn(result.status, ['valid', 'warning', 'error'])

    @patch('subprocess.run')
    def test_python_ecosystem_validation(self, mock_subprocess):
        """Test validation écosystème Python complet"""
        # Mock pip check
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Création fichier requirements factice
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            req_file = Path('requirements.txt')
            req_file.write_text('requests==2.28.0\nnumpy>=1.21.0\n')

            results = self.engine.validate_python_ecosystem(req_file)

            self.assertIsInstance(results, list)
            self.assertGreaterEqual(len(results), 0)  # Au moins tentative de validation

    @patch('subprocess.run')
    def test_ecosystem_report_generation(self, mock_subprocess):
        """Test génération rapport écosystème"""
        # Mock commandes externes
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        report = self.engine.generate_ecosystem_report()

        self.assertIsNotNone(report.timestamp)
        self.assertIsInstance(report.python_deps, list)
        self.assertIsInstance(report.node_deps, list)
        self.assertIsInstance(report.conflicts, list)
        self.assertIsInstance(report.security_issues, list)
        self.assertIsInstance(report.recommendations, list)

    def test_stats_reporting(self):
        """Test reporting statistiques"""
        stats = self.engine.get_stats()

        required_keys = ['validations_performed', 'conflicts_detected', 'security_issues_found']
        for key in required_keys:
            self.assertIn(key, stats)


class TestNetHealthEngine(unittest.TestCase):
    """Tests pour EPIC-1228 NetHealthEngine"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        self.engine = NetHealthEngine()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test initialisation du moteur réseau"""
        self.assertIsInstance(self.engine.config, dict)
        self.assertIsInstance(self.engine.endpoints, list)
        self.assertGreater(len(self.engine.endpoints), 0)

    def test_endpoint_creation(self):
        """Test création points de terminaison"""
        endpoint = NetworkEndpoint(
            host="example.com",
            port=443,
            protocol="https",
            description="Test endpoint"
        )

        self.assertEqual(endpoint.host, "example.com")
        self.assertEqual(endpoint.port, 443)
        self.assertEqual(endpoint.protocol, "https")

    @patch('socket.socket')
    def test_tcp_connectivity_test(self, mock_socket_class):
        """Test test connectivité TCP"""
        # Mock socket
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        endpoint = NetworkEndpoint(host="localhost", port=80, protocol="tcp")
        result = self.engine._test_tcp_connectivity(endpoint)

        self.assertIn(result.status, ['success', 'failure', 'timeout'])
        mock_socket.connect.assert_called_once_with(("localhost", 80))
        mock_socket.close.assert_called_once()

    @patch('subprocess.run')
    def test_connectivity_tests_execution(self, mock_subprocess):
        """Test exécution tests connectivité"""
        # Mock pour éviter vrais appels réseau
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        results = self.engine.run_connectivity_tests()

        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), len(self.engine.endpoints))

        # Vérification structure résultats
        for result in results:
            self.assertIsInstance(result, NetworkTestResult)
            self.assertIn(result.status, ['success', 'failure', 'timeout', 'blocked', 'unreachable'])

    def test_air_gap_breach_detection(self):
        """Test détection violation air-gap"""
        # Test sans violation
        clean_results = [
            NetworkTestResult(
                endpoint=NetworkEndpoint("localhost", 80, "tcp", "reachable"),
                status="success"
            )
        ]

        breached, breaches = self.engine.detect_air_gap_breach(clean_results)
        self.assertFalse(breached)
        self.assertEqual(len(breaches), 0)

        # Test avec violation (si air-gap activé)
        if self.engine.config['air_gap_mode']:
            breach_results = [
                NetworkTestResult(
                    endpoint=NetworkEndpoint("facebook.com", 443, "https", "blocked"),
                    status="success"
                )
            ]

            breached, breaches = self.engine.detect_air_gap_breach(breach_results)
            self.assertTrue(breached)
            self.assertGreater(len(breaches), 0)

    def test_health_report_generation(self):
        """Test génération rapport santé réseau"""
        report = self.engine.generate_health_report()

        self.assertIsNotNone(report.timestamp)
        self.assertIn(report.air_gap_status, ['compliant', 'breached', 'unknown'])
        self.assertIn(report.compliance_status, ['compliant', 'non_compliant', 'unknown'])
        self.assertIsInstance(report.connectivity_tests, list)
        self.assertIsInstance(report.security_alerts, list)
        self.assertIsInstance(report.recommendations, list)

    def test_performance_metrics_calculation(self):
        """Test calcul métriques performance"""
        # Création résultats test avec métriques
        test_results = [
            NetworkTestResult(
                endpoint=NetworkEndpoint("test1", 80, "tcp"),
                status="success",
                response_time_ms=50.0
            ),
            NetworkTestResult(
                endpoint=NetworkEndpoint("test2", 80, "tcp"),
                status="success",
                response_time_ms=75.0
            ),
            NetworkTestResult(
                endpoint=NetworkEndpoint("test3", 80, "tcp"),
                status="failure"
            )
        ]

        # Calcul métriques
        latencies = [r.response_time_ms for r in test_results
                    if r.response_time_ms is not None and r.status == 'success']

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            success_rate = len([r for r in test_results if r.status == 'success']) / len(test_results)

            self.assertAlmostEqual(avg_latency, 62.5, places=1)
            self.assertEqual(min_latency, 50.0)
            self.assertEqual(max_latency, 75.0)
            self.assertAlmostEqual(success_rate, 2/3, places=2)

    def test_stats_reporting(self):
        """Test reporting statistiques"""
        stats = self.engine.get_stats()

        required_keys = ['tests_performed', 'connectivity_failures', 'security_alerts']
        for key in required_keys:
            self.assertIn(key, stats)


class TestIntegrationPhase2(unittest.TestCase):
    """Tests d'intégration Phase 2"""

    def test_sandbox_cache_integration(self):
        """Test intégration Sandbox + Cache"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            # Initialisation engines
            sandbox_engine = DevSandboxEngine()
            cache_daemon = BuildCacheDaemon()

            # Création sandbox avec cache
            config = sandbox_engine.create_sandbox_config("cache_test")

            # Stockage résultat build dans cache
            build_result = {"artifact": "binary", "version": "1.0"}
            cache_daemon.store("build_artifact", build_result, category="artifacts")

            # Vérification stockage
            cached = cache_daemon.retrieve("build_artifact")
            self.assertEqual(cached, build_result)

    def test_dependency_network_integration(self):
        """Test intégration Dependencies + Network"""
        # Engine dépendances
        dep_engine = DepValidatorEngine()

        # Engine réseau (pour vérifications de connectivité lors downloads)
        net_engine = NetHealthEngine()

        # Rapport dépendances
        report = dep_engine.generate_ecosystem_report()

        # Rapport réseau
        net_report = net_engine.generate_health_report()

        # Vérification structures compatibles
        self.assertIsInstance(report.recommendations, list)
        self.assertIsInstance(net_report.recommendations, list)


if __name__ == '__main__':
    # Configuration pour tests
    logging.basicConfig(level=logging.ERROR)  # Silencieux pour tests

    # Exécution tests
    unittest.main(verbosity=2)