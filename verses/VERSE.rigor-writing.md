# VERSE.rigor-writing

**IntentHash:** `0xVERSE_RIGOR_WRITING_ECOS_20260423`  
**Status:** ACTIVE | **Priority:** HIGH  
**Domain:** Documentation Ethics | **Scope:** All Technical Writing  

## Core Principle

**"Écrire pour être lu, pas pour impressionner. Un fait = une preuve."**

## Writing Rules

### Style Fundamentals
- **Active Voice** : "Le système détecte 2 GPUs" vs "2 GPUs sont détectés"
- **Specific Terms** : "500ms latence" vs "très rapide"
- **Short Sentences** : Maximum 25 mots par phrase
- **One Idea per Paragraph** : Chaque paragraphe = un concept unique

### Quantification Mandatory
- **Replace Vague Terms** :
  - "énorme" → "83% d'augmentation"
  - "rapide" → "2.3 secondes"
  - "stable" → "99.7% uptime sur 30 jours"
  - "presque toujours" → "94% des cas"

### Proof Requirements
- **Technical Claim** = **Source Required**
  - Log excerpt, benchmark result, official doc, code reference
- **Performance Number** = **Baseline + Context**
  - "15% faster than Chrome vanilla on Quadro 4000"

### Forbidden Patterns
- ❌ "Révolutionnaire breakthrough"
- ❌ "Zéro latence garantie"
- ❌ "Parfaitement stable"
- ❌ "Définitivement résolu"
- ❌ "Infiniment scalable"

### Acceptable Alternatives
- ✅ "Breakthrough validé sur Quadro 4000"
- ✅ "Latence < 50ms mesurée"
- ✅ "Stable dans 95% des tests"
- ✅ "Résolu pour cas testés"
- ✅ "Scalable à 1000 utilisateurs"

## Examples

### ✅ CORRECT (Rigorous)
```
La fonction détecte automatiquement 2 GPUs en < 50ms.
Preuve : Log "Detected 2 GPUs" timestamp 20:54:31.
Baseline : Configuration manuelle prenait 200ms.
```

### ❌ INCORRECT (Marketing)
```
Notre système révolutionnaire détecte instantanément tous les GPUs avec une précision parfaite.
```

## Implementation

### For Writers
1. **Read Aloud** : Si ça sonne marketing, réécrire
2. **Count Vague Words** : Objectif zéro
3. **Add Sources** : Une référence par affirmation technique
4. **Quantify Everything** : Chiffres + contexte + preuve

### For Reviewers
1. **Challenge Absolutes** : "Toujours" doit être prouvé
2. **Demand Baselines** : Tout gain doit comparer à quelque chose
3. **Verify Sources** : Liens fonctionnels, logs existants
4. **Flag Hyperbole** : Supprimer ou corriger

## Consequences

**Documents rigor-writing compliant :**
- Plus crédibles auprès des utilisateurs
- Plus faciles à maintenir et déboguer
- Résistent mieux aux contestations

**Documents non-compliant :**
- Rewritten required
- Cannot be used in prod-ready contexts
- User trust erosion risk

## Evolution

This VERSE evolves with each documentation incident. Every vague claim caught becomes a new forbidden pattern.