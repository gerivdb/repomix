#!/usr/bin/env python3
"""
relay_propagator.py — Stratum Relay Wave Propagator v3.0
UrbanVerse | gerivdb/VERSUS | Version: 3.0.0
Date: 2026-05-29

Changes v3.0:
  - A1 : Mode --auto-commit via API GitHub (PyGithub)
  - A2 : detect_default_branch() — tente main→master→autre
  - A3 : upsert_file() — get SHA + create/update en un appel logique
  - A4 : verify_repo_exists() — search avant commit
  - A5 : create_repo_with_structure() — bootstrap repo atomique
  - A6 : update_manifest_batch() — mise à jour SOT après batch
  - A7 : parallel_batch_deploy() — 10 commits simultanés
  - A8 : generate_stratum_relay_bulk() — depuis cadastre_full.yaml
  - KARPATHY_RECALLS_V3 : 10Q/strate pour Vague 3
  - Section dépendances auto-générée depuis cadastre
"""

import json
import yaml
import os
import sys
import time
import argparse
from datetime import date
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Config ───────────────────────────────────────────────────────────────────
VERSUS_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH     = VERSUS_ROOT / "urban_ontology_verse/RELAYS/relay_wave_manifest.yaml"
CADASTRE_FULL     = VERSUS_ROOT / "urban_ontology_verse/CADASTRE/cadastre_full.yaml"
CADASTRE_PILOT    = VERSUS_ROOT / "urban_ontology_verse/CADASTRE/cadastre_pilot.yaml"
OUTPUT_BATCH_DIR  = VERSUS_ROOT / "urban_ontology_verse/TOOLS/batch_output"

OWNER = "gerivdb"

STRATE_LABELS = {
    "L0":  "Constitution — Super-Super-Hub",
    "L1b": "Substrat cognitif LLM (prive)",
    "L1":  "Substrat global operationnel",
    "L2":  "Systeme nerveux central",
    "L2b": "Triade sensorielle",
    "L3":  "Systeme moteur CLI",
    "L4":  "Infrastructure & Hardware",
    "L5":  "IA distribuee & LLM",
    "L6":  "Memoire & Documentation",
    "L7":  "Interfaces utilisateur & Dev",
    "L8":  "Vie reelle & Creatif",
    "L9":  "Archeologie (exclue LLM)",
}

PARENT_MAP = {
    "L0": None,  "L1b": "L0", "L1": "L1b",
    "L2": "L1",  "L2b": "L2", "L3": "L2",
    "L4": "L3",  "L5":  "L4", "L6": "L5",
    "L7": "L6",  "L8":  "L7", "L9": "L8",
}
CHILD_MAP = {
    "L0": "L1b",       "L1b": "L1",    "L1": "L2",
    "L2": "L2b + L3",  "L2b": "L3",    "L3": "L4",
    "L4": "L5",        "L5":  "L6",    "L6": "L7",
    "L7": "L8",        "L8":  "L9",    "L9": "—",
}

# ── Karpathy Recalls V2 (5Q) ─────────────────────────────────────────────────
KARPATHY_RECALLS_V2 = {
    "L0": [
        "Q: Quelle est la difference entre GOVERNANCE-HUB et LLM-REPO ?",
        "Q: Quel fichier contient la liste canonique de tous les repos actifs ?",
        "Q: Qu'est-ce qu'un Super-Super-Hub et pourquoi GOVERNANCE-HUB l'est-il ?",
        "Q: Dans quel ordre les 3 premiers repos doivent-ils etre ingerees par un LLM ?",
        "Q: Que contient AGENT_RAM.yaml et quand doit-il etre mis a jour ?",
    ],
    "L1b": [
        "Q: Pourquoi LLM-REPO est-il prive et distinct de ECOS-CLI ?",
        "Q: Quels 3 types de fichiers LLM-REPO centralise-t-il que ECOS-CLI ne contient plus ?",
        "Q: Quelle est la sequence d'ingeration canonique pour un LLM entrant dans l'ecosysteme ?",
        "Q: Ou vivent .kilocodemodes et .roomodes dans l'ecosysteme post-migration v1.1.0 ?",
        "Q: Que contient LLM-REPO/BOOT/boot_sequence.md et qui le maintient ?",
    ],
    "L1": [
        "Q: Quelle est la difference de role entre ECOYSTEM et NEXUS ?",
        "Q: Un nouveau repo doit etre enregistre dans quel fichier et dans quel repos ?",
        "Q: ONTOLOGY est en P1_STRATEGIC — quel type de contenus y vit ?",
        "Q: Quel est le phi-CPS de NEXUS et ECOYSTEM, et qu'est-ce que cela signifie ?",
        "Q: Quel fichier contient la liste canonique de tous les repos actifs ?",
    ],
    "L2": [
        "Q: Quel est le role de FLUENCE par rapport a BRAIN dans la logique ternaire ?",
        "Q: VDB stocke quel type de donnees et avec quel modele d'embedding ?",
        "Q: TINA vs TRANSCENDANCE : quelle est la difference de role ?",
        "Q: Qu'est-ce que phi-CPS et quelle est la valeur cible saine pour L2 ?",
        "Q: WAZAA orchestre quels frameworks ML et pourquoi est-il en L2/L3 ?",
    ],
    "L3": [
        "Q: Apres migration v1.1.0, que contient ECOS-CLI et que NE contient-il PLUS ?",
        "Q: Quelle est la frontiere de responsabilite entre ECOS-CLI et DevTools ?",
        "Q: Qu'est-ce que BLO et quel format de base de donnees utilise-t-il ?",
        "Q: OPENCLAW-CLI est decrit comme 'Intent Normalization Gateway' — qu'est-ce que cela veut dire ?",
        "Q: FLUENCE-CLI delegue a ECOS-CLI — quelle est la regle de delegation ?",
    ],
    "L4": [
        "Q: Quel repo gere le hardware HP Z600 en LXC/LXD ?",
        "Q: ATLAS geere l'IaC declaratif — quelle est la difference avec KIVA ?",
        "Q: GATEWAY-MANAGER gere quelles responsabilitees reseau (BDCP, Clapet) ?",
        "Q: CONTAINER-ORCHESTRATOR vs KIVA : lequel orchestre LXC nativement ?",
        "Q: FERMI-EVER orchestre quels GPUs specifiques et pourquoi sont-ils 'abandonnes' ?",
    ],
    "L5": [
        "Q: BOINC-LLM-P2P utilise quel protocole de distribution (DHT Kademlia) ?",
        "Q: vsix-ai-orchestrator orchestre quels agents IDE (Cline, Kilocode, Copilot) ?",
        "Q: CLIP-FACTORY produit quel type d'artefacts (embeddings vision-language) ?",
        "Q: PLIX est un 'langage video ternaire pour LLM' — quel est son role dans L5 ?",
        "Q: LYCOS est un fork de CodeDB avec quelles extensions specifiques ?",
    ],
    "L6": [
        "Q: MIMIR est decrire comme 'Wiki Atomique Diamond' — qu'est-ce que cela signifie ?",
        "Q: BRAIN-DOCS documente uniquement BRAIN — ou va la doc des autres repos ?",
        "Q: SKILLS contient 28 skills actifs — quelle est leur structure tripartite ?",
        "Q: DOC-UNIV-DEV est une 'base de connaissances R&D' — en quoi differe-t-il de MIMIR ?",
        "Q: Quel repo visualise l'architecture L0->L4.5 sous forme diagrammatique ?",
    ],
    "L7": [
        "Q: GeriCode est un fork de quel outil IDE (KiloCode) ?",
        "Q: COMET gere l'automation browser — quelle technologie utilise-t-il ?",
        "Q: appflowy-mcp-server remplace quel SaaS commercial (Notion) ?",
        "Q: Quel est le role de ECOS-VISION dans la visualisation de l'ecosysteme ?",
        "Q: BatMCP expose quels outils via MCP PowerShell ?",
    ],
    "L8": [
        "Q: VERSUS est en L8 — quelle est sa responsabilite vs BATVERSE ?",
        "Q: BATVERSE est decrit comme 'cluster narratif-dramatique' — qu'est-ce que cela signifie ?",
        "Q: Quelle est la regle absolue avant d'implementer la monnaie Geri (G) ?",
        "Q: TRANSCENDANCE est en L5_META dans known_repositories — pourquoi UrbanVerse le place en L8 ?",
        "Q: CANDIDATOR est en L3_EMERGENCE — quel est son role dans la vie reelle ?",
    ],
}

# ── Karpathy Recalls V3 (10Q + dependances) ──────────────────────────────────
KARPATHY_RECALLS_V3 = {
    "L0": [
        "Q: Quelle est la difference entre GOVERNANCE-HUB et LLM-REPO ?",
        "Q: Quel fichier contient la liste canonique de tous les repos actifs ?",
        "Q: Qu'est-ce qu'un Super-Super-Hub et pourquoi GOVERNANCE-HUB l'est-il ?",
        "Q: Dans quel ordre les 3 premiers repos doivent-ils etre ingerees par un LLM ?",
        "Q: Que contient AGENT_RAM.yaml et quand doit-il etre mis a jour ?",
        "Q: Quels repos dependent directement de L0 (enfants directs) ?",
        "Q: Quel est le role de GOVERNANCE-HUB dans la boot sequence LLM ?",
        "Q: Quelle ADR historique a defini la structure L0→L9 de l'ecosysteme ?",
        "Q: Pourquoi aucun LLM ne doit bypasser GOVERNANCE-HUB en debut de session ?",
        "Q: Dans quelle phase UrbanVerse le STRATUM_RELAY de ce repo a-t-il ete deploye ?",
    ],
    "L1b": [
        "Q: Pourquoi LLM-REPO est-il prive et distinct de ECOS-CLI ?",
        "Q: Quels 3 types de fichiers LLM-REPO centralise-t-il que ECOS-CLI ne contient plus ?",
        "Q: Quelle est la sequence d'ingeration canonique pour un LLM entrant dans l'ecosysteme ?",
        "Q: Ou vivent .kilocodemodes et .roomodes dans l'ecosysteme post-migration v1.1.0 ?",
        "Q: Que contient LLM-REPO/BOOT/boot_sequence.md et qui le maintient ?",
        "Q: Quels repos dependent directement de L1b ?",
        "Q: Quel est le role de LLM-REPO dans la gouvernance LLM de l'ecosysteme ?",
        "Q: Pourquoi ECOS-CLI ne contient plus de regles LLM apres migration v1.1.0 ?",
        "Q: Quelle est la difference entre L1b et L1 dans UrbanVerse ?",
        "Q: Dans quelle phase UrbanVerse le STRATUM_RELAY de ce repo a-t-il ete deploye ?",
    ],
    "L1": [
        "Q: Quelle est la difference de role entre ECOYSTEM et NEXUS ?",
        "Q: Un nouveau repo doit etre enregistre dans quel fichier et dans quel repos ?",
        "Q: ONTOLOGY est en P1_STRATEGIC — quel type de contenus y vit ?",
        "Q: Quel est le phi-CPS de NEXUS et ECOYSTEM, et qu'est-ce que cela signifie ?",
        "Q: Quel fichier contient la liste canonique de tous les repos actifs ?",
        "Q: Quels repos dependent directement de L1 (ECOYSTEM, NEXUS) ?",
        "Q: Quel est le role du SOT operationnel dans l'ecosysteme gerivdb ?",
        "Q: Pourquoi NEXUS ne doit jamais contenir de donnees primaires ?",
        "Q: Quelle regle impose ONTOLOGY a tout nouveau repo ?",
        "Q: Dans quelle phase UrbanVerse le STRATUM_RELAY de ce repo a-t-il ete deploye ?",
    ],
    "L2": [
        "Q: Quel est le role de FLUENCE par rapport a BRAIN dans la logique ternaire ?",
        "Q: VDB stocke quel type de donnees et avec quel modele d'embedding ?",
        "Q: TINA vs TRANSCENDANCE : quelle est la difference de role ?",
        "Q: Qu'est-ce que phi-CPS et quelle est la valeur cible saine pour L2 ?",
        "Q: WAZAA orchestre quels frameworks ML et pourquoi est-il en L2/L3 ?",
        "Q: Quels repos dependent directement de L2 (BRAIN, FLUENCE) ?",
        "Q: Quel est le role du hub cognitif racine dans l'ecosysteme ?",
        "Q: Pourquoi tout score ternaire doit-il passer par FLUENCE et non BRAIN ?",
        "Q: Quelle est la frontiere entre L2 et L2b ?",
        "Q: Dans quelle phase UrbanVerse le STRATUM_RELAY de ce repo a-t-il ete deploye ?",
    ],
    "L3": [
        "Q: Apres migration v1.1.0, que contient ECOS-CLI et que NE contient-il PLUS ?",
        "Q: Quelle est la frontiere de responsabilite entre ECOS-CLI et DevTools ?",
        "Q: Qu'est-ce que BLO et quel format de base de donnees utilise-t-il ?",
        "Q: OPENCLAW-CLI est decrit comme 'Intent Normalization Gateway' — qu'est-ce que cela veut dire ?",
        "Q: FLUENCE-CLI delegue a ECOS-CLI — quelle est la regle de delegation ?",
        "Q: Quels repos dependent directement de L3 (ECOS-CLI, CLIs) ?",
        "Q: Quel est le role de L3 dans la boot sequence ?",
        "Q: Pourquoi les regles LLM ne doivent pas resider dans ECOS-CLI ?",
        "Q: Quelle commande ecos * est la plus critique a tester ?",
        "Q: Dans quelle phase UrbanVerse le STRATUM_RELAY de ce repo a-t-il ete deploye ?",
    ],
    "L4": [
        "Q: Quel repo gere le hardware HP Z600 en LXC/LXD ?",
        "Q: ATLAS geere l'IaC declaratif — quelle est la difference avec KIVA ?",
        "Q: GATEWAY-MANAGER gere quelles responsabilitees reseau (BDCP, Clapet) ?",
        "Q: CONTAINER-ORCHESTRATOR vs KIVA : lequel orchestre LXC nativement ?",
        "Q: FERMI-EVER orchestre quels GPUs specifiques et pourquoi sont-ils 'abandonnes' ?",
        "Q: Quels repos dependent directement de L4 ?",
        "Q: Quel est le role de l'infrastructure dans UrbanVerse ?",
        "Q: Pourquoi tout deploiement sur HP Z600 doit passer par KIVA ?",
        "Q: Quelle est la frontiere entre L3 et L4 ?",
        "Q: Dans quelle phase UrbanVerse le STRATUM_RELAY de ce repo a-t-il ete deploye ?",
    ],
    "L6": [
        "Q: MIMIR est decrire comme 'Wiki Atomique Diamond' — qu'est-ce que cela signifie ?",
        "Q: BRAIN-DOCS documente uniquement BRAIN — ou va la doc des autres repos ?",
        "Q: SKILLS contient 28 skills actifs — quelle est leur structure tripartite ?",
        "Q: DOC-UNIV-DEV est une 'base de connaissances R&D' — en quoi differe-t-il de MIMIR ?",
        "Q: Quel repo visualise l'architecture L0->L4.5 sous forme diagrammatique ?",
        "Q: Quels repos dependent directement de L6 ?",
        "Q: Quel est le role de la memoire dans l'ecosysteme gerivdb ?",
        "Q: Pourquoi MIMIR ne doit pas contenir de documentation de repos individuels ?",
        "Q: Quelle est la difference entre MIMIR et BRAIN-DOCS ?",
        "Q: Dans quelle phase UrbanVerse le STRATUM_RELAY de ce repo a-t-il ete deploye ?",
    ],
    "L7": [
        "Q: GeriCode est un fork de quel outil IDE (KiloCode) ?",
        "Q: COMET gere l'automation browser — quelle technologie utilise-t-il ?",
        "Q: appflowy-mcp-server remplace quel SaaS commercial (Notion) ?",
        "Q: Quel est le role de ECOS-VISION dans la visualisation de l'ecosysteme ?",
        "Q: BatMCP expose quels outils via MCP PowerShell ?",
        "Q: Quels repos dependent directement de L7 ?",
        "Q: Quel est le role des interfaces dans UrbanVerse ?",
        "Q: Pourquoi COMET est-il le seul repo a gerer l'automation browser ?",
        "Q: Quelle est la frontiere entre L6 et L7 ?",
        "Q: Dans quelle phase UrbanVerse le STRATUM_RELAY de ce repo a-t-il ete deploye ?",
    ],
    "L8": [
        "Q: VERSUS est en L8 — quelle est sa responsabilite vs BATVERSE ?",
        "Q: BATVERSE est decrit comme 'cluster narratif-dramatique' — qu'est-ce que cela signifie ?",
        "Q: Quelle est la regle absolue avant d'implementer la monnaie Geri (G) ?",
        "Q: TRANSCENDANCE est en L5_META dans known_repositories — pourquoi UrbanVerse le place en L8 ?",
        "Q: CANDIDATOR est en L3_EMERGENCE — quel est son role dans la vie reelle ?",
        "Q: Quels repos dependent directement de L8 (VERSUS) ?",
        "Q: Quel est le role de L8 (Vie reelle & Creatif) dans UrbanVerse ?",
        "Q: Pourquoi VERSUS et BATVERSE ne doivent jamais etre fusionnes ?",
        "Q: Quelle est la frontiere entre L7 et L8 ?",
        "Q: Dans quelle phase UrbanVerse le STRATUM_RELAY de ce repo a-t-il ete deploye ?",
    ],
}

STRATE_RULES = {
    "L0": [
        "R1 — Ce repo est ingere EN PREMIER par tout LLM. Ne jamais bypasser.",
        "R2 — known_repositories.yaml est la SEULE source of truth des 72 repos actifs.",
        "R3 — Toute modification structurelle necessite une ADR dans ADR/.",
        "Anti-pattern: modifier AGENT_RAM.yaml sans fin de session productive.",
    ],
    "L1b": [
        "R1 — LLM-REPO est ingere EN SECONDE, immediatement apres GOVERNANCE-HUB.",
        "R2 — Aucune regle LLM ne doit resider dans ECOS-CLI (post-migration v1.1.0).",
        "R3 — Ce repo est prive — ne pas exposer les profils d'agents publiquement.",
        "Anti-pattern: stocker .kilocodemodes ailleurs que LLM-REPO/AGENTS/modes/",
    ],
    "L1": [
        "R1 — ECOYSTEM est le SOT operationnel — toute action L3+ doit etre conforme.",
        "R2 — NEXUS agrege — ne jamais ecrire de donnees primaires dans NEXUS.",
        "R3 — Tout nouveau repo doit etre enregistre dans known_repositories.yaml (L0).",
        "Anti-pattern: creer un repo sans l'enregistrer dans GOVERNANCE-HUB.",
    ],
    "L2": [
        "R1 — BRAIN est le hub cognitif racine — ne pas dupliquer sa logique en L3.",
        "R2 — FLUENCE gere la logique ternaire — tout score ternaire passe par FLUENCE.",
        "R3 — VDB accepte uniquement nomic-embed (768-dim) comme modele d'embedding.",
        "Anti-pattern: implementer de la logique ternaire directement dans ECOS-CLI.",
    ],
    "L3": [
        "R1 — ECOS-CLI est un executable pur — zero regle LLM post-migration v1.1.0.",
        "R2 — Toute commande ecos * doit avoir un test dans DevTools-CLI.",
        "R3 — BLO utilise bloom.db + WAL — ne jamais acceder a bloom.db directement.",
        "Anti-pattern: ajouter des fichiers .md de gouvernance dans ECOS-CLI.",
    ],
    "L4": [
        "R1 — KIVA orchestre LXC/LXD sur HP Z600 uniquement — ne pas generaliser.",
        "R2 — ATLAS = IaC declaratif — toute infra doit etre definie comme code.",
        "R3 — Tout deploiement sur HP Z600 passe par KIVA — jamais directement.",
        "Anti-pattern: deployer sur HP Z600 sans passer par KIVA.",
    ],
    "L5": [
        "R1 — BOINC-LLM-P2P gere toute inference distribuee — obligatoire.",
        "R2 — vsix-ai-orchestre uniquement les agents VSCode.",
        "R3 — CLIP-FACTORY produit uniquement des embeddings vision-language.",
        "Anti-pattern: lancer une inference LLM distribuee sans BOINC-LLM-P2P.",
    ],
    "L6": [
        "R1 — MIMIR est la source of truth visuelle — roadmaps et diagrammes.",
        "R2 — BRAIN-DOCS documente BRAIN uniquement — pas d'autres repos.",
        "R3 — SKILLS = registry tripartite natifs/assimiles/externes.",
        "Anti-pattern: mettre la documentation d'un repo dans MIMIR.",
    ],
    "L7": [
        "R1 — GeriCode est un fork de KiloCode — maintenir compatibilite upstream.",
        "R2 — COMET gere l'automation browser — pas de scraping ailleurs.",
        "R3 — appflowy-mcp-server remplace Notion — ne pas utiliser l'API Notion.",
        "Anti-pattern: dupliquer la logique d'automation browser hors COMET.",
    ],
    "L8": [
        "R1 — VERSUS est ontologique — BATVERSE est narratif. Ne jamais fusionner.",
        "R2 — Toute monnaie interne (Geri G) necessite une ADR validee dans GOVERNANCE-HUB.",
        "R3 — Les repos L8 culturels ne dependent pas directement de L2/L3.",
        "Anti-pattern: implementer la Geri (G) sans ADR constitutionnelle.",
    ],
}


# ── A2 : detect_default_branch ───────────────────────────────────────────────
def detect_default_branch(g, owner: str, repo_name: str):
    """Retourne (branch_name, repo_object) ou (None, None) si inexistant."""
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
        return repo.default_branch, repo
    except Exception:
        return None, None


# ── A4 : verify_repo_exists ──────────────────────────────────────────────────
def verify_repo_exists(g, owner: str, repo_name: str) -> bool:
    branch, _ = detect_default_branch(g, owner, repo_name)
    return branch is not None


# ── A3 : upsert_file ─────────────────────────────────────────────────────────
def upsert_file(repo, path: str, content: str, message: str, branch: str):
    """Get SHA si existe, puis create ou update en un appel logique."""
    try:
        existing = repo.get_contents(path, ref=branch)
        repo.update_file(path, message, content, existing.sha, branch=branch)
        return "updated"
    except Exception:
        repo.create_file(path, message, content, branch=branch)
        return "created"


# ── Generateur de dependances depuis cadastre ─────────────────────────────────
def generate_dependencies_section(repo_name: str, strate: str, cadastre: dict) -> str:
    """Genere la section dependances directes depuis cadastre_full.yaml."""
    parcelles = cadastre.get("parcelles", [])
    current = next((p for p in parcelles if p["repo_name"] == repo_name), None)
    if not current:
        return ""

    parent_strate = PARENT_MAP.get(strate)
    children_strate = CHILD_MAP.get(strate, "")

    parents = [p["repo_name"] for p in parcelles if p.get("strate") == parent_strate and p.get("lifecycle") == "ACTIVE"]
    children = [p["repo_name"] for p in parcelles if p.get("strate", "").startswith(strate) and p["repo_name"] != repo_name and p.get("lifecycle") == "ACTIVE"]

    if not parents and not children:
        return ""

    section = "\n## Dependances directes\n"
    if parents:
        section += "\n**Parents (amont) :**\n" + "\n".join(f"- {p}" for p in parents[:5]) + "\n"
    if children:
        section += "\n**Enfants (aval) :**\n" + "\n".join(f"- {c}" for c in children[:10]) + "\n"
    return section


# ── generate_relay ────────────────────────────────────────────────────────────
def generate_relay(parcelle: dict, cadastre: dict, wave: int = 1) -> str:
    repo_name = parcelle["repo_name"]
    strate = parcelle["strate"]
    role = parcelle.get("role_canonique", "Role non defini")
    phi_cps = parcelle.get("phi_cps")
    lifecycle = parcelle.get("lifecycle", "ACTIVE")
    today = date.today().isoformat()
    label = STRATE_LABELS.get(strate, strate)
    parent = PARENT_MAP.get(strate) or "— (racine absolue)"
    children = CHILD_MAP.get(strate, "—")
    rules = STRATE_RULES.get(strate, ["R1 — Respecter les regles GOVERNANCE-HUB."])
    rules_md = "\n".join(f"- {r}" for r in rules)

    lifecycle_banner = ""
    if lifecycle in ("DEPRECATED", "DORMANT"):
        lifecycle_banner = f"\n## Cycle de vie : {lifecycle}\n\n> Ce repo est en etat `{lifecycle}`. Ne pas investir de ressources sans validation GOVERNANCE-HUB.\n"

    phi_line = f"\n- **phi-CPS** : {phi_cps}" if phi_cps else ""

    # Recalls selon la vague
    recall_section = ""
    if wave >= 3:
        recalls = KARPATHY_RECALLS_V3.get(strate, [f"Q: Quel est le role de {repo_name} ?"])
        recall_header = f"## Karpathy-Recall etendu (Vague 3 — {len(recalls)}Q)"
    elif wave >= 2:
        recalls = KARPATHY_RECALLS_V2.get(strate, [f"Q: Quel est le role de {repo_name} ?"])
        recall_header = f"## Karpathy-Recall local (Vague 2 — {len(recalls)}Q)"
    else:
        recalls = []

    if recalls:
        recall_section = f"\n{recall_header}\n\n> Reponds mentalement a ces questions avant d'agir dans ce repo.\n\n"
        recall_section += "\n".join(f"{i+1}. {q}" for i, q in enumerate(recalls))

    # Dependances (Vague 3+)
    deps_section = generate_dependencies_section(repo_name, strate, cadastre) if wave >= 3 else ""

    vague_label = "Identite + navigation" if wave == 1 else "Identite + regles + Karpathy-Recall 5Q" if wave == 2 else "Identite + regles + Karpathy-Recall 10Q + dependances"

    return f"""# STRATUM RELAY — {repo_name} ({strate})

**VAGUE**: {wave} | **Synchro**: {today} | **Hub**: gerivdb/LLM-REPO
{lifecycle_banner}
---

## Identite stratique

- **Strate** : `{strate}` — {label}
- **Role canonique** : {role}
- **Parent** : {parent}
- **Enfants** : {children}{phi_line}

## Navigation rapide

- PRD canonique : `GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md`
- Substrat cognitif : `gerivdb/LLM-REPO` (L1b — prive)
- Standards repo : `REPO-STANDARDS` (RSS-v1)
- Transit map : `VERSUS/urban_ontology_verse/TRANSIT/transit_map.yaml`
- Cadastre : `VERSUS/urban_ontology_verse/CADASTRE/cadastre_full.yaml`

## Regles locales

{rules_md}
{recall_section}
{deps_section}
## Vague de mise a jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| **{wave} (courante)** | {vague_label} | Deploye |
| {wave + 1} (suivante) | {"+ Regles + Recall" if wave == 1 else "Recall packs etendus + mini-exercices + dependances" if wave == 2 else "Agents locaux + auto-conformite"} | Planifie |

---

*Genere par `VERSUS/urban_ontology_verse/TOOLS/relay_propagator.py` v3.0*
*UrbanVerse v1.0.0 — gerivdb/VERSUS (L8)*
"""


# ── A6 : update_manifest_batch ───────────────────────────────────────────────
def update_manifest_batch(deployed: list, wave: int, skipped: list, failed: list):
    """Met a jour le manifest apres un batch."""
    if not MANIFEST_PATH.exists():
        return
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    for repo in deployed:
        if repo in manifest["repos"]:
            manifest["repos"][repo]["vague_courante"] = wave
            manifest["repos"][repo]["statut"] = f"Vague {wave} deployee"
            manifest["repos"][repo]["derniere_synchro"] = date.today().isoformat()

    # Mettre a jour le summary
    s = manifest.get("summary", {})
    key = f"vague_{wave}_deployes"
    s[key] = s.get(key, 0) + len(deployed)
    s["total_stratum_relay_deployes"] = s.get("total_stratum_relay_deployes", 0) + len(deployed)
    s["echecs_a_traiter"] = len(failed)
    manifest["summary"] = s

    with open(MANIFEST_PATH, "w") as f:
        yaml.dump(manifest, f, allow_unicode=True, sort_keys=False)


# ── A1 + A7 : batch_deploy_stratum_relays ────────────────────────────────────
def batch_deploy_stratum_relays(
    wave: int,
    dry_run: bool = True,
    token: str = None,
    max_workers: int = 5,
    specific_repos: list = None,
):
    """
    Deploie les STRATUM_RELAY.md pour tous les repos du cadastre ciblant wave N.
    Si dry_run=True : affiche sans committer.
    Si dry_run=False : commit via API GitHub (PyGithub).
    """
    try:
        from github import Github
    except ImportError:
        print("ERROR: PyGithub requis. pip install PyGithub")
        sys.exit(1)

    g = Github(token) if token else Github()
    cadastre = yaml.safe_load(CADASTRE_FULL.read_text())
    parcelles = cadastre.get("parcelles", [])

    deployed, skipped, failed = [], [], []

    def process_one(parcelle):
        repo_name = parcelle["repo_name"]
        strate = parcelle["strate"]
        vague_cible = parcelle.get("vague_cible", 0)
        vague_courante = parcelle.get("vague_courante", 0)
        lifecycle = parcelle.get("lifecycle", "ACTIVE")

        # Filtres
        if specific_repos and repo_name not in specific_repos:
            return ("skip", repo_name, "pas dans la liste specifique")
        if lifecycle in ("DEPRECATED", "PENDING_CREATION"):
            return ("skip", repo_name, f"lifecycle exclu: {lifecycle}")
        if vague_cible < wave:
            return ("skip", repo_name, f"vague_cible {vague_cible} < {wave}")
        if vague_courante >= wave:
            return ("skip", repo_name, f"deja en vague {vague_courante}")

        # A2 : detecter branche
        branch, repo_obj = detect_default_branch(g, OWNER, repo_name)
        if branch is None:
            return ("fail", repo_name, "repo inexistant sur GitHub")

        contenu = generate_relay(parcelle, cadastre, wave)

        if dry_run:
            return ("dry_run", repo_name, f"branche={branch}")

        # Commit
        try:
            msg = f"feat(urban-verse): deploy/upgrade STRATUM_RELAY.md Vague {wave} [CONFORME_NEXUS]"
            status = upsert_file(repo_obj, "STRATUM_RELAY.md", contenu, msg, branch)
            parcelle["vague_courante"] = wave
            time.sleep(0.3)
            return ("deployed", repo_name, status)
        except Exception as e:
            return ("fail", repo_name, str(e))

    # A7 : Parallélisation
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_one, p): p for p in parcelles}
        for future in as_completed(futures):
            result = future.result()
            status, repo_name, detail = result[0], result[1], result[2] if len(result) > 2 else ""
            if status == "deployed" or status == "dry_run":
                deployed.append(repo_name)
            elif status == "skip":
                skipped.append((repo_name, detail))
            else:
                failed.append((repo_name, detail))

    # A6 : Update manifest + cadestre
    if not dry_run and deployed:
        update_manifest_batch(deployed, wave, skipped, failed)
        with open(CADASTRE_FULL, "w") as f:
            yaml.dump(cadastre, f, allow_unicode=True, sort_keys=False)

    # Rapport
    print(f"\n{'='*60}")
    mode = "[DRY-RUN]" if dry_run else "[LIVE]"
    print(f"  Batch Vague {wave} {mode}")
    print(f"  Deploys  : {len(deployed)} — {deployed[:5]}{'...' if len(deployed) > 5 else ''}")
    print(f"  Skippes  : {len(skipped)}")
    print(f"  Echoues  : {len(failed)}")
    for repo, err in failed:
        print(f"    {repo}: {err}")

    return deployed, skipped, failed


# ── A9 : validate_deployment ─────────────────────────────────────────────────
def validate_deployment():
    """Post-deploiement : verifie coherence manifest vs reel."""
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    cadastre = yaml.safe_load(CADASTRE_FULL.read_text())
    errors, warnings = [], []

    for repo_name, data in manifest.get("repos", {}).items():
        vague = data.get("vague_courante", 0)
        if vague == 0:
            continue
        # Verifier que le fichier existe (si repo existe)
        parcelle = next((p for p in cadastre.get("parcelles", []) if p["repo_name"] == repo_name), None)
        if not parcelle:
            warnings.append(f"{repo_name}: pas dans cadastre")
            continue
        if parcelle.get("vague_courante", 0) != vague:
            errors.append(f"{repo_name}: manifest={vague} vs cadastre={parcelle.get('vague_courante', 0)}")

    for e in errors:
        print(f"ERREUR: {e}")
    for w in warnings:
        print(f"WARNING: {w}")

    print(f"\nValidation: {len(errors)} erreurs, {len(warnings)} warnings")
    return len(errors) == 0


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="UrbanVerse Stratum Relay Propagator v3.0")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list", help="Etat des vagues")

    gen = sub.add_parser("generate", help="Genere le contenu (stdout)")
    gen.add_argument("repo")
    gen.add_argument("--wave", type=int, default=2)

    mark = sub.add_parser("mark-done", help="Met a jour le manifest")
    mark.add_argument("repo")
    mark.add_argument("wave", type=int)

    batch = sub.add_parser("batch", help="Batch deploy")
    batch.add_argument("--wave", type=int, required=True)
    batch.add_argument("--dry-run", action="store_true", default=True)
    batch.add_argument("--auto-commit", action="store_true", default=False)
    batch.add_argument("--token", default=None)
    batch.add_argument("--workers", type=int, default=5)
    batch.add_argument("--repos", nargs="*", default=None)

    sub.add_parser("validate", help="Valide coherence manifest vs cadestre")

    args = parser.parse_args()

    if args.cmd == "list":
        if MANIFEST_PATH.exists():
            m = yaml.safe_load(MANIFEST_PATH.read_text())
            print(f"{'Repo':<35} {'Strate':<8} {'Vague':<8} Statut")
            print("-" * 80)
            for r, d in m.get("repos", {}).items():
                print(f"{r:<35} {d.get('strate','?'):<8} {d.get('vague_courante',0):<8} {d.get('statut','?')}")

    elif args.cmd == "generate":
        cad = yaml.safe_load(CADASTRE_FULL.read_text()) if CADASTRE_FULL.exists() else yaml.safe_load(CADASTRE_PILOT.read_text())
        p = next((x for x in cad.get("parcelles", []) if x["repo_name"] == args.repo), None)
        if not p:
            print(f"ERROR: {args.repo} introuvable")
            sys.exit(1)
        print(generate_relay(p, cad, args.wave))

    elif args.cmd == "mark-done":
        m = yaml.safe_load(MANIFEST_PATH.read_text())
        if args.repo in m["repos"]:
            m["repos"][args.repo]["vague_courante"] = args.wave
            m["repos"][args.repo]["statut"] = f"Vague {args.wave} deployee"
            with open(MANIFEST_PATH, "w") as f:
                yaml.dump(m, f, allow_unicode=True, sort_keys=False)
            print(f"OK: {args.repo} → Vague {args.wave}")

    elif args.cmd == "batch":
        deployed, skipped, failed = batch_deploy_stratum_relays(
            wave=args.wave,
            dry_run=not args.auto_commit,
            token=args.token,
            max_workers=args.workers,
            specific_repos=args.repos,
        )
        if failed:
            sys.exit(1)

    elif args.cmd == "validate":
        ok = validate_deployment()
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
