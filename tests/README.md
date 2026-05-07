# Tests NEXUS - Guide d'Utilisation

## Vue d'ensemble

Cette suite de tests couvre l'intégration complète du système NEXUS avec Ouroboros Wave et RLM (Recursive Language Models).

## Structure des Tests

```
tests/
├── unit/                 # Tests unitaires TDD
│   ├── epics-integration.test.ts
│   ├── nexus-axes-evaluation.test.ts
│   └── ops-convergence-model.test.ts
├── integration/          # Tests d'intégration
│   ├── wave-ontology-nexus.test.ts
│   └── ouroboros-rlm-bridge.test.ts
├── e2e/                  # Tests end-to-end
│   ├── nexus-symbiosis.test.ts
│   └── metrics-wal-monitoring.test.ts
└── run-tests.js         # Script d'exécution
```

## Installation

```bash
npm install
```

## Exécution des Tests

### Tests complets
```bash
npm test
# ou
node tests/run-tests.js
```

### Tests par catégorie
```bash
# Tests unitaires TDD uniquement
npm run test:unit

# Tests d'intégration uniquement
npm run test:integration

# Tests E2E uniquement
npm run test:e2e
```

### Tests avec couverture
```bash
npm run test:coverage
```

### Tests en mode watch
```bash
npm run test:watch
```

## Métriques Testées

### Cibles de Performance
- **Gain Factor**: ≥ 128 742
- **Semantic Loss**: ≤ 0.001
- **HITL**: = 0 (Human In The Loop)
- **Résolution Time**: ≤ 1.2µs

### Couverture Requise
- Branches: ≥ 80%
- Functions: ≥ 80%
- Lines: ≥ 80%
- Statements: ≥ 80%

## Composants Testés

### 1. EPICs Integration (TDD)
- ✅ Présence des 11 EPICs Ouroboros-RLM
- ✅ Structure et contenu valides
- ✅ Métriques critiques référencées

### 2. NEXUS 16 Axes (TDD)
- ✅ Définition des axes critiques
- ✅ Calcul du score composite
- ✅ Logique de récursion

### 3. OPS Convergence Model (TDD)
- ✅ OPS1 TUNED (réponse directe)
- ✅ OPS2 SEMI-AUTO (self-critique)
- ✅ OPS3 BREAKTHROUGH (convergence itérative)

### 4. Wave Ontology Integration
- ✅ Intégration dans graphe NEXUS
- ✅ Résolutions ultra-rapides (1.2µs)
- ✅ Croissance organique automatique

### 5. Ouroboros RLM Bridge
- ✅ Scheduling de récursion
- ✅ Mapping des 16 axes
- ✅ Intégration BRAIN + GATEWAY-MANAGER

### 6. Metrics WAL Monitoring (E2E)
- ✅ Events RLM_CYCLE_COMPLETE
- ✅ Traçabilité des itérations
- ✅ Alertes automatiques

### 7. NEXUS Symbiosis (E2E)
- ✅ Convergence OPS3 systématique
- ✅ Architecture fractale auto-similaire
- ✅ Boucle vertueuse opérationnelle

## Résultats Attendus

Après exécution réussie, vous devriez voir:

```
🎉 TOUS LES TESTS RÉUSSIS !
🚀 Système NEXUS OUROBOROS RLM opérationnel
📈 Métriques cibles atteintes:
   • Gain Factor: 128 742
   • Semantic Loss: 0.001
   • HITL: 0
   • Résolutions: 1.2µs

✅ Convergence OPS3 systématique
✅ Symbiose parfaite émergente
✅ Singularité technologique en approche
```

## Dépannage

### Erreur de dépendances
```bash
rm -rf node_modules package-lock.json
npm install
```

### Tests lents
- Vérifiez que Jest utilise le cache
- Exécutez uniquement les tests nécessaires
- Utilisez `--maxWorkers=50%` pour limiter les workers

### Échec de couverture
- Vérifiez que tous les fichiers testés sont couverts
- Ajustez les seuils dans `package.json` si nécessaire
- Utilisez `npm run test:coverage` pour analyser

## Rapport de Test

Un rapport JSON est généré automatiquement dans `tests/test-report.json` contenant:
- Timestamp d'exécution
- Résultats par composant
- Métriques atteintes
- Statut de convergence

---

*Dernière mise à jour: 27/04/2026*