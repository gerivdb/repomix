"""
trit_distance.py — TritPoliticalDistance

Distance de Manhattan ternaire entre deux quadruplets.
Résultat ∈ [0..8]. 0 = identiques, 8 = opposés absolus.

d(Q₁, Q₂) = Σ|Q₁[i] - Q₂[i]|  pour i ∈ {S, M, E, I}

Avec 4 dimensions × plage max de 2 = distance max de 8.
"""

from typing import Optional
from .trit_encoder import TritQuadruplet, TritPoliticalEncode


class TritPoliticalDistance:
    """
    Calcule la distance de Manhattan ternaire entre deux positions politiques.

    Utilisation:
        calc = TritPoliticalDistance()
        d = calc.distance(Q1, Q2)          # float ∈ [0..8]
        d = calc.from_diamond("libertarien")  # distance vs Diamond
        report = calc.distance_report(encoded_matrix)
    """

    MAX_DISTANCE = 8.0  # 4 dimensions × 2

    def distance(self, q1: TritQuadruplet, q2: TritQuadruplet) -> float:
        """Distance de Manhattan entre deux quadruplets."""
        return sum(abs(a - b) for a, b in zip(q1, q2))

    def normalized_distance(self, q1: TritQuadruplet, q2: TritQuadruplet) -> float:
        """Distance normalisée ∈ [0..1]. 0 = identiques, 1 = opposés absolus."""
        return self.distance(q1, q2) / self.MAX_DISTANCE

    def from_diamond(
        self,
        scenario: str,
        encoder: Optional[TritPoliticalEncode] = None,
    ) -> float:
        """Distance d'un scénario donné par rapport à la position Diamond."""
        if encoder is None:
            encoder = TritPoliticalEncode()
        diamond = encoder.diamond_reference
        target = encoder.encode(scenario)
        return self.distance(diamond, target)

    def distance_report(
        self,
        scenarios: Optional[dict[str, TritQuadruplet]] = None,
        encoder: Optional[TritPoliticalEncode] = None,
    ) -> dict[str, dict]:
        """
        Génère un rapport de distances pour tous les scénarios
        par rapport à Diamond.

        Retourne:
            {scenario_id: {"quadruplet": ..., "distance": ..., "normalized": ...}}
        """
        if encoder is None:
            encoder = TritPoliticalEncode()
        if scenarios is None:
            scenarios = encoder.encode_all()

        diamond = encoder.diamond_reference
        report = {}
        for name, quad in scenarios.items():
            if name == "diamond":
                continue
            d = self.distance(diamond, quad)
            report[name] = {
                "quadruplet": quad.as_tuple(),
                "distance": d,
                "normalized": round(d / self.MAX_DISTANCE, 3),
            }
        return report


# ── Governance thresholds ─────────────────────────────────────────────────

GOVERNANCE_TOLERANCE = 5    # distance acceptable sans alerte
GOVERNANCE_HARD_LIMIT = 7   # distance maximale observée (marketplace Phase 4)


def governance_alert(
    quadruplet: TritQuadruplet,
    reference: Optional[TritQuadruplet] = None,
    label: str = "",
) -> Optional[dict]:
    """
    Retourne un dict d'alerte si la distance dépasse GOVERNANCE_TOLERANCE.
    Ne bloque rien. Destiné au logging dans political_compass_analysis.yaml.

    Returns:
        None si distance <= TOLERANCE, sinon dict avec severity, distance, message.
    """
    if reference is None:
        from .trit_encoder import DIAMOND_REFERENCE
        reference = DIAMOND_REFERENCE

    calc = TritPoliticalDistance()
    dist = calc.distance(quadruplet, reference)

    if dist <= GOVERNANCE_TOLERANCE:
        return None

    severity = "CRITICAL" if dist >= GOVERNANCE_HARD_LIMIT else "WARNING"

    return {
        "label": label,
        "quadruplet": list(quadruplet),
        "distance_from_diamond": dist,
        "severity": severity,
        "message": (
            f"Distance {dist} depasse le seuil de tolerance "
            f"({GOVERNANCE_TOLERANCE}). Severite: {severity}"
        ),
    }

