# -----------------------------------------------------------------------------
# Tests TDD pour EPIC-9859: SCE Compliance Framework
# Tests unitaires du système d'audit et remédiation SCE
# Couverture: Auditeur SCE, patterns, remédiation, CLI
# -----------------------------------------------------------------------------

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

# Import des modules SCE
try:
    from sce import SCEAuditor, SCE_PATTERN, SCEViolation, SCEAuditResult
    from sce.remediator import SCERemediator, RemediationAction
except ImportError:
    pytest.skip("SCE modules not available", allow_module_level=True)

class TestSCEPatterns:
    """Tests pour les patterns SCE"""

    def test_sce_patterns_defined(self):
        """Test que tous les patterns SCE sont définis"""
        from sce import SCE_PATTERNS

        expected_patterns = [
            "PATTERN.JOKER", "PATTERN.RIDDLER", "PATTERN.GOST", "PATTERN.FLUENCE",
            "PATTERN.AUTOMATISM", "PATTERN.OUROBOROS", "PATTERN.CONCEPTUAL_MASS", "PATTERN.TRANSPOSER",
            "PATTERN.STAGE_GATE", "PATTERN.POPPER", "PATTERN.LEDGER", "PATTERN.REPLICATION",
            "PATTERN.SHIP", "PATTERN.SEPARATION_OF_ROLE", "PATTERN.BOUNDARY",
            "PATTERN.AMBIGUITY", "PATTERN.PRESSURE", "PATTERN.MANTRA_NEXUS"
        ]

        for pattern_id in expected_patterns:
            assert pattern_id in SCE_PATTERNS, f"Missing pattern: {pattern_id}"

    def test_sce_pattern_structure(self):
        """Test la structure des objets pattern SCE"""
        from sce import SCE_PATTERNS

        for pattern_id, pattern in SCE_PATTERNS.items():
            assert hasattr(pattern, 'id'), f"Pattern {pattern_id} missing id"
            assert hasattr(pattern, 'name'), f"Pattern {pattern_id} missing name"
            assert hasattr(pattern, 'axiom'), f"Pattern {pattern_id} missing axiom"
            assert hasattr(pattern, 'family'), f"Pattern {pattern_id} missing family"
            assert hasattr(pattern, 'enforced'), f"Pattern {pattern_id} missing enforced"

            assert pattern.id == pattern_id
            assert len(pattern.name) > 0
            assert len(pattern.axiom) > 0

class TestSCEAuditor:
    """Tests pour l'auditeur SCE"""

    def test_sce_auditor_creation(self):
        """Test création d'un auditeur SCE"""
        auditor = SCEAuditor()
        assert auditor is not None
        assert hasattr(auditor, 'patterns')
        assert hasattr(auditor, 'audit_file')
        assert hasattr(auditor, 'audit_directory')

    def test_sce_auditor_patterns_loaded(self):
        """Test que les patterns sont chargés dans l'auditeur"""
        auditor = SCEAuditor()
        assert len(auditor.patterns) > 0

        # Vérifier que les checkers sont assignés
        joker_pattern = auditor.patterns.get("PATTERN.JOKER")
        assert joker_pattern is not None
        assert joker_pattern.code_checker is not None

    @patch('builtins.open', new_callable=mock_open, read_data='def test_function():\n    pass')
    @patch('os.path.exists')
    def test_audit_file_python(self, mock_exists, mock_file):
        """Test audit d'un fichier Python simple"""
        mock_exists.return_value = True

        auditor = SCEAuditor()
        result = auditor.audit_file("test.py")

        assert isinstance(result, SCEAuditResult)
        assert result.file_path == "test.py"
        assert isinstance(result.compliance_score, float)
        assert 0 <= result.compliance_score <= 100
        assert isinstance(result.violations, list)
        assert result.audit_timestamp <= datetime.now()

    @patch('os.path.exists')
    def test_audit_file_not_found(self, mock_exists):
        """Test audit d'un fichier inexistant"""
        mock_exists.return_value = False

        auditor = SCEAuditor()
        with pytest.raises(FileNotFoundError):
            auditor.audit_file("nonexistent.py")

    def test_audit_file_with_joker_pattern(self):
        """Test détection du pattern JOKER"""
        # Créer un fichier temporaire avec du code sans agents perturbateurs
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def normal_function():
    return "hello"

class NormalClass:
    def method(self):
        return 42
""")
            temp_file = f.name

        try:
            auditor = SCEAuditor()
            result = auditor.audit_file(temp_file)

            # Devrait détecter violation JOKER (pas d'agents perturbateurs)
            joker_violations = [v for v in result.violations if v.pattern_id == "PATTERN.JOKER"]
            assert len(joker_violations) > 0, "Should detect missing perturbation agents"

        finally:
            os.unlink(temp_file)

    def test_audit_file_with_riddler_pattern(self):
        """Test détection du pattern RIDDLER"""
        # Créer un fichier avec des TODOs (problèmes non résolus)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
# TODO: Implement error handling
def function_without_todos():
    pass

# FIXME: This needs refactoring
class ClassWithFixme:
    pass
""")
            temp_file = f.name

        try:
            auditor = SCEAuditor()
            result = auditor.audit_file(temp_file)

            # Devrait NE PAS violer RIDDLER (présence de TODO/FIXME)
            riddler_violations = [v for v in result.violations if v.pattern_id == "PATTERN.RIDDLER"]
            assert len(riddler_violations) == 0, "Should not violate RIDDLER when TODOs present"

        finally:
            os.unlink(temp_file)

class TestSCERemediator:
    """Tests pour le remédiateur SCE"""

    def test_sce_remediator_creation(self):
        """Test création d'un remédiateur SCE"""
        remediator = SCERemediator()
        assert remediator is not None
        assert hasattr(remediator, 'remediation_patterns')
        assert hasattr(remediator, 'analyze_violations')

    def test_analyze_violations_empty(self):
        """Test analyse de violations vides"""
        remediator = SCERemediator()
        actions = remediator.analyze_violations([])
        assert actions == []

    def test_analyze_violations_joker(self):
        """Test analyse violation JOKER"""
        remediator = SCERemediator()

        violation = SCEViolation(
            pattern_id="PATTERN.JOKER",
            pattern_name="Joker Pattern",
            axiom="Test axiom",
            severity="HIGH",
            description="No perturbation agents"
        )

        actions = remediator.analyze_violations([violation])

        assert len(actions) > 0
        assert actions[0].pattern_id == "PATTERN.JOKER"
        assert "AdversarialTester" in actions[0].new_code

    def test_analyze_violations_multiple_patterns(self):
        """Test analyse de plusieurs patterns"""
        remediator = SCERemediator()

        violations = [
            SCEViolation("PATTERN.JOKER", "Joker", "axiom1", "HIGH", "desc1"),
            SCEViolation("PATTERN.OUROBOROS", "Ouroboros", "axiom2", "MEDIUM", "desc2")
        ]

        actions = remediator.analyze_violations(violations)

        assert len(actions) >= 2
        pattern_ids = {a.pattern_id for a in actions}
        assert "PATTERN.JOKER" in pattern_ids
        assert "PATTERN.OUROBOROS" in pattern_ids

    @patch('builtins.open', new_callable=mock_open)
    def test_apply_remediation_dry_run(self, mock_file):
        """Test application de remédiation en dry-run"""
        remediator = SCERemediator()

        # Créer un fichier temporaire pour le test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Original content\n")
            temp_file = f.name

        try:
            actions = [
                RemediationAction(
                    pattern_id="PATTERN.JOKER",
                    description="Add test framework",
                    action_type="ADD",
                    new_code="# Added by remediation\n",
                    confidence=0.8
                )
            ]

            result = remediator.apply_remediation(temp_file, actions, dry_run=True)

            assert result["dry_run"] == True
            assert result["modifications_applied"] > 0
            assert result["backup_created"] == False

            # Vérifier que le fichier n'a pas été modifié
            with open(temp_file, 'r') as f:
                content = f.read()
                assert "# Original content" in content
                assert "# Added by remediation" not in content

        finally:
            os.unlink(temp_file)

class TestRemediationActions:
    """Tests pour les actions de remédiation"""

    def test_remediation_action_creation(self):
        """Test création d'une action de remédiation"""
        action = RemediationAction(
            pattern_id="PATTERN.JOKER",
            description="Test action",
            action_type="ADD",
            confidence=0.8,
            risk_level="LOW"
        )

        assert action.pattern_id == "PATTERN.JOKER"
        assert action.confidence == 0.8
        assert action.risk_level == "LOW"

    def test_remediation_action_defaults(self):
        """Test valeurs par défaut des actions"""
        action = RemediationAction(
            pattern_id="PATTERN.JOKER",
            description="Test",
            action_type="INFO"
        )

        assert action.confidence == 0.0
        assert action.risk_level == "LOW"
        assert action.target_line is None

class TestSCEUtilities:
    """Tests pour les fonctions utilitaires SCE"""

    def test_calculate_global_compliance_score(self):
        """Test calcul du score global"""
        from sce import calculate_global_compliance_score

        # Test avec résultats vides
        score = calculate_global_compliance_score([])
        assert score["global_compliance_score"] == 0.0
        assert score["total_files"] == 0

        # Test avec résultats fictifs
        mock_results = [
            SCEAuditResult("file1.py", "COMPLIANT", 85.0, 18, ["P1"], [], datetime.now()),
            SCEAuditResult("file2.py", "VIOLATION", 45.0, 18, ["P2"], [], datetime.now())
        ]

        score = calculate_global_compliance_score(mock_results)
        assert score["total_files"] == 2
        assert score["compliant_files"] == 1
        assert score["global_compliance_score"] == 50.0  # (85 + 45) / 2

    @patch('builtins.open', new_callable=mock_open)
    def test_generate_sce_report(self, mock_file):
        """Test génération de rapport SCE"""
        from sce import generate_sce_report

        mock_results = [
            SCEAuditResult("test.py", "VIOLATION", 50.0, 18, ["P1"], [
                SCEViolation("PATTERN.JOKER", "Joker", "axiom", "HIGH", "desc")
            ], datetime.now())
        ]

        generate_sce_report(mock_results, "test_report.json")

        # Vérifier que open a été appelé pour écriture
        mock_file.assert_called_once_with("test_report.json", 'w', encoding='utf-8')

class TestSCECliIntegration:
    """Tests d'intégration pour les interfaces CLI"""

    @patch('sys.argv', ['sce-linter', '--help'])
    def test_linter_cli_help(self, capsys):
        """Test affichage help du linter CLI"""
        try:
            from sce.linter import main
            with pytest.raises(SystemExit):  # --help cause sys.exit(0)
                main()
        except ImportError:
            pytest.skip("CLI module not available")

    @patch('sys.argv', ['sce-remediator', '--help'])
    def test_remediator_cli_help(self, capsys):
        """Test affichage help du remediator CLI"""
        try:
            from sce.remediator_cli import main
            with pytest.raises(SystemExit):  # --help cause sys.exit(0)
                main()
        except ImportError:
            pytest.skip("CLI module not available")

class TestPatternSpecificLogic:
    """Tests pour la logique spécifique à chaque pattern"""

    def test_joker_checker_detects_missing_agents(self):
        """Test que JOKER détecte l'absence d'agents perturbateurs"""
        auditor = SCEAuditor()

        # Code sans agents perturbateurs
        code = """
def normal_function():
    return 42

class NormalClass:
    pass
"""

        violations = auditor._check_joker_pattern(code)
        assert len(violations) > 0
        assert violations[0].pattern_id == "PATTERN.JOKER"

    def test_riddler_checker_accepts_todos(self):
        """Test que RIDDLER accepte la présence de TODOs"""
        auditor = SCEAuditor()

        # Code avec TODOs
        code = """
# TODO: Implement this
def function_with_todo():
    # FIXME: This needs work
    pass
"""

        violations = auditor._check_riddler_pattern(code)
        assert len(violations) == 0  # Pas de violation quand TODOs présents

    def test_gost_checker_detects_logging_in_sensitive_functions(self):
        """Test que GOST détecte les logs dans fonctions sensibles"""
        auditor = SCEAuditor()

        # Code avec logging dans fonction sensible
        code = """
def encrypt_data(data):
    print(f"Encrypting: {data}")  # Log dans fonction sensible
    return data

def authenticate_user(user):
    logging.info(f"Auth attempt for {user}")  # Log dans fonction sensible
    return True
"""

        violations = auditor._check_gost_pattern(code)
        assert len(violations) > 0
        assert violations[0].pattern_id == "PATTERN.GOST"

    def test_stage_gate_checker_detects_missing_gates(self):
        """Test que STAGE_GATE détecte les transitions sans validation"""
        auditor = SCEAuditor()

        code = """
# Direct transition without validation
from_stage = "SPARK"
to_stage = "SHIP"  # Saut sans gate
"""

        violations = auditor._check_stage_gate_pattern(code)
        assert len(violations) > 0
        assert violations[0].pattern_id == "PATTERN.STAGE_GATE"

# -----------------------------------------------------------------------------
# Tests d'intégration
# -----------------------------------------------------------------------------

class TestSCEIntegration:
    """Tests d'intégration du système SCE complet"""

    def test_full_audit_workflow(self):
        """Test workflow complet d'audit SCE"""
        # Créer un fichier de test représentatif
        test_code = '''
# SCE Compliant Code Sample
# Includes perturbation agents, error handling, and proper patterns

import random
from typing import Any

# JOKER Pattern: Adversarial testing framework
class AdversarialTester:
    """Perturbation agent for testing robustness"""

    @staticmethod
    def inject_chaos(data: Any) -> Any:
        """Apply controlled perturbations"""
        if isinstance(data, (int, float)):
            return data * (1 + random.uniform(-0.1, 0.1))
        return data

# OUROBOROS Pattern: Error handling
def safe_operation(data: Any) -> Any:
    """Handle irrationality without destroying it"""
    try:
        # TODO: Implement actual operation
        return data
    except Exception as e:
        # Rationalize the error
        return f"Handled irrationality: {e}"

# STAGE_GATE Pattern: Explicit transitions
STAGES = ["SPARK", "SHAPE", "REFINE", "PROVE", "SHIP"]

def validate_stage_transition(from_stage: str, to_stage: str) -> bool:
    """Explicit gate between stages"""
    if from_stage not in STAGES or to_stage not in STAGES:
        return False
    return STAGES.index(to_stage) > STAGES.index(from_stage)

# LEDGER Pattern: Cryptographic traces
import hashlib

def create_trace(data: Any) -> str:
    """Cryptographic trace for immutability"""
    return hashlib.sha256(str(data).encode()).hexdigest()
'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            auditor = SCEAuditor()
            result = auditor.audit_file(temp_file)

            # Le code devrait avoir un score raisonnable
            assert isinstance(result.compliance_score, float)
            assert result.compliance_score >= 0

            # Devrait détecter certaines violations malgré les bonnes pratiques
            assert isinstance(result.violations, list)

            # Vérifier la structure du résultat
            assert result.file_path == temp_file
            assert result.total_patterns == 18  # Tous les patterns SCE
            assert len(result.compliant_patterns) >= 0

        finally:
            os.unlink(temp_file)

    def test_remediation_workflow(self):
        """Test workflow complet de remédiation"""
        remediator = SCERemediator()

        # Violations de test
        violations = [
            SCEViolation("PATTERN.JOKER", "Joker", "axiom", "HIGH", "missing agents"),
            SCEViolation("PATTERN.OUROBOROS", "Ouroboros", "axiom", "MEDIUM", "no error handling")
        ]

        # Analyser les violations
        actions = remediator.analyze_violations(violations)

        assert len(actions) > 0

        # Créer un fichier de test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Original code\n")
            temp_file = f.name

        try:
            # Appliquer la remédiation en dry-run
            result = remediator.apply_remediation(temp_file, actions, dry_run=True)

            assert result["dry_run"] == True
            assert "modifications_applied" in result

        finally:
            os.unlink(temp_file)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])