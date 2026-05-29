# STRATUM RELAY TEMPLATE — v2.0.0
# UrbanVerse | gerivdb/VERSUS
# Date: 2026-05-29

## Instructions d'utilisation

Ce template est utilise par `relay_propagator.py` v3+ pour generer les STRATUM_RELAY.md.

Parametres:
- `{REPO_NOM}` — Nom du repo GitHub
- `{STRATE}` — Strate UrbanVerse (L0, L1b, L1, L2, L2b, L3, L4, L5, L6, L7, L8, L9)
- `{ROLE_CANONIQUE}` — Description du role dans l'ecosysteme
- `{PARENT}` — Strate parente (depuis PARENT_MAP)
- `{ENFANTS}` — Strates enfants (depuis CHILD_MAP)
- `{PHI_CPS}` — Valeur phi-CPS (optionnel)
- `{LIFECYCLE}` — ACTIVE, DEPRECATED, DORMANT, PENDING_CREATION
- `{VAGUE}` — Niveau de vague (1, 2, 3)
- `{REGLES_LOCALES}` — Liste de regles (depuis STRATE_RULES)
- `{KARPATHY_RECALLS}` — Questions de rappel (depuis KARPATHY_RECALLS_V2 ou V3)
- `{DEPENDANCES}` — Section dependances (Vague 3+ uniquement)
- `{JOUR}` — Date du jour (YYYY-MM-DD)

---

```markdown
# STRATUM RELAY — {REPO_NOM} ({STRATE})

**VAGUE**: {VAGUE} | **Synchro**: {JOUR} | **Hub**: gerivdb/LLM-REPO
{{#if LIFECYCLE == "DEPRECATED" || LIFECYCLE == "DORMANT"}}
## Cycle de vie : {LIFECYCLE}

> Ce repo est en etat `{LIFECYCLE}`. Ne pas investir de ressources sans validation GOVERNANCE-HUB.
{{/if}}
---

## Identite stratique

- **Strate** : `{STRATE}` — {STRATE_LABEL}
- **Role canonique** : {ROLE_CANONIQUE}
- **Parent** : {PARENT}
- **Enfants** : {ENFANTS}
{{#if PHI_CPS}}
- **phi-CPS** : {PHI_CPS}
{{/if}}

## Navigation rapide

- 📋 PRD canonique : `GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md`
- 🧭 Substrat cognitif : `gerivdb/LLM-REPO` (L1b — prive)
- 📐 Standards repo : `REPO-STANDARDS` (RSS-v1)
- 🗺️ Transit map : `VERSUS/urban_ontology_verse/TRANSIT/transit_map.yaml`
- 📦 Cadastre : `VERSUS/urban_ontology_verse/CADASTRE/cadastre_full.yaml`

## Regles locales

{REGLES_LOCALES}

{{#if VAGUE >= 2}}
## Karpathy-Recall local (Vague {VAGUE} — {NB_QUESTIONS}Q)

> Reponds mentalement a ces questions avant d'agir dans ce repo.

{KARPATHY_RECALLS}
{{/if}}

{{#if VAGUE >= 3}}
## Dependances directes

{DEPENDANCES}
{{/if}}

## Vague de mise a jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| **{VAGUE} (courante)** | {VAGUE_LABEL} | ✅ Deploye |
| {VAGUE_SUIVANTE} (suivante) | {SUIVANT_LABEL} | ⏳ Planifie |

---

*Genere par `VERSUS/urban_ontology_verse/TOOLS/relay_propagator.py` v3.0*
*UrbanVerse v1.0.0 — gerivdb/VERSUS (L8)*
```

## Legende des vagues

| Vague | Contenu | Sections obligatoires |
|-------|---------|----------------------|
| **Vague 1** | Identite + navigation | Identite, Navigation, Regles, Vague |
| **Vague 2** | + Karpathy-Recall 5Q | + Karpathy-Recall (5 questions) |
| **Vague 3** | + Karpathy-Recall 10Q + dependances | + Karpathy-Recall (10 questions) + Dependances directes |
