"""
trit_encoder.py — TritPoliticalEncode

Convertit un scénario (texte ou nom canonique) en quadruplet ternaire
(S, M, E, I) ∈ {0,1,2}⁴.

Axes du tétraèdre :
  S = Solidarité      (0=individualiste, 1=mixte, 2=solidaire)
  M = Marché          (0=non-marchand, 1=régulé, 2=marchand)
  E = Écologie        (0=extractiviste, 1=modérée, 2=sobre)
  I = Intelligence Artificielle  (0=absente, 1=frugale, 2=omniprésente)
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import yaml
from pathlib import Path


@dataclass(frozen=True)
class TritQuadruplet:
    """Quadruplet ternaire (S, M, E, I) — état politique dans le tétraèdre."""
    S: int  # Solidarité ∈ {0, 1, 2}
    M: int  # Marché ∈ {0, 1, 2}
    E: int  # Écologie ∈ {0, 1, 2}
    I: int  # IA ∈ {0, 1, 2}

    def as_tuple(self) -> Tuple[int, int, int, int]:
        return (self.S, self.M, self.E, self.I)

    def __iter__(self):
        yield self.S
        yield self.M
        yield self.E
        yield self.I

    def __repr__(self) -> str:
        return f"TritQuadruplet(S={self.S}, M={self.M}, E={self.E}, I={self.I})"


# ── Position Diamond de référence ──────────────────────────────────────────
DIAMOND_REFERENCE: TritQuadruplet = TritQuadruplet(S=2, M=0, E=2, I=1)

# ── Encodage canonique des 11 scénarios ───────────────────────────────────
CANONICAL_SCENARIOS: dict[str, Tuple[int, int, int, int]] = {
    "libertarien":               (0, 2, 0, 2),
    "capitalisme_pur":           (0, 2, 0, 2),
    "liberalisme_modere":        (0, 2, 1, 2),
    "gaulliste_souverainiste":   (1, 1, 1, 1),
    "social_democratie":         (2, 1, 1, 1),
    "communisme_pur":            (2, 0, 1, 2),
    "anarcho_gauche":            (2, 1, 2, 0),
    "ecologie_thermodynamique":  (1, 0, 2, 1),
    "capitalisme_surveillance":  (0, 2, 0, 2),
    "communisme_plateforme":     (2, 0, 1, 1),
    "ecologie_numerique":        (1, 0, 2, 0),
    "diamond":                   (2, 0, 2, 1),
}


class TritPoliticalEncode:
    """
    Encode un scénario politique en quadruplet ternaire.

    Utilisation:
        encoder = TritPoliticalEncode()
        q = encoder.encode("capitalisme_surveillance")
        print(q)  # TritQuadruplet(S=0, M=2, E=0, I=2)

    L'encodeur normalise les noms (minuscules, remplacements d'espaces)
    et cherche d'abord dans les scénarios canoniques, puis dans un
    fichier YAML optionnel.
    """

    def __init__(self, yaml_path: Optional[Path] = None):
        self._overrides: dict[str, Tuple[int, int, int, int]] = {}
        if yaml_path and yaml_path.exists():
            self._load_yaml(yaml_path)

    def _load_yaml(self, path: Path) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        for entry in data.get("scenarios", []):
            name = self._normalize(entry["name"])
            self._overrides[name] = (
                int(entry["S"]),
                int(entry["M"]),
                int(entry["E"]),
                int(entry["I"]),
            )

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().lower().replace(" ", "_").replace("-", "_")

    def encode(self, scenario: str) -> TritQuadruplet:
        """Encode un texte ou un nom canonique en TritQuadruplet."""
        key = self._normalize(scenario)

        if key in self._overrides:
            s, m, e, i = self._overrides[key]
        elif key in CANONICAL_SCENARIOS:
            s, m, e, i = CANONICAL_SCENARIOS[key]
        else:
            raise ValueError(
                f"Scénario inconnu : '{scenario}'. "
                f"Disponibles : {list(CANONICAL_SCENARIOS.keys())}"
            )

        return TritQuadruplet(S=s, M=m, E=e, I=i)

    def encode_all(self) -> dict[str, TritQuadruplet]:
        """Encode tous les scénarios canoniques."""
        merged = {**CANONICAL_SCENARIOS, **self._overrides}
        return {name: TritQuadruplet(*vals) for name, vals in merged.items()}

    @property
    def diamond_reference(self) -> TritQuadruplet:
        """Retourne la position Diamond de référence."""
        return DIAMOND_REFERENCE
