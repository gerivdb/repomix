# geri_currency_ADR_draft.md — Brouillon ADR Monnaie Geri (Ğ)
# Version: 0.1.0 (brouillon) | Date: 2026-05-29

## Statut
**BROUILLON — NE PAS DEPLOYER** sans ADR validee dans GOVERNANCE-HUB/ADR/

## Contexte
En parallele au deploiement UrbanVerse, une monnaie interne appelee **Geri (Ğ)** est documentee pour :
- Gerer les exchanges economiques internes entre repos/agents
- Etablir un systeme d'appreciation coherent dans tout l'ecosysteme

## Risques identifies
1. Dette de complexite — ajoute une couche de gestion non necessaire
2. Gouvernance — necessite une ADR formelle avant tout deploiement
3. Interoperabilite — doit s'integrer avec les regles de strate existantes

## Principes de conception (si deploye)
1. Ğ est une unite de mesure, non une monnaie reelle
2. Les exchanges sont enregistres dans un ledger dedie
3. Chaque repo/actor a un solde Ğ initial de 0
4. Les transferts sont effectues via smart contracts ou signatures

## Prochaines etapes (si valide)
1. Rediger l'ADR complete dans GOVERNANCE-HUB/ADR/
2. Obtenir la validation de gerivdb
3. Creer le repo GERI-CURRENCY-LEDGER
4. Integrer avec STRATUM_RELAY.md (section economique)

## Regle absolue
> Le systeme de credits Ğ ne peut etre implemente qu'apres validation d'une ADR dans GOVERNANCE-HUB/ADR/. Toute implementation sans ADR = anti-pattern constitutionnel (L0 violation).

*IntentHash: 0xGERI_CURRENCY_ADR_DRAFT_20260529*
