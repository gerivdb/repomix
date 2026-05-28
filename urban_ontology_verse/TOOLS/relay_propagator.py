#!/usr/bin/env python3
"""
relay_propagator.py — Stratum Relay Wave Propagator
UrbanVerse | gerivdb/VERSUS | Version: 1.0.0
Date: 2026-05-28

Generates and commits STRATUM_RELAY.md files to target repos.
Uses GitHub API via MCP or direct git operations.
"""

import json
import yaml
import os
import sys
import subprocess
from datetime import date
from pathlib import Path
from typing import Optional

# -- Config --------------------------------------------------------------------
VERSUS_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = VERSUS_ROOT / "urban_ontology_verse" / "RELAYS" / "relay_wave_manifest.yaml"
TEMPLATE_PATH = VERSUS_ROOT / "urban_ontology_verse" / "TEMPLATES" / "STRATUM_RELAY_TEMPLATE.md"
CADASTRE_PILOT_PATH = VERSUS_ROOT / "urban_ontology_verse" / "CADASTRE" / "cadastre_pilot.yaml"

STRATE_LABELS = {
    "L0":  "Constitution — Super-Super-Hub",
    "L1b": "Substrat cognitif LLM",
    "L1":  "Substrat global opérationnel",
    "L2":  "Système nerveux central",
    "L2b": "Triade sensorielle",
    "L3":  "Système moteur CLI",
    "L4":  "Infrastructure & Hardware",
    "L5":  "IA distribuée & LLM",
    "L6":  "Mémoire & Documentation",
    "L7":  "Interfaces utilisateur & Dev",
    "L8":  "Vie réelle & Créatif",
    "L9":  "Archéologie (exclue LLM)",
}

PARENT_MAP = {
    "L0": None, "L1b": "L0", "L1": "L1b",
    "L2": "L1", "L2b": "L2", "L3": "L2",
    "L4": "L3", "L5": "L4", "L6": "L5",
    "L7": "L6", "L8": "L7", "L9": "L8",
}

CHILD_MAP = {
    "L0": "L1b", "L1b": "L1", "L1": "L2",
    "L2": "L2b + L3", "L2b": "L3", "L3": "L4",
    "L4": "L5", "L5": "L6", "L6": "L7",
    "L7": "L8", "L8": "L9", "L9": "—",
}

# -- Recall packs per strate (Karpathy-style, 3 questions per strate) ----------
KARPATHY_RECALLS = {
    "L0": [
        "Q: Quelle est la différence entre GOVERNANCE-HUB et LLM-REPO ?",
        "Q: Quel fichier contient la liste canonique de tous les repos actifs ?",
        "Q: Qu'est-ce qu'un Super-Super-Hub et pourquoi GOVERNANCE-HUB l'est-il ?",
    ],
    "L1b": [
        "Q: Pourquoi LLM-REPO est-il privé et distinct de ECOS-CLI ?",
        "Q: Quels 3 types de fichiers LLM-REPO centralise-t-il que ECOS-CLI ne doit plus contenir ?",
        "Q: Quelle est la séquence d'ingestion canonique pour un LLM entrant dans l'écosystème ?",
    ],
    "L1": [
        "Q: Quelle est la différence de rôle entre ECOYSTEM et NEXUS ?",
        "Q: Qu'est-ce que RSS-v1 et dans quel repo vit-il ?",
        "Q: Un nouveau repo créé doit être enregistré dans quel fichier et dans quel repo ?",
    ],
    "L2": [
        "Q: Quel est le rôle de FLUENCE par rapport à BRAIN ?",
        "Q: VDB stocke quel type de données et avec quel modèle d'embedding ?",
        "Q: TINA vs TRANSCENDANCE : quelle est la différence de rôle ?",
    ],
    "L2b": [
        "Q: Décris le pipeline atomique IRIS → KRONOS → FLUX en une phrase par étape.",
        "Q: Quelle est la durée d'expiration des événements dans FLUX ?",
        "Q: ARGUS surveille quoi et pourquoi est-il le 'système immunitaire' ?",
    ],
    "L3": [
        "Q: Après la migration vers LLM-REPO, que doit contenir ECOS-CLI exclusivement ?",
        "Q: Quelle est la frontière de responsabilité entre ECOS-CLI et DevTools ?",
        "Q: Qu'est-ce que BLO et quel format de base de données utilise-t-il ?",
    ],
    "L4": [
        "Q: Quel repo gère le hardware HP Z600 en LXC/LXD ?",
        "Q: Pourquoi CodeDB-E5620 existe-t-il en fork séparé de CodeDB ?",
        "Q: GATEWAY-MANAGER gère quelles responsabilités réseau ?",
    ],
    "L5": [
        "Q: BOINC-LLM-P2P utilise quel protocole de distribution et quelle version d'ECOS ?",
        "Q: Quel repo orchestre les agents multi-IDE (Cline/RooCode/Copilot) dans VSCode ?",
        "Q: CLIP-FACTORY produit quel type d'artefacts ?",
    ],
    "L6": [
        "Q: MIMIR est décrit comme 'Wiki Atomique Diamond' — qu'est-ce que cela signifie ?",
        "Q: SKILLS vs DOC-UNIV-DEV : quelle est la différence de contenu ?",
        "Q: Quel repo visualise l'architecture L0→L4.5 sous forme diagrammatique ?",
    ],
    "L7": [
        "Q: GeriCode est un fork de quel outil IDE ?",
        "Q: Quel est le rôle de COMET dans l'écosystème ?",
        "Q: appflowy-mcp-server remplace quel SaaS commercial ?",
    ],
    "L8": [
        "Q: VERSUS est en L8 — quelle est sa responsabilité par rapport à BATVERSE ?",
        "Q: Quelle est la règle absolue avant d'implémenter la monnaie Geri (Ğ) ?",
        "Q: Citez 3 repos L8 qui ont une finalité humaine culturelle (pas technique).",
    ],
}

# -- Local rules per strate ----------------------------------------------------
STRATE_RULES = {
    "L0": [
        "R1 — Ce repo est ingéré EN PREMIER par tout LLM. Ne jamais bypasser.",
        "R2 — known_repositories.yaml est la SEULE source of truth des repos.",
        "R3 — Toute modification structurelle nécessite une ADR dans ADR/.",
        "Anti-pattern: modifier AGENT_RAM.yaml sans fin de session productive.",
    ],
    "L1b": [
        "R1 — LLM-REPO est ingéré EN SECOND, immédiatement après GOVERNANCE-HUB.",
        "R2 — Aucune règle LLM ne doit résider dans ECOS-CLI (post-migration).",
        "R3 — Ce repo est privé — ne pas exposer les profils d'agents publiquement.",
        "Anti-pattern: stocker .kilocodemodes ou .roomodes ailleurs que LLM-REPO/AGENTS/modes/",
    ],
    "L1": [
        "R1 — ECOYSTEM est le SOT opérationnel — toute action L3+ doit être conforme.",
        "R2 — Tout nouveau repo doit respecter ONTOLOGY + REPO-STANDARDS avant enregistrement.",
        "R3 — NEXUS agrège — ne jamais écrire de données primaires dans NEXUS.",
        "Anti-pattern: créer un repo sans l'enregistrer dans known_repositories.yaml.",
    ],
    "L2": [
        "R1 — BRAIN est le hub cognitif racine — ne pas dupliquer sa logique en L3.",
        "R2 — FLUENCE gère la logique ternaire — tout score ternaire passe par FLUENCE.",
        "R3 — VDB accepte uniquement nomic-embed (768-dim) comme modèle d'embedding.",
        "Anti-pattern: implémenter de la logique ternaire directement dans ECOS-CLI.",
    ],
    "L2b": [
        "R1 — IRIS ne traite que les signaux externes. Jamais de signaux internes.",
        "R2 — FLUX expire les événements après 90 jours — ne pas persister au-delà.",
        "R3 — ARGUS surveille uniquement — il ne modifie jamais les repos qu'il surveille.",
        "Anti-pattern: faire pointer IRIS sur des repos internes gerivdb.",
    ],
    "L3": [
        "R1 — ECOS-CLI est un exécutable pur — zéro règle LLM, zéro fichier de gouvernance.",
        "R2 — Toute commande `ecos *` doit avoir un test dans DevTools-CLI.",
        "R3 — BLO utilise bloom.db + WAL — ne jamais accéder à bloom.db directement.",
        "Anti-pattern: ajouter des fichiers .md de philosophie dans ECOS-CLI.",
    ],
    "L4": [
        "R1 — KIVA orchestre LXC/LXD sur HP Z600 uniquement — ne pas généraliser.",
        "R2 — ATLAS = IaC déclaratif — toute infra doit être définie comme code.",
        "R3 — GATEWAY-MANAGER gère le rate limiting — ne pas contourner.",
        "Anti-pattern: déployer sur HP Z600 sans passer par KIVA.",
    ],
    "L5": [
        "R1 — BOINC-LLM-P2P utilise DHT Kademlia — toute inférence distribuée passe par lui.",
        "R2 — vsix-ai-orchestrator orchestre uniquement les agents VSCode — pas les autres.",
        "R3 — CLIP-FACTORY produit uniquement des embeddings vision-language.",
        "Anti-pattern: lancer une inférence LLM distribuée sans BOINC-LLM-P2P.",
    ],
    "L6": [
        "R1 — MIMIR est la source of truth visuelle — toute roadmap diagrammatique vit là.",
        "R2 — BRAIN-DOCS documente BRAIN uniquement — pas d'autres repos.",
        "R3 — SKILLS = registry natifs/assimilés/externes — structure tripartite obligatoire.",
        "Anti-pattern: mettre de la documentation de repo dans MIMIR au lieu du repo.",
    ],
    "L7": [
        "R1 — GeriCode est un fork de KiloCode — maintenir la compatibilité upstream.",
        "R2 — COMET gère l'automation browser — ne pas implémenter de scraping ailleurs.",
        "R3 — appflowy-mcp-server remplace Notion — ne pas utiliser l'API Notion.",
        "Anti-pattern: dupliquer l'interface habits dans deux repos L7 distincts.",
    ],
    "L8": [
        "R1 — VERSUS est ontologique — BATVERSE est narratif. Ne jamais fusionner.",
        "R2 — Toute monnaie interne (Geri Ğ) nécessite une ADR validée dans GOVERNANCE-HUB.",
        "R3 — Les repos culturels (GVDB-MEDIA, ROCK-REIMS) ne dépendent pas de L2/L3.",
        "Anti-pattern: implémenter la Geri (Ğ) sans ADR constitutionnelle.",
    ],
}

# -- Relay generator ------------------------------------------------------------

def generate_relay(repo_name: str, strate: str, role: str, wave: int = 1) -> str:
    """Generate STRATUM_RELAY.md content for a given repo."""
    today = date.today().isoformat()
    label = STRATE_LABELS.get(strate, strate)
    parent = PARENT_MAP.get(strate, "—") or "—"
    children = CHILD_MAP.get(strate, "—")
    rules = STRATE_RULES.get(strate, ["R1 — Respecter les règles GOVERNANCE-HUB."])
    recalls = KARPATHY_RECALLS.get(strate, ["Q: Quel est le rôle de ce repo dans l'écosystème ?"])

    rules_md = "\n".join(f"- {r}" for r in rules)

    if wave >= 2:
        recall_section = "\n## 🧠 Karpathy-Recall local (Vague {})\n\n> Réponds mentalement à ces questions avant d'agir dans ce repo.\n\n".format(wave)
        recall_section += "\n".join("{}. {}".format(i+1, q) for i, q in enumerate(recalls))
    else:
        recall_section = ""

    wave_next = wave + 1
    wave_next_date = "À planifier (Vague 3 = recall packs complets)"

    return """# 🔁 STRATUM RELAY — {} ({})

🔄 **VAGUE**: {} | ⏱️ **Synchro**: {} | **Hub**: gerivdb/LLM-REPO

---

## 🧬 Identité stratique

- **Strate** : `{}` — {}
- **Rôle canonique** : {}
- **Parent** : {}
- **Enfants** : {}

## 🧭 Navigation rapide

- 📋 PRD canonique : `GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md`
- 🧭 Substrat cognitif : `gerivdb/LLM-REPO` (L1b — privé)
- 📐 Standards repo : `REPO-STANDARDS` (RSS-v1)
- 🗺️ Transit map : `VERSUS/urban_ontology_verse/TRANSIT/transit_map.yaml`
- 📦 Cadastre : `VERSUS/urban_ontology_verse/CADASTRE/cadastre_pilot.yaml`

## 🚦 Règles locales

{}
{}

## 📡 Vague de mise à jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| **{} (courante)** | {} | ✅ Déployé |
| {} (suivante) | {} | ⏳ Planifié |

---

*Ce fichier est géré par `VERSUS/urban_ontology_verse/TOOLS/relay_propagator.py`*
*Ne pas modifier manuellement — utiliser le propagateur ou soumettre une PR.*
*UrbanVerse v1.0.0 — gerivdb/VERSUS (L8)*
""".format(
        repo_name, strate, wave, today, strate, label, role, parent, children,
        rules_md, recall_section,
        wave, "Identité + navigation" if wave == 1 else "Identité + règles + recall",
        wave_next, wave_next_date
    )


def load_manifest() -> dict:
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


def save_manifest(manifest: dict) -> None:
    with open(MANIFEST_PATH, "w") as f:
        yaml.dump(manifest, f, allow_unicode=True, sort_keys=False)


def load_cadastre() -> dict:
    with open(CADASTRE_PILOT_PATH) as f:
        return yaml.safe_load(f)


def print_relay(repo_name: str) -> None:
    """Print relay content to stdout for manual commit."""
    manifest = load_manifest()
    cadastre = load_cadastre()
    repos = manifest.get("repos", {})

    if repo_name not in repos:
        print("ERROR: '{}' not found in manifest. Available: {}".format(repo_name, list(repos.keys())))
        sys.exit(1)

    entry = repos[repo_name]
    strate = entry["strate"]
    wave = entry.get("vague_cible", 1)

    parcelles = cadastre.get("parcelles", [])
    role = next(
        (p.get("role_canonique", "Rôle non défini") for p in parcelles if p.get("repo_name") == repo_name),
        "Rôle non défini — à compléter dans cadastre_pilot.yaml"
    )

    content = generate_relay(repo_name, strate, role, wave)
    print(content)
    print("\n# -- A commettre dans : gerivdb/{}/STRATUM_RELAY.md --".format(repo_name))


def update_manifest_status(repo_name: str, wave: int) -> None:
    manifest = load_manifest()
    if repo_name in manifest["repos"]:
        manifest["repos"][repo_name]["vague_courante"] = wave
        manifest["repos"][repo_name]["statut"] = "✅ Vague déployée"
        manifest["repos"][repo_name]["derniere_synchro"] = date.today().isoformat()
    save_manifest(manifest)
    print("✅ Manifest mis à jour : {} → Vague {}".format(repo_name, wave))


def list_pending() -> None:
    manifest = load_manifest()
    print("{:<30} {:<8} {:<16} {}".format("Repo", "Strate", "Vague actuelle", "Statut"))
    print("-" * 75)
    for repo, data in manifest["repos"].items():
        print("{:<30} {:<8} {:<16} {}".format(repo, data["strate"], data["vague_courante"], data["statut"]))


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  relay_propagator.py list                    # Affiche état des vagues")
        print("  relay_propagator.py generate <REPO_NAME>    # Génère le relay (stdout)")
        print("  relay_propagator.py mark-done <REPO_NAME> <WAVE>  # Met à jour manifest")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "list":
        list_pending()
    elif cmd == "generate" and len(sys.argv) >= 3:
        print_relay(sys.argv[2])
    elif cmd == "mark-done" and len(sys.argv) >= 4:
        update_manifest_status(sys.argv[2], int(sys.argv[3]))
    else:
        print("Commande inconnue : {}".format(cmd))
        sys.exit(1)


if __name__ == "__main__":
    main()
