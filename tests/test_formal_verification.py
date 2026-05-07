import pytest
import json
import os
import sys
from unittest.mock import patch, mock_open

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

# Assuming z3 is installed, otherwise skip
z3_available = True
try:
    from z3 import *
except ImportError:
    z3_available = False


@pytest.mark.skipif(not z3_available, reason="Z3 not available")
def test_citizen_hierarchy_proof():
    """Test basic Z3 proof for citizen hierarchy"""
    from scripts.formal_verification_z3 import create_citizen_hierarchy_proof

    result = create_citizen_hierarchy_proof()
    assert result is True, "Citizen hierarchy proof should pass"


def test_load_ontology_constraints():
    """Test loading constraints from ontology JSON"""
    from scripts.formal_verification_z3 import load_ontology_constraints

    # Mock ontology data
    mock_data = {
        "TestTerm": {
            "constraints": ["latency ≤ 5000ms", "resource_usage ≤ system_limits"]
        }
    }

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        constraints = load_ontology_constraints("mock_path")
        assert len(constraints) == 2
        assert "latency ≤ 5000ms" in constraints


def test_main_execution():
    """Test main function generates report"""
    from scripts.formal_verification_z3 import main

    with (
        patch(
            "scripts.formal_verification_z3.load_ontology_constraints", return_value=[]
        ),
        patch("builtins.open", mock_open()) as mock_file,
    ):
        main()

        # Check if report file was written
        mock_file.assert_called_once_with("formal_verification_report.json", "w")


def test_report_structure():
    """Test generated report has correct structure"""
    report_path = "formal_verification_report.json"

    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            report = json.load(f)

        assert "timestamp" in report
        assert "proofs_run" in report
        assert "results" in report
        assert "execution_time_ms" in report

        assert "citizen_hierarchy" in report["results"]
    else:
        pytest.skip("Report file not generated")
