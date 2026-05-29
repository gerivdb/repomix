"""
bridges/bridge_to_socio.py — Projection causale vers socioverse

Socioverse est la couche d'absorption causale entre le political compass
et UrbanVerse. Elle calcule les effets intermédiaires (inégalités, mobilité
sociale, accès aux communs) avant projection géographique.
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from ..trit_encoder import TritQuadruplet


@dataclass
class SocioEffectVector:
    """Effets sociaux intermédiaires d'un scénario politique."""
    scenario_name: str
    coefficient_gini: float         # 0.0 (égalitaire) à 1.0 (inégalitaire)
    mobilite_sociale: str           # "haute" | "modérée" | "basse"
    acces_communs: str              # "universel" | "restreint" | "privatisé"
    capital_social: float           # 0.0 à 1.0
    conflict_potential: float       # 0.0 (pacifique) à 1.0 (insurrectionnel)


# ── Mapping socio-économique par quadruplet ───────────────────────────────

SOCIO_MAPPING = {
    "S": {
        0: {"gini": 0.7, "mobilite": "basse", "communs": "privatisé", "conflict": 0.6},
        1: {"gini": 0.4, "mobilite": "modérée", "communs": "restreint", "conflict": 0.3},
        2: {"gini": 0.2, "mobilite": "haute", "communs": "universel", "conflict": 0.1},
    },
    "M": {
        0: {"gini": 0.3, "capital_social": 0.8},
        1: {"gini": 0.4, "capital_social": 0.5},
        2: {"gini": 0.6, "capital_social": 0.2},
    },
}


class TritPoliticalSocioBridge:
    """
    Calcule les effets sociaux intermédiaires d'un scénario politique.

    Utilisation:
        bridge = TritPoliticalSocioBridge()
        socio = bridge.project(quadruplet)
    """

    def project(self, quadruplet: TritQuadruplet) -> SocioEffectVector:
        """Projette sur les variables sociales."""
        s, m, e, i = quadruplet

        s_data = SOCIO_MAPPING["S"][s]
        m_data = SOCIO_MAPPING["M"][m]

        gini = s_data["gini"] * 0.7 + m_data["gini"] * 0.3
        capital = m_data["capital_social"] * 0.5 + s_data.get("mobilite_score", 0.5) * 0.5

        return SocioEffectVector(
            scenario_name=f"({s},{m},{e},{i})",
            coefficient_gini=round(gini, 2),
            mobilite_sociale=s_data["mobilite"],
            acces_communs=s_data["communs"],
            capital_social=round(capital, 2),
            conflict_potential=s_data["conflict"],
        )
