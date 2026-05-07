#!/usr/bin/env python3
"""
Tests Phase 2 - EPIC 9033: dbt Integration
IntentHash: 0xTEST_PHASE2_DBT_INTEGRATION_20260426
"""

import unittest
import os
import tempfile
import json
from pathlib import Path


class TestPhase2DbtIntegration(unittest.TestCase):
    """Tests pour l'intégration dbt de Phase 2"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.project_root = Path(__file__).parent.parent
        self.dbt_dir = self.project_root / "dbt"

    def test_dbt_directory_structure(self):
        """Test que la structure dbt est correcte"""
        self.assertTrue(self.dbt_dir.exists(), "Dossier dbt manquant")

        required_files = [
            "profiles.yml",
            "models/daily_analysis_count.sql",
            "models/top_patterns.sql",
            "models/avg_performance.sql"
        ]

        for file_path in required_files:
            full_path = self.dbt_dir / file_path
            self.assertTrue(full_path.exists(),
                          f"Fichier dbt manquant: {file_path}")

    def test_dbt_profiles_config(self):
        """Test que la configuration profiles.yml est valide"""
        profiles_path = self.dbt_dir / "profiles.yml"

        self.assertTrue(profiles_path.exists(), "profiles.yml manquant")

        with open(profiles_path) as f:
            import yaml
            try:
                config = yaml.safe_load(f)
                self.assertIn("nexus", config, "Profil nexus manquant")
                self.assertIn("target", config["nexus"], "Target manquant")
                self.assertIn("dev", config["nexus"]["outputs"], "Output dev manquant")
            except yaml.YAMLError as e:
                self.fail(f"profiles.yml invalide: {e}")

    def test_dbt_models_syntax(self):
        """Test que les modèles SQL ont une syntaxe basique valide"""
        model_files = [
            "models/daily_analysis_count.sql",
            "models/top_patterns.sql",
            "models/avg_performance.sql"
        ]

        for model_file in model_files:
            with self.subTest(model=model_file):
                model_path = self.dbt_dir / model_file
                self.assertTrue(model_path.exists(),
                              f"Modèle manquant: {model_file}")

                with open(model_path) as f:
                    sql_content = f.read()

                # Tests basiques de syntaxe SQL
                self.assertIn("SELECT", sql_content.upper(),
                            f"Pas de SELECT dans {model_file}")
                self.assertIn("FROM", sql_content.upper(),
                            f"Pas de FROM dans {model_file}")

    def test_dbt_config_file(self):
        """Test que le fichier de config dbt existe"""
        config_path = self.project_root / "config" / "phase2_dbt_config.json"
        self.assertTrue(config_path.exists(),
                       "Config dbt phase2 manquante")

        with open(config_path) as f:
            config = json.load(f)

        required_fields = ["name", "version", "profile", "models"]
        for field in required_fields:
            self.assertIn(field, config,
                         f"Champ requis manquant dans config dbt: {field}")

    def test_dbt_project_structure(self):
        """Test que la structure projet dbt est complète"""
        required_dirs = ["models", "target", "logs"]
        for dir_name in required_dirs:
            dir_path = self.dbt_dir / dir_name
            # Ne pas tester target/logs qui peuvent ne pas exister
            if dir_name == "models":
                self.assertTrue(dir_path.exists(),
                              f"Dossier dbt requis manquant: {dir_name}")


if __name__ == "__main__":
    unittest.main()