#!/usr/bin/env python3
"""
Tests pour DecisionEngine et GitManager
"""

import pytest
import tempfile
import subprocess
from pathlib import Path

from NEXUS.autoresearch.decision_engine import DecisionEngine
from NEXUS.autoresearch.git_manager import GitManager


class TestDecisionEngine:
    def test_decision_engine_init(self):
        """Test initialization"""
        engine = DecisionEngine("/tmp/repo")
        assert engine.repo_path == Path("/tmp/repo")
        assert engine.require_improvement_percent == 5.0

    def test_set_baseline(self):
        """Test setting baseline metric"""
        engine = DecisionEngine("/tmp/repo")
        engine.set_baseline(10.0)
        assert engine.baseline_metric == 10.0
        assert engine.best_metric == 10.0

    def test_evaluate_iteration_improvement(self):
        """Test evaluation with improvement"""
        engine = DecisionEngine("/tmp/repo")
        engine.set_baseline(10.0)

        metric_result = {"success": True, "value": 8.0}  # 20% improvement
        keep, improvement = engine.evaluate_iteration(metric_result, "abc123")

        assert keep is True
        assert improvement == 2.0
        assert engine.best_metric == 8.0
        assert engine.best_commit == "abc123"

    def test_evaluate_iteration_no_improvement(self):
        """Test evaluation without improvement"""
        engine = DecisionEngine("/tmp/repo")
        engine.set_baseline(10.0)

        metric_result = {"success": True, "value": 10.5}  # Worse
        keep, improvement = engine.evaluate_iteration(metric_result, "abc123")

        assert keep is False
        assert improvement is None
        assert engine.best_metric == 10.0  # Unchanged

    def test_evaluate_iteration_insufficient_improvement(self):
        """Test evaluation with insufficient improvement"""
        engine = DecisionEngine("/tmp/repo", require_improvement_percent=10.0)
        engine.set_baseline(10.0)

        metric_result = {
            "success": True,
            "value": 9.5,
        }  # 5% improvement, but threshold is 10%
        keep, improvement = engine.evaluate_iteration(metric_result, "abc123")

        assert keep is False
        assert improvement == 0.5
        assert engine.best_metric == 10.0  # Unchanged

    def test_evaluate_iteration_failed_metric(self):
        """Test evaluation with failed metric"""
        engine = DecisionEngine("/tmp/repo")
        engine.set_baseline(10.0)

        metric_result = {"success": False, "value": None}
        keep, improvement = engine.evaluate_iteration(metric_result, "abc123")

        assert keep is False
        assert improvement is None

    def test_should_keep_with_low_success_rate(self):
        """Test should_keep with low success rate"""
        engine = DecisionEngine("/tmp/repo")
        engine.set_baseline(10.0)

        metric_result = {"success": True, "value": 8.0}
        keep = engine.should_keep(metric_result, success_rate=0.90)  # < 0.95

        assert keep is False

    def test_generate_commit_message(self):
        """Test commit message generation"""
        engine = DecisionEngine("/tmp/repo")
        engine.set_baseline(10.0)
        engine.best_metric = 8.0

        message = engine.generate_commit_message(5, 2.0, 0.97)
        assert "chore(autoresearch)" in message
        assert "speedup +20.0%" in message
        assert "time_per_iter=8.000s" in message
        assert "success_rate=0.97" in message
        assert "iter 5" in message


class TestGitManager:
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

        # Create initial commit
        (self.repo_path / "test.txt").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"], cwd=self.repo_path, check=True
        )

    def teardown_method(self):
        """Cleanup"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_git_manager_init(self):
        """Test initialization"""
        manager = GitManager(str(self.repo_path))
        assert manager.repo_path == self.repo_path
        assert manager.base_branch == "main"

    def test_git_manager_invalid_repo(self):
        """Test with invalid repo"""
        with pytest.raises(ValueError, match="Not a git repository"):
            GitManager("/nonexistent")

    def test_create_experiment_branch(self):
        """Test creating experiment branch"""
        manager = GitManager(str(self.repo_path))
        branch_name = manager.create_experiment_branch("test-experiment")

        assert "autoresearch-test-experiment" in branch_name

        # Verify branch exists
        result = subprocess.run(
            ["git", "branch"], cwd=self.repo_path, capture_output=True, text=True
        )
        assert branch_name in result.stdout

    def test_get_current_branch(self):
        """Test getting current branch"""
        manager = GitManager(str(self.repo_path))
        branch = manager.get_current_branch()
        assert branch == "master" or branch == "main"

    def test_commit_changes(self):
        """Test committing changes"""
        # Create a change
        (self.repo_path / "test.txt").write_text("modified")

        manager = GitManager(str(self.repo_path))
        commit_hash = manager.commit_changes("Test commit")

        assert len(commit_hash) >= 7  # Git hash length

        # Verify commit
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        assert "Test commit" in result.stdout

    def test_revert_to_commit(self):
        """Test reverting to commit"""
        manager = GitManager(str(self.repo_path))
        original_commit = manager.get_current_commit()

        # Create and commit a change
        (self.repo_path / "test.txt").write_text("modified")
        manager.commit_changes("Test change")

        # Revert
        manager.revert_to_commit(original_commit)

        # Verify content is back to original
        content = (self.repo_path / "test.txt").read_text()
        assert content == "initial"
