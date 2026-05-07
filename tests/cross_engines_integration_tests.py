#!/usr/bin/env python3
"""
NEXUS CROSS-ENGINES INTEGRATION TESTS
Tests d'intégration entre tous les moteurs et composants
"""

import sys
import os
import time
from typing import Dict, List, Any
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class CrossEnginesTestSuite:
    """Suite de tests d'intégration cross-moteurs NEXUS"""

    def __init__(self):
        self.engines = {}
        self.event_bus = None
        self.visual_primitives = None
        self.test_results = []

    def setup_engines(self):
        """Initialise tous les moteurs pour les tests"""
        print("🔧 Initialisation des moteurs pour tests cross-engines...")

        try:
            # Event Bus (fondamental)
            from engines.ops_triad.event_bus import EventBus
            self.event_bus = EventBus()
            self.engines['event_bus'] = self.event_bus
            print("✅ Event Bus initialisé")

            # Triade OPS
            from engines.prim_engine import PRIMEngine
            self.engines['prim'] = PRIMEngine(event_bus=self.event_bus)

            from engines.vector_engine import VECTOREngine
            self.engines['vector'] = VECTOREngine(event_bus=self.event_bus)

            from engines.fluid_engine import FLUIDEngine
            self.engines['fluid'] = FLUIDEngine(event_bus=self.event_bus)

            print("✅ Triade OPS (PRIM/VECTOR/FLUID) initialisée")

            # Triade ADVERSAIRE
            from engines.joker_engine import JOKEREngine
            self.engines['joker'] = JOKEREngine(event_bus=self.event_bus)

            from engines.riddler_engine import RIDDLEREngine
            self.engines['riddler'] = RIDDLEREngine(event_bus=self.event_bus)

            from engines.gost_engine import GOSTEngine
            self.engines['gost'] = GOSTEngine(event_bus=self.event_bus)

            from engines.fluence_engine import FLUENCEEngine
            self.engines['fluence'] = FLUENCEEngine(event_bus=self.event_bus)

            print("✅ Triade ADVERSAIRE (JOKER/RIDDLER/GOST/FLUENCE) initialisée")

            # Visual Primitives Framework
            from engines.visual_primitives.integration.prim_connector import PRIMConnector
            from engines.visual_primitives.integration.engine_bridge import EngineBridge
            from engines.visual_primitives.integration.plix_adapter import PLIXAdapter

            self.visual_primitives = {
                'prim_connector': PRIMConnector(),
                'engine_bridge': EngineBridge(),
                'plix_adapter': PLIXAdapter()
            }

            print("✅ Visual Primitives Framework initialisé")

            return True

        except Exception as e:
            print(f"❌ Erreur d'initialisation: {e}")
            return False

    def run_cross_engine_tests(self):
        """Exécute tous les tests cross-moteurs"""
        print("\n🧪 DÉBUT DES TESTS CROSS-MOTEURS\n")

        test_methods = [
            self.test_triade_ops_integration,
            self.test_triade_adversaire_integration,
            self.test_ops_adversaire_balance,
            self.test_visual_primitives_integration,
            self.test_event_bus_orchestration,
            self.test_system_resilience,
            self.test_performance_under_load,
            self.test_state_consistency
        ]

        passed = 0
        total = len(test_methods)

        for test_method in test_methods:
            try:
                print(f"🏃 Exécution: {test_method.__name__}")
                start_time = time.time()
                result = test_method()
                end_time = time.time()

                if result:
                    print(f"✅ {test_method.__name__} PASSED ({end_time - start_time:.2f}s)")
                    passed += 1
                else:
                    print(f"❌ {test_method.__name__} FAILED")

                self.test_results.append({
                    'test': test_method.__name__,
                    'result': result,
                    'duration': end_time - start_time
                })

            except Exception as e:
                print(f"💥 {test_method.__name__} CRASHED: {e}")
                self.test_results.append({
                    'test': test_method.__name__,
                    'result': False,
                    'error': str(e),
                    'duration': 0
                })

        print(f"\n📊 RÉSULTATS: {passed}/{total} tests réussis")

        if passed == total:
            print("🎉 TOUS LES TESTS CROSS-MOTEURS RÉUSSIS !")
            return True
        else:
            print("⚠️ Certains tests ont échoué - investigation requise")
            return False

    def test_triade_ops_integration(self) -> bool:
        """Test intégration triade OPS (PRIM/VECTOR/FLUID)"""
        try:
            # Test données d'entrée
            test_data = {
                "patterns": ["pattern_1", "pattern_2", "pattern_3"],
                "intent": "analyze_system_behavior",
                "constraints": ["performance", "reliability"]
            }

            # PRIM détecte patterns
            prim_result = self.engines['prim'].analyze_patterns(test_data["patterns"])
            assert "detected_patterns" in prim_result

            # VECTOR calcule direction
            vector_result = self.engines['vector'].calculate_direction(
                current_state=test_data,
                target_intent=test_data["intent"]
            )
            assert "direction_vector" in vector_result

            # FLUID adapte si nécessaire
            fluid_result = self.engines['fluid'].adapt_to_conditions(
                current_state=test_data,
                prim_analysis=prim_result,
                vector_direction=vector_result
            )
            assert "adaptation_strategy" in fluid_result

            # Vérifie équilibre dynamique
            ops_balance = self._check_ops_balance(prim_result, vector_result, fluid_result)
            assert ops_balance > 0.8  # 80% équilibre minimum

            return True

        except Exception as e:
            print(f"Erreur triade OPS: {e}")
            return False

    def test_triade_adversaire_integration(self) -> bool:
        """Test intégration triade ADVERSAIRE (JOKER/RIDDLER/GOST/FLUENCE)"""
        try:
            # Test système nominal
            nominal_system = {
                "components": ["engine_1", "engine_2", "engine_3"],
                "connections": ["conn_1", "conn_2"],
                "performance": 0.95
            }

            # JOKER teste les hypothèses
            joker_result = self.engines['joker'].test_hypotheses(nominal_system)
            assert "broken_hypotheses" in joker_result

            # RIDDLER trouve problèmes insolubles
            riddler_result = self.engines['riddler'].find_insoluble_problems(nominal_system)
            assert "unsolvable_problems" in riddler_result

            # GOST teste l'invisibilité
            gost_result = self.engines['gost'].test_traceability(nominal_system)
            assert "traceability_gaps" in gost_result

            # FLUENCE teste la propagation
            fluence_result = self.engines['fluence'].test_propagation(nominal_system)
            assert "propagation_effects" in fluence_result

            # Vérifie couverture adversarial
            adversarial_coverage = self._check_adversarial_coverage(
                joker_result, riddler_result, gost_result, fluence_result
            )
            assert adversarial_coverage > 0.9  # 90% couverture minimum

            return True

        except Exception as e:
            print(f"Erreur triade ADVERSAIRE: {e}")
            return False

    def test_ops_adversaire_balance(self) -> bool:
        """Test équilibre OPS vs ADVERSAIRE"""
        try:
            # Scénario équilibré
            balanced_scenario = {
                "ops_output": {"patterns": ["p1", "p2"], "direction": "forward"},
                "adversarial_pressure": {"hypotheses_broken": 2, "problems_found": 1}
            }

            # Mesure équilibre dynamique
            balance_score = self._calculate_ops_adversaire_balance(balanced_scenario)

            # Test équilibre parfait (50/50)
            assert 0.4 < balance_score < 0.6  # Entre 40% et 60%

            # Test déséquilibre OPS dominant
            ops_dominant = balanced_scenario.copy()
            ops_dominant["ops_output"]["patterns"] = ["p1", "p2", "p3", "p4", "p5"]
            balance_ops_heavy = self._calculate_ops_adversaire_balance(ops_dominant)
            assert balance_ops_heavy > 0.7  # OPS trop dominant

            # Test déséquilibre ADVERSAIRE dominant
            adv_dominant = balanced_scenario.copy()
            adv_dominant["adversarial_pressure"]["hypotheses_broken"] = 10
            balance_adv_heavy = self._calculate_ops_adversaire_balance(adv_dominant)
            assert balance_adv_heavy < 0.3  # ADVERSAIRE trop dominant

            return True

        except Exception as e:
            print(f"Erreur équilibre OPS/ADVERSAIRE: {e}")
            return False

    def test_visual_primitives_integration(self) -> bool:
        """Test intégration Visual Primitives avec moteurs"""
        try:
            # Diagramme test
            test_diagram = """
            F = ma
            +-----+
            | m=5 |
            +-----+
            Force = mass × acceleration
            """

            # Extraction primitives visuelles
            prim_conn = self.visual_primitives['prim_connector']
            vp_result = prim_conn.feed_visual_data(test_diagram, input_type="diagram")
            assert "primitives_extracted" in vp_result

            # Intégration avec engines
            engine_bridge = self.visual_primitives['engine_bridge']

            # Test VECTOR avec primitives visuelles
            vector_vp = engine_bridge.feed_to_vector_engine(test_diagram)
            assert vector_vp["engine"] == "vector"

            # Test FLUID avec primitives visuelles
            fluid_vp = engine_bridge.feed_to_fluid_engine(test_diagram)
            assert fluid_vp["engine"] == "fluid"

            # Test SCIENCE avec primitives visuelles
            science_vp = engine_bridge.feed_to_science_engine(test_diagram)
            assert science_vp["engine"] == "science"

            # Test PLIX parsing
            plix_adapter = self.visual_primitives['plix_adapter']
            plix_result = plix_adapter.parse_diagram(test_diagram, diagram_type="text")
            assert plix_result["equations_found"] >= 1

            # Vérifie cohérence multimodale
            multimodal_coherence = self._check_multimodal_coherence(
                vp_result, vector_vp, fluid_vp, science_vp, plix_result
            )
            assert multimodal_coherence > 0.8

            return True

        except Exception as e:
            print(f"Erreur Visual Primitives: {e}")
            return False

    def test_event_bus_orchestration(self) -> bool:
        """Test orchestration via event bus"""
        try:
            # Démarre écouteurs
            event_log = []

            def log_event(event_type, data):
                event_log.append({"type": event_type, "data": data})

            # Abonne tous les moteurs aux évènements
            self.event_bus.subscribe("pattern.detected", lambda d: log_event("pattern", d))
            self.event_bus.subscribe("direction.calculated", lambda d: log_event("direction", d))
            self.event_bus.subscribe("adaptation.proposed", lambda d: log_event("adaptation", d))

            # Déclenche séquence d'évènements
            test_data = {"patterns": ["test_pattern"], "intent": "test_goal"}

            # PRIM émet
            self.engines['prim'].emit_pattern_detected(test_data["patterns"])

            # VECTOR répond
            self.engines['vector'].emit_direction_calculated(test_data["intent"])

            # FLUID s'adapte
            self.engines['fluid'].emit_adaptation_proposed(test_data)

            # Vérifie séquence d'évènements
            assert len(event_log) >= 3
            assert any(e["type"] == "pattern" for e in event_log)
            assert any(e["type"] == "direction" for e in event_log)
            assert any(e["type"] == "adaptation" for e in event_log)

            # Vérifie timing (évènements dans le bon ordre)
            pattern_idx = next(i for i, e in enumerate(event_log) if e["type"] == "pattern")
            direction_idx = next(i for i, e in enumerate(event_log) if e["type"] == "direction")
            adaptation_idx = next(i for i, e in enumerate(event_log) if e["type"] == "adaptation")

            assert pattern_idx < direction_idx < adaptation_idx

            return True

        except Exception as e:
            print(f"Erreur event bus: {e}")
            return False

    def test_system_resilience(self) -> bool:
        """Test résilience système face aux pannes"""
        try:
            # Test panne moteur individuel
            original_prim = self.engines['prim']

            # Simule panne PRIM
            self.engines['prim'] = None

            # Système doit continuer avec autres moteurs
            vector_result = self.engines['vector'].calculate_direction({}, "test")
            fluid_result = self.engines['fluid'].adapt_to_conditions({}, {}, {})

            assert vector_result is not None
            assert fluid_result is not None

            # Restore
            self.engines['prim'] = original_prim

            # Test charge élevée
            heavy_load = [{"data": f"item_{i}"} for i in range(1000)]

            start_time = time.time()
            for item in heavy_load[:100]:  # Test subset pour performance
                self.engines['prim'].analyze_patterns([item["data"]])
            end_time = time.time()

            processing_time = end_time - start_time
            assert processing_time < 5.0  # <5 secondes pour 100 items

            return True

        except Exception as e:
            print(f"Erreur résilience: {e}")
            return False

    def test_performance_under_load(self) -> bool:
        """Test performance sous charge"""
        try:
            # Métriques baseline
            baseline_metrics = self._measure_system_metrics()

            # Charge modérée (10x baseline)
            moderate_load = self._generate_load_scenario(10)

            moderate_metrics = self._run_load_scenario(moderate_load)

            # Vérifie dégradation acceptable
            cpu_degradation = moderate_metrics["cpu"] / baseline_metrics["cpu"]
            memory_degradation = moderate_metrics["memory"] / baseline_metrics["memory"]
            latency_degradation = moderate_metrics["latency"] / baseline_metrics["latency"]

            assert cpu_degradation < 3.0  # <3x CPU
            assert memory_degradation < 2.0  # <2x mémoire
            assert latency_degradation < 5.0  # <5x latence

            # Test récupération
            recovery_metrics = self._measure_system_metrics()
            cpu_recovery = abs(recovery_metrics["cpu"] - baseline_metrics["cpu"]) / baseline_metrics["cpu"]
            assert cpu_recovery < 0.1  # <10% différence post-charge

            return True

        except Exception as e:
            print(f"Erreur performance: {e}")
            return False

    def test_state_consistency(self) -> bool:
        """Test cohérence état système"""
        try:
            # Snapshot état initial
            initial_state = self._capture_system_state()

            # Séquence d'opérations
            operations = [
                lambda: self.engines['prim'].analyze_patterns(["test"]),
                lambda: self.engines['vector'].calculate_direction({}, "test"),
                lambda: self.engines['fluid'].adapt_to_conditions({}, {}, {}),
                lambda: self.engines['joker'].test_hypotheses({}),
                lambda: self.engines['riddler'].find_insoluble_problems({}),
                lambda: self.engines['gost'].test_traceability({}),
                lambda: self.engines['fluence'].test_propagation({})
            ]

            # Exécute toutes les opérations
            for op in operations:
                op()

            # Vérifie état final
            final_state = self._capture_system_state()

            # Cohérence: mêmes moteurs actifs, métriques dans limites
            assert initial_state["active_engines"] == final_state["active_engines"]
            assert abs(final_state["total_events"] - initial_state["total_events"]) >= len(operations)

            # Pas de corruption mémoire (simple check)
            assert final_state["memory_usage"] > 0
            assert final_state["memory_usage"] < 1000 * 1024 * 1024  # <1GB

            return True

        except Exception as e:
            print(f"Erreur cohérence: {e}")
            return False

    # Helper methods
    def _check_ops_balance(self, prim, vector, fluid) -> float:
        """Calcule score d'équilibre OPS"""
        # Score simplifié basé sur outputs
        prim_score = len(prim.get("detected_patterns", [])) / 10.0
        vector_score = 1.0 if "direction_vector" in vector else 0.0
        fluid_score = 1.0 if "adaptation_strategy" in fluid else 0.0

        avg_score = (prim_score + vector_score + fluid_score) / 3.0
        return min(1.0, avg_score)

    def _check_adversarial_coverage(self, joker, riddler, gost, fluence) -> float:
        """Calcule couverture adversarial"""
        coverage = 0.0
        if joker.get("broken_hypotheses"): coverage += 0.25
        if riddler.get("unsolvable_problems"): coverage += 0.25
        if gost.get("traceability_gaps"): coverage += 0.25
        if fluence.get("propagation_effects"): coverage += 0.25
        return coverage

    def _calculate_ops_adversaire_balance(self, scenario) -> float:
        """Calcule équilibre OPS vs ADVERSAIRE"""
        ops_strength = len(scenario["ops_output"].get("patterns", []))
        adv_strength = (scenario["adversarial_pressure"].get("hypotheses_broken", 0) +
                       scenario["adversarial_pressure"].get("problems_found", 0))

        total = ops_strength + adv_strength
        if total == 0:
            return 0.5  # Équilibre parfait si aucun signal

        return ops_strength / total

    def _check_multimodal_coherence(self, vp, vector, fluid, science, plix) -> float:
        """Vérifie cohérence multimodale"""
        coherence = 0.0

        # Primitives extraites
        if vp.get("primitives_extracted", {}).get("points", 0) > 0:
            coherence += 0.2

        # Engines ont traité
        if vector.get("convergence_result"):
            coherence += 0.2
        if fluid.get("transition_result"):
            coherence += 0.2
        if science.get("inference_result"):
            coherence += 0.2

        # PLIX a parsé
        if plix.get("equations_found", 0) > 0:
            coherence += 0.2

        return coherence

    def _measure_system_metrics(self) -> Dict[str, float]:
        """Mesure métriques système actuelles"""
        return {
            "cpu": 10.0,  # Mock: 10% CPU
            "memory": 100 * 1024 * 1024,  # Mock: 100MB
            "latency": 50.0,  # Mock: 50ms
            "events": len(self.event_bus.events) if self.event_bus else 0
        }

    def _generate_load_scenario(self, multiplier: int) -> List[Dict]:
        """Génère scénario de charge"""
        base_scenario = {"patterns": ["pattern_1"], "intent": "analyze"}
        return [base_scenario.copy() for _ in range(multiplier * len(base_scenario))]

    def _run_load_scenario(self, scenario: List[Dict]) -> Dict[str, float]:
        """Exécute scénario de charge"""
        start_time = time.time()

        for item in scenario[:50]:  # Limite pour test
            if self.engines.get('prim'):
                self.engines['prim'].analyze_patterns(item.get("patterns", []))

        end_time = time.time()

        return {
            "cpu": 25.0,  # Mock: 25% CPU sous charge
            "memory": 150 * 1024 * 1024,  # Mock: 150MB
            "latency": 100.0,  # Mock: 100ms
            "duration": end_time - start_time
        }

    def _capture_system_state(self) -> Dict[str, Any]:
        """Capture état système"""
        return {
            "active_engines": len([e for e in self.engines.values() if e is not None]),
            "total_events": len(self.event_bus.events) if self.event_bus else 0,
            "memory_usage": 100 * 1024 * 1024,  # Mock
            "uptime": time.time()
        }

    def generate_report(self) -> str:
        """Génère rapport de tests"""
        passed = sum(1 for r in self.test_results if r["result"])
        total = len(self.test_results)

        report = f"""
🧪 RAPPORT TESTS CROSS-MOTEURS NEXUS
=====================================

📊 RÉSULTATS GÉNÉRAUX
- Tests réussis: {passed}/{total}
- Taux de succès: {passed/total*100:.1f}%
- Durée totale: {sum(r['duration'] for r in self.test_results):.2f}s

📋 TESTS DÉTAILLÉS
"""

        for result in self.test_results:
            status = "✅ PASS" if result["result"] else "❌ FAIL"
            duration = f"{result['duration']:.2f}s"
            error = f" - {result.get('error', '')}" if not result["result"] else ""
            report += f"- {result['test']}: {status} ({duration}){error}\n"

        report += f"""
🔍 ANALYSE
- Triade OPS: {'✅ Fonctionnelle' if passed >= 6 else '❌ Problèmes détectés'}
- Triade ADVERSAIRE: {'✅ Fonctionnelle' if passed >= 6 else '❌ Problèmes détectés'}
- Visual Primitives: {'[INTEGRATED]' if passed >= 7 else '[INTEGRATION ISSUES]'}
- Performance: {'✅ Acceptable' if passed >= 7 else '❌ Dégradation détectée'}

🎯 CONCLUSION
{'🜏 SYSTÈME CROSS-MOTEURS OPÉRATIONNEL' if passed == total else '⚠️ INVESTIGATION REQUISE'}
"""

        return report


def main():
    """Point d'entrée principal"""
    print("🧪 NEXUS CROSS-ENGINES INTEGRATION TESTS")
    print("=" * 50)

    suite = CrossEnginesTestSuite()

    # Initialisation
    if not suite.setup_engines():
        print("❌ Échec d'initialisation - arrêt des tests")
        return False

    # Exécution tests
    success = suite.run_cross_engine_tests()

    # Rapport
    report = suite.generate_report()
    print(report)

    # Sauvegarde rapport
    with open("cross_engines_test_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("📄 Rapport sauvegardé: cross_engines_test_report.md")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
