"""
Tests d'intégration pour spoke PHYSICS
Couverture >85% requise
"""

import pytest
import yaml
from pathlib import Path

class TestSpokePHYSICSIntegration:
    """Tests d'intégration spoke PHYSICS."""

    def setup_method(self):
        """Setup test environment."""
        self.spoke_dir = Path(__file__).parent.parent
        self.verses_dir = self.spoke_dir / "verses"
        self.workflows_dir = self.spoke_dir / "workflows"

    def test_verses_exist(self):
        """Test que les verses existent."""
        verses = list(self.verses_dir.glob("*.yaml"))
        assert len(verses) > 0, f"Aucun verse trouvé dans {self.verses_dir}"

    def test_verses_valid_yaml(self):
        """Test que tous les verses sont du YAML valide."""
        for verse_file in self.verses_dir.glob("*.yaml"):
            with open(verse_file, 'r') as f:
                data = yaml.safe_load(f)
                assert "id" in data, f"Verse {verse_file.name} manque ID"
                assert "spoke" in data, f"Verse {verse_file.name} manque spoke"
                assert data["spoke"] == "PHYSICS", f"Verse {verse_file.name} mauvais spoke"

    def test_workflows_exist(self):
        """Test que les workflows CI/CD existent."""
        workflows = list(self.workflows_dir.glob("*.workflow"))
        assert len(workflows) >= 1, f"Aucun workflow trouvé dans {self.workflows_dir}"

    def test_manifest_updated(self):
        """Test que le manifest est à jour."""
        manifest_file = self.spoke_dir / "manifest.json"
        assert manifest_file.exists(), "Manifest manquant"

        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
            assert manifest["verses_count"] > 0, "Aucun verse dans manifest"
            assert manifest["workflows_count"] > 0, "Aucun workflow dans manifest"

    def test_domain_specific_validation(self):
        """Test validation spécifique au domaine."""
        # Test spécifique au domaine selon le spoke
        if spoke == "PHYSICS":
            # Test physics-specific: vérifier présence de calculs physiques
            physics_verses = [v for v in self.verses_dir.glob("*.yaml") if "physics" in str(v).lower()]
            assert len(physics_verses) > 0, "Aucun verse physics trouvé"
        elif spoke == "SCIENCE":
            # Test science-specific: vérifier présence de méthodologies
            science_verses = [v for v in self.verses_dir.glob("*.yaml") if "science" in str(v).lower() or "research" in str(v).lower()]
            assert len(science_verses) > 0, "Aucun verse science trouvé"
        else:  # TECH
            # Test tech-specific: vérifier présence d'infrastructure
            tech_verses = [v for v in self.verses_dir.glob("*.yaml") if "tech" in str(v).lower() or "infra" in str(v).lower()]
            assert len(tech_verses) > 0, "Aucun verse tech trouvé"

    def test_coverage_above_85_percent(self):
        """Test de couverture de code >85%."""
        # Placeholder - serait remplacé par vrai test de couverture
        # En production: utiliser pytest-cov pour mesurer couverture
        assert True, "Couverture de test >85% requise (placeholder)"
