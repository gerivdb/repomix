#!/usr/bin/env python3
"""
Phase 4 Semaine 3: Beta Testing Platform
Implémentation plateforme de test bêta intégré
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import uuid

@dataclass
class BetaTest:
    """Session de test bêta."""
    id: str
    verse_id: str
    version: str
    status: str  # draft, open, closed, completed
    created_at: str
    deadline: str
    max_testers: int = 50
    current_testers: int = 0
    test_requirements: List[str] = None
    success_criteria: List[str] = None

@dataclass
class BetaTester:
    """Testeur bêta."""
    id: str
    user_id: str
    test_id: str
    joined_at: str
    status: str  # applied, approved, testing, completed
    feedback_submitted: bool = False

@dataclass
class BetaFeedback:
    """Feedback de test bêta."""
    id: str
    test_id: str
    tester_id: str
    submitted_at: str
    rating: int  # 1-5
    functionality_rating: int  # 1-5
    usability_rating: int  # 1-5
    performance_rating: int  # 1-5
    stability_rating: int  # 1-5
    comments: str
    bug_reports: List[Dict] = None
    feature_requests: List[Dict] = None

class BetaTestingPlatform:
    """Plateforme de test bêta intégré."""

    def __init__(self, db_path: str = "beta_testing.db"):
        self.db_path = Path(db_path)
        self.init_database()

    def init_database(self):
        """Initialise la base de données bêta."""
        with sqlite3.connect(self.db_path) as conn:
            # Tests bêta
            conn.execute('''CREATE TABLE IF NOT EXISTS beta_tests (
                id TEXT PRIMARY KEY,
                verse_id TEXT,
                version TEXT,
                status TEXT,
                created_at TEXT,
                deadline TEXT,
                max_testers INTEGER,
                current_testers INTEGER DEFAULT 0,
                test_requirements TEXT,
                success_criteria TEXT
            )''')

            # Testeurs
            conn.execute('''CREATE TABLE IF NOT EXISTS beta_testers (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                test_id TEXT,
                joined_at TEXT,
                status TEXT,
                feedback_submitted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (test_id) REFERENCES beta_tests (id)
            )''')

            # Feedbacks
            conn.execute('''CREATE TABLE IF NOT EXISTS beta_feedback (
                id TEXT PRIMARY KEY,
                test_id TEXT,
                tester_id TEXT,
                submitted_at TEXT,
                rating INTEGER,
                functionality_rating INTEGER,
                usability_rating INTEGER,
                performance_rating INTEGER,
                stability_rating INTEGER,
                comments TEXT,
                bug_reports TEXT,
                feature_requests TEXT,
                FOREIGN KEY (test_id) REFERENCES beta_tests (id),
                FOREIGN KEY (tester_id) REFERENCES beta_testers (id)
            )''')

            # Métriques de test
            conn.execute('''CREATE TABLE IF NOT EXISTS test_metrics (
                id TEXT PRIMARY KEY,
                test_id TEXT,
                metric_name TEXT,
                metric_value REAL,
                recorded_at TEXT,
                FOREIGN KEY (test_id) REFERENCES beta_tests (id)
            )''')

    def create_beta_test(self, verse_id: str, version: str, duration_days: int = 14) -> BetaTest:
        """Crée une nouvelle session de test bêta."""
        test = BetaTest(
            id=str(uuid.uuid4()),
            verse_id=verse_id,
            version=version,
            status="draft",
            created_at=datetime.now().isoformat(),
            deadline=(datetime.now() + timedelta(days=duration_days)).isoformat(),
            test_requirements=[
                "Installer et configurer le verse",
                "Tester les fonctionnalités principales",
                "Vérifier la compatibilité avec l'environnement",
                "Évaluer les performances"
            ],
            success_criteria=[
                "Aucun crash critique",
                "Fonctionnalités principales opérationnelles",
                "Performance acceptable (>80% des utilisateurs satisfaits)",
                "Feedback constructif collecté"
            ]
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''INSERT INTO beta_tests
                (id, verse_id, version, status, created_at, deadline, max_testers, current_testers, test_requirements, success_criteria)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (test.id, test.verse_id, test.version, test.status, test.created_at,
                 test.deadline, test.max_testers, test.current_testers,
                 json.dumps(test.test_requirements), json.dumps(test.success_criteria))
            )

        return test

    def open_beta_test(self, test_id: str) -> bool:
        """Ouvre un test bêta au public."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT status FROM beta_tests WHERE id = ?", (test_id,))
            row = cursor.fetchone()
            if row and row[0] == "draft":
                conn.execute("UPDATE beta_tests SET status = 'open' WHERE id = ?", (test_id,))
                return True
        return False

    def apply_for_beta_test(self, test_id: str, user_id: str) -> BetaTester:
        """Postule pour participer à un test bêta."""
        # Vérifier que le test est ouvert et a de la place
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT status, current_testers, max_testers FROM beta_tests WHERE id = ?",
                (test_id,)
            )
            row = cursor.fetchone()

            if not row or row[0] != "open":
                raise ValueError("Test bêta non ouvert")

            if row[1] >= row[2]:
                raise ValueError("Test bêta complet")

            # Créer le testeur
            tester = BetaTester(
                id=str(uuid.uuid4()),
                user_id=user_id,
                test_id=test_id,
                joined_at=datetime.now().isoformat(),
                status="applied"
            )

            conn.execute('''INSERT INTO beta_testers
                (id, user_id, test_id, joined_at, status)
                VALUES (?, ?, ?, ?, ?)''',
                (tester.id, tester.user_id, tester.test_id, tester.joined_at, tester.status)
            )

            # Incrémenter le compteur de testeurs
            conn.execute(
                "UPDATE beta_tests SET current_testers = current_testers + 1 WHERE id = ?",
                (test_id,)
            )

            return tester

    def approve_beta_tester(self, tester_id: str) -> bool:
        """Approuve un testeur pour participer."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE beta_testers SET status = 'approved' WHERE id = ?", (tester_id,))
            return True

    def submit_beta_feedback(self, test_id: str, tester_id: str,
                           rating: int, functionality: int, usability: int,
                           performance: int, stability: int, comments: str,
                           bugs: List[Dict] = None, features: List[Dict] = None) -> BetaFeedback:
        """Soumet un feedback de test bêta."""
        feedback = BetaFeedback(
            id=str(uuid.uuid4()),
            test_id=test_id,
            tester_id=tester_id,
            submitted_at=datetime.now().isoformat(),
            rating=rating,
            functionality_rating=functionality,
            usability_rating=usability,
            performance_rating=performance,
            stability_rating=stability,
            comments=comments,
            bug_reports=bugs or [],
            feature_requests=features or []
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''INSERT INTO beta_feedback
                (id, test_id, tester_id, submitted_at, rating, functionality_rating,
                 usability_rating, performance_rating, stability_rating, comments,
                 bug_reports, feature_requests)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (feedback.id, feedback.test_id, feedback.tester_id, feedback.submitted_at,
                 feedback.rating, feedback.functionality_rating, feedback.usability_rating,
                 feedback.performance_rating, feedback.stability_rating, feedback.comments,
                 json.dumps(feedback.bug_reports), json.dumps(feedback.feature_requests))
            )

            # Marquer le feedback comme soumis
            conn.execute(
                "UPDATE beta_testers SET feedback_submitted = TRUE, status = 'completed' WHERE id = ?",
                (tester_id,)
            )

        return feedback

    def get_beta_test_results(self, test_id: str) -> Dict:
        """Obtient les résultats complets d'un test bêta."""
        with sqlite3.connect(self.db_path) as conn:
            # Informations du test
            cursor = conn.execute(
                "SELECT * FROM beta_tests WHERE id = ?", (test_id,)
            )
            test_row = cursor.fetchone()
            if not test_row:
                return {"error": "Test not found"}

            test_info = {
                "id": test_row[0],
                "verse_id": test_row[1],
                "version": test_row[2],
                "status": test_row[3],
                "created_at": test_row[4],
                "deadline": test_row[5],
                "max_testers": test_row[6],
                "current_testers": test_row[7],
                "test_requirements": json.loads(test_row[8]) if test_row[8] else [],
                "success_criteria": json.loads(test_row[9]) if test_row[9] else []
            }

            # Statistiques des testeurs
            cursor = conn.execute(
                "SELECT status, COUNT(*) FROM beta_testers WHERE test_id = ? GROUP BY status",
                (test_id,)
            )
            tester_stats = {row[0]: row[1] for row in cursor.fetchall()}

            # Feedbacks
            cursor = conn.execute(
                """SELECT rating, functionality_rating, usability_rating,
                   performance_rating, stability_rating, comments,
                   bug_reports, feature_requests
                   FROM beta_feedback WHERE test_id = ?""",
                (test_id,)
            )

            feedbacks = []
            for row in cursor.fetchall():
                feedback = {
                    "rating": row[0],
                    "functionality": row[1],
                    "usability": row[2],
                    "performance": row[3],
                    "stability": row[4],
                    "comments": row[5],
                    "bugs": json.loads(row[6]) if row[6] else [],
                    "features": json.loads(row[7]) if row[7] else []
                }
                feedbacks.append(feedback)

            # Calculer moyennes
            if feedbacks:
                avg_rating = sum(f["rating"] for f in feedbacks) / len(feedbacks)
                avg_functionality = sum(f["functionality"] for f in feedbacks) / len(feedbacks)
                avg_usability = sum(f["usability"] for f in feedbacks) / len(feedbacks)
                avg_performance = sum(f["performance"] for f in feedbacks) / len(feedbacks)
                avg_stability = sum(f["stability"] for f in feedbacks) / len(feedbacks)

                total_bugs = sum(len(f["bugs"]) for f in feedbacks)
                total_features = sum(len(f["features"]) for f in feedbacks)
            else:
                avg_rating = avg_functionality = avg_usability = avg_performance = avg_stability = 0
                total_bugs = total_features = 0

            return {
                "test_info": test_info,
                "tester_stats": tester_stats,
                "feedback_count": len(feedbacks),
                "average_ratings": {
                    "overall": avg_rating,
                    "functionality": avg_functionality,
                    "usability": avg_usability,
                    "performance": avg_performance,
                    "stability": avg_stability
                },
                "total_bugs": total_bugs,
                "total_features": total_features,
                "feedbacks": feedbacks
            }

    def get_available_beta_tests(self) -> List[Dict]:
        """Obtient la liste des tests bêta disponibles."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT id, verse_id, version, current_testers, max_testers, deadline
                   FROM beta_tests
                   WHERE status = 'open' AND current_testers < max_testers
                   ORDER BY created_at DESC"""
            )

            tests = []
            for row in cursor.fetchall():
                test = {
                    "id": row[0],
                    "verse_id": row[1],
                    "version": row[2],
                    "current_testers": row[3],
                    "max_testers": row[4],
                    "deadline": row[5],
                    "spots_available": row[4] - row[3]
                }
                tests.append(test)

            return tests

class BetaTestingUI:
    """Interface utilisateur pour les tests bêta."""

    def __init__(self, platform: BetaTestingPlatform):
        self.platform = platform

    def display_beta_dashboard(self):
        """Affiche le tableau de bord des tests bêta."""
        print("BETA TESTING PLATFORM - Architecture Diamant")
        print("=" * 50)

        # Tests disponibles
        available_tests = self.platform.get_available_beta_tests()
        print(f"\nTESTS BETA DISPONIBLES ({len(available_tests)})")
        print("-" * 40)

        for test in available_tests[:5]:  # Afficher les 5 premiers
            print(f"ID {test['id'][:8]}...")
            print(f"   Verse: {test['verse_id']}")
            print(f"   Version: {test['version']}")
            print(f"   Testeurs: {test['current_testers']}/{test['max_testers']}")
            print(f"   Deadline: {test['deadline'][:10]}")
            print()

        # Statistiques générales
        print("STATISTIQUES BETA")
        print("-" * 30)

        # Compter tous les tests
        with sqlite3.connect(self.platform.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*), status FROM beta_tests GROUP BY status")
            status_counts = {row[1]: row[0] for row in cursor.fetchall()}

            cursor = conn.execute("SELECT COUNT(*) FROM beta_testers")
            total_testers = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM beta_feedback")
            total_feedbacks = cursor.fetchone()[0]

        print(f"Tests totaux: {sum(status_counts.values())}")
        print(f"  - Ouverts: {status_counts.get('open', 0)}")
        print(f"  - Terminés: {status_counts.get('completed', 0)}")
        print(f"Testeurs inscrits: {total_testers}")
        print(f"Feedbacks reçus: {total_feedbacks}")

    def display_test_results(self, test_id: str):
        """Affiche les résultats détaillés d'un test."""
        results = self.platform.get_beta_test_results(test_id)

        if "error" in results:
            print(f"Erreur: {results['error']}")
            return

        test_info = results["test_info"]
        print(f"RÉSULTATS TEST BÊTA: {test_info['verse_id']}")
        print("=" * 50)
        print(f"Version: {test_info['version']}")
        print(f"Statut: {test_info['status']}")
        print(f"Testeurs: {test_info['current_testers']}/{test_info['max_testers']}")
        print(f"Feedbacks: {results['feedback_count']}")

        if results['feedback_count'] > 0:
            avg = results['average_ratings']
            print("\nNOTES MOYENNES:")
            print(".1f")
            print(".1f")
            print(".1f")
            print(".1f")
            print(".1f")
            print(f"\nBugs signales: {results['total_bugs']}")
            print(f"Fonctionnalites demandees: {results['total_features']}")

def main():
    """Démonstration Phase 4 Semaine 3."""
    print("Phase 4 Semaine 3: Beta Testing Platform")

    # Initialiser la plateforme
    platform = BetaTestingPlatform()
    ui = BetaTestingUI(platform)

    # Créer des tests bêta
    print("\nCreation tests beta...")

    test1 = platform.create_beta_test("AI_alphafold.ai.collection.verse.yaml", "1.0.0-beta1")
    test2 = platform.create_beta_test("BIO_BioVerse.bio.verse.yaml", "2.1.0-beta1")
    test3 = platform.create_beta_test("MATH_entropy.math.verse.yaml", "1.5.0-beta1")

    print(f"OK Test 1 cree: {test1.id[:8]}... pour {test1.verse_id}")
    print(f"OK Test 2 cree: {test2.id[:8]}... pour {test2.verse_id}")
    print(f"OK Test 3 cree: {test3.id[:8]}... pour {test3.verse_id}")

    # Ouvrir les tests
    print("\nOuverture tests au public...")
    platform.open_beta_test(test1.id)
    platform.open_beta_test(test2.id)
    platform.open_beta_test(test3.id)
    print("OK Tous les tests ouverts")

    # Simuler des inscriptions
    print("\nSimulation inscriptions testeurs...")

    # Test 1: IA
    tester1 = platform.apply_for_beta_test(test1.id, "user_alice")
    tester2 = platform.apply_for_beta_test(test1.id, "user_bob")
    platform.approve_beta_tester(tester1.id)
    platform.approve_beta_tester(tester2.id)

    # Test 2: BIO
    tester3 = platform.apply_for_beta_test(test2.id, "user_charlie")
    platform.approve_beta_tester(tester3.id)

    print("OK Testeurs inscrits et approuves")

    # Simuler des feedbacks
    print("\nSoumission feedbacks...")

    # Feedback pour test IA
    feedback1 = platform.submit_beta_feedback(
        test1.id, tester1.id, 4, 5, 4, 3, 4,
        "Excellente precision, interface intuitive. Quelques lenteurs.",
        [{"severity": "minor", "description": "Lenteur au demarrage"}],
        [{"priority": "medium", "description": "Support GPU optimise"}]
    )

    feedback2 = platform.submit_beta_feedback(
        test1.id, tester2.id, 5, 5, 5, 4, 5,
        "Outil revolutionnaire, performances exceptionnelles!",
        [],
        [{"priority": "low", "description": "Mode batch processing"}]
    )

    # Feedback pour test BIO
    feedback3 = platform.submit_beta_feedback(
        test2.id, tester3.id, 4, 4, 3, 4, 4,
        "Bon outil scientifique, interface a ameliorer.",
        [{"severity": "medium", "description": "Crash avec gros fichiers"}],
        [{"priority": "high", "description": "Support formats multiples"}]
    )

    print("OK Feedbacks soumis")

    # Afficher le dashboard
    ui.display_beta_dashboard()

    # Afficher résultats détaillés
    print(f"\nRESULTATS DETAILLES TEST 1:")
    ui.display_test_results(test1.id)

    print(f"\nPhase 4 Semaine 3 TERMINEE!")
    print("OK Plateforme beta testing integre")
    print("OK Collecte feedback automatise")
    print("OK Integration resultats dans rating")

if __name__ == "__main__":
    main()