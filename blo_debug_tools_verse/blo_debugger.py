#!/usr/bin/env python3
"""BLODebugger - Outils debugging avancés cross-repo"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DebugSession:
    session_id: str
    repo_path: str
    start_time: str
    logs: List[str] = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []


class BLODebugger:
    """Outils debugging avancés BLO cross-repo"""

    def __init__(self, work_dir: str = "."):
        self.work_dir = Path(work_dir)
        self.sessions: Dict[str, DebugSession] = {}

    def start_session(self, repo_path: str = None) -> DebugSession:
        """Démarrer session debugging"""
        session_id = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = DebugSession(
            session_id=session_id,
            repo_path=repo_path or str(self.work_dir),
            start_time=datetime.now().isoformat()
        )
        self.sessions[session_id] = session
        return session

    def diagnose_repo(self, repo_path: str = None) -> Dict:
        """Diagnostic complet d'un repo"""
        repo = Path(repo_path or self.work_dir)
        diagnosis = {
            "path": str(repo),
            "git_health": self._check_git_health(repo),
            "structure": self._check_structure(repo),
            "dependencies": self._check_dependencies(repo),
            "performance": self._check_performance(repo)
        }
        return diagnosis

    def _check_git_health(self, repo: Path) -> Dict:
        try:
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo, capture_output=True, text=True
            )
            log = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=repo, capture_output=True, text=True
            )
            return {
                "clean": status.stdout.strip() == "",
                "modified_files": len(status.stdout.strip().split('\n')) if status.stdout.strip() else 0,
                "recent_commits": log.stdout.strip().split('\n')[:5]
            }
        except Exception as e:
            return {"error": str(e)}

    def _check_structure(self, repo: Path) -> Dict:
        py_files = list(repo.rglob("*.py"))
        md_files = list(repo.rglob("*.md"))
        return {
            "python_files": len(py_files),
            "markdown_files": len(md_files),
            "directories": len([d for d in repo.rglob("*") if d.is_dir()])
        }

    def _check_dependencies(self, repo: Path) -> Dict:
        req_files = ["requirements.txt", "pyproject.toml", "package.json"]
        found = [f for f in req_files if (repo / f).exists()]
        return {"config_files": found}

    def _check_performance(self, repo: Path) -> Dict:
        total_size = sum(f.stat().st_size for f in repo.rglob('*') if f.is_file())
        return {
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "file_count": len(list(repo.rglob('*'))),
            "large_files": [str(f) for f in repo.rglob('*') if f.is_file() and f.stat().st_size > 10*1024*1024]
        }

    def cross_repo_check(self, repos: List[str]) -> Dict:
        """Vérification cross-repo"""
        results = {}
        for repo in repos:
            try:
                results[repo] = self.diagnose_repo(repo)
            except Exception as e:
                results[repo] = {"error": str(e)}
        return results

    def generate_report(self, diagnosis: Dict) -> str:
        """Générer rapport debugging"""
        report = []
        report.append("=== BLO DEBUG REPORT ===")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        for key, value in diagnosis.items():
            report.append(f"## {key.upper()}")
            report.append(json.dumps(value, indent=2, default=str))
            report.append("")
        
        return "\n".join(report)


if __name__ == "__main__":
    debugger = BLODebugger()
    diagnosis = debugger.diagnose_repo()
    print(debugger.generate_report(diagnosis))