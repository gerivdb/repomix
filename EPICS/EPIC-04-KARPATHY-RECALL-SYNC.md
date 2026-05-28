# EPIC-04 — Synchronisation Karpathy Recall × UrbanVerse

---

**EPIC** : EPIC-04  
**Titre** : Karpathy Recall — Spirale d'apprentissage × Transit cognitif  
**PRD parent** : `PRD/PRD_URBAN_ONTOLOGY_VERSE_V1.md`  
**Version** : 1.0.0  
**Date** : 2026-05-28  
**Statut** : 🔵 PLANIFIÉ  
**Priorité** : P2 — Dépend de EPIC-02 et EPIC-03  
**Dépendances** : EPIC-02, EPIC-03 terminés ; LLM-REPO/TRAINING/ créé

---

## Objectif

Synchroniser la **logique Karpathy-Recall** (LLM-REPO/TRAINING/) avec la **métaphore urbaine** (UrbanVerse).
Chaque ligne de métro devient une spirale d'apprentissage ; chaque station = un recall pack.

## User Stories

| ID | Story | Critères d'acceptation |
|----|-------|----------------------|
| US-04-1 | En tant qu'agent LLM, après avoir ingéré L0, je réponds à un recall avant de passer à L1b | `L0_recall_pack.md` intégré dans `transit_map.yaml` comme "test de station" |
| US-04-2 | En tant que dev, la mise à jour d'un recall pack déclenche la mise à jour du relais correspondant | Procédure documentée dans `SYNC/recall_relay_sync.md` |
| US-04-3 | En tant qu'agent LLM, je suis la Ligne M1 avec un recall à chaque station | `transit_map.yaml` référence le recall pack de chaque strate |
| US-04-4 | En tant que mainteneur, je peux vérifier la cohérence recall ↔ relais | Script `recall_coherence_check.py` opérationnel |

## Tâches techniques

- [ ] Enrichir `transit_map.yaml` : ajouter champ `recall_pack` à chaque arrêt Ligne M1
- [ ] Créer `urban_ontology_verse/SYNC/recall_relay_sync.md` (procédure de synchronisation)
- [ ] Créer `urban_ontology_verse/TOOLS/recall_coherence_check.py`
- [ ] Mettre à jour les relais Vague 2 (5 repos critiques) avec micro-rappels Karpathy
- [ ] Lien bidirectionnel : LLM-REPO/TRAINING/README.md référence `transit_map.yaml`

## Définition de "Done"

- [ ] `transit_map.yaml` inclut `recall_pack` pour chaque strate de M1
- [ ] Script de cohérence passe sans erreur sur les 10 repos pilotes
- [ ] LLM-REPO/TRAINING/ et UrbanVerse sont en référence croisée validée
