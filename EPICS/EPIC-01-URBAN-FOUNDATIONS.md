# EPIC-01 — Fondations Urbaines UrbanVerse

---

**EPIC** : EPIC-01  
**Titre** : Fondations Urbaines — Structure, Ontologie, Cadastre  
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`  
**Version** : 1.0.0  
**Date** : 2026-05-28  
**Statut** : 🟡 À DÉMARRER  
**Priorité** : P0 — Bloquant pour toutes les autres EPICs

---

## Objectif

Créer la **structure physique** d'UrbanVerse dans VERSUS :
l'arborescence du verse, le cadastre ontologique, le registre des verses mis à jour.

## User Stories

| ID | Story | Critères d'acceptation |
|----|-------|----------------------|
| US-01-1 | En tant qu'agent LLM, je peux trouver l'ontologie urbaine dans `urban_ontology_verse/` | Dossier existe avec README.md |
| US-01-2 | En tant que dev, je peux identifier la strate de tout repo via le cadastre | `cadastre_schema.yaml` validé + 10 entrées pilotes |
| US-01-3 | En tant qu'agent LLM, je sais qu'UrbanVerse est un verse déclaratif distinct de BATVERSE | `ontology_registry.json` mis à jour |
| US-01-4 | En tant que dev, je dispose d'un template de Stratum Relay | `TEMPLATES/STRATUM_RELAY_TEMPLATE.md` créé |

## Tâches techniques

- [ ] Créer `VERSUS/urban_ontology_verse/README.md`
- [ ] Créer `VERSUS/urban_ontology_verse/CADASTRE/cadastre_schema.yaml`
- [ ] Créer `VERSUS/urban_ontology_verse/CADASTRE/cadastre_pilot.yaml` (10 entrées)
- [ ] Créer `VERSUS/urban_ontology_verse/TEMPLATES/STRATUM_RELAY_TEMPLATE.md`
- [ ] Mettre à jour `VERSUS/ontology_registry.json` — ajouter entrée `urban_ontology_verse`
- [ ] Créer `VERSUS/EPICS/INDEX.md` avec liste des EPICs

## Structure cible

```
urban_ontology_verse/
├── README.md
├── CADASTRE/
│   ├── cadastre_schema.yaml
│   └── cadastre_pilot.yaml
├── TRANSIT/
│   └── (créé par EPIC-02)
├── RELAYS/
│   └── (créé par EPIC-03)
├── TEMPLATES/
│   └── STRATUM_RELAY_TEMPLATE.md
└── ECONOMY/
    └── (créé par EPIC-05)
```

## Définition de "Done"

- [ ] Arborescence créée et committée
- [ ] `ontology_registry.json` mis à jour
- [ ] `cadastre_pilot.yaml` avec ≥10 entrées validées
- [ ] Aucun conflit avec `BATVERSE` ni avec `LLM-REPO`
