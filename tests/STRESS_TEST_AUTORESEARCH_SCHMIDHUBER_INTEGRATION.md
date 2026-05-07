# STRESS-TEST: AUTORESEARCH INTEGRATION DANS SCHMIDHUBER-VERSE
# Validation end-to-end de l'intégration autoresearch dans un verse existant

## Contexte du Test
**Objectif** : Valider que `autoresearch_loop` s'intègre correctement dans le Schmidhuber-verse sans casser l'existant et apporte de la valeur opérationnelle.

**Scope** :
- Verse : `schmidhuber-2003-godel-machines` (auto-amélioration, meta-learning)
- Integration : `autoresearch_loop` comme primitive complémentaire
- Contraintes : Compatible Z600/E5620, métriques mécaniques uniquement

## Query de Test
```
Query NEXUS: "Propose une boucle d'auto-amélioration contrainte matériellement pour un codebase lié au meta-learning selon Schmidhuber."

Context additionnel:
- Matériel: Xeon E5620 (8 cores, 32GB RAM, 2010)
- Budget: max 30min par itération, 1-2 jobs parallèles max
- Métriques: uniquement mécaniques (performance, accuracy, temps)
- Repo: codebase meta-learning existant
```

## Attendus d'Output

### 1. Sélection Primitive Correcte
**Expected** : `autoresearch_loop` sélectionnée comme primitive pertinente
```
Primitives candidates:
- get_concept_sources (Schmidhuber)
- autoresearch_loop (complementary)
- mechanical_metric_verification (constraint)
```

### 2. Mapping NEXUS Cohérent
**Expected** : Intégration propre avec concepts existants
```
Mappings activés:
├── LearningCurve (amélioration continue)
├── EnergyFunction (métriques mécaniques)
├── IntentionManager (choix objectifs/budgets)
└── autoresearch_loop (exécution concrète)
```

### 3. Output Fonctionnel Compatible Matériel
**Expected** : Configuration réaliste pour Z600/E5620
```python
# Output attendu
autoresearch_config = {
    "primitive": "autoresearch_loop",
    "repo_path": "/path/to/meta_learning_codebase",
    "metric_command": "python train_meta.py | grep 'meta_loss' | awk '{print $2}'",
    "budget": {
        "type": "time",
        "max_budget": 1800,  # 30min compatible Z600
        "checkpoint_interval": 60
    },
    "constraints": {
        "max_file_size": 1000000,
        "allowed_extensions": [".py"],
        "max_parallel_jobs": 1,  # Sécurité Z600
        "environment_vars": {
            "CUDA_VISIBLE_DEVICES": "",  # CPU only
            "OMP_NUM_THREADS": "4"
        }
    }
}
```

### 4. Traçabilité Verse → Engine Complète
**Expected** : Chaîne complète depuis source académique
```
Traçabilité:
├── Source: schmidhuber-2003-godel-machines.yaml
├── Verse: VERSE_SCHMIDHUBER_GODEL_MACHINES.md
├── Digestion: nutriments + autoresearch_loop
├── Engines: BRAIN + DATA_MINER + AutoresearchOptimizationEngine
└── Primitives: get_concept_sources + autoresearch_loop
```

## Critères de Succès

### ✅ SUCCESS Criteria (All Must Pass)

1. **Primitive Selection** : `autoresearch_loop` proposée comme complément Schmidhuber
2. **No Conflicts** : Pas de conflits avec mappings existants LearningCurve/EnergyFunction
3. **Hardware Compatibility** : Configuration respecte contraintes Z600 (1 job, 30min/itération)
4. **Mechanical Metrics** : Métriques proposées sont purement mécaniques (mesurables)
5. **Citation Awareness** : Réponse cite Schmidhuber + autoresearch sources
6. **Traceability** : Liens vers verse + nutriments + engines opérationnels

### ❌ FAILURE Criteria (Any = FAIL)

1. **Integration Broken** : autoresearch casse mappings Schmidhuber existants
2. **Hardware Ignored** : Configuration ignore contraintes Z600/E5620
3. **Subjective Metrics** : Métriques non-mécaniques proposées
4. **No Citations** : Réponse sans traçabilité académique
5. **Timeout** : Réponse >30s (pipeline trop lent)

## Hooks NEXUS à Observer

### 1. BRAIN Response Generation
**Hook** : `brain_functions/self_improvement.py` + `autoresearch-karpathy-codex_engine.py`
**Observe** :
- Sélection concepts : `self-improvement` + `autoresearch_loop`
- Cohérence réponse : Schmidhuber + Karpathy
- Performance : <5s génération

### 2. Primitive Resolution
**Hook** : `ontology/primitives/autoresearch_loop.yaml`
**Observe** :
- Interface respectée : inputs/outputs conformes
- Contraintes appliquées : Z600/E5620 intégrées
- Validation : schema YAML valide

### 3. Ontology Service
**Hook** : Service ontologique live
**Observe** :
- Résolution concepts : `LearningCurve` + `EnergyFunction`
- Cross-references : mappings cohérents
- Performance : <1s résolution

### 4. Digestion Pipeline
**Hook** : `academic-digestion-engine-simple.py`
**Observe** :
- Nutriments générés : autoresearch + schmidhuber
- Engines déployés : compatibilité vérifiée
- Métriques : succès déploiement

## Métriques de Validation

| Métrique | Seuil Succès | Observation |
|----------|-------------|-------------|
| **Response Time** | <30s | Temps génération réponse complète |
| **Citation Accuracy** | 100% | Toutes sources correctement citées |
| **Hardware Compliance** | 100% | Configuration respecte contraintes |
| **Integration Errors** | 0 | Pas d'erreurs mapping/croisement |
| **Traceability Links** | 100% | Tous liens verse→engine valides |

## Commandes d'Exécution

### 1. Préparation
```bash
# S'assurer sources présentes
ls sources/schmidhuber-2003-godel-machines.yaml
ls sources/autoresearch-karpathy-codex.yaml

# Vérifier métriques industrialisation
python academic-ingestion-metrics.py
```

### 2. Exécution Test
```bash
# Query via BRAIN (à adapter selon interface)
python brain_query.py --query "Propose une boucle d'auto-amélioration contrainte matériellement pour un codebase lié au meta-learning selon Schmidhuber."
```

### 3. Validation Post-Test
```bash
# Vérifier génération engines
ls engines/brain_functions/ | grep -E "(schmidhuber|autoresearch)"

# Vérifier déploiement
python nutrient-deployment-pipeline.py --test

# Vérifier métriques
python academic-ingestion-metrics.py
```

## Résultats Attendus

### ✅ SUCCESS Scenario
```
[RESULT] Query processed in 8.3s
[PRIMITIVES] Selected: get_concept_sources, autoresearch_loop
[MAPPINGS] LearningCurve ✓, EnergyFunction ✓, IntentionManager ✓
[HARDWARE] Z600 compliant: 1 job, 30min budget ✓
[CITATIONS] Schmidhuber + Karpathy cited ✓
[TRACEABILITY] Full chain verse→engine ✓
[GLOBAL SCORE] 98.5/100 ✓
```

### ❌ FAILURE Scenario
```
[ERROR] Integration conflict: autoresearch_loop conflicts with LearningCurve
[HARDWARE] Non-compliant: 4 parallel jobs requested
[CITATIONS] Missing autoresearch references
[TIMEOUT] Query took 45.2s > 30s threshold
```

## Actions Correctives si Échec

### High Priority
1. **Conflict Resolution** : Ajuster mappings autoresearch/Schmidhuber
2. **Hardware Constraints** : Forcer respect contraintes dans primitive
3. **Performance** : Optimiser pipeline digestion (<5s target)

### Medium Priority  
4. **Citation Engine** : Améliorer sélection sources pertinentes
5. **Traceability** : Renforcer liens verse→nutriment→engine

### Low Priority
6. **UI/UX** : Améliorer présentation réponse
7. **Monitoring** : Ajouter métriques autoresearch spécifiques

---

## Sign-off
| Critère | Status | Notes |
|---------|--------|-------|
| **Query Defined** | ✅ | Citation-aware + hardware constraints |
| **Success Criteria** | ✅ | 6 critères binaires + métriques |
| **Hooks Identified** | ✅ | 4 hooks NEXUS critiques |
| **Commands Ready** | ✅ | Scripts d'exécution préparés |
| **Failure Handling** | ✅ | Actions correctives hiérarchisées |

**Test prêt à exécution** 🚀