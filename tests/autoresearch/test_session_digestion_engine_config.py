# Test d'intégration minimale pour session autoresearch AcademicDigestionEngine (Phase 2)

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from NEXUS.autoresearch.contracts import SessionConfig


def test_digestion_engine_config_loading():
    """Test que la config YAML digestion_engine se charge sans erreur"""

    config_path = (
        Path(__file__).parent.parent
        / "configs"
        / "autoresearch"
        / "digestion_engine_optimization.yaml"
    )
    assert config_path.exists(), f"Config file not found: {config_path}"

    config = SessionConfig.from_yaml(config_path)
    assert config.repo_path is not None
    assert config.metric_command is not None
    assert config.safety_config is not None

    safety = config.safety_config
    assert safety.max_lines_changed_per_session == 500
    assert safety.max_files_changed_per_session == 50

    print("✅ Config digestion_engine chargée avec succès")
    return True


def test_digestion_engine_allowed_paths():
    """Test que les chemins autorisés sont corrects"""

    config_path = (
        Path(__file__).parent.parent
        / "configs"
        / "autoresearch"
        / "digestion_engine_optimization.yaml"
    )
    config = SessionConfig.from_yaml(config_path)

    assert "academic-digestion-engine.py" in config.constraints.allowed_paths

    print("✅ Chemins autorisés digestion_engine validés")
    return True


if __name__ == "__main__":
    print("🧪 Test d'intégration Phase 2 - AcademicDigestionEngine")

    try:
        test_digestion_engine_config_loading()
        test_digestion_engine_allowed_paths()
        print("✅ Tous les tests d'intégration digestion_engine réussis")
    except Exception as e:
        print(f"❌ Échec test: {e}")
        sys.exit(1)
