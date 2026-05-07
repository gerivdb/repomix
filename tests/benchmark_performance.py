#!/usr/bin/env python3
"""
Performance Benchmarks for NFIRS System - Phase 6
Benchmarks performance et scalabilité, validation targets.

IntentHash: 0xNFIRS_BENCHMARKS_20260419
"""

import os
import time
import psutil
import statistics
from pathlib import Path
import tempfile
import shutil


class NFIRSPerformanceBenchmarks:
    """Benchmarks de performance pour le système NFIRS"""

    def __init__(self):
        self.results = {}
        self.temp_dir = None

    def setup_test_environment(self, num_files=100):
        """Setup environnement de test avec fichiers"""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Créer fichiers de test
        for i in range(num_files):
            test_file = self.temp_dir / "02d"
            test_file.write_text(f"# Test File {i}\n" + "Content line\n" * 10)

        # Créer snapshot
        snapshot_dir = self.temp_dir / "snapshots" / "benchmark_snapshot"
        snapshot_dir.mkdir(parents=True)

        for test_file in self.temp_dir.glob("*.md"):
            shutil.copy2(test_file, snapshot_dir / test_file.name)

        return self.temp_dir

    def cleanup_test_environment(self):
        """Nettoyer environnement de test"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def benchmark_recovery_time(self, num_files=10):
        """Benchmark temps de récupération"""
        print("[BENCHMARK] Benchmarking recovery time...")

        test_dir = self.setup_test_environment(num_files)
        original_cwd = Path.cwd()
        os.chdir(test_dir)

        try:
            from plix_recovery import PLIXRecovery

            # Supprimer fichiers
            deleted_files = []
            for i in range(min(5, num_files)):
                file_path = test_dir / "02d"
                if file_path.exists():
                    os.remove(file_path)
                    deleted_files.append(f"test_{i:02d}.md")

            if not deleted_files:
                return {"error": "No files to recover"}

            # Mesurer récupération
            plix = PLIXRecovery()

            start_time = time.time()
            recovered = 0

            for file in deleted_files:
                try:
                    success = plix.reconstruct_from_snapshot("benchmark_snapshot", file)
                    if success:
                        recovered += 1
                except:
                    pass

            recovery_time = time.time() - start_time

            result = {
                "operation": "file_recovery",
                "files_attempted": len(deleted_files),
                "files_recovered": recovered,
                "total_time_seconds": recovery_time,
                "avg_time_per_file": recovery_time / len(deleted_files),
                "success_rate": recovered / len(deleted_files),
                "meets_target": recovery_time < 300,  # < 5 minutes
            }

            self.results["recovery_time"] = result
            return result

        finally:
            os.chdir(original_cwd)
            self.cleanup_test_environment()

    def benchmark_integrity_scan(self, num_files=50):
        """Benchmark scan d'intégrité"""
        print("🔬 Benchmarking integrity scan...")

        test_dir = self.setup_test_environment(num_files)
        original_cwd = Path.cwd()
        os.chdir(test_dir)

        try:
            from skills.integrity_monitor import IntegrityMonitor

            monitor = IntegrityMonitor()

            # Mesurer plusieurs scans
            times = []
            issues = []

            for _ in range(5):
                start_time = time.time()
                current_issues = monitor.scan_integrity()
                scan_time = time.time() - start_time
                times.append(scan_time)
                issues = current_issues  # Keep last scan results

            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)

            result = {
                "operation": "integrity_scan",
                "files_scanned": num_files,
                "avg_time_seconds": avg_time,
                "min_time_seconds": min_time,
                "max_time_seconds": max_time,
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                "issues_found": len(issues),
                "meets_target": avg_time < 2.0,  # < 2 secondes pour 50 fichiers
            }

            self.results["integrity_scan"] = result
            return result

        finally:
            os.chdir(original_cwd)
            self.cleanup_test_environment()

    def benchmark_memory_usage(self):
        """Benchmark utilisation mémoire"""
        print("🔬 Benchmarking memory usage...")

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Importer composants
        imports = [
            ("plix_recovery", "PLIXRecovery"),
            ("skills.integrity_monitor", "IntegrityMonitor"),
            ("skills.recovery_agent", "RecoveryAgent"),
            ("entities.file_guardian", "FileGuardian"),
            ("verses.file_integrity_verse", "FileIntegrityVerse"),
        ]

        memory_peaks = []

        for module, cls in imports:
            try:
                __import__(module)
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_peaks.append(current_memory - initial_memory)
            except:
                continue

        avg_memory_increase = statistics.mean(memory_peaks) if memory_peaks else 0
        max_memory_increase = max(memory_peaks) if memory_peaks else 0

        result = {
            "operation": "memory_usage",
            "components_loaded": len(memory_peaks),
            "avg_memory_increase_mb": avg_memory_increase,
            "max_memory_increase_mb": max_memory_increase,
            "initial_memory_mb": initial_memory,
            "meets_target": max_memory_increase < 100,  # < 100 MB increase
        }

        self.results["memory_usage"] = result
        return result

    def benchmark_concurrent_operations(self, num_threads=5):
        """Benchmark opérations concurrentes"""
        print("🔬 Benchmarking concurrent operations...")

        import threading
        import queue

        test_dir = self.setup_test_environment(20)
        original_cwd = Path.cwd()
        os.chdir(test_dir)

        try:
            results_queue = queue.Queue()

            def worker_thread(thread_id):
                try:
                    from skills.integrity_monitor import IntegrityMonitor

                    monitor = IntegrityMonitor()

                    start_time = time.time()
                    issues = monitor.scan_integrity()
                    end_time = time.time()

                    results_queue.put(
                        {
                            "thread_id": thread_id,
                            "duration": end_time - start_time,
                            "issues_found": len(issues),
                            "success": True,
                        }
                    )
                except Exception as e:
                    results_queue.put(
                        {"thread_id": thread_id, "error": str(e), "success": False}
                    )

            # Lancer threads
            threads = []
            for i in range(num_threads):
                t = threading.Thread(target=worker_thread, args=(i,))
                threads.append(t)
                t.start()

            # Attendre completion
            for t in threads:
                t.join(timeout=10)

            # Collecter résultats
            results = []
            while not results_queue.empty():
                results.append(results_queue.get())

            successful = [r for r in results if r.get("success", False)]
            avg_duration = (
                statistics.mean([r["duration"] for r in successful])
                if successful
                else 0
            )

            result = {
                "operation": "concurrent_operations",
                "threads_launched": num_threads,
                "threads_completed": len(successful),
                "avg_duration_seconds": avg_duration,
                "success_rate": len(successful) / num_threads,
                "meets_target": avg_duration < 5.0,  # < 5 secondes en moyenne
            }

            self.results["concurrent_operations"] = result
            return result

        finally:
            os.chdir(original_cwd)
            self.cleanup_test_environment()

    def benchmark_system_scalability(self):
        """Benchmark scalabilité système"""
        print("🔬 Benchmarking system scalability...")

        file_counts = [10, 50, 100]
        scalability_results = {}

        for num_files in file_counts:
            print(f"   Testing with {num_files} files...")

            test_dir = self.setup_test_environment(num_files)
            original_cwd = Path.cwd()
            os.chdir(test_dir)

            try:
                from skills.integrity_monitor import IntegrityMonitor

                monitor = IntegrityMonitor()

                start_time = time.time()
                issues = monitor.scan_integrity()
                scan_time = time.time() - start_time

                scalability_results[str(num_files)] = {
                    "files": num_files,
                    "scan_time": scan_time,
                    "time_per_file": scan_time / num_files,
                    "issues": len(issues),
                }

            finally:
                os.chdir(original_cwd)
                self.cleanup_test_environment()

        # Analyser scalabilité
        times = [r["scan_time"] for r in scalability_results.values()]
        scaling_factor = times[-1] / times[0] if times[0] > 0 else float("inf")

        result = {
            "operation": "scalability_test",
            "file_counts_tested": file_counts,
            "results": scalability_results,
            "scaling_factor": scaling_factor,
            "meets_target": scaling_factor
            < 10,  # Pas plus de 10x plus lent pour 10x plus de fichiers
        }

        self.results["scalability"] = result
        return result

    def run_all_benchmarks(self):
        """Exécuter tous les benchmarks"""
        print("[START] Starting NFIRS Performance Benchmarks...")
        print("=" * 50)

        benchmarks = [
            ("Recovery Time", self.benchmark_recovery_time),
            ("Integrity Scan", self.benchmark_integrity_scan),
            ("Memory Usage", self.benchmark_memory_usage),
            ("Concurrent Operations", self.benchmark_concurrent_operations),
            ("System Scalability", self.benchmark_system_scalability),
        ]

        all_passed = True

        for name, benchmark_func in benchmarks:
            try:
                print(f"\n📊 Running {name} Benchmark...")
                result = benchmark_func()

                if result.get("meets_target", False):
                    print("✅ PASSED")
                else:
                    print("❌ FAILED")
                    all_passed = False

                # Afficher métriques clés
                if "total_time_seconds" in result:
                    print(f"   ⏱️  Total time: {result['total_time_seconds']:.2f}s")
                if "avg_time_seconds" in result:
                    print(f"   📈 Avg time: {result['avg_time_seconds']:.3f}s")
                if "success_rate" in result:
                    print(f"   🎯 Success rate: {result['success_rate']:.1%}")
                if "max_memory_increase_mb" in result:
                    print(
                        f"   💾 Memory increase: {result['max_memory_increase_mb']:.1f}MB"
                    )

            except Exception as e:
                print(f"❌ {name} Benchmark ERROR: {e}")
                all_passed = False

        print("\n" + "=" * 50)
        print("🏁 Benchmarks Complete!")
        print(f"Overall Result: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")

        return all_passed

    def generate_report(self):
        """Générer rapport de benchmarks"""
        report = "# NFIRS Performance Benchmarks Report\n\n"
        report += f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "## Summary\n\n"
        total_benchmarks = len(self.results)
        passed_benchmarks = sum(
            1 for r in self.results.values() if r.get("meets_target", False)
        )

        report += f"- **Benchmarks Run:** {total_benchmarks}\n"
        report += f"- **Benchmarks Passed:** {passed_benchmarks}\n"
        report += f"- **Success Rate:** {passed_benchmarks / total_benchmarks:.1f}%\n"
        report += "\n## Detailed Results\n\n"

        for benchmark_name, result in self.results.items():
            report += f"### {benchmark_name.replace('_', ' ').title()}\n\n"

            if result.get("meets_target"):
                report += "✅ **PASSED**\n\n"
            else:
                report += "❌ **FAILED**\n\n"

            # Métriques clés
            for key, value in result.items():
                if key not in ["meets_target", "operation"]:
                    if isinstance(value, float):
                        report += f"- **{key}:** {value:.3f}\n"
                    else:
                        report += f"- **{key}:** {value}\n"

            report += "\n"

        # Sauvegarder rapport
        with open("nfirs_benchmarks_report.md", "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 Benchmark report saved to: nfirs_benchmarks_report.md")
        return report


if __name__ == "__main__":
    import os

    # Assurer que nous sommes dans le bon répertoire
    script_dir = Path(__file__).parent
    if script_dir.name == "tests":
        os.chdir(script_dir.parent)

    # Exécuter benchmarks
    benchmarks = NFIRSPerformanceBenchmarks()
    success = benchmarks.run_all_benchmarks()
    benchmarks.generate_report()

    if success:
        print("\n🎉 All performance targets met! NFIRS Phase 6 benchmarks successful.")
    else:
        print(
            "\n⚠️  Some benchmarks failed. Check nfirs_benchmarks_report.md for details."
        )

    exit(0 if success else 1)
