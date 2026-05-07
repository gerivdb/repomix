# Test d'intégration minimale pour session autoresearch NexusOntologyService (Phase 2)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from NEXUS.autoresearch.contracts import SessionConfig


def test_ontology_service_config_loading():
    """Test que la config YAML ontology_service se charge sans erreur"""

    config_path = (
        Path(__file__).parent.parent
        / "configs"
        / "autoresearch"
        / "ontology_service_optimization.yaml"
    )
    assert config_path.exists(), f"Config file not found: {config_path}"

    config = SessionConfig.from_yaml(config_path)
    assert config.repo_path is not None
    assert config.metric_command is not None
    assert config.safety_config is not None

    safety = config.safety_config
    assert safety.max_lines_changed_per_session == 500
    assert safety.max_files_changed_per_session == 50

    print("✅ Config ontology_service chargée avec succès")
    return True


def test_ontology_service_allowed_paths():
    """Test que les chemins autorisés sont corrects"""

    config_path = (
        Path(__file__).parent.parent
        / "configs"
        / "autoresearch"
        / "ontology_service_optimization.yaml"
    )
    config = SessionConfig.from_yaml(config_path)

    assert "nexus_ontology_api_v0_1_0.py" in config.constraints.allowed_paths

    print("✅ Chemins autorisés ontology_service validés")
    return True


if __name__ == "__main__":
    print("🧪 Test d'intégration Phase 2 - NexusOntologyService")

    try:
        test_ontology_service_config_loading()
        test_ontology_service_allowed_paths()
        print("✅ Tous les tests d'intégration ontology_service réussis")
    except Exception as e:
        print(f"❌ Échec test: {e}")
        sys.exit(1)
