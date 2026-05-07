#!/usr/bin/env python3
"""
Tests pour CLI benchmark de engine.py
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path


class TestEngineBenchmarkCLI:
    def test_cli_benchmark_help(self):
        """Test that --help works"""
        result = subprocess.run(
            [sys.executable, "-m", "NEXUS.autoresearch.engine", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--benchmark" in result.stdout
        assert "--repo" in result.stdout

    def test_cli_benchmark_basic(self):
        """Test basic benchmark CLI execution"""
        test_repo = "tests/fixtures/test_repo"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "NEXUS.autoresearch.engine",
                "--benchmark",
                "--repo",
                test_repo,
                "--iterations",
                "2",
                "--metric",
                "time_per_iter",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # Should output valid JSON
        try:
            data = json.loads(result.stdout)
            assert "status" in data
            assert "time_per_iter" in data
            assert data["iterations"] == 2
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {result.stdout}")

    def test_cli_benchmark_invalid_repo(self):
        """Test benchmark with invalid repo path"""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "NEXUS.autoresearch.engine",
                "--benchmark",
                "--repo",
                "/nonexistent/path",
                "--iterations",
                "1",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        # Should fail
        assert result.returncode == 1  # Exception in Python

    def test_cli_normal_mode_not_implemented(self):
        """Test that normal mode gives appropriate message"""
        result = subprocess.run(
            [sys.executable, "-m", "NEXUS.autoresearch.engine", "--repo", "dummy"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 1
        assert "not implemented" in result.stdout.lower()
