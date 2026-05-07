# VERSUS-AI

Spoke spécialisé dans les verses liés à l'intelligence artificielle et machine learning.

## Domaines couverts
- Deep Learning
- Reinforcement Learning
- NLP et transformers
- Computer Vision
- IA quantique

## Verses actifs
- `transformer-architecture.verse.yaml`
- `attention-mechanism.verse.yaml`
- `diffusion-models.verse.yaml`

## Intégration
```python
from versus_client import VersesSyncManager

manager = VersesSyncManager(domain="AI")
manager.sync_selective(["transformer-architecture", "attention-mechanism"])
```