# STRATUM RELAY — VERSUS (L8)

**VAGUE**: 3 | **Synchro**: 2026-05-29 | **Hub**: gerivdb/LLM-REPO

---

## Identite stratique

- **Strate** : `L8` — Vie reelle & Creatif
- **Role canonique** : Architecture Diamant — hub des verses ontologiques de l'ecosysteme gerivdb
- **Parent** : L7 (GeriCode/COMET interfaces)
- **Enfants** : L9 (archeologie — verses obsoletes archives)

## Navigation rapide

- PRD canonique : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md` (dans ce repo)
- Substrat cognitif : `gerivdb/LLM-REPO`
- UrbanVerse : `urban_ontology_verse/` (ce repo)
- Narratif : `gerivdb/BATVERSE` (repo dedie — distinct)
- Transit map : `urban_ontology_verse/TRANSIT/transit_map.yaml`
- Cadastre : `urban_ontology_verse/CADASTRE/cadastre_full.yaml`
- Propagateur : `urban_ontology_verse/TOOLS/relay_propagator.py` v3.0

## Regles locales

- R1 — VERSUS est ontologique (verses declaratifs) — BATVERSE est narratif. Ne jamais fusionner.
- R2 — UrbanVerse vit dans `VERSUS/urban_ontology_verse/` — ne jamais creer un repo dedie.
- R3 — La monnaie Geri (G) est documentee dans EPIC-05 mais bloquee jusqu'a ADR validee.
- R4 — ontology_registry.json est la source of truth des verses — toujours mettre a jour.
- Anti-pattern: creer un repo dedie UrbanVerse / fusionner VERSUS et BATVERSE.

## Karpathy-Recall etendu (Vague 3 — 10Q)

1. Quelle est la difference fondamentale entre UrbanVerse et BATVERSE ?
2. Pourquoi UrbanVerse vit dans VERSUS plutot que dans un repo dedie ?
3. Qu'est-ce qu'un Stratum Relay et quel fichier sert a les propager ?
4. Quelle regle absolue bloque l'implementation de la monnaie Geri (G) ?
5. Que represente chaque "ligne de metro" dans le transit map d'UrbanVerse ?
6. Quels repos dependent directement de L8 (VERSUS) ?
7. Quel est le role de L8 (Vie reelle & Creatif) dans l'ecosysteme ?
8. Pourquoi VERSUS et BATVERSE ne doivent-ils jamais etre fusionnes ?
9. Quelle est la difference entre VERSUS (L8) et BATVERSE (L8) ?
10. Dans quelle phase UrbanVerse ce STRATUM_RELAY a-t-il ete deploye ?

## Dependances directes

**Parents (amont)** :
- L7 : GeriCode, COMET

**Enfants (aval)** :
- L9 : ATHENA, ARES, APOLLO, HERMES, VULKAN (EXCLU — DEPRECATED)

## Vague de mise a jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| **3 (courante)** | Identite + regles + Karpathy-Recall 10Q + dependances | Deploye |
| 4 (suivante) | Agents locaux + auto-conformite | Planifie |

---

*Genere par `VERSUS/urban_ontology_verse/TOOLS/relay_propagator.py` v3.0*
*UrbanVerse v1.0.0 — gerivdb/VERSUS (L8)*
