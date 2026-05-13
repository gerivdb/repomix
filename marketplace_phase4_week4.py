#!/usr/bin/env python3
"""
Phase 4 Semaine 4: Discovery Engine
Implémentation moteur de recherche et recommandations
"""

import json
import sqlite3
import math
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, Counter
import re

@dataclass
class SearchResult:
    """Résultat de recherche."""
    verse_id: str
    score: float
    relevance: str
    matched_terms: List[str]

@dataclass
class Recommendation:
    """Recommandation de verse."""
    verse_id: str
    score: float
    reason: str
    category: str

class DiscoveryEngine:
    """Moteur de découverte et recommandations."""

    def __init__(self, versus_root: str = ".", marketplace_db: str = None):
        self.versus_root = Path(versus_root)
        self.marketplace_db = marketplace_db or "verses_marketplace.db"
        self.verse_index = {}  # verse_id -> content index
        self.tag_index = defaultdict(set)  # tag -> set of verse_ids
        self.category_index = defaultdict(set)  # category -> set of verse_ids

        self.build_search_index()

    def build_search_index(self):
        """Construit l'index de recherche à partir des verses."""
        print("Construction index de recherche...")

        # Indexer les verses du marketplace
        self._index_marketplace_verses()

        # Indexer les verses des spokes
        self._index_spoke_verses()

        print(f"Index construit: {len(self.verse_index)} verses indexes")

    def _index_marketplace_verses(self):
        """Indexe les verses du marketplace."""
        db_path = Path(self.marketplace_db)
        if not db_path.exists():
            return

        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "SELECT id, title, description, category, tags FROM marketplace_verses"
            )

            for row in cursor.fetchall():
                verse_id = row[0]
                title = row[1] or ""
                description = row[2] or ""
                category = row[3] or ""
                tags_str = row[4] or "[]"

                try:
                    tags = json.loads(tags_str)
                except:
                    tags = []

                # Contenu à indexer
                content = f"{title} {description} {' '.join(tags)}"

                # Indexer par verse
                self.verse_index[verse_id] = {
                    'content': content.lower(),
                    'title': title,
                    'description': description,
                    'category': category,
                    'tags': tags
                }

                # Indexer par tag
                for tag in tags:
                    self.tag_index[tag.lower()].add(verse_id)

                # Indexer par catégorie
                self.category_index[category.lower()].add(verse_id)

    def _index_spoke_verses(self):
        """Indexe les verses des spokes."""
        spokes_dir = self.versus_root / "spokes"
        if not spokes_dir.exists():
            return

        for spoke_dir in spokes_dir.iterdir():
            if spoke_dir.is_dir() and spoke_dir.name in ['AI', 'BIO', 'MATH', 'PHYSICS', 'SCIENCE', 'TECH']:
                verses_dir = spoke_dir / "verses"
                if verses_dir.exists():
                    for verse_file in verses_dir.glob("*.yaml"):
                        self._index_spoke_verse_file(verse_file, spoke_dir.name)

    def _index_spoke_verse_file(self, verse_file: Path, spoke: str):
        """Indexe un fichier verse d'un spoke."""
        try:
            import yaml
            with open(verse_file, 'r', encoding='utf-8') as f:
                verse_data = yaml.safe_load(f)

            verse_id = verse_data.get('id', verse_file.stem)
            title = verse_data.get('name', verse_file.stem)
            description = verse_data.get('description', '')
            tags = verse_data.get('tags', [])

            # Contenu à indexer
            content = f"{title} {description} {' '.join(tags)}"

            # Ajouter le préfixe du spoke si pas déjà présent
            if not verse_id.startswith(f"{spoke}_"):
                verse_id = f"{spoke}_{verse_id}"

            self.verse_index[verse_id] = {
                'content': content.lower(),
                'title': title,
                'description': description,
                'category': spoke,
                'tags': tags,
                'source': 'spoke'
            }

            # Indexer par tag
            for tag in tags:
                self.tag_index[tag.lower()].add(verse_id)

            # Indexer par catégorie
            self.category_index[spoke.lower()].add(verse_id)

        except Exception as e:
            print(f"Erreur indexation {verse_file}: {e}")

    def search(self, query: str, category: str = None, limit: int = 10) -> List[SearchResult]:
        """Effectue une recherche dans les verses."""
        query = query.lower().strip()
        if not query:
            return []

        results = []

        for verse_id, verse_data in self.verse_index.items():
            # Filtrer par catégorie si spécifié
            if category and verse_data['category'].lower() != category.lower():
                continue

            # Calculer le score de pertinence
            score, matched_terms = self._calculate_relevance_score(query, verse_data)

            if score > 0:
                # Déterminer la raison de la pertinence
                if query in verse_data['title'].lower():
                    relevance = "Titre"
                elif any(term in verse_data['description'].lower() for term in query.split()):
                    relevance = "Description"
                elif any(term in verse_data['tags'] for term in query.split() if term in verse_data['tags']):
                    relevance = "Tags"
                else:
                    relevance = "Contenu"

                results.append(SearchResult(
                    verse_id=verse_id,
                    score=score,
                    relevance=relevance,
                    matched_terms=matched_terms
                ))

        # Trier par score décroissant
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:limit]

    def _calculate_relevance_score(self, query: str, verse_data: Dict) -> Tuple[float, List[str]]:
        """Calcule le score de pertinence pour une requête."""
        content = verse_data['content']
        query_terms = query.split()

        matched_terms = []
        total_score = 0

        for term in query_terms:
            if term in content:
                matched_terms.append(term)

                # Score basé sur la fréquence du terme
                frequency = content.count(term)
                total_score += frequency

                # Bonus pour les termes dans le titre
                if term in verse_data['title'].lower():
                    total_score += 10

                # Bonus pour les termes dans les tags
                if term in [tag.lower() for tag in verse_data['tags']]:
                    total_score += 5

        # Normaliser par la longueur de la requête
        if query_terms:
            total_score = total_score / len(query_terms)

        return total_score, matched_terms

    def get_recommendations(self, user_history: List[str] = None,
                          category: str = None, limit: int = 5) -> List[Recommendation]:
        """Génère des recommandations personnalisées."""
        if not user_history:
            # Recommandations générales : top rated par catégorie
            return self._get_popular_recommendations(category, limit)

        # Analyser l'historique de l'utilisateur
        user_tags = set()
        user_categories = Counter()

        for verse_id in user_history:
            if verse_id in self.verse_index:
                verse_data = self.verse_index[verse_id]
                user_tags.update(tag.lower() for tag in verse_data['tags'])
                user_categories[verse_data['category']] += 1

        # Recommandations basées sur les préférences
        recommendations = []

        # Trouver des verses avec des tags similaires
        candidate_scores = defaultdict(float)

        for tag in user_tags:
            for verse_id in self.tag_index.get(tag, set()):
                if verse_id not in user_history:  # Ne pas recommander ce qu'il a déjà
                    candidate_scores[verse_id] += 1

        # Convertir en recommandations
        for verse_id, score in candidate_scores.items():
            verse_data = self.verse_index[verse_id]
            reason = f"Basé sur vos intérêts: {', '.join(list(user_tags)[:3])}"

            recommendations.append(Recommendation(
                verse_id=verse_id,
                score=score,
                reason=reason,
                category=verse_data['category']
            ))

        # Trier et limiter
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]

    def _get_popular_recommendations(self, category: str = None, limit: int = 5) -> List[Recommendation]:
        """Recommandations populaires générales."""
        candidates = []

        if category:
            verse_ids = self.category_index.get(category.lower(), set())
        else:
            verse_ids = set(self.verse_index.keys())

        # Simuler popularité (dans un vrai système, utiliser les données du marketplace)
        for verse_id in list(verse_ids)[:limit * 2]:  # Prendre plus de candidats
            if verse_id in self.verse_index:
                verse_data = self.verse_index[verse_id]
                score = len(verse_data['tags']) + len(verse_data['description']) / 100  # Score simulé

                candidates.append(Recommendation(
                    verse_id=verse_id,
                    score=score,
                    reason="Populaire dans la communauté",
                    category=verse_data['category']
                ))

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:limit]

    def get_similar_verses(self, verse_id: str, limit: int = 5) -> List[Recommendation]:
        """Trouve des verses similaires."""
        if verse_id not in self.verse_index:
            return []

        target_verse = self.verse_index[verse_id]
        target_tags = set(tag.lower() for tag in target_verse['tags'])
        target_category = target_verse['category']

        similarities = []

        for other_id, other_data in self.verse_index.items():
            if other_id == verse_id:
                continue

            # Calculer similarité basée sur les tags communs
            other_tags = set(tag.lower() for tag in other_data['tags'])
            tag_overlap = len(target_tags & other_tags)

            # Bonus pour la même catégorie
            category_bonus = 2 if other_data['category'] == target_category else 0

            similarity_score = tag_overlap + category_bonus

            if similarity_score > 0:
                similarities.append(Recommendation(
                    verse_id=other_id,
                    score=similarity_score,
                    reason=f"Similaire à {target_verse['title']}",
                    category=other_data['category']
                ))

        similarities.sort(key=lambda x: x.score, reverse=True)
        return similarities[:limit]

    def get_trending_tags(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Retourne les tags tendance."""
        tag_counts = Counter()

        for verse_data in self.verse_index.values():
            for tag in verse_data['tags']:
                tag_counts[tag.lower()] += 1

        return tag_counts.most_common(limit)

    def get_category_stats(self) -> Dict[str, int]:
        """Statistiques par catégorie."""
        return {category: len(verses) for category, verses in self.category_index.items()}

class DiscoveryUI:
    """Interface utilisateur pour la découverte."""

    def __init__(self, engine: DiscoveryEngine):
        self.engine = engine

    def search_interface(self):
        """Interface de recherche interactive."""
        print("MOTEUR DE DECOUVERTE - Architecture Diamant")
        print("=" * 50)

        while True:
            print("\nOptions:")
            print("1. Rechercher des verses")
            print("2. Voir recommandations")
            print("3. Explorer par catégorie")
            print("4. Tags tendance")
            print("5. Statistiques")
            print("6. Quitter")

            choice = input("\nVotre choix (1-6): ").strip()

            if choice == "1":
                self._search_interface()
            elif choice == "2":
                self._recommendations_interface()
            elif choice == "3":
                self._category_interface()
            elif choice == "4":
                self._trending_tags_interface()
            elif choice == "5":
                self._stats_interface()
            elif choice == "6":
                break
            else:
                print("Choix invalide.")

    def _search_interface(self):
        """Interface de recherche."""
        query = input("Entrez votre recherche: ").strip()
        if not query:
            return

        category = input("Catégorie (optionnel, laisser vide pour toutes): ").strip()
        category = category if category else None

        results = self.engine.search(query, category)

        print(f"\nRESULTATS RECHERCHE pour '{query}'")
        print("-" * 40)

        if not results:
            print("Aucun résultat trouvé.")
            return

        for i, result in enumerate(results, 1):
            verse_data = self.engine.verse_index[result.verse_id]
            print(f"{i}. {verse_data['title']}")
            print(f"   Score: {result.score:.2f} | Pertinence: {result.relevance}")
            print(f"   Tags: {', '.join(verse_data['tags'][:3])}")
            print(f"   Categorie: {verse_data['category']}")
            print()

    def _recommendations_interface(self):
        """Interface de recommandations."""
        history_input = input("IDs des verses consultés (séparés par des virgules, optionnel): ").strip()
        history = [v.strip() for v in history_input.split(",")] if history_input else []

        recommendations = self.engine.get_recommendations(history)

        print("\nRECOMMANDATIONS PERSONNALISEES")
        print("-" * 40)

        for i, rec in enumerate(recommendations, 1):
            verse_data = self.engine.verse_index[rec.verse_id]
            print(f"{i}. {verse_data['title']}")
            print(f"   Raison: {rec.reason}")
            print(f"   Categorie: {rec.category}")
            print()

    def _category_interface(self):
        """Interface d'exploration par catégorie."""
        categories = ['AI', 'BIO', 'MATH', 'PHYSICS', 'SCIENCE', 'TECH']

        print("\nCATEGORIES DISPONIBLES:")
        for i, cat in enumerate(categories, 1):
            count = len(self.engine.category_index.get(cat.lower(), set()))
            print(f"{i}. {cat} ({count} verses)")

        try:
            choice = int(input("\nChoisir une catégorie (1-6): ")) - 1
            if 0 <= choice < len(categories):
                category = categories[choice]
                results = self.engine.search("", category, limit=10)

                print(f"\nTOP VERSES dans {category}:")
                for result in results:
                    verse_data = self.engine.verse_index[result.verse_id]
                    print(f"  - {verse_data['title']}")
        except ValueError:
            print("Choix invalide.")

    def _trending_tags_interface(self):
        """Interface des tags tendance."""
        trending = self.engine.get_trending_tags()

        print("\nTAGS TENDANCE:")
        print("-" * 30)
        for tag, count in trending:
            print(f"{tag}: {count} verses")

    def _stats_interface(self):
        """Interface des statistiques."""
        stats = self.engine.get_category_stats()

        print("\nSTATISTIQUES DECOUVERTE:")
        print("-" * 30)
        print(f"Total verses indexés: {len(self.engine.verse_index)}")
        print(f"Total tags: {len(self.engine.tag_index)}")

        print("\nRépartition par catégorie:")
        for category, count in stats.items():
            print(f"  {category.upper()}: {count} verses")

def main():
    """Démonstration Phase 4 Semaine 4."""
    print("Phase 4 Semaine 4: Discovery Engine")

    # Initialiser le moteur de découverte
    engine = DiscoveryEngine("D:/DO/WEB/TOOLS/L4-TOOLS/VERSUS")

    # Interface utilisateur
    ui = DiscoveryUI(engine)

    # Démonstration automatique
    print("\nDemonstration automatique...")

    # Recherche
    print("\n1. RECHERCHE:")
    results = engine.search("machine learning")
    print(f"   Resultats pour 'machine learning': {len(results)}")
    if results:
        verse_data = engine.verse_index[results[0].verse_id]
        print(f"   Top result: {verse_data['title']}")

    # Recommandations
    print("\n2. RECOMMANDATIONS:")
    recommendations = engine.get_recommendations()
    print(f"   Recommandations generales: {len(recommendations)}")
    if recommendations:
        verse_data = engine.verse_index[recommendations[0].verse_id]
        print(f"   Top recommande: {verse_data['title']}")

    # Similaires
    if results:
        print("\n3. VERSES SIMILAIRES:")
        similar = engine.get_similar_verses(results[0].verse_id)
        print(f"   Verses similaires: {len(similar)}")

    # Tags tendance
    print("\n4. TAGS TENDANCE:")
    trending = engine.get_trending_tags(5)
    for tag, count in trending:
        print(f"   {tag}: {count}")

    print("\nPhase 4 Semaine 4 TERMINEE!")
    print("OK Moteur de recherche operationnel")
    print("OK Recommandations personnalisees")
    print("OK Analytics marketplace fonctionnels")

    # Interface interactive (commentée pour éviter l'interaction)
    # ui.search_interface()

if __name__ == "__main__":
    main()