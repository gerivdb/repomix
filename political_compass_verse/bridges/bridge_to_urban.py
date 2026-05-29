"""
bridges/bridge_to_urban.py — Projection causale vers UrbanVerse

Implémente TritPoliticalCause : projette un scénario politique sur les
variables urbaines de urban_ontology_verse.

Ce bridge consomme les données de urban_ontology_verse/ECONOMY/zonage_idf.yaml
pour contextualiser les effets causaux.
"""

from pathlib import Path
from typing import Optional

from ..trit_encoder import TritQuadruplet
from ..political_compass_verse import CausalEffectVector

# ── Chemins par défaut vers urban_ontology_verse ──────────────────────────
DEFAULT_URBAN_ZONAGE_PATH = (
    Path(__file__).parent.parent.parent
    / "urban_ontology_verse"
    / "ECONOMY"
    / "zonage_idf.yaml"
)


class TritPoliticalCause:
    """
    Projette un scénario politique sur les variables urbaines.

    Utilisation:
        cause = TritPoliticalCause()
        vector = cause.project(quadruplet, context)
    """

    def __init__(self, zonage_path: Optional[Path] = None):
        self.zonage_path = zonage_path or DEFAULT_URBAN_ZONAGE_PATH
        self._zonage_data = None

    def _load_zonage(self) -> dict:
        if self._zonage_data is not None:
            return self._zonage_data
        if not self.zonage_path.exists():
            return {}
        import yaml
        with open(self.zonage_path, "r", encoding="utf-8") as f:
            self._zonage_data = yaml.safe_load(f) or {}
        return self._zonage_data

    def project(
        self,
        quadruplet: TritQuadruplet,
        context: dict,
    ) -> CausalEffectVector:
        """
        Projette le scénario sur les variables urbaines.

        Paramètres:
            quadruplet : position politique (S, M, E, I)
            context    : {zone_idf, density, energy_mix}

        Retourne:
            CausalEffectVector
        """
        from ..political_compass_verse import PoliticalCompassVerse

        verse = PoliticalCompassVerse()
        return verse.causal_effect(quadruplet, context)

    def project_all(
        self,
        scenarios: dict[str, TritQuadruplet],
        context: dict,
    ) -> dict[str, CausalEffectVector]:
        """Projette tous les scénarios sur le même contexte urbain."""
        results = {}
        for name, quad in scenarios.items():
            if name == "diamond":
                continue
            results[name] = self.project(quad, context)
        return results
