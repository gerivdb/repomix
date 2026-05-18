#!/usr/bin/env python3
"""
FileIntegrity Verse - NFIRS Phase 5
Protection fichiers temps réel.

IntentHash: 0xFILE_INTEGRITY_VERSE_20260419
"""

import os
import json
import time
import hashlib
import threading
from datetime import datetime, timedelta
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileIntegrityVerse:
    """Verse pour protection intégrité fichiers temps réel"""

    def __init__(self):
        self.integrity_config = "file_integrity_config.json"
        self.integrity_state = "file_integrity_state.json"
        self.violation_log = "integrity_violations.log"
        self.observer = None
        self.monitor_thread = None
        self.is_monitoring = False
        self.load_config()

    def load_config(self):
        """Charge la configuration d'intégrité"""
        if os.path.exists(self.integrity_config):
            try:
                with open(self.integrity_config, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except:
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self.save_config()

    def _default_config(self):
        """Configuration par défaut"""
        return {
            "monitored_paths": ["."],
            "critical_files": [
                "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md",
                "EPIC_NEXUS_FILE_INTEGRITY_RECOVERY.md",
                "ARCHITECTURAL_INTENT.md",
                "ECOSROOT.json",
                "wal_nexus_extension.py",
                "plix_recovery.py",
            ],
            "protection_rules": {
                "prevent_deletion": True,
                "prevent_modification": False,  # Seulement alerte
                "auto_backup": True,
                "real_time_scan": True,
            },
            "scan_interval_seconds": 60,
            "violation_response": {
                "alert_console": True,
                "alert_log": True,
                "auto_recover": True,
                "escalate_high_severity": True,
            },
            "backup_settings": {
                "max_backups_per_file": 5,
                "backup_retention_days": 7,
                "compressed_backups": True,
            },
        }

    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.integrity_config, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def start_protection(self):
        """Démarre la protection temps réel"""
        if self.is_monitoring:
            print("[FILE_INTEGRITY_VERSE] Protection already active")
            return

        self.is_monitoring = True

        # Démarrer monitoring filesystem
        if self.config["protection_rules"]["real_time_scan"]:
            self._start_filesystem_monitoring()

        # Démarrer scan périodique
        self.monitor_thread = threading.Thread(target=self._periodic_scan, daemon=True)
        self.monitor_thread.start()

        print("[FILE_INTEGRITY_VERSE] File integrity protection activated")

        # Scan initial
        self.perform_integrity_scan()

    def stop_protection(self):
        """Arrête la protection"""
        self.is_monitoring = False

        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        print("[FILE_INTEGRITY_VERSE] File integrity protection deactivated")

    def _start_filesystem_monitoring(self):
        """Démarre le monitoring filesystem"""
        event_handler = IntegrityEventHandler(self)
        self.observer = Observer()

        for path in self.config["monitored_paths"]:
            if os.path.exists(path):
                self.observer.schedule(event_handler, path, recursive=True)

        self.observer.start()

    def _periodic_scan(self):
        """Scan périodique d'intégrité"""
        while self.is_monitoring:
            time.sleep(self.config["scan_interval_seconds"])
            if self.is_monitoring:  # Vérifier encore après sleep
                self.perform_integrity_scan()

    def perform_integrity_scan(self):
        """Effectue un scan d'intégrité complet"""
        violations = []

        for file_path in self.config["critical_files"]:
            if os.path.exists(file_path):
                violation = self._check_file_integrity(file_path)
                if violation:
                    violations.append(violation)
            else:
                violations.append(
                    {
                        "file": file_path,
                        "type": "missing",
                        "severity": "high",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        if violations:
            self._handle_violations(violations)

        return violations

    def _check_file_integrity(self, file_path):
        """Vérifie l'intégrité d'un fichier"""
        try:
            # Calculer hash actuel
            current_hash = self._calculate_file_hash(file_path)

            # Charger hash de référence
            baseline_hash = self._get_baseline_hash(file_path)

            if baseline_hash and current_hash != baseline_hash:
                return {
                    "file": file_path,
                    "type": "modified",
                    "severity": "medium",
                    "current_hash": current_hash,
                    "baseline_hash": baseline_hash,
                    "timestamp": datetime.now().isoformat(),
                }

            # Mettre à jour baseline si pas défini
            if not baseline_hash:
                self._update_baseline_hash(file_path, current_hash)

        except Exception as e:
            return {
                "file": file_path,
                "type": "error",
                "severity": "high",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

        return None

    def _calculate_file_hash(self, file_path):
        """Calcule le hash SHA256 d'un fichier"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return None

    def _get_baseline_hash(self, file_path):
        """Récupère le hash de référence"""
        if os.path.exists(self.integrity_state):
            try:
                with open(self.integrity_state, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    return state.get("baselines", {}).get(file_path)
            except:
                pass
        return None

    def _update_baseline_hash(self, file_path, hash_value):
        """Met à jour le hash de référence"""
        if os.path.exists(self.integrity_state):
            try:
                with open(self.integrity_state, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except:
                state = {"baselines": {}, "last_scan": None}
        else:
            state = {"baselines": {}, "last_scan": None}

        state["baselines"][file_path] = hash_value
        state["last_scan"] = datetime.now().isoformat()

        with open(self.integrity_state, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def _handle_violations(self, violations):
        """Gère les violations d'intégrité"""
        for violation in violations:
            self._log_violation(violation)
            self._respond_to_violation(violation)

    def _log_violation(self, violation):
        """Log une violation"""
        with open(self.violation_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(violation) + "\n")

    def _respond_to_violation(self, violation):
        """Répond à une violation"""
        severity = violation.get("severity", "low")
        violation_type = violation.get("type", "unknown")

        # Alertes
        if self.config["violation_response"]["alert_console"]:
            print(
                f"[FILE_INTEGRITY_VERSE] VIOLATION: {violation['file']} - {violation_type} (severity: {severity})"
            )

        # Auto-recovery pour fichiers critiques manquants
        if (
            violation_type == "missing"
            and self.config["violation_response"]["auto_recover"]
            and severity == "high"
        ):
            self._attempt_auto_recovery(violation)

        # Escalade pour violations haute sévérité
        if (
            severity == "high"
            and self.config["violation_response"]["escalate_high_severity"]
        ):
            self._escalate_violation(violation)

    def _attempt_auto_recovery(self, violation):
        """Tente récupération automatique"""
        file_path = violation["file"]

        try:
            from skills.recovery_agent import RecoveryAgent

            agent = RecoveryAgent()
            success = agent.auto_recover_missing()

            if success:
                print(
                    f"[FILE_INTEGRITY_VERSE] Auto-recovery successful for {file_path}"
                )
            else:
                print(f"[FILE_INTEGRITY_VERSE] Auto-recovery failed for {file_path}")

        except Exception as e:
            print(f"[FILE_INTEGRITY_VERSE] Auto-recovery error: {e}")

    def _escalate_violation(self, violation):
        """Escalade une violation"""
        print(
            f"[FILE_INTEGRITY_VERSE] ESCALATING: High severity violation for {violation['file']}"
        )

        # Ici on pourrait envoyer des notifications, créer des issues, etc.

    def create_backup(self, file_path):
        """Crée une sauvegarde d'un fichier"""
        if not self.config["protection_rules"]["auto_backup"]:
            return

        try:
            backup_dir = Path("backups") / Path(file_path).name
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Créer backup avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = (
                backup_dir
                / f"{Path(file_path).stem}_{timestamp}{Path(file_path).suffix}"
            )

            import shutil

            shutil.copy2(file_path, backup_path)

            # Nettoyer anciens backups
            self._cleanup_old_backups(backup_dir)

            print(f"[FILE_INTEGRITY_VERSE] Backup created: {backup_path}")

        except Exception as e:
            print(f"[FILE_INTEGRITY_VERSE] Backup failed: {e}")

    def _cleanup_old_backups(self, backup_dir):
        """Nettoie les anciens backups"""
        try:
            backups = sorted(backup_dir.glob("*"), reverse=True)
            max_backups = self.config["backup_settings"]["max_backups_per_file"]

            if len(backups) > max_backups:
                for old_backup in backups[max_backups:]:
                    old_backup.unlink()

            # Supprimer backups trop anciens
            cutoff = datetime.now() - timedelta(
                days=self.config["backup_settings"]["backup_retention_days"]
            )
            for backup in backups:
                try:
                    # Extraire timestamp du nom de fichier
                    timestamp_str = backup.stem.split("_")[-1]
                    backup_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    if backup_time < cutoff:
                        backup.unlink()
                except:
                    continue

        except Exception as e:
            print(f"[FILE_INTEGRITY_VERSE] Cleanup error: {e}")

    def get_integrity_status(self):
        """Retourne le statut d'intégrité"""
        last_scan = None
        violation_count = 0

        if os.path.exists(self.integrity_state):
            try:
                with open(self.integrity_state, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    last_scan = state.get("last_scan")
            except:
                pass

        if os.path.exists(self.violation_log):
            try:
                with open(self.violation_log, "r", encoding="utf-8") as f:
                    violation_count = len(f.readlines())
            except:
                pass

        return {
            "protection_active": self.is_monitoring,
            "monitored_files": len(self.config["critical_files"]),
            "last_scan": last_scan,
            "total_violations": violation_count,
            "auto_backup_enabled": self.config["protection_rules"]["auto_backup"],
        }


class IntegrityEventHandler(FileSystemEventHandler):
    """Gestionnaire d'événements filesystem pour l'intégrité"""

    def __init__(self, integrity_verse):
        self.verse = integrity_verse

    def on_modified(self, event):
        if (
            not event.is_directory
            and event.src_path in self.verse.config["critical_files"]
        ):
            print(f"[FILE_INTEGRITY_VERSE] File modified: {event.src_path}")
            self.verse.create_backup(event.src_path)
            # Vérifier intégrité après modification
            violation = self.verse._check_file_integrity(event.src_path)
            if violation:
                self.verse._handle_violations([violation])

    def on_deleted(self, event):
        if (
            not event.is_directory
            and event.src_path in self.verse.config["critical_files"]
        ):
            print(f"[FILE_INTEGRITY_VERSE] CRITICAL: File deleted: {event.src_path}")

            if self.verse.config["protection_rules"]["prevent_deletion"]:
                # Tenter récupération immédiate
                violation = {
                    "file": event.src_path,
                    "type": "deleted",
                    "severity": "critical",
                    "timestamp": datetime.now().isoformat(),
                }
                self.verse._handle_violations([violation])


if __name__ == "__main__":
    verse = FileIntegrityVerse()
    verse.start_protection()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        verse.stop_protection()
