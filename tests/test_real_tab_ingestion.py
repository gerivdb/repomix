#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test E2E sur onglet réel — Ingestion d'un papier arXiv via ENV2

Repo: gerivdb/NEXUS
Layer: ENV2 (Browser Automation + Internet)
Statut: CONFORME_NEXUS
OPS: OPS3_BREAKTHROUGH
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add managers directory to path (relative import fix)
managers_path = Path(__file__).parent.parent / "managers"
sys.path.insert(0, str(managers_path))
# Also add parent directory for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_real_tab_ingestion():
    """Teste l'ingestion d'un papier arXiv sur un onglet réel"""
    from managers.pipeline_v6_executor import PipelineV6Executor
    from managers.arxiv_classifier import ArxivClassifier
    from managers.pipeline_v6_events import get_pipeline_events
    
    print("=" * 60)
    print("TEST E2E: Ingestion papier arXiv sur onglet réel")
    print("=" * 60)
    
    # Initialiser les composants
    executor = PipelineV6Executor()
    classifier = ArxivClassifier()
    events = get_pipeline_events()
    
    # Papier arXiv à tester (Attention Is All You Need)
    test_arxiv_id = "1706.03762"
    
    print(f"\n[1] Détection du papier arXiv: {test_arxiv_id}")
    events.emit_paper_detected(test_arxiv_id, "test_e2e")
    
    # Émettre event détection
    print(f"  → Event émis: paper_detected")
    
    print(f"\n[2] Ouverture du papier via CDP...")
    try:
        result = await executor.open_arxiv_paper(test_arxiv_id)
        print(f"  → Titre: {result.title}")
        print(f"  → URL: {result.url}")
        print(f"  → Target ID: {result.target_id}")
        print(f"  → Classification: {result.classification}")
        
        events.emit_paper_opened(test_arxiv_id, result.title, result.url)
        print(f"  → Event émis: paper_opened")
    except Exception as e:
        print(f"  ✗ Erreur ouverture: {e}")
        print(f"  → Event émis: error")
        events.emit_error("open_paper", str(e))
        return False
    
    print(f"\n[3] Analyse du papier via ENV5...")
    try:
        analysis = await executor.analyze_paper(test_arxiv_id)
        print(f"  → Analyse: {json.dumps(analysis, indent=2, ensure_ascii=False)[:500]}...")
    except Exception as e:
        print(f"  ✗ Erreur analyse: {e}")
        events.emit_error("analyze_paper", str(e))
    
    print(f"\n[4] Classification sémantique via ENV5...")
    try:
        classification = await classifier.classify(
            test_arxiv_id,
            result.title,
            "Attention mechanism for sequence transduction"
        )
        print(f"  → Catégorie: {classification.category} ({classification.category_name})")
        print(f"  → Confiance: {classification.confidence:.2%}")
        print(f"  → Mots-clés: {classification.keywords}")
        print(f"  → ECOSystème: {classification.is_ecosystem}")
        print(f"  → Repos liés: {classification.related_repos}")
        
        events.emit_classification_complete(
            test_arxiv_id,
            classification.category,
            classification.confidence,
            classification.keywords
        )
        print(f"  → Event émis: classification_complete")
    except Exception as e:
        print(f"  ✗ Erreur classification: {e}")
        events.emit_error("classify_paper", str(e))
    
    print(f"\n[5] Résumé du test E2E...")
    print(f"  → Papier: {test_arxiv_id}")
    print(f"  → Titre: {result.title[:80]}...")
    print(f"  → Events émis: {len(events._event_queue)}")
    print(f"  → Statut: {'✅ SUCCÈS' if result.target_id else '❌ ÉCHEC'}")
    
    events.emit_pipeline_complete("test_e2e", 1, 0)
    print(f"  → Event émis: pipeline_complete")
    
    return result.target_id is not None


async def test_note_processing():
    """Teste le traitement d'une note avec détection de papiers"""
    from managers.env1_orchestrator import ENV1Orchestrator
    
    print("\n" + "=" * 60)
    print("TEST E2E: Traitement d'une note avec papiers arXiv")
    print("=" * 60)
    
    # Créer une note de test
    test_note = Path("output/test_note_e2e.md")
    test_note.parent.mkdir(parents=True, exist_ok=True)
    test_note.write_text("""# Ma Note de Recherche

## Contexte
J'étudie l'architecture Transformer pour NEXUS.

## Papers à analyser
- arXiv:1706.03762 - Attention Is All You Need (Vaswani et al.)
- arXiv:1810.04805 - BERT: Pre-training of Deep Bidirectional Transformers

## Objectifs
1. Comprendre l'attention multi-têtes
2. Implémenter dans DevTools
3. Corréler avec FLUENCE matrix
""")
    
    print(f"\n[1] Note créée: {test_note}")
    
    orchestrator = ENV1Orchestrator()
    
    print(f"\n[2] Détection des papiers arXiv...")
    papers = await orchestrator.detect_arxiv_papers(test_note.read_text())
    print(f"  → Papiers détectés: {len(papers)}")
    for paper in papers:
        print(f"    - {paper}")
    
    print(f"\n[3] Résumé du test...")
    print(f"  → Note: {test_note}")
    print(f"  → Papiers détectés: {len(papers)}")
    print(f"  → Statut: {'✅ SUCCÈS' if len(papers) >= 2 else '❌ ÉCHEC'}")
    
    # Nettoyer
    test_note.unlink()
    print(f"\n[4] Note nettoyée: {test_note}")
    
    return len(papers) >= 2


async def main():
    """Fonction principale"""
    print(f"\n{'='*60}")
    print(f"TESTS E2E PIPELINE V6 + ENV2")
    print(f"Date: {datetime.now().isoformat()}")
    print(f"{'='*60}")
    
    results = {}
    
    # Test 1: Ingestion papier réel
    try:
        results["tab_ingestion"] = await test_real_tab_ingestion()
    except Exception as e:
        print(f"\n✗ Test tab_ingestion échoué: {e}")
        results["tab_ingestion"] = False
    
    # Test 2: Traitement note
    try:
        results["note_processing"] = await test_note_processing()
    except Exception as e:
        print(f"\n✗ Test note_processing échoué: {e}")
        results["note_processing"] = False
    
    # Résumé final
    print(f"\n{'='*60}")
    print(f"RÉSULTATS DES TESTS E2E")
    print(f"{'='*60}")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    print(f"\n  Total: {total_passed}/{total_tests} tests pass")
    
    if total_passed == total_tests:
        print(f"\n🎉 TOUS LES TESTS E2E SONT PASSÉS !")
    else:
        print(f"\n⚠️  Certains tests ont échoué")
    
    # Sauvegarder rapport
    report = {
        "date": datetime.now().isoformat(),
        "results": results,
        "total_passed": total_passed,
        "total_tests": total_tests,
        "all_passed": total_passed == total_tests
    }
    
    report_path = Path("output/e2e_test_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n  Rapport sauvegardé: {report_path}")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)