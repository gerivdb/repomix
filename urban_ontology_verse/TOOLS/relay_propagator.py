#!/usr/bin/env python3
"""
relay_propagator.py — Stratum Relay Wave Propagator v2.0
UrbanVerse | gerivdb/VERSUS | Version: 2.0.0
Date: 2026-05-29

Changes v2.0:
  - Mode batch : itere sur cadastre_full.yaml
  - Generation groupee par strate ou par vague cible
  - Output markdown par lot (pret pour commit MCP)
  - Dry-run mode : affiche sans ecrire
"""

import json
import yaml
import os
import sys
from datetime import date
from pathlib import Path

VERSUS_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH     = VERSUS_ROOT / "urban_ontology_verse/RELAYS/relay_wave_manifest.yaml"
CADASTRE_FULL     = VERSUS_ROOT / "urban_ontology_verse/CADASTRE/cadastre_full.yaml"
CADASTRE_PILOT    = VERSUS_ROOT / "urban_ontology_verse/CADASTRE/cadastre_pilot.yaml"
OUTPUT_BATCH_DIR  = VERSUS_ROOT / "urban_ontology_verse/TOOLS/batch_output"

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

LAYER_TO_STRATE = {
    "L0_INFRASTRUCTURE": "L4",
    "L1_CAUSALITY":      "L1",
    "L2_COMPOSITION":    "L3",
    "L3_EMERGENCE":      "L2",
    "L4_GOVERNANCE":     "L7",
    "L5_META":           "L8",
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

KARPATHY_RECALLS = {
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
        "Q: Pourquoi ECOYSTEM a-t-il 742 issues alors que NEXUS n'en a que 41 ?",
        "Q: Quel est le phi-CPS de NEXUS et ECOYSTEM, et qu'est-ce que cela signifie ?",
    ],
    "L2": [
        "Q: Quel est le role de FLUENCE par rapport a BRAIN dans la logique ternaire ?",
        "Q: VDB stocke quel type de donnees et avec quel modele d'embedding ?",
        "Q: TINA vs TRANSCENDANCE : quelle est la difference de role ?",
        "Q: Qu'est-ce que phi-CPS et quelle est la valeur cible saine pour L2 ?",
        "Q: WAZAA orchestre quels frameworks ML et pourquoi est-il en L2/L3 ?",
    ],
    "L2b": [
        "Q: Decris le pipeline atomique IRIS -> KRONOS -> FLUX en une phrase par etape.",
        "Q: Quelle est la duree d'expiration des evenements dans FLUX ?",
        "Q: ARGUS surveille quoi et pourquoi est-il le 'systeme immunitaire' ?",
        "Q: Quel est le role de KRONOS distinct de celui de IRIS ?",
        "Q: Pourquoi L2b est-il distinct de L2 dans la strate cognitive ?",
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
    "L2b": [
        "R1 — IRIS ne traite que les signaux externes. Jamais de signaux internes.",
        "R2 — FLUX expire les evenements apres 90 jours — ne pas persister au-dela.",
        "R3 — ARGUS surveille uniquement — il ne modifie jamais les repos qu'il surveille.",
        "Anti-pattern: faire pointer IRIS sur des repos internes gerivdb.",
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


def generate_relay(repo_name, strate, role, wave=1, phi_cps=None, lifecycle="ACTIVE"):
    today = date.today().isoformat()
    label = STRATE_LABELS.get(strate, strate)
    parent = PARENT_MAP.get(strate) or "— (racine absolue)"
    children = CHILD_MAP.get(strate, "—")
    rules = STRATE_RULES.get(strate, ["R1 — Respecter les regles GOVERNANCE-HUB."])
    recalls = KARPATHY_RECALLS.get(strate, ["Q: Quel est le role de ce repo dans l'ecosysteme ?"])
    rules_md = "\n".join("- {}".format(r) for r in rules)

    lifecycle_banner = ""
    if lifecycle in ("DEPRECATED", "DORMANT"):
        lifecycle_banner = "\n## Cycle de vie : {}\n\n> Ce repo est en etat `{}`. Ne pas investir de ressources sans validation GOVERNANCE-HUB.\n".format(lifecycle, lifecycle)

    phi_line = "\n- **phi-CPS** : {}".format(phi_cps) if phi_cps else ""

    recall_section = ""
    if wave >= 2:
        recall_section = "\n## Karpathy-Recall local (Vague {})\n\n> Reponds mentalement a ces questions avant d'agir dans ce repo.\n\n".format(wave)
        recall_section += "\n".join("{}. {}".format(i+1, q) for i, q in enumerate(recalls))

    return """# STRATUM RELAY — {} ({})

**VAGUE**: {} | **Synchro**: {} | **Hub**: gerivdb/LLM-REPO
{}
---

## Identite stratique

- **Strate** : `{}` — {}
- **Role canonique** : {}
- **Parent** : {}
- **Enfants** : {}{}

## Navigation rapide

- PRD canonique : `GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md`
- Substrat cognitif : `gerivdb/LLM-REPO` (L1b — prive)
- Standards repo : `REPO-STANDARDS` (RSS-v1)
- Transit map : `VERSUS/urban_ontology_verse/TRANSIT/transit_map.yaml`
- Cadastre : `VERSUS/urban_ontology_verse/CADASTRE/cadastre_full.yaml`

## Regles locales

{}
{}

## Vague de mise a jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| **{} (courante)** | {} | Deploye |
| {} (suivante) | {} | Planifie |

---

*Genere par `VERSUS/urban_ontology_verse/TOOLS/relay_propagator.py` v2.0*
*UrbanVerse v1.0.0 — gerivdb/VERSUS (L8)*
""".format(
        repo_name, strate, wave, today, lifecycle_banner,
        strate, label, role, parent, children, phi_line,
        rules_md, recall_section,
        wave, "Identite + navigation" if wave == 1 else "Identite + regles + Karpathy-Recall 5Q",
        wave + 1, "+ Regles + Recall" if wave == 1 else "Recall packs etendus + mini-exercices"
    )


def batch_generate(wave_filter=None, strate_filter=None, lifecycle_filter=None, dry_run=True):
    if not CADASTRE_FULL.exists():
        print("ERROR: {} introuvable. Creer cadastre_full.yaml d'abord.".format(CADASTRE_FULL))
        sys.exit(1)

    cadastre = yaml.safe_load(CADASTRE_FULL.read_text())
    parcelles = cadastre.get("parcelles", [])
    generated = []

    for p in parcelles:
        repo = p["repo_name"]
        strate = p["strate"]
        role = p.get("role_canonique", "Role non defini")
        wave = p.get("vague_cible", 1)
        phi = p.get("phi_cps")
        lifecycle = p.get("lifecycle", "ACTIVE")

        if wave_filter and wave != wave_filter:
            continue
        if strate_filter and strate != strate_filter:
            continue
        if lifecycle_filter and lifecycle not in lifecycle_filter:
            continue

        content = generate_relay(repo, strate, role, wave, phi, lifecycle)

        if dry_run:
            print("\n" + "=" * 60)
            print("# DRY-RUN -> gerivdb/{}/STRATUM_RELAY.md (Vague {})".format(repo, wave))
            print("=" * 60)
            print(content[:400] + "\n[...tronque en dry-run...]")
        else:
            out_dir = OUTPUT_BATCH_DIR / repo
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / "STRATUM_RELAY.md"
            out_file.write_text(content)
            print("Genere : {}".format(out_file))
            generated.append({"repo": repo, "strate": strate, "wave": wave})

    if not dry_run:
        print("\nBatch termine : {} relais generes dans {}".format(len(generated), OUTPUT_BATCH_DIR))

    return generated


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  relay_propagator.py list")
        print("  relay_propagator.py generate <REPO_NAME>")
        print("  relay_propagator.py mark-done <REPO_NAME> <WAVE>")
        print("  relay_propagator.py batch [--wave N] [--strate Lx] [--dry-run]")
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "list":
        if not MANIFEST_PATH.exists():
            print("Manifest introuvable.")
            sys.exit(1)
        manifest = yaml.safe_load(MANIFEST_PATH.read_text())
        print("{:<35} {:<8} {:<8} {}".format("Repo", "Strate", "Vague", "Statut"))
        print("-" * 80)
        for repo, data in manifest.get("repos", {}).items():
            print("{:<35} {:<8} {:<8} {}".format(repo, data["strate"], data["vague_courante"], data["statut"]))

    elif cmd == "generate" and args:
        repo_name = args[0]
        cadastre_path = CADASTRE_FULL if CADASTRE_FULL.exists() else CADASTRE_PILOT
        cadastre = yaml.safe_load(cadastre_path.read_text())
        parcelle = next((p for p in cadastre.get("parcelles", []) if p["repo_name"] == repo_name), None)
        if not parcelle:
            print("ERROR: '{}' introuvable dans le cadastre.".format(repo_name))
            sys.exit(1)
        content = generate_relay(
            repo_name, parcelle["strate"],
            parcelle.get("role_canonique", "Role non defini"),
            parcelle.get("vague_cible", 1),
            parcelle.get("phi_cps"),
            parcelle.get("lifecycle", "ACTIVE"),
        )
        print(content)
        print("\n# -- A commettre dans : gerivdb/{}/STRATUM_RELAY.md --".format(repo_name))

    elif cmd == "mark-done" and len(args) >= 2:
        manifest = yaml.safe_load(MANIFEST_PATH.read_text())
        repo, wave = args[0], int(args[1])
        if repo in manifest["repos"]:
            manifest["repos"][repo]["vague_courante"] = wave
            manifest["repos"][repo]["statut"] = "Vague deployee"
            manifest["repos"][repo]["derniere_synchro"] = date.today().isoformat()
            with open(MANIFEST_PATH, "w") as f:
                yaml.dump(manifest, f, allow_unicode=True, sort_keys=False)
            print("Manifest mis a jour : {} -> Vague {}".format(repo, wave))
        else:
            print("ERROR: '{}' absent du manifest.".format(repo))

    elif cmd == "batch":
        wave_f = int(args[args.index("--wave") + 1]) if "--wave" in args else None
        strate_f = args[args.index("--strate") + 1] if "--strate" in args else None
        dry = "--dry-run" in args
        batch_generate(wave_filter=wave_f, strate_filter=strate_f, dry_run=dry)

    else:
        print("Commande inconnue : {}".format(cmd))
        sys.exit(1)


if __name__ == "__main__":
    main()
