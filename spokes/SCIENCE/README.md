# VERSUS-SCIENCE

Spoke spécialisé dans les verses liés aux sciences fondamentales et appliquées.

## Domaines couverts
- Chimie quantique
- Biologie structurale
- Neurosciences computationnelles
- Écologie théorique
- Médecine translationnelle

## Verses actifs
- `molecular-dynamics.verse.yaml`
- `protein-folding.verse.yaml`
- `neural-networks-biological.verse.yaml`

## Intégration
```python
from versus_client import VersesSyncManager

manager = VersesSyncManager(domain="SCIENCE")
manager.sync_selective(["protein-folding"])
```