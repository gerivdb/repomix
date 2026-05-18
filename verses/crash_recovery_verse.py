#!/usr/bin/env python3
"""
CrashRecovery Verse - NFIRS Phase 5
Récupération automatique de crash.

IntentHash: 0xCRASH_RECOVERY_VERSE_20260419
"""

import os
import json
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path


class CrashRecoveryVerse:
    """Verse pour récupération automatique de crash"""

    def __init__(self):
        self.recovery_config = "crash_recovery_config.json"
        self.crash_history = "crash_history.json"
        self.recovery_state = "recovery_state.json"
        self.load_config()

    def load_config(self):
        """Charge la configuration de récupération"""
        if os.path.exists(self.recovery_config):
            try:
                with open(self.recovery_config, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except:
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self.save_config()

    def _default_config(self):
        """Configuration par défaut"""
        return {
            "auto_recovery": True,
            "max_recovery_attempts": 3,
            "recovery_timeout_seconds": 300,
            "crash_detection": {
                "memory_threshold": 0.9,  # 90% RAM
                "cpu_threshold": 0.95,  # 95% CPU
                "file_corruption_check": True,
                "process_monitoring": True,
            },
            "recovery_strategies": [
                {
                    "name": "gpu_cache_sanitization",
                    "priority": 1,
                    "actions": [
                        "profile_sanitizer.detect_gpu_corruption",
                        "profile_sanitizer.backup_profile",
                        "profile_sanitizer.clean_gpu_caches",
                    ],
                },
                {
                    "name": "file_recovery",
                    "priority": 2,
                    "actions": [
                        "recovery_agent.auto_recover_missing",
                        "plix_recovery.validate_reconstruction",
                    ],
                },
                {
                    "name": "state_reset",
                    "priority": 3,
                    "actions": [
                        "dev_accelerator.run_certification",
                        "integrity_monitor.load_baseline",
                    ],
                },
                {
                    "name": "system_restart",
                    "priority": 4,
                    "actions": ["auto_chain_manager.trigger_chain('recovery_chain')"],
                },
            ],
            "notification_channels": ["console", "log"],
            "recovery_success_metrics": {
                "min_uptime_after_recovery": 300,  # 5 minutes
                "max_recovery_time": 120,  # 2 minutes
            },
        }

    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.recovery_config, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def detect_crash(self):
        """Détecte un crash système"""
        crash_indicators = []

        # Vérifier utilisation mémoire
        memory_percent = psutil.virtual_memory().percent / 100
        if memory_percent > self.config["crash_detection"]["memory_threshold"]:
            crash_indicators.append(
                {
                    "type": "memory_exhaustion",
                    "value": memory_percent,
                    "threshold": self.config["crash_detection"]["memory_threshold"],
                }
            )

        # Vérifier utilisation CPU
        cpu_percent = psutil.cpu_percent(interval=1) / 100
        if cpu_percent > self.config["crash_detection"]["cpu_threshold"]:
            crash_indicators.append(
                {
                    "type": "cpu_overload",
                    "value": cpu_percent,
                    "threshold": self.config["crash_detection"]["cpu_threshold"],
                }
            )

        # Vérifier corruption fichiers
        if self.config["crash_detection"]["file_corruption_check"]:
            corruption_issues = self._check_file_corruption()
            if corruption_issues:
                crash_indicators.append(
                    {"type": "file_corruption", "issues": corruption_issues}
                )

        # Vérifier processus critiques
        if self.config["crash_detection"]["process_monitoring"]:
            process_issues = self._check_critical_processes()
            if process_issues:
                crash_indicators.append(
                    {"type": "process_failure", "issues": process_issues}
                )

        # Vérifier corruption caches GPU (Leçon Comet)
        gpu_cache_issues = self._check_gpu_cache_corruption()
        if gpu_cache_issues:
            crash_indicators.append(
                {"type": "gpu_cache_corruption", "issues": gpu_cache_issues}
            )

        if crash_indicators:
            crash_event = {
                "timestamp": datetime.now().isoformat(),
                "indicators": crash_indicators,
                "severity": self._calculate_severity(crash_indicators),
                "auto_recovery_triggered": self.config["auto_recovery"],
            }

            self._log_crash(crash_event)

            if self.config["auto_recovery"]:
                self.initiate_recovery(crash_event)

            return crash_event

        return None

    def _check_file_corruption(self):
        """Vérifie la corruption des fichiers critiques"""
        issues = []
        critical_files = [
            "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md",
            "EPIC_NEXUS_FILE_INTEGRITY_RECOVERY.md",
            "ARCHITECTURAL_INTENT.md",
        ]

        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        # Vérifier si le fichier est lisible
                        f.read(1024)
                except:
                    issues.append(f"Corruption détectée: {file_path}")

        return issues

    def _check_critical_processes(self):
        """Vérifie les processus critiques"""
        issues = []

        # Liste des processus à surveiller (exemple)
        critical_processes = ["python", "git"]

        for proc_name in critical_processes:
            try:
                # Vérifier si le processus tourne
                processes = [
                    p
                    for p in psutil.process_iter(["name"])
                    if p.info["name"] == proc_name
                ]
                if not processes:
                    issues.append(f"Processus critique absent: {proc_name}")
            except:
                issues.append(f"Erreur vérification processus: {proc_name}")

        return issues

    def _check_gpu_cache_corruption(self):
        """Vérifie la corruption des caches GPU dans les profils browser (Leçon Comet)"""
        issues = []

        # Chemins potentiels de profils browser
        potential_profiles = [
            os.path.expandvars(r"%LOCALAPPDATA%\Perplexity\Comet\User Data"),
            os.path.expandvars(r"%APPDATA%\Google\Chrome\User Data"),
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
        ]

        for profile_path in potential_profiles:
            if os.path.exists(profile_path):
                # Vérifier les caches GPU critiques
                gpu_caches = ["ShaderCache", "GrShaderCache", "GraphiteDawnCache"]

                for cache_dir in gpu_caches:
                    cache_path = os.path.join(profile_path, cache_dir)
                    if os.path.exists(cache_path):
                        try:
                            # Vérifier taille des fichiers data_*
                            data_files = [
                                f
                                for f in os.listdir(cache_path)
                                if f.startswith("data_")
                            ]
                            for data_file in data_files:
                                file_path = os.path.join(cache_path, data_file)
                                file_size = os.path.getsize(file_path)

                                # Flag anormal si taille > 50KB (seuil arbitraire basé sur expérience)
                                if file_size > 50000:
                                    issues.append(
                                        {
                                            "profile": profile_path,
                                            "cache": cache_dir,
                                            "file": data_file,
                                            "size": file_size,
                                            "anomaly": "oversized_cache_file",
                                        }
                                    )

                        except Exception as e:
                            issues.append(
                                {
                                    "profile": profile_path,
                                    "cache": cache_dir,
                                    "error": str(e),
                                    "anomaly": "access_error",
                                }
                            )

        return issues

    def _calculate_severity(self, indicators):
        """Calcule la sévérité du crash"""
        severity_score = 0

        for indicator in indicators:
            if indicator["type"] == "memory_exhaustion":
                severity_score += 3
            elif indicator["type"] == "cpu_overload":
                severity_score += 2
            elif indicator["type"] == "file_corruption":
                severity_score += 4
            elif indicator["type"] == "process_failure":
                severity_score += 3
            elif indicator["type"] == "gpu_cache_corruption":
                severity_score += 5  # Highest priority - causes system crashes

        if severity_score >= 7:
            return "critical"
        elif severity_score >= 4:
            return "high"
        elif severity_score >= 2:
            return "medium"
        else:
            return "low"

    def _log_crash(self, crash_event):
        """Log un événement de crash"""
        if os.path.exists(self.crash_history):
            try:
                with open(self.crash_history, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                history = []
        else:
            history = []

        history.append(crash_event)

        # Garder seulement les 100 derniers crashes
        history = history[-100:]

        with open(self.crash_history, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def initiate_recovery(self, crash_event):
        """Initie la récupération automatique"""
        print(
            f"[CRASH_RECOVERY_VERSE] Initiating recovery for crash severity: {crash_event['severity']}"
        )

        recovery_session = {
            "id": f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "crash_event": crash_event,
            "start_time": datetime.now().isoformat(),
            "strategies_attempted": [],
            "success": False,
            "end_time": None,
        }

        # Essayer les stratégies par priorité
        for strategy in sorted(
            self.config["recovery_strategies"], key=lambda x: x["priority"]
        ):
            if self._execute_recovery_strategy(strategy, recovery_session):
                recovery_session["success"] = True
                break

        recovery_session["end_time"] = datetime.now().isoformat()
        self._save_recovery_state(recovery_session)

        if recovery_session["success"]:
            print("[CRASH_RECOVERY_VERSE] Recovery successful")
            self._notify_recovery_success(recovery_session)
        else:
            print("[CRASH_RECOVERY_VERSE] Recovery failed")
            self._notify_recovery_failure(recovery_session)

        return recovery_session["success"]

    def _execute_recovery_strategy(self, strategy, recovery_session):
        """Exécute une stratégie de récupération"""
        print(f"[CRASH_RECOVERY_VERSE] Attempting strategy: {strategy['name']}")

        success = True
        strategy_result = {
            "strategy": strategy["name"],
            "timestamp": datetime.now().isoformat(),
            "actions": [],
        }

        for action in strategy["actions"]:
            try:
                result = self._execute_recovery_action(action)
                strategy_result["actions"].append(
                    {
                        "action": action,
                        "success": result["success"],
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                if not result["success"]:
                    success = False
                    break

            except Exception as e:
                strategy_result["actions"].append(
                    {
                        "action": action,
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                success = False
                break

        recovery_session["strategies_attempted"].append(strategy_result)
        return success

    def _execute_recovery_action(self, action_path):
        """Exécute une action de récupération"""
        try:
            parts = action_path.split(".", 1)
            if len(parts) != 2:
                return {"success": False, "error": "Invalid action format"}

            module_name, method_name = parts

            # Mapping des actions
            action_map = {
                "recovery_agent": ("skills.recovery_agent", "RecoveryAgent"),
                "plix_recovery": ("plix_recovery", "PLIXRecovery"),
                "dev_accelerator": ("skills.dev_accelerator", "DevAccelerator"),
                "integrity_monitor": ("skills.integrity_monitor", "IntegrityMonitor"),
                "auto_chain_manager": (
                    "entities.auto_chain_manager",
                    "AutoChainManager",
                ),
                "profile_sanitizer": ("skills.profile_sanitizer", "ProfileSanitizer"),
            }

            if module_name in action_map:
                module_path, class_name = action_map[module_name]

                # Import dynamique
                import importlib

                module = importlib.import_module(module_path.replace(".", "_"))
                cls = getattr(module, class_name)
                instance = cls()

                method = getattr(instance, method_name)
                result = method()

                return {"success": True, "result": result}
            else:
                return {
                    "success": False,
                    "error": f"Unknown action module: {module_name}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _save_recovery_state(self, recovery_session):
        """Sauvegarde l'état de récupération"""
        with open(self.recovery_state, "w", encoding="utf-8") as f:
            json.dump(recovery_session, f, indent=2)

    def _notify_recovery_success(self, recovery_session):
        """Notifie le succès de récupération"""
        for channel in self.config["notification_channels"]:
            if channel == "console":
                print(
                    f"[CRASH_RECOVERY_VERSE] ✅ Recovery completed successfully in {len(recovery_session['strategies_attempted'])} attempts"
                )
            elif channel == "log":
                # Log détaillé
                pass

    def _notify_recovery_failure(self, recovery_session):
        """Notifie l'échec de récupération"""
        for channel in self.config["notification_channels"]:
            if channel == "console":
                print(
                    f"[CRASH_RECOVERY_VERSE] ❌ Recovery failed after {len(recovery_session['strategies_attempted'])} attempts"
                )
            elif channel == "log":
                # Log d'erreur détaillé
                pass

    def get_recovery_status(self):
        """Retourne le statut de récupération"""
        if os.path.exists(self.crash_history):
            try:
                with open(self.crash_history, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                history = []
        else:
            history = []

        recent_crashes = [
            c
            for c in history
            if (datetime.now() - datetime.fromisoformat(c["timestamp"])).days < 7
        ]

        return {
            "auto_recovery_enabled": self.config["auto_recovery"],
            "total_crashes": len(history),
            "recent_crashes_7d": len(recent_crashes),
            "last_crash": history[-1] if history else None,
            "recovery_success_rate": self._calculate_success_rate(history),
        }

    def _calculate_success_rate(self, history):
        """Calcule le taux de succès de récupération"""
        recoveries = [c for c in history if c.get("auto_recovery_triggered", False)]
        successful = [c for c in recoveries if c.get("recovery_success", False)]

        return len(successful) / len(recoveries) if recoveries else 0


if __name__ == "__main__":
    verse = CrashRecoveryVerse()

    # Simuler détection de crash
    crash = verse.detect_crash()
    if crash:
        print(f"Crash detected: {crash['severity']}")
    else:
        print("No crash detected")

    print("Recovery status:", verse.get_recovery_status())
