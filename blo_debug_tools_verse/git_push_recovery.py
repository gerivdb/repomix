#!/usr/bin/env python3
"""GitPushRecovery - Diagnostic automatique problèmes Git/push"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PushError(Enum):
    UPSTREAM_NOT_SET = "upstream_not_set"
    PERMISSION_DENIED = "permission_denied"
    AUTH_FAILURE = "auth_failure"
    MERGE_CONFLICT = "merge_conflict"
    SIZE_LIMIT = "size_limit"
    UNKNOWN = "unknown"


@dataclass
class RecoveryAction:
    command: str
    description: str
    risk_level: str  # low, medium, high


class GitPushRecovery:
    """Diagnostic et récupération automatique push Git"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.diagnosis: Dict = {}

    def diagnose(self) -> Dict:
        """Diagnostiquer problème push Git"""
        self.diagnosis = {
            "repo_path": str(self.repo_path),
            "git_status": self._check_git_status(),
            "upstream": self._check_upstream(),
            "permissions": self._check_permissions(),
            "last_error": self._get_last_error(),
            "recommended_action": None
        }

        error_type = self._classify_error()
        self.diagnosis["error_type"] = error_type.value
        self.diagnosis["recommended_action"] = self._get_recovery_action(error_type)

        return self.diagnosis

    def _check_git_status(self) -> Dict:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True, text=True
            )
            return {"clean": result.stdout.strip() == "", "output": result.stdout}
        except Exception as e:
            return {"error": str(e)}

    def _check_upstream(self) -> Dict:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "@'{u}'"],
                cwd=self.repo_path,
                capture_output=True, text=True
            )
            return {"set": result.returncode == 0, "upstream": result.stdout.strip()}
        except Exception:
            return {"set": False, "upstream": None}

    def _check_permissions(self) -> Dict:
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=self.repo_path,
                capture_output=True, text=True
            )
            remotes = result.stdout
            return {"has_write_access": "push" in remotes}
        except Exception:
            return {"has_write_access": False}

    def _get_last_error(self) -> Optional[str]:
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%B"],
                cwd=self.repo_path,
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    def _classify_error(self) -> PushError:
        if not self.diagnosis.get("upstream", {}).get("set", False):
            return PushError.UPSTREAM_NOT_SET
        if not self.diagnosis.get("permissions", {}).get("has_write_access", False):
            return PushError.PERMISSION_DENIED
        return PushError.UNKNOWN

    def _get_recovery_action(self, error: PushError) -> Optional[RecoveryAction]:
        actions = {
            PushError.UPSTREAM_NOT_SET: RecoveryAction(
                command="git push --set-upstream origin $(git branch --show-current)",
                description="Set upstream to current branch",
                risk_level="low"
            ),
            PushError.PERMISSION_DENIED: RecoveryAction(
                command="git remote set-url origin <NEW_URL_WITH_TOKEN>",
                description="Update remote URL with authentication token",
                risk_level="medium"
            ),
            PushError.AUTH_FAILURE: RecoveryAction(
                command="gh auth login --with-token < token.txt",
                description="Re-authenticate with GitHub CLI",
                risk_level="low"
            )
        }
        return actions.get(error)

    def execute_recovery(self) -> bool:
        """Exécuter action de récupération recommandée"""
        action = self.diagnosis.get("recommended_action")
        if not action or action.risk_level == "high":
            return False

        try:
            result = subprocess.run(
                action.command,
                shell=True,
                cwd=self.repo_path,
                capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False


if __name__ == "__main__":
    recovery = GitPushRecovery()
    diagnosis = recovery.diagnose()
    print(json.dumps(diagnosis, indent=2, default=str))