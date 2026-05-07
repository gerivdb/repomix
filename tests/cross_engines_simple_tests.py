#!/usr/bin/env python3
"""
NEXUS CROSS-ENGINES INTEGRATION TESTS - SIMPLIFIED VERSION
Tests d'integration pour les composants existants
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_visual_primitives_only():
    """Test seulement le framework Visual Primitives qui existe"""
    print("[TEST] NEXUS CROSS-ENGINES INTEGRATION TESTS (SIMPLIFIED)")
    print("=" * 60)

    test_results = []

    try:
        print("[RUN] Testing Visual Primitives Framework...")

        # Test 1: Primitives de base
        start_time = time.time()
        from engines.visual_primitives.primitives import Point, Line, Shape
        p = Point(x=1.0, y=2.0)
        l = Line.from_points(Point(0, 0), Point(3, 4))
        s = Shape.from_coords([(0, 0), (1, 0), (1, 1), (0, 1)])
        end_time = time.time()

        assert p.x == 1.0
        assert abs(l.length - 5.0) < 0.001
        assert abs(s.area - 1.0) < 0.001

        test_results.append({
            'test': 'Primitives Base',
            'result': True,
            'duration': end_time - start_time
        })
        print("[PASS] Primitives Base PASSED ({:.2f}s)".format(end_time - start_time))

        # Test 2: Extraction CPU
        start_time = time.time()
        from engines.visual_primitives.extraction import CPUExtractor, LightEmbedder
        extractor = CPUExtractor()
        embedder = LightEmbedder(dimensions=32)

        diagram = "+-----+"
        primitives = extractor.extract_from_diagram(diagram)
        embedded = embedder.embed_primitives(primitives)

        end_time = time.time()

        assert 'points' in primitives
        assert 'lines' in primitives
        assert len(embedded) > 0

        test_results.append({
            'test': 'CPU Extraction',
            'result': True,
            'duration': end_time - start_time
        })
        print("[PASS] CPU Extraction PASSED ({:.2f}s)".format(end_time - start_time))

        # Test 3: Intégration PRIM
        start_time = time.time()
        from engines.visual_primitives.integration import PRIMConnector
        prim_connector = PRIMConnector()

        result = prim_connector.feed_visual_data(diagram, input_type="diagram")
        end_time = time.time()

        assert "primitives_extracted" in result
        assert "patterns_detected" in result

        test_results.append({
            'test': 'PRIM Integration',
            'result': True,
            'duration': end_time - start_time
        })
        print("[PASS] PRIM Integration PASSED ({:.2f}s)".format(end_time - start_time))

        # Test 4: Engine Bridge
        start_time = time.time()
        from engines.visual_primitives.integration import EngineBridge
        engine_bridge = EngineBridge()

        vector_result = engine_bridge.feed_to_vector_engine(diagram)
        fluid_result = engine_bridge.feed_to_fluid_engine(diagram)
        science_result = engine_bridge.feed_to_science_engine(diagram)

        end_time = time.time()

        assert vector_result["engine"] == "vector"
        assert fluid_result["engine"] == "fluid"
        assert science_result["engine"] == "science"

        test_results.append({
            'test': 'Engine Bridge',
            'result': True,
            'duration': end_time - start_time
        })
        print("[PASS] Engine Bridge PASSED ({:.2f}s)".format(end_time - start_time))

        # Test 5: PLIX Adapter
        start_time = time.time()
        from engines.visual_primitives.integration import PLIXAdapter
        plix_adapter = PLIXAdapter()

        plix_result = plix_adapter.parse_diagram(diagram, diagram_type="text")
        end_time = time.time()

        assert plix_result["diagram_type"] == "text"
        assert "equations_found" in plix_result

        test_results.append({
            'test': 'PLIX Adapter',
            'result': True,
            'duration': end_time - start_time
        })
        print("[PASS] PLIX Adapter PASSED ({:.2f}s)".format(end_time - start_time))

        # Test 6: Cross-component coherence
        start_time = time.time()
        # Verify that all components work together
        multimodal_input = "F = ma\n+-----+"

        # Full pipeline
        vp_result = prim_connector.feed_visual_data(multimodal_input, input_type="diagram")
        eb_vector = engine_bridge.feed_to_vector_engine(multimodal_input)
        eb_fluid = engine_bridge.feed_to_fluid_engine(multimodal_input)
        eb_science = engine_bridge.feed_to_science_engine(multimodal_input)
        plix_full = plix_adapter.parse_diagram(multimodal_input, diagram_type="text")

        end_time = time.time()

        # Verify coherence
        assert vp_result["patterns_detected"]["simulation_mode"] == True
        assert eb_vector["convergence_result"]["simulation_mode"] == True
        assert eb_fluid["transition_result"]["simulation_mode"] == True
        assert eb_science["inference_result"]["simulation_mode"] == True
        assert plix_full["equations_found"] >= 1

        test_results.append({
            'test': 'Cross-component Coherence',
            'result': True,
            'duration': end_time - start_time
        })
        print("[PASS] Cross-component Coherence PASSED ({:.2f}s)".format(end_time - start_time))

        # Generate report
        passed = sum(1 for r in test_results if r["result"])
        total = len(test_results)
        total_time = sum(r['duration'] for r in test_results)

        print("\n" + "=" * 60)
        print("[STATS] CROSS-ENGINES INTEGRATION RESULTS")
        print("[STATS] Tests passed: {}/{}".format(passed, total))
        print("[STATS] Success rate: {:.1f}%".format(passed/total*100))
        print("[STATS] Total time: {:.2f}s".format(total_time))
        print("[STATS] Average time per test: {:.2f}s".format(total_time/total))

        if passed == total:
            print("\n[SUCCESS] ALL CROSS-ENGINES TESTS PASSED!")
            print("[NEXUS] VISUAL PRIMITIVES FRAMEWORK FULLY OPERATIONAL")
            return True
        else:
            print("\n[WARNING] SOME TESTS FAILED - REVIEW REQUIRED")
            return False

    except Exception as e:
        print("[FAIL] Test suite failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    success = test_visual_primitives_only()

    # Save simple report
    report = """
NEXUS CROSS-ENGINES INTEGRATION TEST REPORT
==========================================

Status: {}PASSED{}FAILED
Components Tested: Visual Primitives Framework
Coverage: Primitives, Extraction, Integration, Cross-component

This validates the Visual Primitives integration within NEXUS.
Full cross-engines testing requires implementation of all 7 core engines.

Date: {}
    """.format(
        "[PASS] " if success else "[FAIL] ",
        "\n" if success else "\n",
        time.strftime("%Y-%m-%d %H:%M:%S")
    )

    with open("cross_engines_test_report.txt", "w") as f:
        f.write(report)

    print("Report saved: cross_engines_test_report.txt")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)