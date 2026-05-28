# UrbanVerse — Holographie Ontologique Métropole

> **Verse** : `urban_ontology_verse`  
> **Strate** : L8 — Vie réelle & Créatif  
> **Type** : Ontologie opérationnelle (distinct de BATVERSE, narratif)  
> **PRD** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`

---

## Qu'est-ce qu'UrbanVerse ?

UrbanVerse modélise l'écosystème gerivdb (~170 repos) comme une **métropole vivante de type Paris / Île-de-France**.

Ce n'est pas une métaphore narrative — c'est une **grille de lecture opérationnelle** :

- Chaque **repo** = un **immeuble** (parcelle urbaine)
- Chaque **strate** = un **arrondissement**
- Chaque **`STRATUM_RELAY.md`** = une **adresse postale** (identité stratique)
- Le **réseau de transit** = les **lignes RATP** (M1, RER, Tram, Bus, Noctilien)
- Les **Stratum Relays** = les **stations de métro** (infrastructure de gouvernance distribuée)

## Structure

```
urban_ontology_verse/
├── README.md                    # Ce fichier
├── CADASTRE/                    # Ontologie des parcelles (repos)
│   ├── cadastre_schema.yaml     # Schema YAML d'une parcelle
│   └── cadastre_pilot.yaml      # 10 entrées pilotes
├── TRANSIT/                     # Réseau de transport cognitif
│   ├── transit_map.yaml         # Plan de ligne YAML (M1, RER, Tram, Bus)
│   ├── transit_map.mermaid.md   # Diagramme Mermaid du réseau
│   ├── tram_lines.yaml          # Manifeste vagues tram
│   ├── tram_line_template.yaml  # Template ligne tram
│   └── bus_routes.yaml          # Groupes de repos + règles livrées
├── RELAYS/                      # Stratum Relays
│   └── relay_wave_manifest.yaml # État des vagues par repo
├── SYNC/                        # Synchronisation Karpathy Recall
│   └── recall_relay_sync.md     # Procédure sync recall ↔ relais
├── TOOLS/                       # Outils d'automatisation
│   ├── relay_propagator.py      # Script propagation relais
│   └── recall_coherence_check.py # Vérication cohérence recall ↔ relais
├── TEMPLATES/                   # Templates
│   └── STRATUM_RELAY_TEMPLATE.md # Template relais (station de métro)
└── ECONOMY/                     # Économie urbaine & gouvernance IDF
    ├── zonage_idf.yaml          # Zones de confiance 1-4
    ├── peripherique.yaml        # Repos passerelles
    ├── actors_registry.yaml     # Acteurs urbains typés
    ├── rungis_components.yaml   # Composants réutilisables
    └── geri_currency_ADR_draft.md # Brouillon ADR monnaie Geri (NON DÉPLOYÉ)
```

## Réseau de Transit Cognitif

```
Ligne M1  (Métro) : L0 → L1b → L1 → L2 → L3 → L4 → L5 → L6 → L7 → L8 → L9
Ligne RER-A       : L0 ──────────────────────────────────────────→ L9
Ligne RER-B       : L0 → L2 → L5 → L8
Ligne T1 (Tram)   : L4a → L4b → L4c (repos infrastructure)
Ligne T2 (Tram)   : L5a → L5b (IA distribuée)
Bus 72            : Groupe repos API REST
Noctilien N1      : L0 → L1b (mode light)
```

## Quick Start — Navigation

1. Consulter le **PRD** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`
2. Consulter l'**index EPICs** : `EPICS/INDEX.md`
3. Consulter le **plan de ligne** : `TRANSIT/transit_map.yaml`
4. Vérifier l'**état des relais** : `RELAYS/relay_wave_manifest.yaml`

## Références clés

| Document | Localisation | Relation |
|----------|-------------|----------|
| `PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md` | `GOVERNANCE-HUB/PRD/` | PRD constitutionnel (L0) |
| `known_repositories.yaml` | `GOVERNANCE-HUB/` | Cadastre source of truth |
| `ontology_registry.json` | `VERSUS/` | Registre local des verses |
| `behavior_rules.md` | `LLM-REPO/RULES/` | Règles comportementales LLM |
| `boot_sequence.md` | `LLM-REPO/BOOT/` | Séquence d'ingestion |

---

*UrbanVerse — Holographie Ontologique Métropole — gerivdb/VERSUS*
*Version 1.0.0 — 2026-05-28*
