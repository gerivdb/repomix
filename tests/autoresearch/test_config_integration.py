#!/usr/bin/env python3
"""
Tests d'intégration pour la validation et utilisation des configs autoresearch
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from NEXUS.autoresearch.config_validator import (
    validate_config_file,
    validate_config_dict,
    create_config_from_yaml,
    AutoresearchConfigModel,
)


class TestConfigValidation:
    def test_validate_valid_config_dict(self):
        """Test validation d'un dict de config valide"""
        config_dict = {
            "repo_path": "/path/to/repo",
            "metric_command": "echo 1.0",
            "budget": {"type": "time", "max_budget": 3600},
            "constraints": {
                "max_runtime_per_iteration": 300,
                "max_parallel_jobs": 1,
                "cpu_only": True,
                "allowed_paths": ["src/"],
                "protected_files": ["config.py"],
                "max_file_size": 1000000,
                "environment_vars": {"TEST": "value"},
            },
        }

        result = validate_config_dict(config_dict)
        assert isinstance(result, AutoresearchConfigModel)
        assert result.repo_path == "/path/to/repo"
        assert result.budget.type == "time"
        assert result.budget.max_budget == 3600

    def test_validate_invalid_budget_type(self):
        """Test validation avec type de budget invalide"""
        config_dict = {
            "repo_path": "/path/to/repo",
            "metric_command": "echo 1.0",
            "budget": {"type": "invalid_type", "max_budget": 3600},
            "constraints": {
                "max_runtime_per_iteration": 300,
                "max_parallel_jobs": 1,
                "cpu_only": True,
            },
        }

        with pytest.raises(ValueError, match='type must be "time" or "iterations"'):
            validate_config_dict(config_dict)

    def test_validate_missing_required_field(self):
        """Test validation avec champ requis manquant"""
        config_dict = {
            "metric_command": "echo 1.0",
            "budget": {"type": "time", "max_budget": 3600},
            "constraints": {"max_runtime_per_iteration": 300},
        }

        with pytest.raises(ValueError):
            validate_config_dict(config_dict)

    def test_validate_config_file(self):
        """Test validation d'un fichier YAML"""
        config_data = {
            "repo_path": "/test/repo",
            "metric_command": "python -c 'print(1.0)'",
            "budget": {"type": "iterations", "max_budget": 10},
            "constraints": {
                "max_runtime_per_iteration": 60,
                "max_parallel_jobs": 1,
                "cpu_only": True,
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            result = validate_config_file(temp_path)
            assert isinstance(result, AutoresearchConfigModel)
            assert result.repo_path == "/test/repo"
            assert result.budget.type == "iterations"
        finally:
            Path(temp_path).unlink()

    def test_create_config_from_yaml(self):
        """Test création d'AutoresearchConfig depuis YAML"""
        config_data = {
            "repo_path": "/test/repo",
            "metric_command": "echo 1.0",
            "budget": {"type": "time", "max_budget": 7200},
            "constraints": {
                "max_runtime_per_iteration": 300,
                "max_parallel_jobs": 1,
                "cpu_only": True,
                "allowed_paths": ["NEXUS/autoresearch/"],
                "protected_files": ["core.py"],
            },
            "modification_provider": "codex_or_manual",
            "base_branch": "main",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            config = create_config_from_yaml(temp_path)
            assert config.repo_path == "/test/repo"
            assert config.metric_command == "echo 1.0"
            assert config.budget.type == "time"
            assert config.budget.max_budget == 7200
            assert config.constraints.allowed_paths == ["NEXUS/autoresearch/"]
            assert config.constraints.protected_files == ["core.py"]
        finally:
            Path(temp_path).unlink()

    def test_config_with_experiment_name(self):
        """Test config avec nom d'expérimentation personnalisé"""
        config_dict = {
            "repo_path": "/repo",
            "metric_command": "echo 1.0",
            "budget": {"type": "iterations", "max_budget": 5},
            "constraints": {"max_runtime_per_iteration": 60},
            "experiment_name": "test_experiment",
        }

        result = validate_config_dict(config_dict)
        assert result.experiment_name == "test_experiment"


class TestAutoresearchLoop:
    def test_autoresearch_loop_help(self):
        """Test que --help fonctionne"""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "NEXUS.autoresearch.autoresearch_loop", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 0
        assert "--config" in result.stdout

    def test_autoresearch_loop_invalid_config(self):
        """Test avec config invalide"""
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "NEXUS.autoresearch.autoresearch_loop",
                "--config",
                "/nonexistent/config.yaml",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        # Devrait échouer car le fichier n'existe pas
        assert result.returncode != 0 or "error" in result.stdout.lower()
