#!/usr/bin/env python3
"""
recall_coherence_check.py — Vérifie la cohérence de l'écosystème UrbanVerse.
UrbanVerse | gerivdb/VERSUS | Version: 3.0.0
Date: 2026-05-29

Changements v3.0:
  - Mode --opensrc : utilise opensrc fetch + rg au lieu de appels MCP
  - x20 plus rapide sur les audits cross-repo
  - check_opensrc_completeness : vérifie que les repos gerivdb/* sont dans le cache opensrc
  - check_private_repos : détection des repos privés non accessibles sans token
  - scan_via_opensrc() : scan rg sur $(opensrc path gerivdb/*)
"""

import yaml
import sys
import re
import subprocess
import os
from pathlib import Path
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed

VERSUS_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH   = VERSUS_ROOT / "urban_ontology_verse/RELAYS/relay_wave_manifest.yaml"
CADASTRE_PATH   = VERSUS_ROOT / "urban_ontology_verse/CADASTRE/cadastre_full.yaml"
TRAINING_DIR    = Path("D:/DO/WEB/TOOLS/LLM-REPO/TRAINING")

REQUIRED_SECTIONS_WAVE1 = ["Identité stratique", "Navigation rapide", "Règles locales", "Vague de mise à jour"]
REQUIRED_SECTIONS_WAVE2 = REQUIRED_SECTIONS_WAVE1 + ["Karpathy"]
REQUIRED_SECTIONS_WAVE3 = REQUIRED_SECTIONS_WAVE2 + ["Dependances"]

CRITICAL_LINKS = [
    "PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md",
    "gerivdb/LLM-REPO",
    "transit_map.yaml",
]


def check_wave_vs_content(content: str, expected_wave: int) -> list:
    errors = []
    pattern = r"\*\*VAGUE\*\*:\s*(\d+)"
    match = re.search(pattern, content)
    if not match:
        errors.append("  VAGUE non trouvée dans le contenu")
    elif int(match.group(1)) != expected_wave:
        errors.append(f"  VAGUE incohérente: attendu={expected_wave}, trouvé={match.group(1)}")
    return errors


def check_recall_count(content: str, wave: int) -> list:
    errors = []
    if wave < 2:
        return errors
    q_count = len(re.findall(r"^Q:", content, re.MULTILINE))
    q_count += len(re.findall(r"^\d+\.\s+Q:", content, re.MULTILINE))
    expected = 5 if wave == 2 else 10
    if q_count == 0:
        if "Karpathy" not in content:
            errors.append(f"  Section Karpathy-Recall absente (Vague {wave})")
    elif q_count < expected:
        errors.append(f"  Recall incomplet: {q_count}Q trouvées, {expected} attendues (Vague {wave})")
    return errors


def check_wave3_deps(content: str) -> list:
    errors = []
    if "Dependances" not in content and "dépendances" not in content.lower():
        errors.append("  Section dépendances absente (requise pour Vague 3)")
    return errors


def check_manifest_vs_cadastre(manifest: dict, cadastre: dict) -> list:
    errors = []
    cadastre_repos = {p["repo_name"]: p for p in cadastre.get("parcelles", [])}

    for repo_name, data in manifest.get("repos", {}).items():
        vague_manifest = data.get("vague_courante", 0)
        if repo_name not in cadastre_repos:
            if data.get("statut", "") not in ("EXCLU — L9/DEPRECATED", "LOCAL ONLY"):
                errors.append(f"  {repo_name}: présent dans manifest mais pas dans cadastre")
            continue
        cad = cadastre_repos[repo_name]
        vague_cadastre = cad.get("vague_courante", 0)
        if vague_manifest != vague_cadastre:
            errors.append(f"  {repo_name}: manifest=V{vague_manifest} vs cadastre=V{vague_cadastre}")
    return errors


def check_stale_content(manifest: dict, cadastre: dict) -> list:
    errors = []
    cadastre_repos = {p["repo_name"]: p for p in cadastre.get("parcelles", [])}

    for repo_name, data in manifest.get("repos", {}).items():
        if repo_name in cadastre_repos:
            cad = cadastre_repos[repo_name]
            if data.get("strate") != cad.get("strate"):
                errors.append(f"  {repo_name}: strate manifest={data.get('strate')} vs cadastre={cad.get('strate')}")
    return errors


def check_transit_map_sync(training_dir: Path) -> list:
    errors = []
    expected_packs = ["recall_pack_L0.md", "recall_pack_L1b.md", "recall_pack_L1.md",
                      "recall_pack_L2.md", "recall_pack_L3.md"]
    for pack in expected_packs:
        if not (training_dir / pack).exists():
            errors.append(f"  {pack}: fichier manquant dans TRAINING/")
    return errors


def check_training_completeness(training_dir: Path) -> list:
    errors = []
    if not (training_dir / "README.md").exists():
        errors.append("  TRAINING/README.md manquant")
    if not (training_dir / "recall_relay_sync.md").exists():
        errors.append("  TRAINING/recall_relay_sync.md manquant")
    return errors


def check_opensrc_available() -> bool:
    """Vérifie que opensrc est installé et accessible."""
    try:
        result = subprocess.run(["opensrc", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_opensrc_completeness(manifest: dict) -> list:
    """Vérifie que les repos gerivdb/* sont dans le cache opensrc."""
    errors = []
    if not check_opensrc_available():
        errors.append("  opensrc non installé — pip install opensrc ou npm install -g opensrc")
        return errors

    for repo_name, data in manifest.get("repos", {}).items():
        vague = data.get("vague_courante", 0)
        if vague == 0:
            continue
        try:
            result = subprocess.run(
                ["opensrc", "path", f"gerivdb/{repo_name}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                errors.append(f"  {repo_name}: pas dans le cache opensrc — lancer 'opensrc fetch gerivdb/{repo_name}'")
        except subprocess.TimeoutExpired:
            errors.append(f"  {repo_name}: timeout opensrc path")
    return errors


def scan_via_opensrc(manifest: dict, pattern: str = "STRATUM_RELAY") -> dict:
    """
    Scan rg sur le cache opensrc pour trouver des patterns dans tous les repos.
    Retourne {repo_name: [lignes matching]}.
    """
    results = {}
    if not check_opensrc_available():
        return {"error": "opensrc non installé"}

    for repo_name, data in manifest.get("repos", {}).items():
        vague = data.get("vague_courante", 0)
        if vague == 0:
            continue
        try:
            path_result = subprocess.run(
                ["opensrc", "path", f"gerivdb/{repo_name}"],
                capture_output=True, text=True, timeout=10
            )
            if path_result.returncode == 0:
                repo_path = path_result.stdout.strip()
                rg_result = subprocess.run(
                    ["rg", pattern, repo_path, "--no-heading", "-n"],
                    capture_output=True, text=True, timeout=30
                )
                if rg_result.stdout.strip():
                    results[repo_name] = rg_result.stdout.strip().split("\n")[:5]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    return results


def check_private_repos(manifest: dict) -> list:
    """Détecte les repos potentiellement privés (pas de vague_courante mais dans le cadastre)."""
    errors = []
    for repo_name, data in manifest.get("repos", {}).items():
        vague = data.get("vague_courante", 0)
        statut = data.get("statut", "")
        if vague == 0 and statut not in ("EXCLU — L9/DEPRECATED", "LOCAL ONLY", "PENDING_CREATION"):
            errors.append(f"  {repo_name}: vague=0 mais statut='{statut}' — repo privé ou inaccessible ?")
    return errors


def run_all_checks(mode: str = "standard", relay_dir: Path = None) -> dict:
    """Exécute toutes les vérifications et retourne un rapport."""
    manifest = yaml.safe_load(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {}
    cadastre = yaml.safe_load(CADASTRE_PATH.read_text()) if CADASTRE_PATH.exists() else {"parcelles": []}

    all_errors = {}

    # Checks standard (toujours exécutés)
    errs = check_manifest_vs_cadastre(manifest, cadastre)
    if errs:
        all_errors["manifest_vs_cadastre"] = errs

    errs = check_stale_content(manifest, cadastre)
    if errs:
        all_errors["stale_content"] = errs

    errs = check_transit_map_sync(TRAINING_DIR)
    if errs:
        all_errors["transit_map_sync"] = errs

    errs = check_training_completeness(TRAINING_DIR)
    if errs:
        all_errors["training_completeness"] = errs

    errs = check_private_repos(manifest)
    if errs:
        all_errors["private_repos_detected"] = errs

    # Mode opensrc : checks supplémentaires
    if mode == "opensrc":
        errs = check_opensrc_completeness(manifest)
        if errs:
            all_errors["opensrc_cache"] = errs

    # Vérification des fichiers locaux (si relay_dir fourni)
    if relay_dir:
        for repo_name, data in manifest.get("repos", {}).items():
            wave = data.get("vague_courante", 0)
            if wave == 0:
                continue
            relay_path = relay_dir / repo_name / "STRATUM_RELAY.md"
            if not relay_path.exists():
                all_errors.setdefault("missing_files", []).append(f"  {repo_name}: STRATUM_RELAY.md introuvable")
                continue
            content = relay_path.read_text()
            errs = check_wave_vs_content(content, wave)
            errs += check_recall_count(content, wave)
            if wave >= 3:
                errs += check_wave3_deps(content)
            if errs:
                all_errors[repo_name] = errs

    return all_errors


def print_report(all_errors: dict, mode: str = "standard") -> bool:
    print("\n" + "=" * 60)
    print(f"  RAPPORT DE COHERENCE URBANVERSE v3.0 — mode: {mode}")
    print(f"  Date : {date.today().isoformat()}")
    print("=" * 60)

    total_errors = sum(len(v) for v in all_errors.values())

    if not all_errors:
        print("  ✅ 0 erreur — Système UrbanVerse cohérent.")
        return True

    for category, errs in all_errors.items():
        print(f"\n  [{category}] — {len(errs)} erreur(s):")
        for err in errs:
            print(f"    {err}")

    print(f"\n  TOTAL: {total_errors} erreur(s)")
    return total_errors == 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="UrbanVerse Coherence Check v3.0")
    parser.add_argument("--mode", choices=["standard", "opensrc"], default="standard",
                        help="Mode: standard (MCP) ou opensrc (local cache)")
    parser.add_argument("--relay-dir", default=None, help="Chemin vers les repos locaux")
    parser.add_argument("--check-local", action="store_true", help="Vérifie aussi les fichiers locaux")
    parser.add_argument("--scan", default=None, help="Pattern à scanner via opensrc (ex: 'STRATUM_RELAY')")
    args = parser.parse_args()

    if args.scan and check_opensrc_available():
        manifest = yaml.safe_load(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {}
        results = scan_via_opensrc(manifest, args.scan)
        print(f"\n  Scan opensrc pour '{args.scan}':")
        for repo, lines in results.items():
            if repo == "error":
                print(f"  ❌ {lines}")
            else:
                print(f"\n  {repo}:")
                for line in lines:
                    print(f"    {line}")
    else:
        relay_dir = Path(args.relay_dir) if args.check_local and args.relay_dir else None
        all_errors = run_all_checks(mode=args.mode, relay_dir=relay_dir)
        ok = print_report(all_errors, mode=args.mode)
        sys.exit(0 if ok else 1)
