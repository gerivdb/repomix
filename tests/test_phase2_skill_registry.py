#!/usr/bin/env python3
"""
Tests Phase 2 - EPIC 9034: Skill Registry
IntentHash: 0xTEST_PHASE2_SKILL_REGISTRY_20260426
"""

import unittest
import json
import os
from pathlib import Path


class TestPhase2SkillRegistry(unittest.TestCase):
    """Tests pour le registre skills de Phase 2"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.project_root = Path(__file__).parent.parent
        self.skills_dir = self.project_root / "skills"
        self.registry_file = self.skills_dir / "skills_registry.json"

    def test_skill_directory_structure(self):
        """Test que la structure skills est correcte"""
        self.assertTrue(self.skills_dir.exists(), "Dossier skills manquant")

        required_items = ["templates/skill_template.md", "skills_registry.json"]

        for item in required_items:
            item_path = self.skills_dir / item
            self.assertTrue(item_path.exists(), f"Élément skills manquant: {item}")

    def test_skill_registry_format(self):
        """Test que le registre skills a le bon format"""
        self.assertTrue(self.registry_file.exists(), "Registre skills manquant")

        with open(self.registry_file) as f:
            registry = json.load(f)

        required_fields = ["version", "last_updated", "skills"]
        for field in required_fields:
            self.assertIn(
                field, registry, f"Champ requis manquant dans registry: {field}"
            )

        # Vérifier que skills n'est pas vide
        self.assertGreater(len(registry["skills"]), 0, "Aucun skill dans le registre")

    def test_skill_template_exists(self):
        """Test que le template skill existe et est valide"""
        template_path = self.skills_dir / "templates" / "skill_template.md"
        self.assertTrue(template_path.exists(), "Template skill manquant")

        with open(template_path) as f:
            template_content = f.read()

        # Vérifier contenu minimal du template
        required_keywords = ["# SKILL:", "CAPACIT", "ENTR", "SORTIE", "GARANTIES"]

        for keyword in required_keywords:
            self.assertIn(
                keyword, template_content, f"Mot-clé manquant dans template: {keyword}"
            )

    def test_skill_config_validation(self):
        """Test que les configurations skill sont valides"""
        config_path = self.project_root / "config" / "phase2_skill_registry.json"
        self.assertTrue(config_path.exists(), "Config skill registry manquante")

        with open(config_path) as f:
            config = json.load(f)

        # Vérifier structure
        self.assertIn("skills", config, "Section skills manquante")
        self.assertIn("validation_rules", config, "Règles validation manquantes")

        # Vérifier chaque skill
        for skill_name, skill_config in config["skills"].items():
            with self.subTest(skill=skill_name):
                required_skill_fields = ["path", "version", "status", "capabilities"]
                for field in required_skill_fields:
                    self.assertIn(
                        field,
                        skill_config,
                        f"Champ requis manquant pour skill {skill_name}: {field}",
                    )

                # Vérifier version format
                import re

                version_pattern = r"^\d+\.\d+\.\d+$"
                self.assertRegex(
                    skill_config["version"],
                    version_pattern,
                    f"Version invalide pour skill {skill_name}",
                )

    def test_skill_capabilities_format(self):
        """Test que les capabilities respectent le format"""
        with open(self.registry_file) as f:
            registry = json.load(f)

        import re

        capability_pattern = r"^[a-z_]+$"

        for skill_name, skill_info in registry["skills"].items():
            with self.subTest(skill=skill_name):
                capabilities = skill_info["capabilities"]
                self.assertIsInstance(
                    capabilities, list, f"Capabilities pas une liste pour {skill_name}"
                )

                for capability in capabilities:
                    self.assertRegex(
                        capability,
                        capability_pattern,
                        f"Capability invalide '{capability}' pour {skill_name}",
                    )


if __name__ == "__main__":
    unittest.main()
