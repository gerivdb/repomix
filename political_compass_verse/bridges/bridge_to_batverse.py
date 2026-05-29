"""
bridges/bridge_to_batverse.py — Functor narratif vers BatVerse

Implémente TritPoliticalNarrate : transforme un quadruplet ou une
transition (Q1 → Q2) en arc narratif scénarisé dans BatVerse.

Ce module est un BRIDGE : il ne crée pas directement les arcs BatVerse
dans le repo BATVERSE, il produit les données d'entrée (BatVerseArc)
que le workflow GOVERNANCE-HUB/consume pour appeler BatVerse.

Modes :
  - "static"        : un quadruplet → description narrative du monde
  - "transition"    : Q_avant → Q_après → arc narratif de transformation
  - "counterfactual" : hypothèse YAML → débat narratif
"""

import hashlib
import time
from pathlib import Path
from typing import Optional

import yaml

from ..trit_encoder import TritQuadruplet, TritPoliticalEncode
from ..trit_distance import TritPoliticalDistance
from ..political_compass_verse import BatVerseArc


# ── Templates narratifs par axe ───────────────────────────────────────────

AXIS_NARRATIVE = {
    "S": {
        0: "La société se fragmente. Chacun pour soi.",
        1: "Des liens communautaires subsistent, mais fragiles.",
        2: "La solidarité structure les rapports sociaux.",
    },
    "M": {
        0: "L'échange hors-marché domine.",
        1: "Le marché existe mais est encadré.",
        2: "Tout s'achète, tout se vend.",
    },
    "E": {
        0: "La nature est un gisement à exploiter.",
        1: "L'environnement est une contrainte parmi d'autres.",
        2: "La sobriété guide chaque décision.",
    },
    "I": {
        0: "L'intelligence Artificielle est absente ou marginale.",
        1: "L'IA est un outil frugal, au service du collectif.",
        2: "L'IA est omniprésente, elle gouverne l'allocation des ressources.",
    },
}

TRANSITION_NARRATIVE = {
    "S": {
        (0, 2): "Des réseaux de solidarité émergent spontanément.",
        (2, 0): "Les liens communautaires se désintègrent.",
    },
    "M": {
        (0, 2): "Une économise de marché s'installe progressivement.",
        (2, 0): "Le marché est démantelé au profit des communs.",
    },
    "E": {
        (0, 2): "Une prise de conscience écologique transforme les pratiques.",
        (2, 0): "L'extractivisme reprend ses droits.",
    },
    "I": {
        (0, 2): "L'IA colonise tous les secteurs.",
        (2, 0): "L'IA est désactivée, utilisée de façon frugale.",
    },
}


def _generate_arc_id(label: str, mode: str) -> str:
    """Génère un identifiant unique d'arc BatVerse."""
    seed = f"{label}:{mode}:{time.time()}"
    short_hash = hashlib.sha256(seed.encode()).hexdigest()[:10]
    return f"ARC-POL-{mode.upper()}-{short_hash}"


def _static_narrative(quad: TritQuadruplet) -> str:
    """Génère une description narrative du monde pour un quadruplet donné."""
    parts = []
    axes = ("S", "M", "E", "I")
    for axis, val in zip(axes, quad):
        parts.append(AXIS_NARRATIVE[axis][val])
    return "\n".join(parts)


def _transition_narrative(q_before: TritQuadruplet, q_after: TritQuadruplet) -> str:
    """Génère un arc narratif de transition entre deux états."""
    parts = []
    axes = ("S", "M", "E", "I")
    for axis, vals in zip(axes, zip(q_before, q_after)):
        if vals[0] != vals[1]:
            narrative = TRANSITION_NARRATIVE[axis].get(vals, "")
            if narrative:
                parts.append(f"[{axis}] {narrative}")
    return "\n".join(parts) if parts else "Transition silencieuse — aucun axe ne change."


class TritPoliticalNarrate:
    """
    Functor narratif vers BatVerse.

    Transforme un quadruplet ou une transition en BatVerseArc,
    puis peut sérialiser en JSON pour consommation par le workflow.

    Utilisation:
        narrate = TritPoliticalNarrate()

        # Mode statique
        arc = narrate.narrate(quad, label="Description du monde")

        # Mode transition
        arc = narrate.narrate_transition(q1, q2, label="La Grande Bifurcation")

        # Mode contrefactuel (depuis YAML)
        arc = narrate.narrate_counterfactual("path/to/hypothesis.yaml")
    """

    def __init__(self, encoder: Optional[TritPoliticalEncode] = None):
        self.encoder = encoder or TritPoliticalEncode()
        self.distance_calc = TritPoliticalDistance()

    def narrate(
        self,
        quadruplet: TritQuadruplet,
        label: str = "",
    ) -> BatVerseArc:
        """Narrate un état statique."""
        label = label or f"World-{quadruplet}"
        arc_id = _generate_arc_id(label, "static")

        return BatVerseArc(
            arc_id=arc_id,
            label=label,
            source_quadruplet=quadruplet,
            mode="static",
            narrative_summary=_static_narrative(quadruplet),
            coherence_feedback=self._coherence_score(quadruplet),
        )

    def narrate_transition(
        self,
        q_before: TritQuadruplet,
        q_after: TritQuadruplet,
        label: str = "",
    ) -> BatVerseArc:
        """Narrate une transition entre deux états politiques."""
        label = label or f"Transition-{q_before}-{q_after}"
        arc_id = _generate_arc_id(label, "transition")

        return BatVerseArc(
            arc_id=arc_id,
            label=label,
            source_quadruplet=q_before,
            target_quadruplet=q_after,
            mode="transition",
            narrative_summary=_transition_narrative(q_before, q_after),
            coherence_feedback=self._transition_coherence(q_before, q_after),
        )

    def narrate_counterfactual(self, yaml_path: Path) -> BatVerseArc:
        """Narrate une hypothèse contrefactuelle depuis un fichier YAML."""
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        hypothesis = data["hypothesis"]
        label = hypothesis.get("label", "Contrefactuel")
        quad_data = data["quadruplet_hypothetique"]
        quad = TritQuadruplet(quad_data["S"], quad_data["M"], quad_data["E"], quad_data["I"])
        arc_id = _generate_arc_id(label, "counterfactual")

        return BatVerseArc(
            arc_id=arc_id,
            label=label,
            source_quadruplet=quad,
            mode="counterfactual",
            narrative_summary=hypothesis.get("description", ""),
            coherence_feedback=self._counterfactual_tension(quad, data.get("tensions", [])),
        )

    def export_arc(self, arc: BatVerseArc, output_path: Path) -> None:
        """Exporte un arc BatVerse en JSON pour consommation par le workflow."""
        import json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(arc.to_dict(), f, indent=2, ensure_ascii=False)

    def to_character_state(self, arc: "BatVerseArc") -> dict:
        """
        Traduit un BatVerseArc en representation compatible CharacterState BatVerse.

        Adaptateur temporaire jusqu'a formalisation du contrat d'arc.
        Quand BatVerse sera pret a consommer, le NarrativeEntanglementOperator
        saura quoi faire de entanglement_seed.

        Returns:
            dict avec character_id, state_vector, narrative_tension, arc_mode, entanglement_seed.
        """
        question = None
        if arc.mode == "counterfactual" and arc.narrative_summary:
            question = arc.narrative_summary

        return {
            "character_id": f"political_scenario_{arc.arc_id}",
            "state_vector": list(arc.source_quadruplet) if arc.source_quadruplet else [0, 0, 0, 0],
            "narrative_tension": arc.label,
            "arc_mode": arc.mode,
            "entanglement_seed": question,
        }

    # ── Cohérence narrative ────────────────────────────────────────────────

    def _coherence_score(self, quad: TritQuadruplet) -> float:
        """
        Score de cohérence interne d'un quadruplet (0..1).
        Une faible distance à Diamond = cohérence élevée.
        """
        diamond = self.encoder.diamond_reference
        d = self.distance_calc.distance(quad, diamond)
        return round(1.0 - (d / 8.0), 3)

    def _transition_coherence(self, q1: TritQuadruplet, q2: TritQuadruplet) -> float:
        """Score de cohérence d'une transition (les petits pas sont plus cohérents)."""
        d = self.distance_calc.distance(q1, q2)
        return round(max(0, 1.0 - (d / 8.0)), 3)

    def _counterfactual_tension(self, quad: TritQuadruplet, tensions: list) -> float:
        """
        Produit la tension narrative d'un scénario contrefactuel.
        Plus il y a de tensions identifiées, plus le potentiel narratif est élevé.
        """
        base = 0.5
        tension_bonus = min(0.5, len(tensions) * 0.1)
        return round(base + tension_bonus, 3)
