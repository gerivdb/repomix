# Test d'intégration minimale pour session autoresearch NormativeEngine (Phase 2)

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

from NEXUS.autoresearch.contracts import SessionConfig
from NEXUS.autoresearch.config_validator import ConfigValidator


def test_normative_engine_config_loading():
    """Test que la config YAML normative_engine se charge sans erreur"""

    # Chemin vers la config
    config_path = (
        Path(__file__).parent.parent
        / "configs"
        / "autoresearch"
        / "normative_engine_optimization.yaml"
    )

    # Vérifier que le fichier existe
    assert config_path.exists(), f"Config file not found: {config_path}"

    # Charger la config via SessionConfig
    config = SessionConfig.from_yaml(config_path)

    # Vérifications basiques
    assert config.repo_path is not None
    assert config.metric_command is not None
    assert config.budget is not None
    assert config.safety_config is not None

    # Vérifications safety config
    safety = config.safety_config
    assert safety.max_lines_changed_per_session == 500
    assert safety.max_files_changed_per_session == 50
    assert ".git" in safety.protected_paths
    assert "__pycache__" in safety.protected_paths

    print("✅ Config normative_engine chargée avec succès")
    return True


def test_normative_engine_config_validation():
    """Test que la config passe la validation"""

    config_path = (
        Path(__file__).parent.parent
        / "configs"
        / "autoresearch"
        / "normative_engine_optimization.yaml"
    )
    config = SessionConfig.from_yaml(config_path)

    # Valider la config
    validator = ConfigValidator()
    errors = validator.validate_session_config(config)

    assert len(errors) == 0, f"Config validation errors: {errors}"

    print("✅ Config normative_engine validée avec succès")
    return True


def test_normative_engine_allowed_paths():
    """Test que les chemins autorisés sont corrects"""

    config_path = (
        Path(__file__).parent.parent
        / "configs"
        / "autoresearch"
        / "normative_engine_optimization.yaml"
    )
    config = SessionConfig.from_yaml(config_path)

    # Vérifier les chemins autorisés
    assert "engines/normative_engine/norm_engine.py" in config.constraints.allowed_paths

    print("✅ Chemins autorisés normative_engine validés")
    return True


if __name__ == "__main__":
    print("🧪 Test d'intégration Phase 2 - NormativeEngine")

    try:
        test_normative_engine_config_loading()
        test_normative_engine_config_validation()
        test_normative_engine_allowed_paths()

        print("✅ Tous les tests d'intégration normative_engine réussis")

    except Exception as e:
        print(f"❌ Échec test: {e}")
        sys.exit(1)
