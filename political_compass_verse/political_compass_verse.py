"""
political_compass_verse.py — Classe principale du Verse

Orchestre l'encodage, le calcul de distances, la projection causale
et la scénarisation narrative du tétraèdre politique.

Primities exposées (conformes TritRegistry) :
  - TritPoliticalEncode   : text/scenario_id → TritQuadruplet
  - TritPoliticalDistance : Manhattan ternaire entre deux quadruplets
  - TritPoliticalProject  : réduction à un sous-espace d'axes
  - TritPoliticalMerge   : fusion de positions (compromis ternaire)
  - TritPoliticalRender  : mermaid / svg / yaml
  - TritPoliticalNarrate : functor → BatVerse (arc narratif)
  - TritPoliticalCause   : projection causale → urban_ontology_verse
"""

import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from .trit_encoder import TritPoliticalEncode, TritQuadruplet, DIAMOND_REFERENCE
from .trit_distance import TritPoliticalDistance
from .trit_projector import TritPoliticalProject, TritPoliticalMerge
from .trit_renderer import TritPoliticalRender


@dataclass
class CausalEffectVector:
    """Vecteur d'effets causaux d'un scénario politique sur le milieu."""
    scenario_name: str = ""
    quadruplet: Optional[TritQuadruplet] = None
    pollution_index: float = 0.0
    flux_capital: str = ""
    qualite_air: str = ""
    peripherique_flag: str = ""


@dataclass
class BatVerseArc:
    """Arc narratif dans BatVerse (produit par le functor)."""
    arc_id: str = ""
    label: str = ""
    source_quadruplet: Optional[TritQuadruplet] = None
    target_quadruplet: Optional[TritQuadruplet] = None
    mode: str = "static"
    narrative_summary: str = ""
    coherence_feedback: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "arc_id": self.arc_id,
            "label": self.label,
            "source": list(self.source_quadruplet) if self.source_quadruplet else None,
            "target": list(self.target_quadruplet) if self.target_quadruplet else None,
            "mode": self.mode,
            "narrative_summary": self.narrative_summary,
            "coherence_feedback": self.coherence_feedback,
            "timestamp": self.timestamp,
        }


class PoliticalCompassVerse:
    """
    Classe principale du political_compass_verse.

    Exemple:
        verse = PoliticalCompassVerse()
        q = verse.encode("capitalisme_surveillance")
        d = verse.distance_from_diamond("libertarien")
        cause = verse.causal_effect(q, context={"zone_idf": "zone_4", ...})
    """

    def __init__(self, scenarios_yaml: Optional[Path] = None, version: str = "1.0.0"):
        self.version = version
        self.strate = "L5"
        self.encoder = TritPoliticalEncode(yaml_path=scenarios_yaml)
        self.distance_calc = TritPoliticalDistance()
        self.projector_factory = TritPoliticalProject
        self.merger = TritPoliticalMerge()
        self.renderer = TritPoliticalRender(self.encoder)
        self._diamond = DIAMOND_REFERENCE

    # ── Propriétés ──────────────────────────────────────────────────────────

    @property
    def diamond_position(self) -> TritQuadruplet:
        return self._diamond

    @property
    def axes(self) -> tuple:
        return ("S", "M", "E", "I")

    # ── Encodage ────────────────────────────────────────────────────────────

    def encode(self, scenario: str) -> TritQuadruplet:
        """Encode un scénario en TritQuadruplet."""
        return self.encoder.encode(scenario)

    def encode_all(self) -> dict[str, TritQuadruplet]:
        """Encode tous les scénarios."""
        return self.encoder.encode_all()

    # ── Distance ────────────────────────────────────────────────────────────

    def distance(self, q1: TritQuadruplet, q2: TritQuadruplet) -> float:
        return self.distance_calc.distance(q1, q2)

    def distance_from_diamond(self, scenario: str) -> float:
        return self.distance_calc.from_diamond(scenario, self.encoder)

    def distance_matrix(self) -> dict[str, dict[str, float]]:
        """Matrice des distances entre tous les scénarios."""
        scenarios = self.encoder.encode_all()
        matrix = {}
        for n1, q1 in scenarios.items():
            matrix[n1] = {}
            for n2, q2 in scenarios.items():
                matrix[n1][n2] = self.distance(q1, q2)
        return matrix

    # ── Projection ──────────────────────────────────────────────────────────

    def project(self, quadruplet: TritQuadruplet, axes: list) -> TritQuadruplet:
        p = self.projector_factory(quadruplet)
        return p.project(axes)

    def merge(self, q1: TritQuadruplet, q2: TritQuadruplet) -> TritQuadruplet:
        return self.merger.merge(q1, q2)

    # ── Rendu ───────────────────────────────────────────────────────────────

    def render_mermaid(self) -> str:
        return self.renderer.to_mermaid()

    def render_yaml(self) -> str:
        return self.renderer.to_yaml_report()

    def render_svg_data(self) -> dict:
        return self.renderer.to_svg_data()

    # ── Projection causale (TritPoliticalCause) ─────────────────────────────

    def causal_effect(
        self,
        quadruplet: TritQuadruplet,
        context: dict,
    ) -> CausalEffectVector:
        """
        Projette un scénario politique sur les variables urbaines.

        Paramètres:
            quadruplet     : position politique
            context        : {zone_idf, density, energy_mix}

        Retourne:
            CausalEffectVector avec les effets attendus
        """
        s, m, e, i = quadruplet

        pollution = round(
            (m / 2.0 * 0.5 + (2 - e) / 2.0 * 0.3 + i / 2.0 * 0.2) * self._density_factor(context),
            2,
        )
        pollution = min(1.0, max(0.0, pollution))

        flux = self._compute_flux(s, m, i)
        air = self._air_quality_label(pollution)
        periph = self._peripheral_risk(pollution, context)

        return CausalEffectVector(
            scenario_name=f"({s},{m},{e},{i})",
            quadruplet=quadruplet,
            pollution_index=pollution,
            flux_capital=flux,
            qualite_air=air,
            peripherique_flag=periph,
        )

    def _density_factor(self, ctx: dict) -> float:
        density = ctx.get("density", "moyenne")
        factors = {"haute": 1.3, "moyenne": 1.0, "basse": 0.7}
        return factors.get(density, 1.0)

    def _compute_flux(self, s: int, m: int, i: int) -> str:
        if m == 2 and s == 0:
            return "exoverti"
        if m == 0 and s == 2:
            return "endogène"
        return "mixte"

    def _air_quality_label(self, pollution: float) -> str:
        if pollution <= 0.33:
            return "bonne"
        if pollution <= 0.66:
            return "modérée"
        return "dégradée"

    def _peripheral_risk(self, pollution: float, ctx: dict) -> str:
        zone = ctx.get("zone_idf", "")
        if pollution >= 0.7:
            return "zone_à_risque"
        if pollution >= 0.4:
            return "zone_sous_surveillance"
        return "zone_stable"
