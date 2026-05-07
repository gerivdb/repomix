# VERSUS-MATH

Spoke spécialisé dans les verses liés aux mathématiques fondamentales et appliquées.

## Domaines couverts
- Algèbre abstraite
- Analyse complexe
- Géométrie différentielle
- Théorie des nombres
- Topologie algébrique

## Verses actifs
- `tensor-calculus.verse.yaml`
- `group-theory.verse.yaml`
- `knot-theory.verse.yaml`

## Intégration
```python
from versus_client import VersesSyncManager

manager = VersesSyncManager(domain="MATH")
manager.sync_selective(["tensor-calculus", "group-theory"])
```