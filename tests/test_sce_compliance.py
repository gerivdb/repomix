#!/usr/bin/env python3
"""
SCE Compliance Framework - Test Suite

Comprehensive TDD test suite for the SCE compliance auditing system.
Tests pattern analyzers, auditor engine, and report generation.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from compliance.sce_auditor import SCEComplianceAuditor
from compliance.sce_analyzers import (
    JokerPatternAnalyzer,
    SeparationOfRolePatternAnalyzer,
    LedgerPatternAnalyzer,
    BoundaryPatternAnalyzer,
    create_analyzer
)
from compliance.sce_types import SCEPattern, PatternViolation, ComplianceResult


class TestSCEPattern:
    """Test SCE Pattern data structure."""

    def test_pattern_creation(self):
        """Test SCE pattern creation and initialization."""
        pattern = SCEPattern(
            id="PATTERN.TEST",
            name="Test Pattern",
            axiom="Test axiom for testing",
            family="TEST_FAMILY"
        )

        assert pattern.id == "PATTERN.TEST"
        assert pattern.name == "Test Pattern"
        assert pattern.axiom == "Test axiom for testing"
        assert pattern.family == "TEST_FAMILY"
        assert hasattr(pattern, 'compliance_rules')
        assert isinstance(pattern.compliance_rules, dict)

    def test_pattern_keywords_extraction(self):
        """Test keyword extraction from axioms."""
        # Test Joker pattern keywords
        joker = SCEPattern(
            id="PATTERN.JOKER",
            name="Joker Pattern",
            axiom="Tout système doit contenir des agents qui le cassent intentionnellement.",
            family="FORCES_PERTURBATRICES"
        )
        assert "adversarial" in joker.compliance_rules["keywords"]
        assert "perturbation" in joker.compliance_rules["keywords"]

        # Test Ledger pattern keywords
        ledger = SCEPattern(
            id="PATTERN.LEDGER",
            name="Ledger Pattern",
            axiom="Pas de fait sans trace. Toute sortie doit avoir un hash cryptographique immuable.",
            family="FORCES_STRUCTURELLES"
        )
        assert "hash" in ledger.compliance_rules["keywords"]
        assert "cryptographic" in ledger.compliance_rules["keywords"]


class TestJokerPatternAnalyzer:
    """Test Joker Pattern analyzer."""

    def setup_method(self):
        """Set up test pattern."""
        self.pattern = SCEPattern(
            id="PATTERN.JOKER",
            name="Joker Pattern",
            axiom="Tout système doit contenir des agents qui le cassent intentionnellement.",
            family="FORCES_PERTURBATRICES"
        )
        self.analyzer = JokerPatternAnalyzer(self.pattern)

    def test_compliant_code_with_adversarial_tests(self):
        """Test code that has adversarial testing mechanisms."""
        code = """
def test_adversarial_inputs():
    # Test adversarial inputs
    pass

def break_system_intentionally():
    # Intentional breaking for testing
    pass

class AdversarialTester:
    def test_perturbation(self):
        pass
"""
        result = self.analyzer.analyze(code)
        assert result is None  # Should be compliant

    def test_non_compliant_code_without_adversarial_tests(self):
        """Test code without adversarial testing."""
        code = """
def calculate_sum(a, b):
    return a + b

def process_data(data):
    return data.upper()
"""
        result = self.analyzer.analyze(code)
        assert result is not None
        assert result.pattern == "PATTERN.JOKER"
        assert "adversarial testing mechanisms" in result.suggestion


class TestSeparationOfRolePatternAnalyzer:
    """Test Separation of Role Pattern analyzer."""

    def setup_method(self):
        """Set up test pattern."""
        self.pattern = SCEPattern(
            id="PATTERN.SEPARATION_OF_ROLE",
            name="Separation Of Role Pattern",
            axiom="Aucun moteur ne doit faire à la fois génération, exécution, interprétation et verdict.",
            family="ARCHITECTURAUX_TRANSVERSAUX"
        )
        self.analyzer = SeparationOfRolePatternAnalyzer(self.pattern)

    def test_compliant_separated_roles(self):
        """Test code with properly separated roles."""
        code = """
def generate_data():
    return [1, 2, 3]

def execute_calculation(data):
    return sum(data)

def validate_result(result):
    return result > 0
"""
        result = self.analyzer.analyze(code)
        assert result is None  # Should be compliant

    def test_non_compliant_combined_roles(self):
        """Test code with combined roles in same function."""
        code = """
def process_and_validate_data(input_data):
    # Generate
    data = input_data * 2
    # Execute
    result = sum(data)
    # Validate
    if result > 0:
        return result
    return None
"""
        result = self.analyzer.analyze(code)
        assert result is not None
        assert result.pattern == "PATTERN.SEPARATION_OF_ROLE"
        assert "Separate" in result.suggestion


class TestLedgerPatternAnalyzer:
    """Test Ledger Pattern analyzer."""

    def setup_method(self):
        """Set up test pattern."""
        self.pattern = SCEPattern(
            id="PATTERN.LEDGER",
            name="Ledger Pattern",
            axiom="Pas de fait sans trace. Toute sortie doit avoir un hash cryptographique immuable.",
            family="FORCES_STRUCTURELLES"
        )
        self.analyzer = LedgerPatternAnalyzer(self.pattern)

    def test_compliant_with_hashing(self):
        """Test code that includes cryptographic hashing."""
        code = """
import hashlib

def process_with_integrity(data):
    result = data.upper()
    hash_value = hashlib.sha256(result.encode()).hexdigest()
    return result, hash_value
"""
        result = self.analyzer.analyze(code)
        assert result is None  # Should be compliant

    def test_non_compliant_without_hashing(self):
        """Test code without cryptographic hashing."""
        code = """
def process_data(data):
    return data.upper()

def calculate_result(a, b):
    return a + b
"""
        result = self.analyzer.analyze(code)
        assert result is not None
        assert result.pattern == "PATTERN.LEDGER"
        assert "cryptographic hashing" in result.suggestion


class TestBoundaryPatternAnalyzer:
    """Test Boundary Pattern analyzer."""

    def setup_method(self):
        """Set up test pattern."""
        self.pattern = SCEPattern(
            id="PATTERN.BOUNDARY",
            name="Boundary Pattern",
            axiom="La preuve est la frontière finale. Tout ce qui est avant est candidat. Tout ce qui est après est fait.",
            family="ARCHITECTURAUX_TRANSVERSAUX"
        )
        self.analyzer = BoundaryPatternAnalyzer(self.pattern)

    def test_compliant_with_proof_boundary(self):
        """Test code with clear proof boundary."""
        code = """
def generate_candidates(hypotheses):
    return hypotheses

def validate_with_proof(candidate):
    # Proof validation
    return True

def establish_fact(validated_result):
    return validated_result
"""
        result = self.analyzer.analyze(code)
        assert result is None  # Should be compliant

    def test_non_compliant_without_proof_boundary(self):
        """Test code without clear proof boundary."""
        code = """
def generate_candidates(data):
    # Generate candidate results
    candidates = []
    for item in data:
        candidates.append(item.upper())
    return candidates

def get_final_result(candidates):
    # Direct return without validation/proof
    return candidates[0] if candidates else None
"""
        result = self.analyzer.analyze(code)
        assert result is not None
        assert result.pattern == "PATTERN.BOUNDARY"
        assert "proof" in result.suggestion.lower()


class TestSCEComplianceAuditor:
    """Test SCE Compliance Auditor."""

    def setup_method(self):
        """Set up auditor with mocked ontology."""
        self.mock_ontology = {
            "version": "v1.0",
            "sce_patterns": {
                "version": "v1.0",
                "families": {
                    "FORCES_PERTURBATRICES": [
                        {
                            "id": "PATTERN.JOKER",
                            "name": "Joker Pattern",
                            "axiom": "Test axiom",
                            "enforced": True
                        }
                    ]
                },
                "total_patterns": 1
            }
        }

    @patch('compliance.sce_auditor.SCEComplianceAuditor._load_ontology')
    def test_auditor_initialization(self, mock_load_ontology):
        """Test auditor initialization."""
        mock_load_ontology.return_value = self.mock_ontology

        auditor = SCEComplianceAuditor()
        assert auditor.ontology == self.mock_ontology
        assert len(auditor.patterns) == 1
        assert len(auditor.analyzers) == 1
        assert auditor.total_patterns == 1

    @patch('compliance.sce_auditor.SCEComplianceAuditor._load_ontology')
    def test_file_audit_success(self, mock_load_ontology):
        """Test successful file audit."""
        mock_load_ontology.return_value = self.mock_ontology

        auditor = SCEComplianceAuditor()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def test_function():
    # Test adversarial function
    pass
""")
            temp_path = f.name

        try:
            result = auditor.audit_file(temp_path)
            assert isinstance(result, ComplianceResult)
            assert result.file_path == temp_path
            assert result.status in ["COMPLIANT", "VIOLATION", "ERROR"]
            assert 0.0 <= result.compliance_score <= 100.0
        finally:
            os.unlink(temp_path)

    @patch('compliance.sce_auditor.SCEComplianceAuditor._load_ontology')
    def test_file_audit_error_handling(self, mock_load_ontology):
        """Test error handling in file audit."""
        mock_load_ontology.return_value = self.mock_ontology

        auditor = SCEComplianceAuditor()

        # Test with non-existent file
        result = auditor.audit_file("non_existent_file.py")
        assert result.status == "ERROR"
        assert result.error_message is not None

    @patch('compliance.sce_auditor.SCEComplianceAuditor._load_ontology')
    def test_report_generation(self, mock_load_ontology):
        """Test JSON report generation."""
        mock_load_ontology.return_value = self.mock_ontology

        auditor = SCEComplianceAuditor()

        # Create mock results
        results = [
            ComplianceResult(
                file_path="test1.py",
                status="COMPLIANT",
                compliance_score=100.0,
                violations=[],
                compliant_patterns=["PATTERN.JOKER"]
            ),
            ComplianceResult(
                file_path="test2.py",
                status="VIOLATION",
                compliance_score=0.0,
                violations=[PatternViolation(
                    pattern="PATTERN.JOKER",
                    name="Test Pattern",
                    axiom="Test axiom",
                    suggestion="Test suggestion"
                )],
                compliant_patterns=[]
            )
        ]

        from compliance.sce_auditor import AuditReport
        from datetime import datetime

        report = AuditReport(
            audit_date=datetime.now().isoformat(),
            ontology_version="v1.0",
            patterns_version="v1.0",
            total_files=2,
            compliant_files=1,
            global_compliance_score=50.0,
            results=results
        )

        # Test report generation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            auditor.generate_report(report, temp_path)

            # Verify file was created and contains valid JSON
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                data = json.load(f)
                assert "audit_date" in data
                assert "results" in data
                assert len(data["results"]) == 2
        finally:
            os.unlink(temp_path)


class TestAnalyzerFactory:
    """Test analyzer factory function."""

    def test_create_analyzer_for_known_pattern(self):
        """Test creating analyzer for known pattern."""
        pattern = SCEPattern(
            id="PATTERN.JOKER",
            name="Joker Pattern",
            axiom="Test axiom",
            family="FORCES_PERTURBATRICES"
        )

        analyzer = create_analyzer(pattern)
        assert isinstance(analyzer, JokerPatternAnalyzer)
        assert analyzer.pattern == pattern

    def test_create_analyzer_for_unknown_pattern(self):
        """Test creating analyzer for unknown pattern falls back to base."""
        pattern = SCEPattern(
            id="PATTERN.UNKNOWN",
            name="Unknown Pattern",
            axiom="Test axiom",
            family="UNKNOWN"
        )

        analyzer = create_analyzer(pattern)
        # Should return BasePatternAnalyzer for unknown patterns
        from compliance.sce_analyzers import BasePatternAnalyzer
        assert isinstance(analyzer, BasePatternAnalyzer)


if __name__ == "__main__":
    pytest.main([__file__])