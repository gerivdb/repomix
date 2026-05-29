import sys
from pathlib import Path

# Ajouter le dossier VERSUS au sys.path pour que political_compass_verse soit importable comme package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
