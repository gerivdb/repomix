# VERSUS-PHYSICS

Spoke spécialisé dans les verses liés à la physique théorique et appliquée.

## Domaines couverts
- Physique quantique
- Physique classique
- Physique des particules
- Cosmologie
- Thermodynamique

## Verses actifs
- `quantum-entanglement.verse.yaml`
- `hamiltonian-dynamics.verse.yaml`
- `cosmic-microwave-background.verse.yaml`

## Intégration
```python
from versus_client import VersesSyncManager

manager = VersesSyncManager(domain="PHYSICS")
manager.sync_selective(["quantum-entanglement", "hamiltonian-dynamics"])
```