# VERSUS-BIO

Spoke spécialisé dans les verses liés à la biologie computationnelle et biologie systémique.

## Domaines couverts
- Génomique computationnelle
- Bioinformatique structurale
- Biologie des systèmes
- Évolution quantifiée
- Bioingénierie

## Verses actifs
- `genetic-regulation.verse.yaml`
- `metabolic-networks.verse.yaml`
- `evolution-dynamics.verse.yaml`

## Intégration
```python
from versus_client import VersesSyncManager

manager = VersesSyncManager(domain="BIO")
manager.sync_selective(["genetic-regulation"])
```