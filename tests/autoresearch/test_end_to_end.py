#!/usr/bin/env python3
"""
Tests end-to-end pour l'intégration complète autoresearch
"""

import pytest
import tempfile
import subprocess
import json
from pathlib import Path
from unittest.mock import patch

from NEXUS.autoresearch.session_runner import AutoresearchSession
from NEXUS.autoresearch.config_validator import validate_config_file


class TestEndToEndIntegration:
    def setup_method(self):
        """Setup test repo"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)

        # Initialize git repo
        subprocess.run(
            ["git", "init"], cwd=self.repo_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=self.repo_path, check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=self.repo_path,
            check=True,
        )

        # Create initial files and commit
        (self.repo_path / "test.py").write_text("print('hello')")
        (self.repo_path / "README.md").write_text("# Test Repo")
        subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"], cwd=self.repo_path, check=True
        )

    def teardown_method(self):
        """Cleanup"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_session_pipeline(self):
        """Test pipeline complet session autoresearch"""
        # Créer config temporaire
        config_data = {
            "repo_path": str(self.repo_path),
            "metric_command": 'python -c "import time; time.sleep(0.01); print(1.0)"',
            "budget": {"type": "iterations", "max_budget": 2},
            "constraints": {
                "max_runtime_per_iteration": 10,
                "max_parallel_jobs": 1,
                "cpu_only": True,
            },
            "experiment_name": "test_session",
        }

        config_file = self.repo_path / "test_config.yaml"
        import yaml

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Exécuter session
        session = AutoresearchSession(str(config_file))
        results = session.run_session()

        # Vérifications
        assert results["status"] == "success"
        assert "baseline_metric" in results
        assert "best_metric" in results
        assert "total_time" in results
        assert results["iterations_completed"] >= 0

        # Vérifier qu'une branche expérimentale a été créée
        result = subprocess.run(
            ["git", "branch"], cwd=self.repo_path, capture_output=True, text=True
        )
        assert "autoresearch-test_session" in result.stdout

    def test_session_with_repo_override(self):
        """Test session avec override du repo path"""
        # Config pointant vers un autre repo
        config_data = {
            "repo_path": "/fake/path",
            "metric_command": "echo 1.0",
            "budget": {"type": "iterations", "max_budget": 1},
            "constraints": {"max_runtime_per_iteration": 5},
        }

        config_file = self.repo_path / "test_config.yaml"
        import yaml

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Override avec repo réel
        session = AutoresearchSession(str(config_file), str(self.repo_path))
        assert session.config.repo_path == str(self.repo_path)

    def test_config_validation_in_session(self):
        """Test que la validation config fonctionne dans le contexte session"""
        # Config valide
        config_data = {
            "repo_path": str(self.repo_path),
            "metric_command": "echo 1.0",
            "budget": {"type": "time", "max_budget": 60},
            "constraints": {"max_runtime_per_iteration": 10},
        }

        config_file = self.repo_path / "valid_config.yaml"
        import yaml

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Devrait réussir
        session = AutoresearchSession(str(config_file))
        assert session.config is not None
        assert session.config.budget.max_budget == 60

    def test_session_error_handling(self):
        """Test gestion d'erreurs dans session"""
        # Config avec repo invalide
        config_data = {
            "repo_path": "/nonexistent/repo/path",
            "metric_command": "echo 1.0",
            "budget": {"type": "iterations", "max_budget": 1},
            "constraints": {"max_runtime_per_iteration": 5},
        }

        config_file = self.repo_path / "error_config.yaml"
        import yaml

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        session = AutoresearchSession(str(config_file))
        results = session.run_session()

        # Devrait échouer proprement
        assert results["status"] == "error"
        assert "error" in results

    @patch(
        "NEXUS.autoresearch.session_runner.AutoresearchSession._run_baseline_benchmark"
    )
    def test_session_with_failed_baseline(self, mock_baseline):
        """Test session avec benchmark baseline qui échoue"""
        mock_baseline.side_effect = RuntimeError("Baseline failed")

        config_data = {
            "repo_path": str(self.repo_path),
            "metric_command": "echo 1.0",
            "budget": {"type": "iterations", "max_budget": 1},
            "constraints": {"max_runtime_per_iteration": 5},
        }

        config_file = self.repo_path / "test_config.yaml"
        import yaml

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        session = AutoresearchSession(str(config_file))
        results = session.run_session()

        assert results["status"] == "error"
        assert "Baseline failed" in results["error"]


class TestRepoStability:
    def test_repo_jouet_deterministic(self):
        """Test que le repo jouet donne des résultats déterministes"""
        repo_path = "tests/fixtures/test_repo"

        # Plusieurs runs du même benchmark
        results = []
        for i in range(3):
            # Utiliser le benchmark CLI
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "NEXUS.autoresearch.engine",
                    "--benchmark",
                    "--repo",
                    repo_path,
                    "--iterations",
                    "3",
                ],
                capture_output=True,
                text=True,
                cwd=".",
            )

            data = json.loads(result.stdout)
            results.append(data["time_per_iter"])

        # Vérifier que les résultats sont similaires (variation < 10%)
        avg_time = sum(results) / len(results)
        for time_val in results:
            deviation = abs(time_val - avg_time) / avg_time
            assert deviation < 0.1, (
                f"Result {time_val} deviates too much from average {avg_time}"
            )

    def test_repo_jouet_git_clean(self):
        """Test que le repo jouet reste propre après benchmarks"""
        repo_path = "tests/fixtures/test_repo"

        # Vérifier état initial
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == "", "Repo should be clean initially"

        # Run benchmark
        subprocess.run(
            [
                "python",
                "-m",
                "NEXUS.autoresearch.engine",
                "--benchmark",
                "--repo",
                repo_path,
                "--iterations",
                "2",
            ],
            capture_output=True,
            cwd=".",
        )

        # Vérifier que repo est toujours propre
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == "", "Repo should remain clean after benchmark"


class TestReportGeneration:
    def test_report_generation(self):
        """Test génération de rapports"""
        from NEXUS.autoresearch.report_generator import AutoresearchReport

        # Données de test
        config = {"test": "config"}
        results = {
            "status": "success",
            "baseline_metric": 10.0,
            "best_metric": 8.0,
            "total_improvement": 2.0,
        }
        iterations = [
            {"iteration": 0, "kept": True, "improvement": 1.0},
            {"iteration": 1, "kept": False, "improvement": 0.5},
        ]

        report = AutoresearchReport("test_experiment", config, results, iterations)

        # Test dict conversion
        report_dict = report.to_dict()
        assert report_dict["experiment_id"] == "test_experiment"
        assert report_dict["summary"]["kept_iterations"] == 1
        assert report_dict["summary"]["max_improvement"] == 1.0

        # Test sauvegarde JSON (temporaire)
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            report.save(tmp_path)
            assert Path(tmp_path).exists()

            # Vérifier contenu
            with open(tmp_path) as f:
                saved_data = json.load(f)
                assert saved_data["experiment_id"] == "test_experiment"

        finally:
            Path(tmp_path).unlink()
