"""
trit_projector.py — TritPoliticalProject + TritPoliticalMerge

TritPoliticalProject : Réduit un quadruplet à un sous-espace d'axes choisis.
Utile pour comparer deux scénarios sur une seule dimension.

TritPoliticalMerge : Fusionne deux positions en un compromis ternaire
(moyenne arrondie au trit le plus proche). Modélise coalitions et négociations.
"""

from typing import List, Optional, Set
from .trit_encoder import TritQuadruplet, TritPoliticalEncode


# ── Axes valides ──────────────────────────────────────────────────────────
AXES = ("S", "M", "E", "I")
AXIS_INDEX = {"S": 0, "M": 1, "E": 2, "I": 3}

INDEX_TO_AXIS = {v: k for k, v in AXIS_INDEX.items()}


class TritPoliticalProject:
    """
    Réduit un quadruplet à un sous-espace d'axes choisi.

    Utilisation:
        projector = TritPoliticalProject(quadruplet)
        result = projector.project(["E", "I"])  # ne garde que Écologie et IA
    """

    def __init__(self, quadruplet: TritQuadruplet):
        self.quadruplet = quadruplet

    def project(self, axes: List[str]) -> TritQuadruplet:
        """Projette le quadruplet sur les axes spécifiés (les autres = 0)."""
        axes_set: Set[str] = set(axes)
        invalid = axes_set - set(AXES)
        if invalid:
            raise ValueError(f"Axes invalides : {invalid}. Axes valides : {AXES}")

        values = list(self.quadruplet)
        for axis in AXES:
            if axis not in axes_set:
                values[AXIS_INDEX[axis]] = 0
        return TritQuadruplet(*values)

    def compare_on_axis(
        self, axis: str, other_quad: TritQuadruplet
    ) -> dict:
        """Compare deux scénarios sur un seul axe."""
        if axis not in AXIS_INDEX:
            raise ValueError(f"Axe invalide : {axis}. Axes valides : {AXES}")
        idx = AXIS_INDEX[axis]
        v1 = list(self.quadruplet)[idx]
        v2 = list(other_quad)[idx]
        return {
            "axis": axis,
            "self_value": v1,
            "other_value": v2,
            "difference": abs(v1 - v2),
            "compatibility": v1 == v2,
        }


class TritPoliticalMerge:
    """
    Fusionne deux positions en un compromis ternaire.

    Méthode : moyenne arrondie au trit le plus proche (round(x) restreint à {0,1,2}).

    Utilisation:
        merger = TritPoliticalMerge()
        compromise = merger.merge(Q1, Q2)
    """

    @staticmethod
    def _ternary_round(value: float) -> int:
        """Arrondi au trit le plus proche ∈ {0, 1, 2}."""
        return max(0, min(2, round(value)))

    def merge(self, q1: TritQuadruplet, q2: TritQuadruplet) -> TritQuadruplet:
        """Fusionne deux quadruplets en un compromis ternaire."""
        merged = tuple(
            self._ternary_round((a + b) / 2)
            for a, b in zip(q1, q2)
        )
        return TritQuadruplet(*merged)

    def merge_multi(self, quadruplets: List[TritQuadruplet]) -> TritQuadruplet:
        """Fusionne N quadruplets (coalition de N positions)."""
        if not quadruplets:
            raise ValueError("Au moins un quadruplet requis")
        n = len(quadruplets)
        merged = tuple(
            self._ternary_round(
                sum(list(q)[i] for q in quadruplets) / n
            )
            for i in range(4)
        )
        return TritQuadruplet(*merged)
