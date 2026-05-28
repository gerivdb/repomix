# EPIC-03 — Stratum Relays — Déploiement Vague 1 (10 repos pilotes)

---

**EPIC** : EPIC-03  
**Titre** : Stratum Relays — Infrastructure de Maillage Cognitif Distribué  
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`  
**Version** : 1.0.0  
**Date** : 2026-05-28  
**Statut** : 🟡 À DÉMARRER  
**Priorité** : P1 — Dépend de EPIC-01  
**Dépendances** : EPIC-01 terminé ; LLM-REPO accessible

---

## Objectif

Déployer les **Stratum Relays** (stations de métro cognitives) dans les 10 repos pilotes.
Créer le script de propagation automatique pour les vagues suivantes.

## Repos pilotes sélectionnés

| Repo | Strate | Raison de sélection |
|------|--------|---------------------|
| GOVERNANCE-HUB | L0 | Nœud racine, doit se décrire lui-même |
| LLM-REPO | L1b | Hub cognitif central |
| ECOYSTEM | L1 | SOT opérationnel |
| BRAIN | L2 | Hub cognitif racine |
| ECOS-CLI | L3 | Point d'action CLI principal |
| KIVA | L4 | Infrastructure physique |
| BOINC-LLM-P2P | L5 | IA distribuée |
| MIMIR | L6 | Mémoire longue |
| COMET | L7 | Interface utilisateur |
| VERSUS | L8 | Verse hub (ce repo lui-même) |

## User Stories

| ID | Story | Critères d'acceptation |
|----|-------|----------------------|
| US-03-1 | En tant qu'agent LLM, en entrant dans BRAIN, je lis son identité stratique immédiatement | `BRAIN/STRATUM_RELAY.md` Vague 1 présent |
| US-03-2 | En tant que dev, je génère un nouveau relais en 30 secondes | Script `relay_propagator.py` opérationnel |
| US-03-3 | En tant qu'agent LLM, je reçois un micro-rappel Karpathy en Vague 2 | Relais Vague 2 sur 5 repos critiques |
| US-03-4 | En tant que mainteneur, je suis l'état de vague de chaque repo | `relay_wave_manifest.yaml` à jour |

## Tâches techniques

- [ ] Créer `urban_ontology_verse/RELAYS/relay_wave_manifest.yaml`
- [ ] Créer `urban_ontology_verse/TOOLS/relay_propagator.py`
- [ ] Générer `STRATUM_RELAY.md` Vague 1 pour les 10 repos pilotes
- [ ] Commettre chaque relais dans son repo respectif
- [ ] Mettre à jour `relay_wave_manifest.yaml` après chaque commit

## Format relay_wave_manifest.yaml

```yaml
# relay_wave_manifest.yaml — État des vagues par repo
version: 1.0.0
last_updated: 2026-05-28
repos:
  GOVERNANCE-HUB:
    strate: L0
    vague_courante: 0
    vague_cible: 1
    statut: "⏳ À déployer"
  LLM-REPO:
    strate: L1b
    vague_courante: 0
    vague_cible: 1
    statut: "⏳ À déployer"
  # ... (10 entrées pilotes)
```

## Définition de "Done"

- [ ] 10 `STRATUM_RELAY.md` committés dans leurs repos
- [ ] `relay_propagator.py` testé sur au moins 2 repos
- [ ] `relay_wave_manifest.yaml` reflète l'état réel
- [ ] Aucun relais ne contredit les règles de `LLM-REPO/RULES/`
