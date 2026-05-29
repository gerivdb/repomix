# EPIC-06 — Stratum Relays — Déploiement Complet des Vagues (Phases 1-7)

---

**EPIC** : EPIC-06
**Titre** : Déploiement Complet des Stratum Relays — Vagues 1 à 7
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`
**EPIC précédent** : EPIC-03 (Vague 1 pilote)
**Version** : 1.0.0
**Date** : 2026-05-29
**Statut** : 🟢 EN COURS — Phases 1-6 complétées, Phase 7 planifiée
**Priorité** : P0 — Infrastructure de gouvernance cognitive

---

## Objectif

Déployer les **Stratum Relays** dans la totalité de l'écosystème gerivdb (76 repos), strate par strate, en 7 vagues progressives. Chaque Stratum Relay est un fichier `STRATUM_RELAY.md` qui déclare l'identité stratique d'un repo, ses règles locales, son Karpathy-Recall, ses dépendances, et ses capacités d'auto-conformité.

Une ville ne se construit pas d'un coup. Elle se construit arrondissement par arrondissement.

---

## Phases de déploiement

### Phase 1 — Fondations (Vague 1) — 11 repos P0/P1 SOT
*Statut : ✅ Complétée*

Déploiement des Stratum Relays Vague 1 (identité + navigation + règles) dans les 10 repos pilotes + VERSUS.

| Repo | Strate | Vague |
|------|--------|-------|
| GOVERNANCE-HUB | L0 | 1 |
| LLM-REPO | L1b | 1 |
| ECOYSTEM | L1 | 1 |
| BRAIN | L2 | 1 |
| ECOS-CLI | L3 | 1 |
| KIVA | L4 | 1 |
| BOINC-LLM-P2P | L5 | 1 |
| MIMIR | L6 | 1 |
| COMET | L7 | 1 |
| VERSUS | L8 | 1 |

### Phase 2 — Consolidation (Vague 2 partielle) — roots SOT
*Statut : ✅ Complétée*

Passage des 10 repos pilotes de Vague 1 à Vague 2 (5Q + règles). Mise en place du `relay_propagator.py` v2.0.

### Phase 3 — Expansion (IRIS/KRONOS/ARGUS Vague 3)
*Statut : ✅ Complétée (Session G)*

Déploiement Vague 3 (10Q + dépendances) pour les 3 repos de la Triade Cognitive +.correlateur.

| Repo | Strate | Spécificité |
|------|--------|-------------|
| IRIS | L3 | Canal opensrc + triade cognitive |
| KRONOS | L3 | Pipeline source diff |
| ARGUS | L1 | Scan proprioceptif ecos source fetch |

### Phase 4 — Alignement SOT (Vague 3) — 11 repos P0/P1
*Statut : ✅ Complétée (Session H)*

Les 11 repos P0/P1 SOT passent de `vague_courante: 2` à `vague_courante: 3` (leurs fichiers étaient déjà en V3, le manifest était en retard).

| Repo | Strate |
|------|--------|
| GOVERNANCE-HUB | L0 |
| LLM-REPO | L1b |
| ECOYSTEM | L1 |
| NEXUS | L1 |
| BRAIN | L2 |
| FLUENCE | L2 |
| ECOS-CLI | L3 |
| KIVA | L4 |
| MIMIR | L6 |
| COMET | L7 |
| VERSUS | L8 |

### Phase 5 — Batch Vague 2 — 40 repos L1-L8
*Statut : ✅ Complétée (Sessions I-K)*

Déploiement/montée en Vague 2 pour tous les repos L1-L8 restants, par batch :

| Session | Repos | Count |
|---------|-------|-------|
| I | L3 moteur (DevTools, FORGE, KIVA-CLI, etc.) | 10 |
| J | L4/L5/L2 infra+IA (GATEWAY-MANAGER, PULSE, ATLAS, VDB, TINA, etc.) | 14 |
| K | L6/L7/L8/L1 mémoire+vie réelle (SKILLS, MIMIR, GeriCode, CANDIDATOR, etc.) | 16 |

Total Phase 5 : 40 repos passés en Vague 2 (5Q + règles).

### Phase 6 — Enrichissement SOT (Vague 4) — 14 repos critiques
*Statut : ✅ Complétée*

Passage des 14 repos SOT de Vague 3 à Vague 4. Chaque relay enrichi avec :
- **Agents locaux** : section `.roomodes` par strate (agent, role, rules, hub_ref)
- **Auto-conformité** : 3 guards par repo (validation, cohérence, anti-patterns)
- **Patch auto** : ARGUS seulement (fix GAP/ORPHAN dry-run + apply)

| Repo | Strate | Agents locaux | Guards |
|------|--------|--------------|--------|
| GOVERNANCE-HUB | L0 | governance constitution_registry | validate-repos, ADR IntentHash, AGENT_RAM |
| LLM-REPO | L1b | llm-substrate cognitive_substrate | boot_sequence, SKILLS index, AGENTS.md |
| ECOYSTEM | L1 | ecosystem-sot blo_orchestrator | known_repos, PLAN validation, bloom.db |
| NEXUS | L1 | nexus-sot cross_repo_governance | intent_hash, donnees primaires, audit log |
| BRAIN | L2 | brain-cognitive cognitive_hub | FLUENCE ternary, phi-CPS range, L1 validation |
| FLUENCE | L2 | fluence-ternary ternary_orchestrator | score validation, LOGIC validation, ECOS-CLI delegation |
| ARGUS | L1 | argus-correlator automated_governance | WAL, DRIFT_REPORT, COLLISION + patch auto |
| IRIS | L3 | iris-sensor external_sensor | no qualified signals, cache purge, polling interval |
| KRONOS | L3 | kronos-digestor signal_qualifier | D4, score confiance, fiche template |
| ECOS-CLI | L3 | ecos-cli multi_repo_orchestrator | no governance md, test required, bloom.db |
| KIVA | L4 | kiva-runtime lxc_orchestrator | no direct deploy, ATLAS/KIVA, WAL persist |
| MIMIR | L6 | mimir-wiki visual_sot | article autonomy, diagram versioning |
| COMET | L7 | comet-browser browser_automation | browser only, extension sync |
| VERSUS | L8 | versus-hub cognitive_sot | cadastre YAML, manifest coherence |

### Phase 7 — Vague 3+ pour les 40 repos V2 restants
*Statut : 🔮 Planifiée*

Passage des 40 repos de Vague 2 à Vague 3 (10Q + dépendances). Cible : fin Q2 2026.

---

## User Stories

| ID | Story | Critères d'acceptation | Phase |
|----|-------|----------------------|-------|
| US-06-1 | En tant qu'agent LLM, en entrant dans n'importe quel repo actif, je lis son identité, ses règles et ses dépendances immédiatement | `STRATUM_RELAY.md` présent dans 58/76 repos | 1-5 ✅ |
| US-06-2 | En tant qu'agent LLM, je peux répondre aux 10Q de rappel cognitif de n'importe quel repo SOT | Karpathy-Recall 10Q dans les 14 SOT | 4-6 ✅ |
| US-06-3 | En tant que mainteneur, je peux propager automatiquement les Stratum Relays en batch | `relay_propagator.py` v3.0 avec `--vague 2/3/4` | 1-5 ✅ |
| US-06-4 | En tant que repo SOT, je déclare mes agents locaux et mes guards d'auto-conformité | Sections Agents locaux + Auto-conformité dans 14 SOT | 6 ✅ |
| US-06-5 | En tant qu'agent LLM, je sais que ARGUS peut patcher automatiquement les pathologies GAP/ORPHAN | Section Patch auto dans ARGUS | 6 ✅ |
| US-06-6 | En tant que mainteneur, les 40 repos V2 ont passé au niveau Vague 3 (10Q + dépendances) | `vague_courante: 3` dans 40 repos | 7 🔮 |
| US-06-7 | En tant qu'agent LLM, l'audit cross-repo détecte les incohérences automatiquement | `recall_coherence_check.py --opensrc --full` passe sans erreur | 7 🔮 |

---

## Métriques de couverture (fin Phase 6, après Phase 6 SOT)

| Niveau | Nb repos | % de 76 | Description |
|--------|---------|---------|-------------|
| Vague 4 | 14 | 18% | Agents locaux + auto-conformité (SOT uniquement) |
| Vague 2 | 40 | 53% | 5Q + règles locales |
| Vague 1 | 4 | 5% | DORMANT (vague cible = 1) |
| **Total avec relay** | **58** | **76%** | |
| L9 DEPRECATED | 12 | 16% | Exclus du périmètre |
| LOCAL ONLY | 5 | 7% | Pas de repo GitHub |
| **Total** | **76** | **100%** | |

### Fichiers de registre

| Fichier | Path | Rôle |
|---------|------|------|
| Manif vague | `urban_ontology_verse/RELAYS/relay_wave_manifest.yaml` | SOT des déploiements (v3.0.0) |
| Cadastre | `urban_ontology_verse/CADASTRE/cadastre_full.yaml` | Inventaire complet 76 repos (v3.0.0) |
| Template | `urban_ontology_verse/TEMPLATES/STRATUM_RELAY_TEMPLATE.md` | Template V1/V2/V3/V4 |
| Propagateur | `urban_ontology_verse/TOOLS/relay_propagator.py` v3.0 | Script de propagation |
| Audit | `urban_ontology_verse/TOOLS/recall_coherence_check.py` v3.0 | Vérification cross-repo |

---

## Dépendances et prérequis

- EPIC-01 (Urban Foundations) : ✅ Complété
- EPIC-03 (Stratum Relays Wave 1) : ✅ Complété
- `relay_propagator.py` v3.0 : ✅ Déployé
- `gerivdb/opensrc` fork : ✅ Créé (Session F)
- ADR-009 (opensrc integration) : ✅ Committé

---

## Risques et atténuations

| Risque | Impact | Atténuation |
|--------|--------|-------------|
| SAXON : feuilletage YAML multi-fichier | Élevé | Validation stricte dans le feuilletage de chaque parcelle/before iteration |
| Repos locaux sans GitHub | Moyen | Déclarés LOCAL_ONLY dans manifest + cadastre |
| SHA mismatch lors de push API | Moyen | Toujours récupérer le SHA avant update |
| Incohérence manifest ≠ fichiers réels | Moyen | Audit périodique via `recall_coherence_check.py` |
| Phase 7 (40 repos V3+) — charge de travail | Élevé | Script batch `relay_propagator.py --vague 3 --batch` |

---

## Évolution du manifest

| Version | Date | Changements |
|---------|------|-------------|
| 1.0.0 | 2026-05-28 | Création initiale — 55 repos, vague 1/2 |
| 1.5.0 | 2026-05-29 | Ajout TOPOS, opensrc, 73→76 repos |
| 1.6.0 | 2026-05-29 | Ajout IRIS/KRONOS/ARGUS Vague 3 |
| 1.7.0 | 2026-05-29 | Alignement 11 P0/P1 SOT → Vague 3 |
| 2.0.0 | 2026-05-29 | Phase 5 clôture — 58 relays, Phases H-K |
| 3.0.0 | 2026-05-29 | Phase 6 clôture — 14 SOT → Vague 4 |

---

*Genere par OWL (Kilo) — UrbanVerse v3.0.0*
*IntentHash: 0xEPIC06_STRATUM_RELAY_DEPLOYMENT_20260529*