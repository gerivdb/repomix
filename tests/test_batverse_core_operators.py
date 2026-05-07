"""
TESTS UNITAIRES: EPIC-1240 BATVERSE CORE OPERATORS

Implémentation complète des tests pour tous les 7 opérateurs fondamentaux.
Respecte l'architecture TDD Test Engine System.
"""

import pytest
import numpy as np
from engines.batverse_core_operators import (
    DynasticInheritanceOperator,
    NarrativeEntanglementOperator,
    CriminalityTensor,
    FearField,
    InterVerseCouplingMatrix,
    NightProjectionOperator,
    NarrativeWhiteNoise,
    CharacterState,
    BATVERSE_OPERATORS
)


@pytest.fixture
def sample_character():
    """Fixture: Personnage test standard du Batverse"""
    return CharacterState(
        id = "TEST-001",
        verse_id = 3,
        signature = np.random.normal(0, 1, 16),
        karma = 0.618,
        memory = np.random.rand(64),
        timestamp = 1672531200.0
    )


# -----------------------------------------------------------------------------
# TEST 1: OPÉRATEUR D'HÉRITAGE DYNASTIQUE H
# -----------------------------------------------------------------------------
class TestDynasticInheritanceOperator:
    
    def test_initialization(self):
        op = DynasticInheritanceOperator()
        assert op.depth == 7
        assert len(op.coefficients) == 7
        assert np.all(op.coefficients > 0)
    
    def test_apply_character(self, sample_character):
        op = DynasticInheritanceOperator()
        result = op.apply(sample_character)
        
        assert result.id == sample_character.id
        assert result.verse_id == sample_character.verse_id
        assert np.linalg.norm(result.signature) == pytest.approx(1.0, rel=1e-3)
        assert result.karma < sample_character.karma
    
    def test_hermitian_property(self):
        op = DynasticInheritanceOperator()
        assert np.allclose(op.hermitian_matrix, op.hermitian_matrix.conj().T)


# -----------------------------------------------------------------------------
# TEST 2: OPÉRATEUR D'INTRICATION NARRATIVE 𝒱_AB
# -----------------------------------------------------------------------------
class TestNarrativeEntanglementOperator:
    
    @pytest.mark.parametrize("relation_class", ['fratrie', 'alliance', 'connaissance', 'rivalite', 'ennemi'])
    def test_all_relation_classes(self, relation_class):
        op = NarrativeEntanglementOperator(relation_class)
        
        # Vérifier unitaire
        product = op.hermitian_matrix @ op.hermitian_matrix.conj().T
        assert np.allclose(product, np.eye(4), atol=1e-10)
    
    def test_entanglement_correlation(self, sample_character):
        char_a = sample_character
        char_b = CharacterState(
            id = "TEST-002", verse_id = 3,
            signature = np.random.normal(0, 1, 16),
            karma = 0.5, memory = np.random.rand(64), timestamp = 1672531200.0
        )
        
        op_alliance = NarrativeEntanglementOperator('alliance')
        a2, b2 = op_alliance.entangle(char_a, char_b)
        
        # La corrélation doit modifier le karma
        assert abs(a2.karma - char_a.karma) > 1e-3
        assert abs(b2.karma - char_b.karma) > 1e-3


# -----------------------------------------------------------------------------
# TEST 3: TENSEUR DE CRIMINALITÉ C^μν
# -----------------------------------------------------------------------------
class TestCriminalityTensor:
    
    def test_antisymmetric_property(self):
        ct = CriminalityTensor()
        tensor = ct.compute(0.7, 0.8, 0.9, 0.4)
        
        # Vérifier antisymétrie: C^μν = -C^νμ
        for mu in range(4):
            for nu in range(4):
                assert tensor[mu, nu] == -tensor[nu, mu]
    
    def test_criminality_score_range(self):
        ct = CriminalityTensor()
        ct.compute(0.0, 0.0, 0.0, 0.0)
        assert ct.criminality_score() == pytest.approx(0.0)
        
        ct.compute(1.0, 1.0, 1.0, 1.0)
        score = ct.criminality_score()
        assert 0.0 <= score <= 1.0


# -----------------------------------------------------------------------------
# TEST 4: CHAMP DE PEUR Φ̂_peur
# -----------------------------------------------------------------------------
class TestFearField:
    
    def test_field_properties(self):
        field = FearField()
        
        # Vitesse de propagation = c / 137
        assert field.speed == pytest.approx(3e8 / 137, rel=1e-3)
    
    def test_causality(self):
        field = FearField()
        distance = 1000.0
        time = 0.0
        
        # Le champ ne doit pas exister avant le temps de propagation
        value = field.evaluate(distance, time, 1.0)
        assert value == 0.0


# -----------------------------------------------------------------------------
# TEST 5: MATRICE DE COUPLAGE INTER-SUB-VERSES g_ij
# -----------------------------------------------------------------------------
class TestInterVerseCouplingMatrix:
    
    def test_matrix_symmetry(self):
        g = InterVerseCouplingMatrix()
        assert np.allclose(g.matrix, g.matrix.T, atol=1e-1)
    
    def test_normalization(self):
        g = InterVerseCouplingMatrix()
        row_norms = np.linalg.norm(g.matrix, axis=1)
        assert np.allclose(row_norms, np.ones(16), atol=1e-2)
    
    def test_coupling_decay(self):
        g = InterVerseCouplingMatrix()
        for i in range(16):
            val_i = g.matrix[i,i]
            val_i1 = g.matrix[i,(i+1)%16]
            val_i2 = g.matrix[i,(i+2)%16]
            if val_i1 > 0 or val_i2 > 0:
                assert val_i > val_i1 > val_i2
            else:
                assert val_i > val_i1 and val_i > val_i2


# -----------------------------------------------------------------------------
# TEST 6: OPÉRATEUR DE PROJECTION DE NUIT 𝒫_nuit
# -----------------------------------------------------------------------------
class TestNightProjectionOperator:
    
    def test_projection_property(self):
        P = NightProjectionOperator()
        
        # Projecteur idempotent: P² = P
        assert np.allclose(P.hermitian_matrix @ P.hermitian_matrix, P.hermitian_matrix, atol=1e-10)
    
    def test_annihilates_first_component(self):
        P = NightProjectionOperator()
        state = np.zeros(16)
        state[0] = 1.0
        
        result = P.apply(state)
        assert result[0] == pytest.approx(0.0)
    
    def test_project_character(self, sample_character):
        P = NightProjectionOperator()
        projected = P.project_character(sample_character)
        
        assert projected.verse_id == 12  # Verse 12: Tout est un opérateur
        assert projected.karma < sample_character.karma


# -----------------------------------------------------------------------------
# TEST 7: BRUIT BLANC NARRATIF η(t)
# -----------------------------------------------------------------------------
class TestNarrativeWhiteNoise:
    
    def test_density_constant(self):
        assert NarrativeWhiteNoise.DENSITY == pytest.approx(1/137.035999, rel=1e-9)
    
    def test_statistical_properties(self):
        noise = NarrativeWhiteNoise(seed=42)
        samples = noise.sample(100000)
        
        mean = np.mean(samples)
        variance = np.var(samples)
        
        assert abs(mean) < 0.01
        assert variance == pytest.approx(NarrativeWhiteNoise.DENSITY, rel=1e-2)


# -----------------------------------------------------------------------------
# TEST INTÉGRÉ: CALCUL D'INTERACTION COMPLET
# -----------------------------------------------------------------------------
def test_full_character_interaction():
    """
    TEST FINAL: Démontrer que l'on peut calculer une interaction complète
    entre deux personnages en utilisant seulement les opérateurs core.
    
    Ce test valide le critère d'arrêt de l'EPIC 1240.
    """
    
    # 1. Créer deux personnages
    alfred = CharacterState(
        id = "ALFRED", verse_id = 7,
        signature = np.random.normal(0, 1, 16),
        karma = 0.923, memory = np.random.rand(64), timestamp = 1672531200.0
    )
    
    joker = CharacterState(
        id = "JOKER", verse_id = 9,
        signature = np.random.normal(0, 1, 16),
        karma = -0.871, memory = np.random.rand(64), timestamp = 1672531200.0
    )
    
    # 2. Appliquer héritage dynastique
    H = BATVERSE_OPERATORS['H']
    alfred = H.apply(alfred)
    joker = H.apply(joker)
    
    # 3. Intrication narrative (Ennemis héréditaires)
    V = NarrativeEntanglementOperator('ennemi')
    alfred, joker = V.entangle(alfred, joker)
    
    # 4. Calculer tenseur de criminalité pour une action
    C = CriminalityTensor()
    C.compute(intention=0.97, means=0.82, opportunity=0.64, consequence=0.91)
    crime_score = C.criminality_score()
    
    # 5. Calculer champ de peur
    Phi = FearField()
    fear_level = Phi.evaluate(distance=12, time=0.000001, source_intensity=crime_score)
    
    # 6. Coupler verses
    g = BATVERSE_OPERATORS['g']
    coupling = g.couple(alfred.verse_id, joker.verse_id, alfred.signature)
    
    # 7. Ajouter bruit narratif
    eta = BATVERSE_OPERATORS['eta']
    final_noise = eta.sample()
    
    # Calculer résultat final de l'interaction
    interaction_energy = np.linalg.norm(alfred.signature - joker.signature) * crime_score + fear_level + final_noise
    
    # Vérifications finales
    assert isinstance(interaction_energy, float)
    assert not np.isnan(interaction_energy)
    assert not np.isinf(interaction_energy)
    
    print(f"✅ Interaction calculée avec succès. Énergie = {interaction_energy:.4f}")
    print("✅ TOUS LES OPÉRATEURS FONCTIONNENT ENSEMBLE")


# -----------------------------------------------------------------------------
# TEST COMMUTATEURS
# -----------------------------------------------------------------------------
def test_operators_commutation_relations():
    """Vérifie les relations de commutation entre opérateurs"""
    
    H = DynasticInheritanceOperator()
    P = NightProjectionOperator()
    
    commutator = H.commutator(P)
    
    # [H, P] ≠ 0: Les opérateurs ne commutent pas (bien)
    assert not np.allclose(commutator, np.zeros_like(commutator), atol=1e-10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])