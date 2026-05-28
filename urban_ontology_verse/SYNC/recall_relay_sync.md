# recall_relay_sync.md — Procédure de synchronisation Karpathy Recall ↔ UrbanVerse
# Version: 1.0.0 | Date: 2026-05-28

## Objectif

Documenter la procédure de synchronisation bidirectionnelle entre :
- Les **packs Karpathy-Recall** (dans `LLM-REPO/TRAINING/`) — spirales d'apprentissage par strate
- Les **Stratum Relays** (dans chaque repo) — stations de métro cognitives

## Principe

> Chaque station de métro (strate) = un rappel cognitif (Karpathy-Recall).
> Quand l'agent LLM "descend à une station", il déclenche le rappel correspondant.

## Procédure de sync

### A. Recall → Relais (enrichissement)

Quand un nouveau pack Karpathy-Recall est ajouté dans `LLM-REPO/TRAINING/` :

1. Identifier la strate cible du recall pack (ex: L2)
2. Ouvrir le `STRATUM_RELAY.md` du repo pilote correspondant (ex: `BRAIN/STRATUM_RELAY.md`)
3. Enrichir la section `## 🧠 Karpathy-Recall local` avec les nouvelles questions
4. Passer la vague du relais à N+1 si le contenu le justifie
5. Mettre à jour `RELAYS/relay_wave_manifest.yaml`

### B. Relais ↔ Transit Map (cohérence)

Quand un relais est créé ou mis à jour :

1. Vérifier que le champ `recall_pack: true` existe dans `transit_map.yaml` pour la ligne/arrêt concerné
2. Si un nouveau recall pack est ajouté au relais, ajouter la référence dans `transit_map.yaml`
3. Mettre à jour le diagramme Mermaid si une nouvelle ligne ou un nouvel arrêt est créé

### C. Vérification de cohérence

```bash
# Lancer le script de cohérence
python urban_ontology_verse/TOOLS/recall_coherence_check.py
```

Le script vérifie :
- Chaque arrêt M1 avec `recall_pack: true` a un relais avec section Karpathy-Recall non vide
- Chaque relais avec contenu Karpathy-Recall a un arrêt correspondant dans le transit_map
- Aucun recall pack orphelin (dans LLM-REPO sans relais correspondant)

## Fréquence de synchronisation

| Événement | Action | Fréquence |
|-----------|--------|-----------|
| Nouveau recall pack LLM-REPO | Enrichir relais cible | À chaque ajout |
| Nouveau relais déployé | Vérifier cohérence transit_map | À chaque déploiement |
| Mise à jour boot_sequence.md | Vérifier cohérence transit_map + recalls | À chaque mise à jour |
| Audit complet | Script coherence_check | Hebdomadaire |

## Références

- `TRANSIT/transit_map.yaml` — Plan de ligne avec champ `recall_pack`
- `RELAYS/relay_wave_manifest.yaml` — État des vagues par repo
- `TEMPLATES/STRATUM_RELAY_TEMPLATE.md` — Template avec section Karpathy-Recall
- `EPICS/EPIC-04-KARPATHY-RECALL-SYNC.md` — EPIC dédié
