#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests TDD pour ENGINE.DEV
3 tests par mthode publique
"""

import pytest
from unittest.mock import MagicMock, patch
from engines.dev_engine import DevEngine


class TestDevEngine:
    """Tests TDD pour DevEngine"""

    @pytest.fixture
    def dev_engine(self):
        """Fixture pour crer une instance de DevEngine"""
        return DevEngine()

    def test_analyze_codebase_basic_functionality(self, dev_engine):
        """Test 1: analyze_codebase() - Fonctionnalit basique"""
        structure = {
            "patterns": ["mvc", "observer"],
            "complexity": 5.2,
            "lines_of_code": 1500,
            "modules": ["auth", "payment", "ui"]
        }

        result = dev_engine.analyze_codebase(structure)

        assert "architecture_patterns" in result
        assert "complexity_metrics" in result
        assert "maintainability_score" in result
        assert "recommendations" in result
        assert "zops_compliance" in result
        assert isinstance(result["architecture_patterns"], list)
        assert isinstance(result["complexity_metrics"], dict)

    def test_analyze_codebase_pattern_detection(self, dev_engine):
        """Test 2: analyze_codebase() - Dtection de patterns"""
        structure_with_patterns = {
            "layers": True,
            "microservices": True,
            "event_driven": False
        }

        result = dev_engine.analyze_codebase(structure_with_patterns)

        assert "Layered Architecture" in result["architecture_patterns"]
        assert "Microservices" in result["architecture_patterns"]

    def test_analyze_codebase_metrics_calculation(self, dev_engine):
        """Test 3: analyze_codebase() - Calcul des mtriques"""
        structure = {"complexity": 8.5}

        result = dev_engine.analyze_codebase(structure)

        assert "cyclomatic_complexity" in result["complexity_metrics"]
        assert "cognitive_complexity" in result["complexity_metrics"]
        assert "maintainability_index" in result["complexity_metrics"]
        assert result["maintainability_score"] >= 0.0
        assert result["maintainability_score"] <= 1.0

    def test_detect_anti_patterns_basic_functionality(self, dev_engine):
        """Test 1: detect_anti_patterns() - Fonctionnalit basique"""
        codebase = {
            "classes": ["UserService", "DataManager", "PaymentProcessor"],
            "methods": ["processPayment", "validateUser", "saveData"],
            "dependencies": ["A->B", "B->C", "C->A"]
        }

        result = dev_engine.detect_anti_patterns(codebase)

        assert "god_classes" in result["anti_patterns_detected"]
        assert "circular_dependencies" in result["anti_patterns_detected"]
        assert "tight_coupling" in result["anti_patterns_detected"]
        assert "code_duplication" in result["anti_patterns_detected"]
        assert "dead_code" in result["anti_patterns_detected"]
        assert "severity_scores" in result
        assert "critical_issues" in result

    def test_detect_anti_patterns_severity_calculation(self, dev_engine):
        """Test 2: detect_anti_patterns() - Calcul de svrit"""
        codebase_with_issues = {
            "classes": ["VeryLargeClassWithManyResponsibilities"] * 5,
            "dependencies": ["A->B", "B->C", "C->A"] * 3
        }

        result = dev_engine.detect_anti_patterns(codebase_with_issues)

        assert len(result["severity_scores"]) > 0
        for severity in result["severity_scores"].values():
            assert severity >= 0.0
            assert severity <= 1.0

    def test_detect_anti_patterns_critical_detection(self, dev_engine):
        """Test 3: detect_anti_patterns() - Dtection critiques"""
        codebase_critical = {
            "classes": ["GodClass"] * 10,
            "dependencies": ["CircularDep"] * 8
        }

        result = dev_engine.detect_anti_patterns(codebase_critical)

        # Devrait dtecter des problmes critiques
        assert len(result["critical_issues"]) > 0
        assert result["severity_scores"]["god_classes"] > 0.5

    def test_manage_dependencies_basic_functionality(self, dev_engine):
        """Test 1: manage_dependencies() - Fonctionnalit basique"""
        graph = {
            "dependencies": ["A->B", "B->C"],
            "versions": {"A": "1.0", "B": "2.0", "C": "1.5"},
            "licenses": {"A": "MIT", "B": "Apache", "C": "GPL"}
        }

        result = dev_engine.manage_dependencies(graph)

        assert "dependency_analysis" in result
        assert "resolution_plan" in result
        assert "automated_fixes" in result
        assert "manual_interventions_required" in result
        assert "health_score" in result
        assert result["health_score"] >= 0.0
        assert result["health_score"] <= 1.0

    def test_manage_dependencies_conflict_detection(self, dev_engine):
        """Test 2: manage_dependencies() - Dtection de conflits"""
        graph_with_conflicts = {
            "dependencies": ["A->B", "A->C", "B->C", "C->A"],
            "versions": {"A": "1.0", "B": "1.0", "C": "2.0"}
        }

        result = dev_engine.manage_dependencies(graph_with_conflicts)

        assert len(result["dependency_analysis"]["circular_dependencies"]) > 0
        assert result["health_score"] < 1.0

    def test_manage_dependencies_resolution_plan(self, dev_engine):
        """Test 3: manage_dependencies() - Plan de rsolution"""
        graph = {
            "dependencies": ["A->B"],
            "versions": {"A": "1.0", "B": "1.0"}
        }

        result = dev_engine.manage_dependencies(graph)

        assert "actions" in result["resolution_plan"]
        assert isinstance(result["resolution_plan"]["actions"], list)

    def test_method_existence(self, dev_engine):
        """Test: Existence des méthodes publiques"""
        # Vérifier que les 3 méthodes publiques existent
        assert hasattr(dev_engine, 'analyze_codebase')
        assert hasattr(dev_engine, 'detect_anti_patterns')
        assert hasattr(dev_engine, 'manage_dependencies')

        # Vérifier qu'elles sont appelables
        result1 = dev_engine.analyze_codebase({"test": "data"})
        assert isinstance(result1, dict)

        result2 = dev_engine.detect_anti_patterns({"classes": []})
        assert isinstance(result2, dict)

        result3 = dev_engine.manage_dependencies({"dependencies": []})
        assert isinstance(result3, dict)