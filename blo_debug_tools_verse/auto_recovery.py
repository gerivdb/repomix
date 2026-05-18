#!/usr/bin/env python3
"""AutoRecovery - Système réparation automatique échecs"""

import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class RecoveryPlan:
    name: str
    steps: List[str]
    max_attempts: int = 3
    timeout_seconds: int = 300
    success_callback: Optional[Callable] = None


class AutoRecovery:
    """Système récupération automatique incidents"""

    def __init__(self, history_file: str = "recovery_history.json"):
        self.history_file = Path(history_file)
        self.history: List[Dict] = self._load_history()
        self.plans: Dict[str, RecoveryPlan] = {}

    def _load_history(self) -> List[Dict]:
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text())
            except Exception:
                return []
        return []

    def _save_history(self):
        self.history_file.write_text(json.dumps(self.history, indent=2))

    def register_plan(self, plan: RecoveryPlan):
        """Enregistrer plan de récupération"""
        self.plans[plan.name] = plan

    def recover(self, plan_name: str, context: Dict = None) -> Dict:
        """Exécuter plan de récupération"""
        plan = self.plans.get(plan_name)
        if not plan:
            return {"success": False, "error": f"Plan {plan_name} not found"}

        start_time = datetime.now()
        result = {
            "plan": plan_name,
            "start_time": start_time.isoformat(),
            "attempts": 0,
            "success": False,
            "steps_executed": [],
            "error": None
        }

        for attempt in range(plan.max_attempts):
            result["attempts"] = attempt + 1
            try:
                success = self._execute_plan(plan, context or {})
                if success:
                    result["success"] = True
                    result["end_time"] = datetime.now().isoformat()
                    break
            except Exception as e:
                result["error"] = str(e)
                time.sleep(5)

        elapsed = (datetime.now() - start_time).total_seconds()
        result["elapsed_seconds"] = elapsed

        self.history.append(result)
        self._save_history()

        return result

    def _execute_plan(self, plan: RecoveryPlan, context: Dict) -> bool:
        for step in plan.steps:
            result = subprocess.run(
                step, shell=True, capture_output=True, text=True, timeout=plan.timeout_seconds
            )
            step_result = {"step": step, "success": result.returncode == 0}
            result.get("steps_executed", []).append(step_result)
            if result.returncode != 0:
                return False
        return True

    def get_recovery_time(self) -> float:
        """Temps moyen de récupération (minutes)"""
        successful = [h for h in self.history if h.get("success")]
        if not successful:
            return 0
        avg_seconds = sum(h.get("elapsed_seconds", 0) for h in successful) / len(successful)
        return avg_seconds / 60

    def get_uptime_stats(self) -> Dict:
        """Statistiques uptime"""
        total = len(self.history)
        successful = len([h for h in self.history if h.get("success")])
        return {
            "total_recoveries": total,
            "successful": successful,
            "success_rate": successful / total if total > 0 else 1.0,
            "avg_recovery_minutes": self.get_recovery_time(),
            "estimated_uptime": f"{99.9}% (target)" if successful == total else "calculating..."
        }


# Plans prédéfinis
def git_push_recovery_plan() -> RecoveryPlan:
    return RecoveryPlan(
        name="git_push_recovery",
        steps=[
            "git fetch origin",
            "git rebase origin/$(git branch --show-current)",
            "git push --set-upstream origin $(git branch --show-current)"
        ],
        max_attempts=3,
        timeout_seconds=60
    )


def disk_space_recovery_plan() -> RecoveryPlan:
    return RecoveryPlan(
        name="disk_space_recovery",
        steps=[
            "find . -type f -name '*.pyc' -delete",
            "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true",
            "git gc --aggressive"
        ],
        max_attempts=1,
        timeout_seconds=120
    )


if __name__ == "__main__":
    recovery = AutoRecovery()
    recovery.register_plan(git_push_recovery_plan())
    
    stats = recovery.get_uptime_stats()
    print(json.dumps({"stats": stats, "history_count": len(recovery.history)}, indent=2))