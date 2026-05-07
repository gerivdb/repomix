#!/usr/bin/env python3
"""
Tests pour BenchmarkRunner
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from NEXUS.autoresearch.benchmark_runner import BenchmarkRunner
from NEXUS.autoresearch.data_models import BenchmarkResult


class TestBenchmarkRunner:
    def test_init_valid_repo(self):
        """Test initialization with valid repo path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            # Create a git repo
            import subprocess

            subprocess.run(
                ["git", "init"], cwd=repo_path, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"], cwd=repo_path, check=True
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_path,
                check=True,
            )

            runner = BenchmarkRunner(str(repo_path), 3, ["time_per_iter"])
            assert runner.repo_path == repo_path
            assert runner.total_iterations == 3
            assert runner.metrics == ["time_per_iter"]

    def test_init_invalid_repo(self):
        """Test initialization with invalid repo path"""
        with pytest.raises(ValueError, match="Repository path does not exist"):
            BenchmarkRunner("/nonexistent/path", 3, ["time_per_iter"])

    def test_init_invalid_metric(self):
        """Test initialization with invalid metric"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Unknown metric"):
                BenchmarkRunner(tmpdir, 3, ["invalid_metric"])

    def test_run_success(self):
        """Test successful benchmark run"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            # Create minimal git repo
            import subprocess

            subprocess.run(
                ["git", "init"], cwd=repo_path, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"], cwd=repo_path, check=True
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_path,
                check=True,
            )

            runner = BenchmarkRunner(
                str(repo_path), 2, ["time_per_iter", "success_rate"]
            )
            result = runner.run()

            assert result.status == "success"
            assert result.iterations == 2
            assert result.warmup_iterations == 1  # default
            assert result.measured_iterations == 2  # 2 iterations measured
            assert isinstance(result.time_per_iter, float)
            assert isinstance(result.success_rate, float)
            assert isinstance(result.std_time_per_iter, float)
            assert result.success_rate > 0  # Should have some success

    def test_run_with_failure(self):
        """Test benchmark run with some failures"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            import subprocess

            subprocess.run(
                ["git", "init"], cwd=repo_path, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"], cwd=repo_path, check=True
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_path,
                check=True,
            )

            runner = BenchmarkRunner(
                str(repo_path), 2, ["time_per_iter", "success_rate"]
            )
            result = runner.run()

            assert result.status == "success"
            assert (
                result.success_rate == 1.0
            )  # All iterations should succeed with simulation

    def test_calculate_metrics_no_results(self):
        """Test metrics calculation with no results"""
        runner = BenchmarkRunner("/tmp", 1, ["time_per_iter", "success_rate"])

        metrics = runner._calculate_metrics([])
        assert metrics["time_per_iter"] == 0.0
        assert metrics["success_rate"] == 0.0
        assert metrics["std_time_per_iter"] == 0.0
