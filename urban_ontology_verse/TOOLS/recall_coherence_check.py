#!/usr/bin/env python3
"""
recall_coherence_check.py — Vérifie la cohérence entre recall packs et relais déployés.
UrbanVerse | gerivdb/VERSUS | Version: 1.0.0
"""

import yaml
import sys
from pathlib import Path
from datetime import date

VERSUS_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = VERSUS_ROOT / "urban_ontology_verse" / "RELAYS" / "relay_wave_manifest.yaml"
SYNC_PATH = VERSUS_ROOT / "urban_ontology_verse" / "SYNC" / "recall_relay_sync.md"

REQUIRED_SECTIONS_WAVE1 = [
    "Identité stratique",
    "Navigation rapide",
    "Règles locales",
    "Vague de mise à jour",
]

REQUIRED_SECTIONS_WAVE2 = REQUIRED_SECTIONS_WAVE1 + [
    "Karpathy",
]

CRITICAL_LINKS = [
    "PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md",
    "gerivdb/LLM-REPO",
    "transit_map.yaml",
]


def check_relay_content(repo_name: str, wave: int, content: str) -> list:
    """Returns list of errors for a given relay content."""
    errors = []
    required = REQUIRED_SECTIONS_WAVE2 if wave >= 2 else REQUIRED_SECTIONS_WAVE1

    for section in required:
        if section not in content:
            errors.append("  Section manquante : '{}'".format(section))

    for link in CRITICAL_LINKS:
        if link not in content:
            errors.append("  Lien critique absent : '{}'".format(link))

    return errors


def run_check(relay_dir: Path) -> dict:
    """Scan a directory for STRATUM_RELAY.md and validate."""
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    results = {}

    for repo_name, data in manifest["repos"].items():
        wave = data.get("vague_courante", 0)
        relay_path = relay_dir / repo_name / "STRATUM_RELAY.md"

        if wave == 0:
            results[repo_name] = {"status": "Non déployé", "errors": []}
            continue

        if not relay_path.exists():
            results[repo_name] = {
                "status": "Fichier introuvable localement",
                "errors": ["  Chemin attendu : {}".format(relay_path)]
            }
            continue

        content = relay_path.read_text()
        errors = check_relay_content(repo_name, wave, content)

        if errors:
            results[repo_name] = {"status": "Avertissements", "errors": errors}
        else:
            results[repo_name] = {"status": "Conforme", "errors": []}

    return results


def print_report(results: dict) -> None:
    ok = sum(1 for r in results.values() if "Conforme" in r["status"])
    warn = sum(1 for r in results.values() if "Avertissements" in r["status"])
    pending = sum(1 for r in results.values() if "Non déploy" in r["status"])
    missing = sum(1 for r in results.values() if "introuvable" in r["status"])

    print("\n" + "=" * 60)
    print("  RAPPORT DE COHERENCE — STRATUM RELAYS")
    print("  Date : {}".format(date.today().isoformat()))
    print("=" * 60)
    print("  Conformes      : {}".format(ok))
    print("  Avertissements : {}".format(warn))
    print("  Non déployés  : {}".format(pending))
    print("  Introuvables   : {}".format(missing))
    print("=" * 60 + "\n")

    for repo, data in results.items():
        print("  {}  {}".format(data["status"], repo))
        for err in data["errors"]:
            print(err)

    if warn > 0 or missing > 0:
        print("\n  Relancer relay_propagator.py pour corriger les anomalies.")
        sys.exit(1)
    else:
        print("\n  Tous les relais déployés sont conformes.")


if __name__ == "__main__":
    relay_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "repos"
    results = run_check(relay_dir)
    print_report(results)
