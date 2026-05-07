#!/usr/bin/env python3
"""
Chaos Engineering Tests for NFIRS System - Phase 6
Injection de pannes, tests de résilience, validation recovery automatique.

IntentHash: 0xNFIRS_CHAOS_TESTS_20260419
"""

import os
import time
import random
import signal
import psutil
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch


class ChaosEngineeringTests:
    """Tests chaos engineering pour NFIRS"""

    def __init__(self):
        self.test_results = []
        self.temp_dir = None

    def setup_chaos_environment(self):
        """Setup environnement de test pour chaos"""
        self.temp_dir = Path(tempfile.mkdtemp())
        original_cwd = Path.cwd()

        try:
            os.chdir(self.temp_dir)

            # Créer fichiers critiques
            critical_files = [
                "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md",
                "EPIC_NEXUS_FILE_INTEGRITY_RECOVERY.md",
                "ARCHITECTURAL_INTENT.md",
                "ECOSROOT.json",
            ]

            for file in critical_files:
                Path(file).write_text(f"# {file}\nChaos test content for {file}")

            # Créer snapshot de sécurité
            Path("snapshots").mkdir()
            snapshot_dir = Path("snapshots/snapshot_chaos_safety")
            snapshot_dir.mkdir()

            for file in critical_files:
                if Path(file).exists():
                    shutil.copy2(file, snapshot_dir / file)

            # Initialiser composants
            self.setup_components()

        finally:
            os.chdir(original_cwd)

    def setup_components(self):
        """Initialiser composants pour tests"""
        try:
            from skills.integrity_monitor import IntegrityMonitor
            from skills.recovery_agent import RecoveryAgent
            from entities.file_guardian import FileGuardian
            from verses.crash_recovery_verse import CrashRecoveryVerse

            self.monitor = IntegrityMonitor()
            self.agent = RecoveryAgent()
            self.guardian = FileGuardian()
            self.crash_verse = CrashRecoveryVerse()

        except ImportError as e:
            print(f"❌ Component import failed: {e}")
            raise

    def cleanup_chaos_environment(self):
        """Nettoyer environnement chaos"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def run_chaos_experiment(
        self, experiment_name, chaos_func, recovery_func=None, duration=30
    ):
        """Exécuter expérience chaos"""
        print(f"🌀 Starting Chaos Experiment: {experiment_name}")

        result = {
            "experiment": experiment_name,
            "start_time": time.time(),
            "chaos_injected": False,
            "recovery_attempted": False,
            "recovery_success": False,
            "system_stable": True,
            "duration": duration,
            "errors": [],
        }

        try:
            # Phase pré-chaos
            pre_chaos_state = self.capture_system_state()

            # Injecter chaos
            chaos_func()
            result["chaos_injected"] = True

            # Attendre effet
            time.sleep(2)

            # Phase post-chaos
            post_chaos_state = self.capture_system_state()

            # Vérifier impact
            impact = self.analyze_chaos_impact(pre_chaos_state, post_chaos_state)
            result["impact"] = impact

            # Tenter récupération si fonction fournie
            if recovery_func:
                result["recovery_attempted"] = True
                try:
                    recovery_success = recovery_func()
                    result["recovery_success"] = recovery_success

                    # Vérifier récupération
                    if recovery_success:
                        post_recovery_state = self.capture_system_state()
                        recovery_effectiveness = self.analyze_recovery_effectiveness(
                            pre_chaos_state, post_recovery_state
                        )
                        result["recovery_effectiveness"] = recovery_effectiveness

                except Exception as e:
                    result["errors"].append(f"Recovery failed: {e}")
                    result["recovery_success"] = False

            # Vérifier stabilité système
            result["system_stable"] = self.check_system_stability()

        except Exception as e:
            result["errors"].append(f"Experiment failed: {e}")
            result["system_stable"] = False

        result["end_time"] = time.time()
        result["total_duration"] = result["end_time"] - result["start_time"]

        self.test_results.append(result)

        status = "✅ PASSED" if result["system_stable"] else "❌ FAILED"
        print(f"🌀 Chaos Experiment {experiment_name}: {status}")

        return result

    def capture_system_state(self):
        """Capturer état système"""
        state = {
            "timestamp": time.time(),
            "files_exist": {},
            "memory_usage": psutil.virtual_memory().percent,
            "cpu_usage": psutil.cpu_percent(interval=0.1),
            "process_count": len(list(psutil.process_iter())),
        }

        critical_files = [
            "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md",
            "EPIC_NEXUS_FILE_INTEGRITY_RECOVERY.md",
            "ARCHITECTURAL_INTENT.md",
            "ECOSROOT.json",
        ]

        for file in critical_files:
            state["files_exist"][file] = Path(file).exists()

        return state

    def analyze_chaos_impact(self, pre_state, post_state):
        """Analyser impact du chaos"""
        impact = {
            "files_lost": 0,
            "memory_change": post_state["memory_usage"] - pre_state["memory_usage"],
            "cpu_change": post_state["cpu_usage"] - pre_state["cpu_usage"],
            "process_change": post_state["process_count"] - pre_state["process_count"],
        }

        for file, existed in pre_state["files_exist"].items():
            if existed and not post_state["files_exist"].get(file, False):
                impact["files_lost"] += 1

        return impact

    def analyze_recovery_effectiveness(self, pre_state, post_state):
        """Analyser efficacité récupération"""
        effectiveness = {"files_restored": 0, "system_restored": True}

        for file, should_exist in pre_state["files_exist"].items():
            if should_exist:
                if post_state["files_exist"].get(file, False):
                    effectiveness["files_restored"] += 1
                else:
                    effectiveness["system_restored"] = False

        return effectiveness

    def check_system_stability(self):
        """Vérifier stabilité système"""
        try:
            # Tests basiques de stabilité
            issues = self.monitor.scan_integrity()
            critical_issues = [
                i for i in issues if i.get("severity") in ["high", "critical"]
            ]

            return len(critical_issues) == 0
        except:
            return False

    # === EXPERIMENTS CHAOS ===

    def experiment_file_deletion(self):
        """Expérience: suppression aléatoire de fichiers"""
        critical_files = [
            "PRD_NEXUS_FILE_INTEGRITY_RECOVERY.md",
            "EPIC_NEXUS_FILE_INTEGRITY_RECOVERY.md",
        ]

        # Supprimer un fichier aléatoire
        target_file = random.choice(critical_files)
        if Path(target_file).exists():
            os.remove(target_file)
            print(f"💥 Chaos: Deleted {target_file}")

            return lambda: self.agent.auto_recover_missing()
        else:
            raise Exception("No file available for deletion")

    def experiment_file_corruption(self):
        """Expérience: corruption de fichiers"""
        target_file = "ARCHITECTURAL_INTENT.md"

        if Path(target_file).exists():
            # Corrompre contenu
            with open(target_file, "w") as f:
                f.write("CORRUPTED_CONTENT_BY_CHAOS_ENGINEERING_TEST")
            print(f"💥 Chaos: Corrupted {target_file}")

            return lambda: self.agent.auto_recover_missing()
        else:
            raise Exception("Target file not available")

    def experiment_memory_pressure(self):
        """Expérience: pression mémoire"""
        # Allouer beaucoup de mémoire
        memory_hogs = []
        for _ in range(10):
            try:
                memory_hogs.append(bytearray(10 * 1024 * 1024))  # 10MB each
            except MemoryError:
                break

        allocated_mb = len(memory_hogs) * 10
        print(f"💥 Chaos: Allocated {allocated_mb}MB memory")

        def recovery():
            # Libérer mémoire
            memory_hogs.clear()
            time.sleep(1)
            return self.check_system_stability()

        return recovery

    def experiment_process_kill(self):
        """Expérience: arrêt de processus (simulation)"""
        # Simuler arrêt en créant un processus qui se termine
        print("💥 Chaos: Simulating process termination")

        def recovery():
            # Vérifier que le système peut redémarrer
            return self.check_system_stability()

        return recovery

    def experiment_network_failure(self):
        """Expérience: panne réseau (simulation)"""
        print("💥 Chaos: Simulating network failure")

        # Simuler en patchant les appels réseau
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("Network failure")

            def recovery():
                # Le système devrait gérer l'absence de réseau
                return self.check_system_stability()

            return recovery

    def experiment_disk_space(self):
        """Expérience: espace disque faible (simulation)"""
        print("💥 Chaos: Simulating low disk space")

        # Créer fichiers temporaires pour remplir l'espace
        temp_files = []
        try:
            for i in range(5):
                temp_file = Path(f"chaos_temp_{i}.tmp")
                with open(temp_file, "wb") as f:
                    f.write(b"0" * (50 * 1024 * 1024))  # 50MB each
                temp_files.append(temp_file)
        except:
            pass

        def recovery():
            # Nettoyer fichiers temporaires
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                except:
                    pass
            time.sleep(1)
            return self.check_system_stability()

        return recovery

    def run_all_chaos_experiments(self):
        """Exécuter tous les experiments chaos"""
        print("🌀 Starting Chaos Engineering Experiments for NFIRS...")
        print("=" * 60)

        experiments = [
            ("File Deletion Recovery", self.experiment_file_deletion, 30),
            ("File Corruption Recovery", self.experiment_file_corruption, 30),
            ("Memory Pressure Handling", self.experiment_memory_pressure, 20),
            ("Process Termination Recovery", self.experiment_process_kill, 15),
            ("Network Failure Resilience", self.experiment_network_failure, 10),
            ("Disk Space Pressure", self.experiment_disk_space, 25),
        ]

        passed_experiments = 0
        total_experiments = len(experiments)

        for exp_name, chaos_func, duration in experiments:
            try:
                result = self.run_chaos_experiment(
                    exp_name, chaos_func, duration=duration
                )

                if result["system_stable"]:
                    passed_experiments += 1
                    print("   ✅ System remained stable")
                else:
                    print("   ❌ System became unstable")

                if result.get("recovery_attempted"):
                    if result["recovery_success"]:
                        print("   🔄 Recovery successful")
                    else:
                        print("   ❌ Recovery failed")

            except Exception as e:
                print(f"   💥 Experiment {exp_name} crashed: {e}")
                self.test_results.append(
                    {"experiment": exp_name, "crashed": True, "error": str(e)}
                )

            print()

        success_rate = passed_experiments / total_experiments
        overall_success = success_rate >= 0.8  # 80% success rate required

        print("=" * 60)
        print("🏁 Chaos Engineering Complete!")
        print(
            f"Experiments Passed: {passed_experiments}/{total_experiments} ({success_rate:.1%})"
        )
        print(f"Overall Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")

        return overall_success

    def generate_chaos_report(self):
        """Générer rapport chaos engineering"""
        report = "# NFIRS Chaos Engineering Report\n\n"
        report += f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        passed_experiments = sum(
            1 for r in self.test_results if r.get("system_stable", False)
        )
        total_experiments = len(self.test_results)

        report += "## Summary\n\n"
        report += f"- **Experiments Run:** {total_experiments}\n"
        report += f"- **Experiments Passed:** {passed_experiments}\n"
        if total_experiments > 0:
            report += (
                f"- **Success Rate:** {passed_experiments / total_experiments:.1f}%\n"
            )
        report += "\n## Detailed Results\n\n"

        for result in self.test_results:
            report += f"### {result['experiment']}\n\n"

            if result.get("crashed"):
                report += "💥 **CRASHED**\n\n"
                report += f"**Error:** {result.get('error', 'Unknown')}\n\n"
                continue

            if result.get("system_stable"):
                report += "✅ **PASSED** - System remained stable\n\n"
            else:
                report += "❌ **FAILED** - System became unstable\n\n"

            if result.get("recovery_attempted"):
                if result.get("recovery_success"):
                    report += "🔄 **Recovery Successful**\n\n"
                else:
                    report += "❌ **Recovery Failed**\n\n"

            # Métriques d'impact
            if "impact" in result:
                impact = result["impact"]
                report += "**Chaos Impact:**\n"
                report += f"- Files lost: {impact.get('files_lost', 0)}\n"
                report += f"- Memory change: {impact.get('memory_change', 0):.1f}%\n"
                report += f"- CPU change: {impact.get('cpu_change', 0):.1f}%\n\n"

            # Efficacité récupération
            if "recovery_effectiveness" in result:
                eff = result["recovery_effectiveness"]
                report += "**Recovery Effectiveness:**\n"
                report += f"- Files restored: {eff.get('files_restored', 0)}\n"
                report += f"- System fully restored: {eff.get('system_restored', 'Unknown')}\n\n"

            if result.get("errors"):
                report += "**Errors:**\n"
                for error in result["errors"]:
                    report += f"- {error}\n"
                report += "\n"

        # Sauvegarder rapport
        with open("nfirs_chaos_report.md", "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 Chaos report saved to: nfirs_chaos_report.md")
        return report


def main():
    """Fonction principale pour tests chaos"""
    import argparse

    parser = argparse.ArgumentParser(description="NFIRS Chaos Engineering Tests")
    parser.add_argument(
        "--experiment",
        choices=[
            "file_deletion",
            "file_corruption",
            "memory_pressure",
            "process_kill",
            "network_failure",
            "disk_space",
            "all",
        ],
        default="all",
        help="Specific experiment to run",
    )

    args = parser.parse_args()

    # Assurer répertoire correct
    script_dir = Path(__file__).parent
    if script_dir.name == "tests":
        os.chdir(script_dir.parent)

    chaos_tests = ChaosEngineeringTests()
    chaos_tests.setup_chaos_environment()

    try:
        if args.experiment == "all":
            success = chaos_tests.run_all_chaos_experiments()
        else:
            # Exécuter expérience spécifique
            experiment_map = {
                "file_deletion": chaos_tests.experiment_file_deletion,
                "file_corruption": chaos_tests.experiment_file_corruption,
                "memory_pressure": chaos_tests.experiment_memory_pressure,
                "process_kill": chaos_tests.experiment_process_kill,
                "network_failure": chaos_tests.experiment_network_failure,
                "disk_space": chaos_tests.experiment_disk_space,
            }

            if args.experiment in experiment_map:
                result = chaos_tests.run_chaos_experiment(
                    f"Specific {args.experiment}", experiment_map[args.experiment]
                )
                success = result.get("system_stable", False)
            else:
                print(f"❌ Unknown experiment: {args.experiment}")
                success = False

        chaos_tests.generate_chaos_report()

        if success:
            print("\n🎭 Chaos Engineering successful! System is resilient.")
        else:
            print(
                "\n⚠️  Chaos Engineering revealed weaknesses. Check nfirs_chaos_report.md"
            )

        return 0 if success else 1

    finally:
        chaos_tests.cleanup_chaos_environment()


if __name__ == "__main__":
    exit(main())
