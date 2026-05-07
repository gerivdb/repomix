"""Tests for VERSUS spokes integration."""
import pytest
from pathlib import Path
import os

# Force correct working directory
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)


class TestSpokesStructure:
    """Test spokes directory structure."""

    def test_physics_spoke_exists(self):
        """Test PHYSICS spoke directory exists."""
        physics_path = PROJECT_ROOT / "spokes" / "PHYSICS"
        assert physics_path.exists(), "PHYSICS spoke directory should exist"
        assert physics_path.is_dir(), "PHYSICS should be a directory"

    def test_math_spoke_exists(self):
        """Test MATH spoke directory exists."""
        math_path = PROJECT_ROOT / "spokes" / "MATH"
        assert math_path.exists(), "MATH spoke directory should exist"

    def test_science_spoke_exists(self):
        """Test SCIENCE spoke directory exists."""
        science_path = PROJECT_ROOT / "spokes" / "SCIENCE"
        assert science_path.exists(), "SCIENCE spoke directory should exist"

    def test_ai_spoke_exists(self):
        """Test AI spoke directory exists."""
        ai_path = PROJECT_ROOT / "spokes" / "AI"
        assert ai_path.exists(), "AI spoke directory should exist"

    def test_bio_spoke_exists(self):
        """Test BIO spoke directory exists."""
        bio_path = PROJECT_ROOT / "spokes" / "BIO"
        assert bio_path.exists(), "BIO spoke directory should exist"

    def test_tech_spoke_exists(self):
        """Test TECH spoke directory exists."""
        tech_path = PROJECT_ROOT / "spokes" / "TECH"
        assert tech_path.exists(), "TECH spoke directory should exist"


class TestSpokesReadme:
    """Test spokes README files."""

    def test_physics_readme_exists(self):
        """Test PHYSICS README exists."""
        readme_path = PROJECT_ROOT / "spokes" / "PHYSICS" / "README.md"
        assert readme_path.exists(), "PHYSICS README should exist"

    def test_physics_readme_has_domains(self):
        """Test PHYSICS README contains domains."""
        readme_path = PROJECT_ROOT / "spokes" / "PHYSICS" / "README.md"
        content = readme_path.read_text(encoding="utf-8", errors="ignore")
        assert "Physique quantique" in content, "Should contain quantum physics"
        assert "Physique classique" in content, "Should contain classical physics"


class TestSpokesIntegration:
    """Test spokes integration capabilities."""

    def test_all_spokes_have_integration_examples(self):
        """Test all spokes have integration code examples."""
        spokes = ["PHYSICS", "MATH", "SCIENCE", "AI", "BIO", "TECH"]
        for spoke in spokes:
            readme_path = PROJECT_ROOT / "spokes" / spoke / "README.md"
            content = readme_path.read_text(encoding="utf-8", errors="ignore")
            assert "VersesSyncManager" in content, f"{spoke} should have integration example"

    def test_spokes_cover_all_domains(self):
        """Test spokes cover the required domains."""
        expected_domains = {
            "PHYSICS": ["quantum", "physics"],
            "MATH": ["tensor", "group"],
            "SCIENCE": ["molecular", "protein"],
            "AI": ["transformer", "attention"],
            "BIO": ["genetic", "metabolic"],
            "TECH": ["kubernetes", "security"],
        }
        for spoke, keywords in expected_domains.items():
            readme_path = PROJECT_ROOT / "spokes" / spoke / "README.md"
            content_raw = readme_path.read_text(encoding="utf-8", errors="ignore").lower()
            for keyword in keywords:
                assert keyword in content_raw, f"{spoke} README should mention {keyword}"