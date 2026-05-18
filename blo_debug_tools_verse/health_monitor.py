#!/usr/bin/env python3
"""HealthMonitor - Surveillance distribuée santé repos/agents"""

import time
import json
import psutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class HealthMetric:
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def status(self) -> str:
        if self.value >= self.threshold_critical:
            return "CRITICAL"
        if self.value >= self.threshold_warning:
            return "WARNING"
        return "OK"


class HealthMonitor:
    """Monitoring santé système distribué"""

    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else None
        self.metrics: List[HealthMetric] = []
        self.repos: List[str] = []
        self.alerts: List[Dict] = []

    def add_repo(self, repo_path: str):
        """Ajouter repo à surveiller"""
        self.repos.append(repo_path)

    def collect_metrics(self) -> Dict:
        """Collecter métriques système"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": self._collect_system_metrics(),
            "repos": self._collect_repo_metrics(),
            "overall_status": "OK"
        }

        critical_count = sum(1 for m in metrics["system"] if m.get("status") == "CRITICAL")
        if critical_count > 0:
            metrics["overall_status"] = "CRITICAL"
        elif any(m.get("status") == "WARNING" for m in metrics["system"]):
            metrics["overall_status"] = "WARNING"

        self.metrics = metrics
        return metrics

    def _collect_system_metrics(self) -> List[Dict]:
        return [
            {
                "name": "cpu_percent",
                "value": psutil.cpu_percent(interval=1),
                "unit": "%",
                "threshold_warning": 80,
                "threshold_critical": 95,
                "status": "OK" if psutil.cpu_percent(interval=1) < 80 else "WARNING"
            },
            {
                "name": "memory_percent",
                "value": psutil.virtual_memory().percent,
                "unit": "%",
                "threshold_warning": 85,
                "threshold_critical": 95,
                "status": "OK" if psutil.virtual_memory().percent < 85 else "WARNING"
            },
            {
                "name": "disk_percent",
                "value": psutil.disk_usage('/').percent,
                "unit": "%",
                "threshold_warning": 90,
                "threshold_critical": 98,
                "status": "OK" if psutil.disk_usage('/').percent < 90 else "WARNING"
            }
        ]

    def _collect_repo_metrics(self) -> Dict:
        repo_data = {}
        for repo in self.repos:
            repo_path = Path(repo)
            if repo_path.exists():
                git_dir = repo_path / ".git"
                repo_data[repo] = {
                    "exists": True,
                    "size_mb": sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file()) / 1024 / 1024,
                    "git_healthy": git_dir.exists(),
                    "modified_files": len(list(repo_path.glob("**/*.py")))
                }
            else:
                repo_data[repo] = {"exists": False}
        return repo_data

    def check_alerts(self) -> List[Dict]:
        """Vérifier et générer alertes"""
        alerts = []
        for metric in self._flatten_metrics():
            if metric.get("status") in ["CRITICAL", "WARNING"]:
                alerts.append({
                    "severity": metric["status"],
                    "metric": metric["name"],
                    "value": metric["value"],
                    "message": f"{metric['name']} at {metric['value']}{metric['unit']}"
                })
        self.alerts = alerts
        return alerts

    def _flatten_metrics(self) -> List[Dict]:
        results = []
        if self.metrics:
            for m in self.metrics.get("system", []):
                results.append(m)
        return results

    def to_json(self) -> str:
        return json.dumps(self.metrics, indent=2, default=str)


if __name__ == "__main__":
    monitor = HealthMonitor()
    monitor.add_repo(".")
    metrics = monitor.collect_metrics()
    alerts = monitor.check_alerts()
    print(json.dumps({"metrics": metrics, "alerts": alerts}, indent=2))