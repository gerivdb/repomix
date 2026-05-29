"""
tests/test_political_distance.py

Tests unitaires pour le political_compass_verse.
Couvre : encodage, distance, projection, merge, rendu.
"""

import pytest
from pathlib import Path

from political_compass_verse import (
    PoliticalCompassVerse,
    TritPoliticalEncode,
    TritQuadruplet,
    TritPoliticalDistance,
    TritPoliticalProject,
    TritPoliticalMerge,
    TritPoliticalRender,
)
from political_compass_verse.bridges.bridge_to_batverse import TritPoliticalNarrate


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def verse():
    return PoliticalCompassVerse()

@pytest.fixture
def encoder():
    return TritPoliticalEncode()

@pytest.fixture
def distance():
    return TritPoliticalDistance()


# ── Tests d'encodage ──────────────────────────────────────────────────────

class TestTritPoliticalEncode:

    def test_encode_capitalisme_surveillance(self, encoder):
        q = encoder.encode("capitalisme_surveillance")
        assert q == TritQuadruplet(S=0, M=2, E=0, I=2)

    def test_encode_diamond(self, encoder):
        q = encoder.encode("diamond")
        assert q == TritQuadruplet(S=2, M=0, E=2, I=1)

    def test_encode_communisme_plateforme(self, encoder):
        q = encoder.encode("communisme_plateforme")
        assert q == TritQuadruplet(S=2, M=0, E=1, I=1)

    def test_encode_unknown_raises(self, encoder):
        with pytest.raises(ValueError, match="Scénario inconnu"):
            encoder.encode("scénario_inexistant")

    def test_encode_case_insensitive(self, encoder):
        q1 = encoder.encode("Capitalisme_Surveillance")
        q2 = encoder.encode("capitalisme_surveillance")
        assert q1 == q2

    def test_diamond_reference(self, encoder):
        assert encoder.diamond_reference == TritQuadruplet(2, 0, 2, 1)

    def test_encode_all_returns_all_scenarios(self, encoder):
        all_scenarios = encoder.encode_all()
        assert len(all_scenarios) >= 11
        assert "diamond" in all_scenarios

    def test_quadruplet_as_tuple(self):
        q = TritQuadruplet(2, 0, 2, 1)
        assert q.as_tuple() == (2, 0, 2, 1)

    def test_quadruplet_iteration(self):
        q = TritQuadruplet(1, 1, 1, 1)
        assert list(q) == [1, 1, 1, 1]


# ── Tests de distance ─────────────────────────────────────────────────────

class TestTritPoliticalDistance:

    def test_distance_identical(self, distance):
        q = TritQuadruplet(2, 0, 2, 1)
        assert distance.distance(q, q) == 0

    def test_distance_max(self, distance):
        q1 = TritQuadruplet(0, 0, 0, 0)
        q2 = TritQuadruplet(2, 2, 2, 2)
        assert distance.distance(q1, q2) == 8

    def test_distance_diamond_vs_surveillance(self, distance):
        diamond = TritQuadruplet(2, 0, 2, 1)
        surveillance = TritQuadruplet(0, 2, 0, 2)
        d = distance.distance(diamond, surveillance)
        assert d == 7  # |2-0|+|0-2|+|2-0|+|1-2| = 2+2+2+1 = 7

    def test_distance_diamond_vs_communisme_plateforme(self, distance):
        diamond = TritQuadruplet(2, 0, 2, 1)
        communisme = TritQuadruplet(2, 0, 1, 1)
        d = distance.distance(diamond, communisme)
        assert d == 1  # seul E diffère de 1

    def test_normalized_distance(self, distance):
        assert distance.normalized_distance(
            TritQuadruplet(0, 0, 0, 0),
            TritQuadruplet(2, 2, 2, 2),
        ) == 1.0

    def test_normalized_distance_zero(self, distance):
        q = TritQuadruplet(1, 1, 1, 1)
        assert distance.normalized_distance(q, q) == 0.0

    def test_from_diamond(self, distance):
        d = distance.from_diamond("libertarien")
        assert d == 7

    def test_distance_report(self, distance):
        encoder = TritPoliticalEncode()
        report = distance.distance_report(encoder=encoder)
        assert "libertarien" in report
        assert report["libertarien"]["distance"] == 7
        assert "diamond" not in report

    def test_distance_report_fibonacci_scenario(self, distance):
        """Vérification : communisme_plateforme est à distance 2 de Diamond."""
        encoder = TritPoliticalEncode()
        report = distance.distance_report(encoder=encoder)
        assert report["communisme_plateforme"]["distance"] == 2


# ── Tests de projection ───────────────────────────────────────────────────

class TestTritPoliticalProject:

    def test_project_single_axis(self):
        q = TritQuadruplet(2, 0, 2, 1)
        result = TritPoliticalProject(q).project(["E"])
        assert result == TritQuadruplet(0, 0, 2, 0)

    def test_project_multiple_axes(self):
        q = TritQuadruplet(2, 0, 2, 1)
        result = TritPoliticalProject(q).project(["E", "I"])
        assert result == TritQuadruplet(0, 0, 2, 1)

    def test_project_invalid_axis(self):
        q = TritQuadruplet(1, 1, 1, 1)
        with pytest.raises(ValueError, match="Axes invalides"):
            TritPoliticalProject(q).project(["X"])


# ── Tests de merge ────────────────────────────────────────────────────────

class TestTritPoliticalMerge:

    def test_merge_identical(self):
        q = TritQuadruplet(2, 0, 2, 1)
        result = TritPoliticalMerge().merge(q, q)
        assert result == q

    def test_merge_opposite(self):
        q1 = TritQuadruplet(0, 0, 0, 0)
        q2 = TritQuadruplet(2, 2, 2, 2)
        result = TritPoliticalMerge().merge(q1, q2)
        assert result == TritQuadruplet(1, 1, 1, 1)

    def test_merge_diamond_with_surveillance(self):
        diamond = TritQuadruplet(2, 0, 2, 1)
        surveillance = TritQuadruplet(0, 2, 0, 2)
        result = TritPoliticalMerge().merge(diamond, surveillance)
        assert result == TritQuadruplet(1, 1, 1, 1)

    def test_merge_multi(self):
        q1 = TritQuadruplet(2, 0, 2, 1)
        q2 = TritQuadruplet(1, 1, 1, 1)
        q3 = TritQuadruplet(0, 2, 0, 2)
        result = TritPoliticalMerge().merge_multi([q1, q2, q3])
        # Moyenne : S=(2+1+0)/3=1, M=(0+1+2)/3=1, E=(2+1+0)/3=1, I=(1+1+2)/3=1.33→1
        assert result == TritQuadruplet(1, 1, 1, 1)

    def test_merge_multi_empty_raises(self):
        with pytest.raises(ValueError, match="Au moins un"):
            TritPoliticalMerge().merge_multi([])


# ── Tests du Verse principal ──────────────────────────────────────────────

class TestPoliticalCompassVerse:

    def test_initialization(self, verse):
        assert verse.version == "1.0.0"
        assert verse.strate == "L5"
        assert verse.axes == ("S", "M", "E", "I")

    def test_diamond_position(self, verse):
        assert verse.diamond_position == TritQuadruplet(2, 0, 2, 1)

    def test_encode(self, verse):
        q = verse.encode("libertarien")
        assert q == TritQuadruplet(0, 2, 0, 2)

    def test_distance(self, verse):
        d = verse.distance(
            TritQuadruplet(2, 0, 2, 1),
            TritQuadruplet(0, 2, 0, 2),
        )
        assert d == 7

    def test_distance_from_diamond(self, verse):
        assert verse.distance_from_diamond("capitalisme_surveillance") == 7
        assert verse.distance_from_diamond("communisme_plateforme") == 1

    def test_distance_matrix(self, verse):
        matrix = verse.distance_matrix()
        assert matrix["diamond"]["libertarien"] == 7
        assert matrix["communisme_plateforme"]["diamond"] == 1
        assert matrix["diamond"]["diamond"] == 0

    def test_project(self, verse):
        q = TritQuadruplet(2, 0, 2, 1)
        result = verse.project(q, ["S", "E"])
        assert result == TritQuadruplet(2, 0, 2, 0)

    def test_merge(self, verse):
        result = verse.merge(
            TritQuadruplet(2, 0, 2, 1),
            TritQuadruplet(0, 2, 0, 2),
        )
        assert result == TritQuadruplet(1, 1, 1, 1)

    def test_causal_effect(self, verse):
        q = TritQuadruplet(0, 2, 0, 2)
        context = {"zone_idf": "zone_4", "density": "haute", "energy_mix": "fossile"}
        effect = verse.causal_effect(q, context)
        assert effect.pollution_index > 0.5
        assert effect.flux_capital == "exoverti"
        assert effect.qualite_air == "dégradée"

    def test_causal_effect_sobre(self, verse):
        q = TritQuadruplet(2, 0, 2, 1)
        context = {"zone_idf": "zone_1", "density": "basse", "energy_mix": "renouvelable"}
        effect = verse.causal_effect(q, context)
        assert effect.pollution_index < 0.3
        assert effect.flux_capital == "endogène"


# ── Tests du render ───────────────────────────────────────────────────────

class TestTritPoliticalRender:

    def test_mermaid_output(self, verse):
        mermaid = verse.render_mermaid()
        assert "mermaid" in mermaid
        assert "Diamond" in mermaid

    def test_yaml_report(self, verse):
        report = verse.render_yaml()
        assert "political_compass_report" in report
        assert "diamond_reference" in report

    def test_svg_data(self, verse):
        data = verse.render_svg_data()
        assert "vertices" in data
        assert "S" in data["vertices"]
        assert "scenarios" in data
        assert "diamond" in data["scenarios"]


# ── Tests du bridge BatVerse ──────────────────────────────────────────────

class TestTritPoliticalNarrate:

    def test_narrate_static(self, verse):
        narrate = TritPoliticalNarrate(encoder=verse.encoder)
        q = verse.encode("capitalisme_surveillance")
        arc = narrate.narrate(q, label="Test Static")
        assert arc.mode == "static"
        assert arc.source_quadruplet == q
        assert len(arc.narrative_summary) > 0

    def test_narrate_transition(self, verse):
        narrate = TritPoliticalNarrate(encoder=verse.encoder)
        q1 = verse.encode("capitalisme_surveillance")
        q2 = verse.encode("diamond")
        arc = narrate.narrate_transition(q1, q2, label="La Grande Bifurcation")
        assert arc.mode == "transition"
        assert arc.source_quadruplet == q1
        assert arc.target_quadruplet == q2

    def test_narrate_counterfactual(self, verse):
        narrate = TritPoliticalNarrate(encoder=verse.encoder)
        yaml_path = Path(__file__).parent.parent / "scenarios" / "hypotheses" / "scenario_post_AGI.yaml"
        arc = narrate.narrate_counterfactual(yaml_path)
        assert arc.mode == "counterfactual"
        assert "Post-AGI" in arc.label

    def test_export_arc(self, verse, tmp_path):
        narrate = TritPoliticalNarrate(encoder=verse.encoder)
        q = verse.encode("communisme_plateforme")
        arc = narrate.narrate(q, label="Test Export")
        output = tmp_path / "test_arc.json"
        narrate.export_arc(arc, output)
        assert output.exists()
        import json
        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["arc_id"] == arc.arc_id
