"""
trit_renderer.py — TritPoliticalRender

Génère des représentations du tétraèdre politique :
  - mermaid_md   → diagramme Mermaid pour documentation
  - yaml_report  → rapport structuré en YAML
  - svg_data     → données pour rendu SVG (points 2D)

Le tétraèdre à 4 pôles (S, M, E, I) est projeté dans un espace 2D
via la projection barycentrique standard.
"""

from typing import Optional
from pathlib import Path
from .trit_encoder import TritQuadruplet, TritPoliticalEncode, DIAMOND_REFERENCE
from .trit_distance import TritPoliticalDistance


# ── Coordonnées 2D des 4 sommets du tétraèdre (projection barycentrique) ──
# S = haut, M = bas-gauche, E = bas-droite, I = centre-haut
VERTEX_2D = {
    "S": (0.5, 0.87),   # haut
    "M": (0.0, 0.0),    # bas gauche
    "E": (1.0, 0.0),    # bas droite
    "I": (0.5, 0.29),   # centre haut
}

AXES_ORDER = ("S", "M", "E", "I")


def _project_barycentric(quad: TritQuadruplet) -> tuple[float, float]:
    """
    Projette un quadruplet dans l'espace 2D du tétraèdre.

    Normalise les poids (S+M+E+I ∈ [0..8]) pour obtenir des
    coordonnées barycentriques, puis calcule le point 2D.
    """
    total = sum(quad)
    if total == 0:
        return (0.5, 0.3)  # centre du tétraèdre pour tout-à-zéro

    weights = [v / total for v in quad]
    x = sum(w * VERTEX_2D[axis][0] for w, axis in zip(weights, AXES_ORDER))
    y = sum(w * VERTEX_2D[axis][1] for w, axis in zip(weights, AXES_ORDER))
    return (round(x, 4), round(y, 4))


class TritPoliticalRender:
    """
    Génère les représentations du tétraèdre politique.

    Utilisation:
        renderer = TritPoliticalRender(encoder)
        mermaid = renderer.to_mermaid()
        report = renderer.to_yaml_report()
    """

    def __init__(self, encoder: Optional[TritPoliticalEncode] = None):
        self.encoder = encoder or TritPoliticalEncode()
        self.dist_calc = TritPoliticalDistance()

    def to_mermaid(self) -> str:
        """Génère un diagramme Mermaid des scénarios dans le tétraèdre."""
        scenarios = self.encoder.encode_all()
        diamond = self.encoder.diamond_reference

        lines = [
            "```mermaid",
            "graph TD",
            "    subgraph Tétraèdre_Politique[L5 — Political Compass Verse]",
            f'        S([Solidarity = {diamond.S}])',
            f'        M([Market = {diamond.M}])',
            f'        E([Ecology = {diamond.E}])',
            f'        I([AI = {diamond.I}])',
            "",
            "        DIAMOND[\"💎 Diamond\\n(2,0,2,1)\"]",
            "        S --- DIAMOND",
            "        M --- DIAMOND",
            "        E --- DIAMOND",
            "        I --- DIAMOND",
            "",
            '        classDef diamond fill:#FFD700,stroke:#FF8C00,stroke-width:3px',
            '        classDef opposite fill:#FF4444,stroke:#8B0000,stroke-width:2px',
            '        classDef near fill:#90EE90,stroke:#006400,stroke-width:2px',
            '        class DIAMOND diamond',
            "",
        ]

        report = self.dist_calc.distance_report(scenarios)
        for name, info in report.items():
            d = info["distance"]
            coords = info["quadruplet"]
            label = name.replace("_", " ").title()
            node_id = name.upper()

            if d <= 2:
                style = "near"
            elif d >= 6:
                style = "opposite"
            else:
                style = ""

            lines.append(f'        {node_id}["{label}\\n{coords}"]')
            if style:
                lines.append(f"        class {node_id} {style}")

        lines.append("    end")
        lines.append("```")
        return "\n".join(lines)

    def to_yaml_report(self) -> str:
        """Génère un rapport YAML complet."""
        scenarios = self.encoder.encode_all()
        diamond = self.encoder.diamond_reference
        report = self.dist_calc.distance_report(scenarios)

        lines = [
            "political_compass_report:",
            f"  version: '1.0.0'",
            f"  strate: L5",
            f"  generated_by: political_compass_verse",
            f"  diamond_reference: {list(diamond)}",
            f"  total_scenarios: {len(scenarios) - 1}",
            "",
            "  scenarios:",
        ]

        for name in CANONICAL_ORDER:
            if name == "diamond" or name not in report:
                continue
            info = report[name]
            coords = info["quadruplet"]
            lines.extend([
                f"    - name: {name}",
                f"      label: {name.replace('_', ' ').title()}",
                f"      coordinates: {list(coords)}",
                f"      distance_from_diamond: {info['distance']}",
                f"      normalized_distance: {info['normalized']}",
                f"      alignment: {_alignment_label(info['distance'])}",
            ])

        lines.append("")
        return "\n".join(lines)

    def to_svg_data(self) -> dict:
        """Retourne les coordonnées 2D de chaque scénario pour rendu SVG."""
        scenarios = self.encoder.encode_all()
        points = {}
        for name, quad in scenarios.items():
            points[name] = {
                "quadruplet": list(quad),
                "x": _project_barycentric(quad)[0],
                "y": _project_barycentric(quad)[1],
            }
        return {
            "vertices": {ax: list(v) for ax, v in VERTEX_2D.items()},
            "scenarios": points,
        }


def _alignment_label(distance: float) -> str:
    if distance == 0:
        return "IDENTIQUE"
    if distance <= 2:
        return "PROCHE"
    if distance <= 4:
        return "MODÉRÉ"
    if distance <= 6:
        return "ÉLOIGNÉ"
    return "OPPOSÉ"


# Ordre canonique de présentation (hors diamond)
CANONICAL_ORDER = [
    "diamond",
    "communisme_plateforme",
    "gaulliste_souverainiste",
    "social_democratie",
    "ecologie_thermodynamique",
    "ecologie_numerique",
    "communisme_pur",
    "anarcho_gauche",
    "liberalisme_modere",
    "capitalisme_pur",
    "libertarien",
    "capitalisme_surveillance",
]
