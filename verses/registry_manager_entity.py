#!/usr/bin/env python3
"""
RegistryManager Entity - Main Implementation
SCO-7 Critical Implementation for 100% Repository Traceability

IntentHash: 0xREGISTRY_MANAGER_IMPLEMENTATION_20260422
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("RegistryManager")


@dataclass
class RepoMetadata:
    """Complete repository metadata"""

    name: str
    local_path: str
    is_git_repo: bool = False
    has_readme: bool = False
    has_dockerfile: bool = False
    file_count: int = 0
    total_size_mb: float = 0.0
    languages: List[str] = None
    criticality: str = "P3"
    layer: str = "L3"
    scan_timestamp: str = ""

    def __post_init__(self):
        if self.languages is None:
            self.languages = []


class RepositoryScanner:
    """Scans all local repositories with complete metadata extraction"""

    def __init__(self):
        self.local_roots = ["D:\\DO\\WEB", "D:\\DO\\WEB\\TOOLS", "C:\\DevTools"]
        self.skip_patterns = {".git", "node_modules", "__pycache__", ".vscode"}

    def scan_all_repositories(self) -> Dict[str, RepoMetadata]:
        """Scan all repositories in parallel"""
        logger.info("Starting repository scan...")

        all_repos = {}

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for root in self.local_roots:
                if os.path.exists(root):
                    futures.append(executor.submit(self._scan_directory_tree, root))

            for future in as_completed(futures):
                try:
                    repos = future.result()
                    all_repos.update(repos)
                except Exception as e:
                    logger.error(f"Scan failed: {e}")

        logger.info(f"Scan completed: {len(all_repos)} repositories found")
        return all_repos

    def _scan_directory_tree(self, root_path: str) -> Dict[str, RepoMetadata]:
        """Recursively scan directory tree"""
        repos = {}

        try:
            for item in os.listdir(root_path):
                item_path = os.path.join(root_path, item)
                if os.path.isdir(item_path) and not item.startswith("."):
                    # Check if it's a repository
                    metadata = self._analyze_repository(item_path, item)
                    if metadata:
                        repos[item] = metadata

        except PermissionError:
            logger.warning(f"Permission denied: {root_path}")
        except Exception as e:
            logger.error(f"Error scanning {root_path}: {e}")

        return repos

    def _analyze_repository(self, path: str, name: str) -> Optional[RepoMetadata]:
        """Analyze single repository with complete metadata"""
        try:
            # Basic checks
            is_git = os.path.exists(os.path.join(path, ".git"))

            # File analysis
            file_count = 0
            total_size = 0
            languages = set()

            for root, dirs, files in os.walk(path):
                # Skip unwanted directories
                dirs[:] = [d for d in dirs if d not in self.skip_patterns]

                for file in files:
                    if not file.startswith("."):
                        file_count += 1
                        try:
                            total_size += os.path.getsize(os.path.join(root, file))

                            # Language detection
                            ext = os.path.splitext(file)[1].lower()
                            if ext in [".py"]:
                                languages.add("Python")
                            elif ext in [".rs"]:
                                languages.add("Rust")
                            elif ext in [".js", ".ts"]:
                                languages.add("JavaScript")
                            elif ext in [".go"]:
                                languages.add("Go")

                        except OSError:
                            pass  # Skip files we can't access

                        # Prevent excessive scanning
                        if file_count > 10000:
                            break

                if file_count > 10000:
                    break

            # Special files
            has_readme = any(
                os.path.exists(os.path.join(path, f))
                for f in ["README.md", "README.txt", "README", "readme.md"]
            )
            has_dockerfile = os.path.exists(os.path.join(path, "Dockerfile"))

            # Basic classification (can be enhanced with ML later)
            criticality = self._infer_criticality(name, languages)
            layer = self._infer_layer(name, languages)

            return RepoMetadata(
                name=name,
                local_path=path,
                is_git_repo=is_git,
                has_readme=has_readme,
                has_dockerfile=has_dockerfile,
                file_count=file_count,
                total_size_mb=round(total_size / (1024 * 1024), 2),
                languages=list(languages),
                criticality=criticality,
                layer=layer,
                scan_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            logger.error(f"Error analyzing {name}: {e}")
            return None

    def _infer_criticality(self, name: str, languages: set) -> str:
        """Basic criticality inference"""
        name_lower = name.lower()

        # P0 Constitutional
        if any(
            keyword in name_lower
            for keyword in ["kiva", "nexus", "gateway-manager", "brain", "ecosystem"]
        ):
            return "P0"

        # P1 Strategic
        if any(keyword in name_lower for keyword in ["fluence", "tina", "gericode"]):
            return "P1"

        # P2 Support
        if any(keyword in name_lower for keyword in ["cli", "docs", "tool"]):
            return "P2"

        # Default P3
        return "P3"

    def _infer_layer(self, name: str, languages: set) -> str:
        """Basic layer inference"""
        name_lower = name.lower()

        # L1 Causality (core infrastructure)
        if any(keyword in name_lower for keyword in ["kiva", "nexus", "gateway"]):
            return "L1"

        # L2 Composition (tooling)
        if "cli" in name_lower or "tool" in name_lower:
            return "L2"

        # L3 Emergence (applications)
        if any(keyword in name_lower for keyword in ["brain", "fluence", "app"]):
            return "L3"

        # Default L3
        return "L3"


class RegistryValidator:
    """Validates registry completeness and consistency"""

    def __init__(self):
        self.registry_sources = [
            "ecosystem/registry/ECOS_ROOT.json",
            "ecosystem/registry/repos.json",
            "registry/repo_map.yaml",
        ]

    def validate_completeness(
        self, local_repos: Dict[str, RepoMetadata]
    ) -> Dict[str, Any]:
        """Validate registry completeness against local repos"""
        logger.info("Validating registry completeness...")

        # Load registered repos
        registered_repos = self._load_all_registry_sources()

        # Calculate completeness
        local_names = set(local_repos.keys())
        registered_names = set(registered_repos.keys())

        missing = list(local_names - registered_names)
        orphaned = list(registered_names - local_names)

        completeness_score = (
            len(registered_names) / len(local_names) * 100 if local_names else 0
        )

        result = {
            "total_local": len(local_repos),
            "total_registered": len(registered_repos),
            "completeness_score": round(completeness_score, 1),
            "missing_count": len(missing),
            "orphaned_count": len(orphaned),
            "missing_repos": missing[:50],  # Limit for readability
            "orphaned_entries": orphaned[:20],
            "validation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "CRITICAL" if completeness_score < 95 else "HEALTHY",
        }

        logger.info(f"Validation complete: {completeness_score:.1f}% completeness")
        return result

    def _load_all_registry_sources(self) -> Dict[str, dict]:
        """Load all registry sources"""
        all_registered = {}

        for source in self.registry_sources:
            source_path = (
                os.path.join("NEXUS", source) if not os.path.isabs(source) else source
            )

            if os.path.exists(source_path):
                try:
                    if source.endswith(".json"):
                        with open(source_path, "r", encoding="utf-8") as f:
                            data = json.load(f)

                        # Extract repo names based on format
                        if "repos" in data:
                            # ECOS_ROOT.json format
                            for repo_name in data["repos"].keys():
                                all_registered[repo_name] = data["repos"][repo_name]
                        elif "repositories" in data:
                            # repos.json format
                            for repo in data["repositories"]:
                                all_registered[repo["name"]] = repo

                    logger.info(f"Loaded {len(all_registered)} repos from {source}")

                except Exception as e:
                    logger.error(f"Error loading {source}: {e}")
            else:
                logger.warning(f"Registry source not found: {source}")

        return all_registered


class AutoRegistrar:
    """Automatically registers missing repositories"""

    def __init__(self):
        self.validator = RegistryValidator()

    def register_missing_repos(
        self, local_repos: Dict[str, RepoMetadata]
    ) -> Dict[str, Any]:
        """Register all missing repositories"""
        logger.info("Starting auto-registration...")

        # Get validation results
        validation = self.validator.validate_completeness(local_repos)

        if validation["missing_count"] == 0:
            logger.info("No missing repositories to register")
            return {"registered": [], "skipped": 0, "errors": 0}

        registered = []
        errors = 0

        # Load current registry
        registry_path = os.path.join("NEXUS", "ecosystem/registry/ECOS_ROOT.json")

        if not os.path.exists(registry_path):
            logger.error("Registry file not found")
            return {"registered": [], "skipped": 0, "errors": 1}

        # Load and update registry
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                registry_data = json.load(f)

            repos_section = registry_data.setdefault("repos", {})

            for repo_name in validation["missing"]:
                if repo_name in local_repos:
                    repo_data = local_repos[repo_name]

                    # Create registry entry
                    registry_entry = {
                        "tier": self._map_layer_to_tier(repo_data.layer),
                        "lifecycle": "ACTIVE",
                        "lang": self._detect_primary_language(repo_data.languages),
                        "private": True,
                        "open_issues": 0,
                        "last_pushed": time.strftime("%Y-%m-%d"),
                        "criticality": repo_data.criticality,
                        "layer": repo_data.layer,
                        "url": f"https://github.com/gerivdb/{repo_name}",
                        "description": f"Auto-registered repository: {repo_name}",
                        "entry_point": self._infer_entry_point(repo_data),
                        "dependencies": [],
                        "has_readme": repo_data.has_readme,
                        "has_dockerfile": repo_data.has_dockerfile,
                        "ci_status": "unknown",
                        "test_coverage": "unknown",
                    }

                    repos_section[repo_name] = registry_entry
                    registered.append(repo_name)
                    logger.info(f"Registered: {repo_name}")

            # Save updated registry
            with open(registry_path, "w", encoding="utf-8") as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"Auto-registration complete: {len(registered)} repos registered"
            )

        except Exception as e:
            logger.error(f"Auto-registration failed: {e}")
            errors += 1

        return {
            "registered": registered,
            "skipped": validation["missing_count"] - len(registered),
            "errors": errors,
        }

    def _map_layer_to_tier(self, layer: str) -> str:
        """Map layer to tier"""
        layer_to_tier = {
            "L1": "T1-CORE",
            "L2": "T1-INFRA",
            "L3": "T2-APPS",
            "L4": "T2-APPS",
            "L5": "T2-APPS",
        }
        return layer_to_tier.get(layer, "T2-APPS")

    def _detect_primary_language(self, languages: List[str]) -> str:
        """Detect primary language"""
        if "Python" in languages:
            return "Python"
        elif "Rust" in languages:
            return "Rust"
        elif "JavaScript" in languages:
            return "TypeScript"
        elif "Go" in languages:
            return "Go"
        return "Unknown"

    def _infer_entry_point(self, repo_data: RepoMetadata) -> str:
        """Infer entry point based on repo characteristics"""
        if repo_data.has_dockerfile:
            return "Dockerfile"
        elif "Python" in repo_data.languages:
            return "src/main.py"
        elif "Rust" in repo_data.languages:
            return "src/main.rs"
        elif "Go" in repo_data.languages:
            return "main.go"
        else:
            return "README.md"


class RegistryManager:
    """Main RegistryManager Entity"""

    def __init__(self):
        self.scanner = RepositoryScanner()
        self.validator = RegistryValidator()
        self.registrar = AutoRegistrar()

    def ensure_complete_traceability(self) -> Dict[str, Any]:
        """Main method: ensure 100% traceability"""
        logger.info("RegistryManager: Ensuring complete traceability...")

        # 1. Scan all repositories
        local_repos = self.scanner.scan_all_repositories()

        # 2. Validate completeness
        validation = self.validator.validate_completeness(local_repos)

        # 3. Auto-register missing repos if needed
        registration_result = None
        if validation["completeness_score"] < 100.0:
            logger.warning(
                f"Completeness {validation['completeness_score']:.1f}% < 100%, auto-registering..."
            )
            registration_result = self.registrar.register_missing_repos(local_repos)

            # Re-validate after registration
            if registration_result and registration_result["registered"]:
                local_repos = self.scanner.scan_all_repositories()
                validation = self.validator.validate_completeness(local_repos)

        # 4. Generate comprehensive report
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "intent_hash": "0xREGISTRY_MANAGER_IMPLEMENTATION_20260422",
            "version": "1.0.0",
            "scan_results": {
                "total_repos": len(local_repos),
                "git_repos": len([r for r in local_repos.values() if r.is_git_repo]),
                "sample_repos": list(local_repos.keys())[:5],
            },
            "validation_results": validation,
            "registration_results": registration_result,
            "final_status": "SUCCESS"
            if validation["completeness_score"] >= 95.0
            else "REQUIRES_ATTENTION",
        }

        logger.info(
            f"RegistryManager complete: {validation['completeness_score']:.1f}% traceability achieved"
        )
        return report


def main():
    """Main entry point"""
    print("=== RegistryManager Entity Implementation ===")
    print("SCO-7 Critical: Ensuring 100% Repository Traceability")
    print()

    manager = RegistryManager()
    report = manager.ensure_complete_traceability()

    # Display results
    print("\n=== RESULTS ===")
    print(f"Total Repositories: {report['scan_results']['total_repos']}")
    print(f"Git Repositories: {report['scan_results']['git_repos']}")
    print(f"Completeness: {report['validation_results']['completeness_score']:.1f}%")
    print(f"Missing Repos: {report['validation_results']['missing_count']}")

    if report["registration_results"]:
        print(f"Auto-Registered: {len(report['registration_results']['registered'])}")

    print(f"Final Status: {report['final_status']}")

    # Save detailed report
    report_path = "registry_manager_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nDetailed report saved to: {report_path}")

    # Exit with appropriate code
    success = report["validation_results"]["completeness_score"] >= 95.0
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
