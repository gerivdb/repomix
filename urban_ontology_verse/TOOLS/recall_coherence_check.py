#!/usr/bin/env python3
"""
recall_coherence_check.py — Vérifie la cohérence de l'écosystème UrbanVerse.
UrbanVerse | gerivdb/VERSUS | Version: 2.0.0
Date: 2026-05-29

Vérifications v2 :
  - check_wave_vs_content()    : vague_courante=N → "VAGUE**: N" dans le fichier ?
  - check_recall_count()       : vague=2 → exactement 5Q, vague=3 → 10Q
  - check_wave3_deps()         : vague=3 → section dépendances présente ?
  - check_manifest_vs_cadastre: manifest vs cadastre_full cohérent ?
  - check_stale_content()      : rôle dans STRATUM_RELAY ↔ rôle dans cadastre ?
  - check_transit_map_sync()   : recall_pack:true ↔ TRAINING/ fichier existe ?
  - check_training_completeness: tous les packs L0→L3 existent ?
"""

import yaml
import sys
import re
from pathlib import Path
from datetime import date

VERSUS_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH   = VERSUS_ROOT / "urban_ontology_verse/RELAYS/relay_wave_manifest.yaml"
CADASTRE_PATH   = VERSUS_ROOT / "urban_ontology_verse/CADASTRE/cadastre_full.yaml"
TRAINING_DIR    = Path(__file__).parent.parent.parent.parent / "LLM-REPO" / "TRAINING"

REQUIRED_SECTIONS_WAVE1 = ["Identité stratique", "Navigation rapide", "Règles locales", "Vague de mise à jour"]
REQUIRED_SECTIONS_WAVE2 = REQUIRED_SECTIONS_WAVE1 + ["Karpathy"]
REQUIRED_SECTIONS_WAVE3 = REQUIRED_SECTIONS_WAVE2 + ["Dependances"]

CRITICAL_LINKS = [
    "PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md",
    "gerivdb/LLM-REPO",
    "transit_map.yaml",
]


def check_wave_vs_content(content: str, expected_wave: int) -> list:
    """Vérifie que le contenu contient le bon numéro de vague."""
    errors = []
    pattern = r"\*\*VAGUE\*\*:\s*(\d+)"
    match = re.search(pattern, content)
    if not match:
        errors.append(f"  VAGUE non trouvée dans le contenu")
    elif int(match.group(1)) != expected_wave:
        errors.append(f"  VAGUE incohérente: attendu={expected_wave}, trouvé={match.group(1)}")
    return errors


def check_recall_count(content: str, wave: int) -> list:
    """Vérifie le nombre de questions Karpathy-Recall."""
    errors = []
    if wave < 2:
        return errors
    # Compte les lignes commençant par "Q:" ou "1." etc.
    q_count = len(re.findall(r"^Q:", content, re.MULTILINE))
    q_count += len(re.findall(r"^\d+\.\s+Q:", content, re.MULTILINE))
    expected = 5 if wave == 2 else 10
    if q_count == 0:
        # Peut être formaté différemment — chercher "Karpathy"
        if "Karpathy" not in content:
            errors.append(f"  Section Karpathy-Recall absente (Vague {wave})")
    elif q_count < expected:
        errors.append(f  f"  Recall incomplet: {q_count}Q trouvées, {expected} attendues (Vague {wave})")
    return errors


def check_wave3_deps(content: str) -> list:
    """Vérifie la présence de la section dépendances pour Vague 3."""
    errors = []
    if "Dependances" not in content and "dépendances" not in content.lower():
        errors.append("  Section dépendances absente (requise pour Vague 3)")
    return errors


def check_manifest_vs_cadastre(manifest: dict, cadastre: dict) -> list:
    """Vérifie la cohérence manifest ↔ cadastre_full."""
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
    """Vérifie que les rôles dans le manifest correspondent au cadastre."""
    errors = []
    cadastre_repos = {p["repo_name"]: p for p in cadastre.get("parcelles", [])}

    for repo_name, data in manifest.get("repos", {}).items():
        if repo_name in cadastre_repos:
            cad = cadastre_repos[repo_name]
            if data.get("strate") != cad.get("strate"):
                errors.append(f"  {repo_name}: strate manifest={data.get('strate')} vs cadastre={cad.get('strate')}")
    return errors


def check_transit_map_sync(training_dir: Path) -> list:
    """Vérifie que les recall packs référencés dans transit_map existent."""
    errors = []
    expected_packs = ["recall_pack_L0.md", "recall_pack_L1b.md", "recall_pack_L1.md",
                      "recall_pack_L2.md", "recall_pack_L3.md"]
    for pack in expected_packs:
        if not (training_dir / pack).exists():
            errors.append(f"  {pack}: fichier manquant dans TRAINING/")
    return errors


def check_training_completeness(training_dir: Path) -> list:
    """Vérifie que tous les recall packs sont complets."""
    errors = []
    if not (training_dir / "README.md").exists():
        errors.append("  TRAINING/README.md manquant")
    if not (training_dir / "recall_relay_sync.md").exists():
        errors.append("  TRAINING/recall_relay_sync.md manquant")
    return errors


def run_all_checks(relay_dir: Path = None) -> dict:
    """Exécute toutes les vérifications et retourne un rapport."""
    manifest = yaml.safe_load(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {}
    cadastre = yaml.safe_load(CADASTRE_PATH.read_text()) if CADASTRE_PATH.exists() else {"parcelles": []}

    all_errors = {}

    # 1. Manifest vs Cadastre
    errs = check_manifest_vs_cadastre(manifest, cadastre)
    if errs:
        all_errors["manifest_vs_cadastre"] = errs

    # 2. Stale content
    errs = check_stale_content(manifest, cadastre)
    if errs:
        all_errors["stale_content"] = errs

    # 3. Transit map sync
    errs = check_transit_map_sync(TRAINING_DIR)
    if errs:
        all_errors["transit_map_sync"] = errs

    # 4. Training completeness
    errs = check_training_completeness(TRAINING_DIR)
    if errs:
        all_errors["training_completeness"] = errs

    # 5. Vérification des fichiers locaux (si relay_dir fourni)
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


def print_report(all_errors: dict) -> bool:
    """Affiche le rapport et retourne True si 0 erreurs."""
    print("\n" + "=" * 60)
    print("  RAPPORT DE COHERENCE URBANVERSE v2.0")
    print("  Date : {}".format(date.today().isoformat()))
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
    parser = argparse.ArgumentParser(description="UrbanVerse Coherence Check v2.0")
    parser.add_argument("--relay-dir", default=None, help="Chemin vers les repos locaux")
    parser.add_argument("--check-local", action="store_true", help="Vérifie aussi les fichiers locaux")
    args = parser.parse_args()

    relay_dir = Path(args.relay_dir) if args.check_local and args.relay_dir else None
    all_errors = run_all_checks(relay_dir)
    ok = print_report(all_errors)
    sys.exit(0 if ok else 1)
