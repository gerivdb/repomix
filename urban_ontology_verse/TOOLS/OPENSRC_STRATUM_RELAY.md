# STRATUM RELAY — opensrc (L3)

**VAGUE**: 2 | **Synchro**: 2026-05-29 | **Hub**: gerivdb/LLM-REPO

---

## Identite stratique

- **Strate** : `L3` — Systeme moteur CLI
- **Role canonique** : Fetch et cache local du source code de n'importe quelle dependance (npm, PyPI, crates.io, GitHub). Permet aux agents LLM de lire le code source reel des dependances sans appel reseau.
- **Parent** : L2 (BRAIN — fournit les patterns de recherche)
- **Enfants** : — (utilise transversalement par IRIS, ARGUS, KRONOS)

## Navigation rapide

- PRD canonique : `GOVERNANCE-HUB/PRD/PRD_ECOSYSTEM_SUPERSTRUCTURE_L0-L9_V1.md`
- Substrat cognitif : `gerivdb/LLM-REPO`
- Cadastre : `VERSUS/urban_ontology_verse/CADASTRE/cadastre_full.yaml`
- ADR gouvernance : `GOVERNANCE-HUB/ADR/ADR-009-opensrc-integration.md`

## Regles locales

- R1 — opensrc fetch uniquement des registries publics (npm, PyPI, crates.io, GitHub public).
- R2 — Ne jamais fetcher de repos prives sans autorisation explicite.
- R3 — Le cache `~/.opensrc/` doit etre purge periodiquement via `ecos-clean-opensrc.ps1`.
- R4 — Verifier l'integrite du cache (checksum/tag Git) avant toute analyse.
- Anti-pattern: fetcher des repos prives sans chiffrement du cache.

## Karpathy-Recall local (Vague 2 — 5Q)

1. Quel est le role d'opensrc dans l'ecosysteme UrbanVerse ?
2. Comment opensrc accelere-t-il les audits cross-repo (vs appels MCP sequentiels) ?
3. Quelles sont les precautions de securite avant de fetcher un repo ?
4. Quelle est la difference entre origin (gerivdb/opensrc) et upstream (vercel-labs/opensrc) ?
5. Dans quelle phase UrbanVerse ce STRATUM_RELAY a-t-il ete deploye ?

## Vague de mise a jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| **2 (courante)** | Identite + regles + Karpathy 5Q | Deploye |
| 3 (suivante) | Integration complete IRIS/ARGUS/KRONOS + coherence_check v3.0 | Planifie |

---

*Genere par `VERSUS/urban_ontology_verse/TOOLS/relay_propagator.py` v3.0*
*UrbanVerse v1.0.0 — gerivdb/VERSUS (L8)*
