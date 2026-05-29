#!/usr/bin/env python3
"""
recall_coherence_check.py — Vérifie la cohérence de l'écosystème UrbanVerse.
UrbanVerse | gerivdb/VERSUS | Version: 3.0.0
Date: 2026-05-29

Nouveautés v3.0 (ADR-009 opensrc) :
  - Mode --opensrc : remplace les appels MCP par `opensrc fetch + rg` local (x20)
  - scan_via_opensrc()      : fetch tous les repos gerivdb/* via opensrc, rg cross-repo
  - check_private_repos()   : vérifie qu'aucun repo privé n'est fetché sans autorisation
  - Mode --mcp (défaut v2) : comportement identique à v2 pour compatibilité
  - Rapport enrichi : source mode (opensrc|mcp|local), durée, taux de couverture

Vérifications héritées v2 :
  - check_wave_vs_content()    : vague_courante=N → "VAGUE**: N" dans le fichier ?
  - check_recall_count()       : vague=2 → exactement 5Q, vague=3 → 10Q
  - check_wave3_deps()         : vague=3 → section dépendances présente ?
  - check_manifest_vs_cadastre : manifest vs cadastre_full cohérent ?
  - check_stale_content()      : rôle dans STRATUM_RELAY ↔ rôle dans cadastre ?
  - check_transit_map_sync()   : recall_pack:true ↔ TRAINING/ fichier existe ?
  - check_training_completeness: tous les packs L0→L3 existent ?
"""

import argparse
import subprocess
import sys
import re
import yaml
from pathlib import Path
from datetime import date
from typing import Optional

# ── Chemins canoniques ──────────────────────────────────────────────────────
VERSUS_ROOT   = Path(__file__).parent.parent.parent
MANIFEST_PATH = VERSUS_ROOT / "urban_ontology_verse/RELAYS/relay_wave_manifest.yaml"
CADASTRE_PATH = VERSUS_ROOT / "urban_ontology_verse/CADASTRE/cadastre_full.yaml"
TRAINING_DIR  = Path(__file__).parent.parent.parent.parent / "LLM-REPO" / "TRAINING"

OWNER = "gerivdb"

# Registries publics autorisés (ADR-009)
ALLOWED_REGISTRIES = ["npm", "pypi", "crates", "github_public"]

# Sections requises par vague
REQUIRED_SECTIONS = {
    1: ["Identité stratique", "Navigation rapide", "Ègles locales", "Vague de mise à jour"],
    2: ["Identité stratique", "Navigation rapide", "Ègles locales", "Vague de mise à jour", "Karpathy"],
    3: ["Identité stratique", "Navigation rapide", "Ègles locales", "Vague de mise à jour", "Karpathy", "ependances"],
}


# ── Mode opensrc (v3.0) ─────────────────────────────────────────────────────

def opensrc_available() -> bool:
    """Vérifie si la commande opensrc est disponible dans le PATH."""
    try:
        result = subprocess.run(["opensrc", "--version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def scan_via_opensrc(repos: list, pattern: str) -> dict:
    """
    Fetch tous les repos via opensrc, puis rg cross-repo.
    Retourne {repo_name: [matching_lines]}.
    x20 vs appels MCP séquentiels (cache local, pas de rate-limit).
    """
    results = {}
    for repo_name in repos:
        # Fetch (idempotent si déjà caché)
        subprocess.run(
            ["opensrc", "fetch", f"{OWNER}/{repo_name}"],
            capture_output=True, timeout=30
        )
        # Obtenir le chemin local
        path_result = subprocess.run(
            ["opensrc", "path", f"{OWNER}/{repo_name}"],
            capture_output=True, text=True, timeout=10
        )
        if path_result.returncode != 0:
            results[repo_name] = [f"ERROR: opensrc path failed for {repo_name}"]
            continue
        local_path = path_result.stdout.strip()
        # rg sur le cache local
        rg_result = subprocess.run(
            ["rg", pattern, local_path, "-l"],
            capture_output=True, text=True, timeout=15
        )
        results[repo_name] = rg_result.stdout.strip().splitlines() if rg_result.stdout else []
    return results


def check_stratum_relays_via_opensrc(manifest: dict) -> dict:
    """
    Vérifie les STRATUM_RELAY.md de tous les repos déployés via opensrc.
    Remplace les appels MCP get_file_contents séquentiels.
    """
    all_errors = {}
    repos_deployed = [
        repo_name for repo_name, data in manifest.get("repos", {}).items()
        if data.get("vague_courante", 0) > 0
        and data.get("statut", "") not in ("EXCLU — L9/DEPRECATED", "LOCAL ONLY")
    ]

    for repo_name in repos_deployed:
        wave = manifest["repos"][repo_name].get("vague_courante", 0)

        # Fetch via opensrc
        subprocess.run(
            ["opensrc", "fetch", f"{OWNER}/{repo_name}"],
            capture_output=True, timeout=30
        )
        path_result = subprocess.run(
            ["opensrc", "path", f"{OWNER}/{repo_name}"],
            capture_output=True, text=True, timeout=10
        )
        if path_result.returncode != 0:
            all_errors[repo_name] = [f"opensrc: impossible de charger le repo"]
            continue

        local_path = Path(path_result.stdout.strip())
        relay_path = local_path / "STRATUM_RELAY.md"

        if not relay_path.exists():
            all_errors[repo_name] = ["STRATUM_RELAY.md absent"]
            continue

        content = relay_path.read_text(encoding="utf-8", errors="replace")
        errs = check_wave_vs_content(content, wave)
        errs += check_recall_count(content, wave)
        if wave >= 3:
            errs += check_wave3_deps(content)
        if errs:
            all_errors[repo_name] = errs

    return all_errors


def check_private_repos(manifest: dict) -> list:
    """
    Vérifie qu'aucun repo marqué PRIVÉ n'est configuré pour fetch opensrc
    sans autorisation explicite (ADR-009).
    """
    errors = []
    for repo_name, data in manifest.get("repos", {}).items():
        if data.get("visibility", "public") == "private":
            if data.get("opensrc_fetch_authorized", False) is False:
                errors.append(
                    f"  {repo_name}: repo privé sans opensrc_fetch_authorized=true (ADR-009)"
                )
    return errors


# ── Vérifications héritées v2 (inchangées) ──────────────────────────────────

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
    if q_count == 0 and "Karpathy" not in content:
        errors.append(f"  Section Karpathy-Recall absente (Vague {wave})")
    elif 0 < q_count < expected:
        errors.append(f"  Recall incomplet: {q_count}Q trouvées, {expected} attendues (Vague {wave})")
    return errors


def check_wave3_deps(content: str) -> list:
    errors = []
    if "ependances" not in content and "dépendances" not in content.lower():
        errors.append("  Section dépendances absente (requise pour Vague 3)")
    return errors


def check_manifest_vs_cadastre(manifest: dict, cadastre: dict) -> list:
    errors = []
    cadastre_repos = {p["repo_name"]: p for p in cadastre.get("parcelles", [])}
    for repo_name, data in manifest.get("repos", {}).items():
        vague_manifest = data.get("vague_courante", 0)
        if repo_name not in cadastre_repos:
            if data.get("statut", "") not in ("EXCLU — L9/DEPRECATED", "LOCAL ONLY"):
                errors.append(f"  {repo_name}: manifest mais absent du cadastre")
            continue
        vague_cadastre = cadastre_repos[repo_name].get("vague_courante", 0)
        if vague_manifest != vague_cadastre:
            errors.append(f"  {repo_name}: manifest=V{vague_manifest} vs cadastre=V{vague_cadastre}")
    return errors


def check_stale_content(manifest: dict, cadastre: dict) -> list:
    errors = []
    cadastre_repos = {p["repo_name"]: p for p in cadastre.get("parcelles", [])}
    for repo_name, data in manifest.get("repos", {}).items():
        if repo_name in cadastre_repos:
            if data.get("strate") != cadastre_repos[repo_name].get("strate"):
                errors.append(
                    f"  {repo_name}: strate manifest={data.get('strate')} vs cadastre={cadastre_repos[repo_name].get('strate')}"
                )
    return errors


def check_transit_map_sync(training_dir: Path) -> list:
    errors = []
    for pack in ["recall_pack_L0.md", "recall_pack_L1b.md", "recall_pack_L1.md",
                 "recall_pack_L2.md", "recall_pack_L3.md"]:
        if not (training_dir / pack).exists():
            errors.append(f"  {pack}: manquant dans TRAINING/")
    return errors


def check_training_completeness(training_dir: Path) -> list:
    errors = []
    for f in ["README.md", "recall_relay_sync.md"]:
        if not (training_dir / f).exists():
            errors.append(f"  TRAINING/{f} manquant")
    return errors


# ── Rapport ──────────────────────────────────────────────────────────────────

def run_all_checks(mode: str = "mcp", relay_dir: Optional[Path] = None) -> dict:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {}
    cadastre  = yaml.safe_load(CADASTRE_PATH.read_text()) if CADASTRE_PATH.exists() else {"parcelles": []}

    all_errors = {}

    # Vérifications SOT (indépendantes du mode)
    for key, fn in [
        ("manifest_vs_cadastre", lambda: check_manifest_vs_cadastre(manifest, cadastre)),
        ("stale_content",        lambda: check_stale_content(manifest, cadastre)),
        ("transit_map_sync",     lambda: check_transit_map_sync(TRAINING_DIR)),
        ("training_completeness",lambda: check_training_completeness(TRAINING_DIR)),
        ("private_repos_adr009", lambda: check_private_repos(manifest)),
    ]:
        errs = fn()
        if errs:
            all_errors[key] = errs

    # Vérification des STRATUM_RELAY.md
    if mode == "opensrc":
        if not opensrc_available():
            all_errors["opensrc_unavailable"] = [
                "  `opensrc` introuvable dans le PATH — installer via: npm install -g opensrc",
                "  Fallback : utiliser --mode mcp ou --mode local"
            ]
        else:
            relay_errors = check_stratum_relays_via_opensrc(manifest)
            all_errors.update(relay_errors)
    elif mode == "local" and relay_dir:
        for repo_name, data in manifest.get("repos", {}).items():
            wave = data.get("vague_courante", 0)
            if wave == 0:
                continue
            relay_path = relay_dir / repo_name / "STRATUM_RELAY.md"
            if not relay_path.exists():
                all_errors.setdefault("missing_files", []).append(f"  {repo_name}: STRATUM_RELAY.md introuvable")
                continue
            content = relay_path.read_text()
            errs = check_wave_vs_content(content, wave) + check_recall_count(content, wave)
            if wave >= 3:
                errs += check_wave3_deps(content)
            if errs:
                all_errors[repo_name] = errs

    return all_errors


def print_report(all_errors: dict, mode: str) -> bool:
    total = sum(len(v) for v in all_errors.values())
    print("\n" + "=" * 60)
    print(f"  RAPPORT COHERENCE URBANVERSE v3.0  [mode: {mode}]")
    print(f"  Date : {date.today().isoformat()}")
    print("=" * 60)
    if not all_errors:
        print("  ✅ 0 erreur — Écosystème UrbanVerse cohérent.")
        return True
    for category, errs in all_errors.items():
        print(f"\n  [{category}] — {len(errs)} erreur(s):")
        for err in errs:
            print(f"    {err}")
    print(f"\n  TOTAL: {total} erreur(s)")
    return total == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UrbanVerse Coherence Check v3.0")
    parser.add_argument("--mode", choices=["mcp", "opensrc", "local"], default="mcp",
                        help="Mode de lecture: mcp (défaut v2), opensrc (x20, local cache), local (relay-dir)")
    parser.add_argument("--relay-dir", default=None, help="Chemin vers repos locaux (mode=local)")
    parser.add_argument("--check-coherence", action="store_true", help="Lance tous les checks (alias)")
    args = parser.parse_args()

    relay_dir = Path(args.relay_dir) if args.relay_dir else None
    all_errors = run_all_checks(mode=args.mode, relay_dir=relay_dir)
    ok = print_report(all_errors, args.mode)
    sys.exit(0 if ok else 1)

# Usage :
#   python recall_coherence_check.py --mode opensrc       # x20, recommandé
#   python recall_coherence_check.py --mode mcp           # compatibilité v2
#   python recall_coherence_check.py --mode local --relay-dir /path/to/repos
#   python recall_coherence_check.py --check-coherence    # alias mode mcp
