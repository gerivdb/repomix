"""
political_compass_verse — Couche causale L5 de l'écosystème Diamond.

Encode les orientations politiques en coordonnées ternaires (S, M, E, I)
et les projette sur UrbanVerse (causalité), socioverse (effets sociaux)
et BatVerse (scénarisation narrative).

Position Diamond de référence : (S=2, M=0, E=2, I=1)
"""

__version__ = "1.0.0"
__strate__ = "L5"
__repo__ = "gerivdb/VERSUS"

from .political_compass_verse import PoliticalCompassVerse
from .trit_encoder import TritPoliticalEncode, TritQuadruplet
from .trit_distance import TritPoliticalDistance
from .trit_projector import TritPoliticalProject, TritPoliticalMerge
from .trit_renderer import TritPoliticalRender
from .bridges.bridge_to_batverse import TritPoliticalNarrate
from .bridges.bridge_to_urban import TritPoliticalCause
from .bridges.bridge_to_socio import TritPoliticalSocioBridge

__all__ = [
    "PoliticalCompassVerse",
    "TritPoliticalEncode",
    "TritQuadruplet",
    "TritPoliticalDistance",
    "TritPoliticalProject",
    "TritPoliticalMerge",
    "TritPoliticalRender",
    "TritPoliticalNarrate",
    "TritPoliticalCause",
    "TritPoliticalSocioBridge",
]
