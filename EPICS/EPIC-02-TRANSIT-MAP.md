# EPIC-02 — Réseau de Transit Cognitif

---

**EPIC** : EPIC-02  
**Titre** : Transit Map — Lignes Métro, RER, Tram, Bus, Noctilien  
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`  
**Version** : 1.0.0  
**Date** : 2026-05-28  
**Statut** : 🟡 À DÉMARRER  
**Priorité** : P1 — Dépend de EPIC-01  
**Dépendances** : EPIC-01 terminé

---

## Objectif

Formaliser le **réseau de transport cognitif** de l'écosystème :
documentation YAML de toutes les lignes, diagramme Mermaid du réseau,
synchronisation avec `boot_sequence.md` dans LLM-REPO.

## User Stories

| ID | Story | Critères d'acceptation |
|----|-------|----------------------|
| US-02-1 | En tant qu'agent LLM, je consulte le plan du métro pour choisir ma route d'ingestion | `transit_map.yaml` lisible et complet |
| US-02-2 | En tant que dev, je visualise le réseau en diagramme | `transit_map.mermaid.md` généré |
| US-02-3 | En tant qu'agent LLM, je prends le Noctilien en session light | Ligne N1 documentée et référencée dans boot_sequence |
| US-02-4 | En tant que mainteneur, je peux ajouter une ligne de tram pour un nouveau groupe de repos | Template `tram_line_template.yaml` disponible |

## Tâches techniques

- [ ] Créer `urban_ontology_verse/TRANSIT/transit_map.yaml` (contenu §4 du PRD)
- [ ] Créer `urban_ontology_verse/TRANSIT/transit_map.mermaid.md` (diagramme visuel)
- [ ] Créer `urban_ontology_verse/TRANSIT/tram_lines.yaml` (manifeste vagues tram)
- [ ] Créer `urban_ontology_verse/TRANSIT/tram_line_template.yaml`
- [ ] Créer `urban_ontology_verse/TRANSIT/bus_routes.yaml` (groupes de repos + règle livrée)
- [ ] Notifier LLM-REPO : ajouter référence `transit_map.yaml` dans `boot_sequence.md`

## Diagramme Mermaid cible

```mermaid
graph LR
  L0[🏛️ L0 GOVERNANCE-HUB] -->|M1| L1b[🧭 L1b LLM-REPO]
  L1b -->|M1| L1[🌍 L1 ECOYSTEM/NEXUS]
  L1 -->|M1| L2[🧠 L2 BRAIN/FLUENCE]
  L2 -->|M1| L2b[👁️ L2b IRIS/KRONOS/FLUX]
  L2b -->|M1| L3[🎮 L3 ECOS-CLI]
  L3 -->|M1| L4[🏗️ L4 KIVA/ATLAS]
  L4 -->|M1| L5[🤖 L5 BOINC-LLM]
  L5 -->|M1| L6[📚 L6 MIMIR/BRAIN-DOCS]
  L6 -->|M1| L7[💻 L7 GeriCode/COMET]
  L7 -->|M1| L8[🎨 L8 VERSUS/BATVERSE]

  L0 -->|RER-A| L3
  L0 -->|RER-A| L6
  L0 -->|RER-A| L9[🦕 L9 Archéologie]

  L0 -->|RER-B| L2
  L0 -->|RER-B| L5
  L0 -->|RER-B| L8
```

## Définition de "Done"

- [ ] `transit_map.yaml` complet et validé
- [ ] Diagramme Mermaid rendu sans erreur
- [ ] `boot_sequence.md` (LLM-REPO) référence `transit_map.yaml`
- [ ] PR soumise avec review par l'humain
