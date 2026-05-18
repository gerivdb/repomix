# WikiVerse - Documentation Interactive Exploratoire
# Implémentation principale du sous-verse de documentation selon PRD-DIAMOND-EVOLUTION-V16.md

import os
import json
import threading
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class ExplorationMode(Enum):
    """Modes d'exploration documentaire"""
    NAVIGATION = "NAVIGATION"  # Recherche rapide
    LEARNING = "LEARNING"      # Exploration approfondie


@dataclass
class WikiVerseConfig:
    """Configuration du WikiVerse"""
    base_path: str = "."
    exploration_mode: ExplorationMode = ExplorationMode.NAVIGATION
    semantic_search_enabled: bool = True
    adr_exploration_enabled: bool = True
    epic_tracking_enabled: bool = True
    context_building_enabled: bool = True
    max_context_depth: int = 3
    auto_index_documents: bool = True
    cache_enabled: bool = True


class WikiVerse:
    """
    WikiVerse - Documentation Interactive Exploratoire
    Point d'entrée principal pour toutes les fonctionnalités documentaires
    """

    def __init__(self, config: Optional[WikiVerseConfig] = None):
        self.config = config or WikiVerseConfig()

        # Initialisation des composants
        self.semantic_search = None
        self.adr_explorer = None
        self.epic_tracker = None
        self.context_builder = None
        self.query_interface = None
        self.benchmark_db = None

        # État interne
        self._document_index = {}
        self._exploration_active = False
        self._indexing_thread: Optional[threading.Thread] = None
        self._query_history: List[Dict] = []
        self._context_cache: Dict[str, Any] = {}

        # Métriques d'exploration
        self._exploration_metrics = {
            'total_queries': 0,
            'documents_indexed': 0,
            'context_builds': 0,
            'search_hits': 0,
            'adr_navigations': 0,
            'epic_views': 0
        }

        # Démarrage automatique de l'indexation si configuré
        if self.config.auto_index_documents:
            self.start_document_indexing()

    def start_document_indexing(self):
        """Démarre l'indexation automatique des documents"""
        if self._exploration_active:
            return

        self._exploration_active = True
        self._indexing_thread = threading.Thread(
            target=self._document_indexing_loop,
            daemon=True
        )
        self._indexing_thread.start()

    def stop_document_indexing(self):
        """Arrête l'indexation des documents"""
        self._exploration_active = False
        if self._indexing_thread:
            self._indexing_thread.join(timeout=5.0)

    def _document_indexing_loop(self):
        """Boucle d'indexation des documents"""
        while self._exploration_active:
            try:
                self._index_documents()
                # Indexation toutes les 5 minutes
                threading.Event().wait(300)
            except Exception as e:
                print(f"Erreur lors de l'indexation: {e}")
                threading.Event().wait(60)  # Retry après 1 minute

    def _index_documents(self):
        """Indexe les documents du système"""
        base_path = Path(self.config.base_path)

        # Documents à indexer
        document_patterns = [
            "**/*.md",      # Markdown files
            "**/*.txt",     # Text files
            "**/*.json",    # JSON configs
            "**/*.py",      # Python docs/code
            "**/ADR-*.md",  # ADR documents
            "**/EPIC-*.md"  # EPIC documents
        ]

        indexed_count = 0
        for pattern in document_patterns:
            for file_path in base_path.glob(pattern):
                if str(file_path).startswith('.'):  # Skip hidden files
                    continue

                try:
                    self._index_single_document(file_path)
                    indexed_count += 1
                except Exception as e:
                    print(f"Erreur indexation {file_path}: {e}")

        self._exploration_metrics['documents_indexed'] = indexed_count

    def _index_single_document(self, file_path: Path):
        """Indexe un document individuel"""
        file_key = str(file_path.relative_to(self.config.base_path))

        if file_key in self._document_index:
            # Vérifier si le fichier a changé
            current_mtime = file_path.stat().st_mtime
            if self._document_index[file_key].get('mtime') == current_mtime:
                return  # Pas de changement

        try:
            # Lire le contenu
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Extraire métadonnées
            metadata = self._extract_metadata(file_path, content)

            # Indexer
            self._document_index[file_key] = {
                'path': file_path,
                'content': content[:10000],  # Limiter la taille pour l'index
                'metadata': metadata,
                'indexed_at': datetime.now(),
                'mtime': file_path.stat().st_mtime,
                'size': len(content)
            }

        except Exception as e:
            print(f"Erreur lecture {file_path}: {e}")

    def _extract_metadata(self, file_path: Path, content: str) -> Dict:
        """Extrait les métadonnées d'un document"""
        metadata = {
            'filename': file_path.name,
            'extension': file_path.suffix,
            'size': len(content),
            'lines': len(content.split('\n'))
        }

        # Détection du type de document
        if 'ADR-' in file_path.name:
            metadata['type'] = 'ADR'
            metadata['adr_number'] = file_path.name.split('-')[1].split('.')[0]
        elif 'EPIC-' in file_path.name:
            metadata['type'] = 'EPIC'
            metadata['epic_number'] = file_path.name.split('-')[1].split('.')[0]
        elif file_path.name.startswith('PRD-'):
            metadata['type'] = 'PRD'
        elif file_path.name.endswith('.py'):
            metadata['type'] = 'CODE'
        else:
            metadata['type'] = 'DOCUMENT'

        # Extraire le titre (première ligne avec #)
        lines = content.split('\n')
        for line in lines[:10]:  # Premières 10 lignes
            if line.strip().startswith('#'):
                metadata['title'] = line.strip('#').strip()
                break

        return metadata

    def search_documents(self, query: str, context: Dict = None) -> List[Dict]:
        """
        Recherche sémantique dans les documents

        Args:
            query: Requête de recherche
            context: Contexte additionnel

        Returns:
            Liste des résultats de recherche
        """
        self._exploration_metrics['total_queries'] += 1

        results = []
        query_lower = query.lower()

        # Créer une copie pour éviter la modification pendant l'itération
        document_items = list(self._document_index.items())

        for file_key, doc_data in document_items:
            content = doc_data['content'].lower()
            metadata = doc_data['metadata']

            # Recherche simple (pour l'instant)
            score = 0
            if query_lower in content:
                score += 10

            # Recherche dans le titre
            if 'title' in metadata and query_lower in metadata['title'].lower():
                score += 20

            # Recherche dans le nom de fichier
            if query_lower in metadata['filename'].lower():
                score += 15

            if score > 0:
                results.append({
                    'file_key': file_key,
                    'metadata': metadata,
                    'score': score,
                    'snippet': self._extract_snippet(content, query_lower),
                    'path': str(doc_data['path'])
                })

        # Trier par score
        results.sort(key=lambda x: x['score'], reverse=True)

        self._exploration_metrics['search_hits'] += len(results)

        return results[:20]  # Limiter à 20 résultats

    def _extract_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Extrait un snippet autour de la requête"""
        query_pos = content.find(query)
        if query_pos == -1:
            return content[:max_length]

        start = max(0, query_pos - max_length // 2)
        end = min(len(content), start + max_length)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def get_document_content(self, file_key: str) -> Optional[Dict]:
        """Récupère le contenu complet d'un document"""
        if file_key not in self._document_index:
            return None

        doc_data = self._document_index[file_key]
        return {
            'metadata': doc_data['metadata'],
            'content': doc_data['content'],
            'path': str(doc_data['path']),
            'indexed_at': doc_data['indexed_at']
        }

    def explore_adr(self, adr_number: str = None) -> List[Dict]:
        """Explore les ADR (Architectural Decision Records)"""
        self._exploration_metrics['adr_navigations'] += 1

        if adr_number:
            # ADR spécifique
            for file_key, doc_data in self._document_index.items():
                if doc_data['metadata'].get('type') == 'ADR':
                    if doc_data['metadata'].get('adr_number') == adr_number:
                        return [self._format_document_result(file_key, doc_data)]
        else:
            # Tous les ADR
            adrs = []
            for file_key, doc_data in self._document_index.items():
                if doc_data['metadata'].get('type') == 'ADR':
                    adrs.append(self._format_document_result(file_key, doc_data))
            return adrs

        return []

    def track_epics(self, epic_number: str = None) -> List[Dict]:
        """Suit les EPICs (Epic Projects)"""
        self._exploration_metrics['epic_views'] += 1

        if epic_number:
            # EPIC spécifique
            for file_key, doc_data in self._document_index.items():
                if doc_data['metadata'].get('type') == 'EPIC':
                    if doc_data['metadata'].get('epic_number') == epic_number:
                        return [self._format_document_result(file_key, doc_data)]
        else:
            # Tous les EPICs
            epics = []
            for file_key, doc_data in self._document_index.items():
                if doc_data['metadata'].get('type') == 'EPIC':
                    epics.append(self._format_document_result(file_key, doc_data))
            return epics

        return []

    def _format_document_result(self, file_key: str, doc_data: Dict) -> Dict:
        """Formate un résultat de document"""
        return {
            'file_key': file_key,
            'metadata': doc_data['metadata'],
            'path': str(doc_data['path']),
            'indexed_at': doc_data['indexed_at'],
            'size': doc_data['size']
        }

    def build_context(self, query: str, depth: int = None) -> Dict:
        """
        Construit un contexte autour d'une requête

        Args:
            query: Requête centrale
            depth: Profondeur de contexte (optionnel)

        Returns:
            Contexte construit
        """
        if depth is None:
            depth = self.config.max_context_depth

        self._exploration_metrics['context_builds'] += 1

        # Recherche de documents liés
        related_docs = self.search_documents(query)

        context = {
            'query': query,
            'timestamp': datetime.now(),
            'related_documents': related_docs[:depth],
            'document_types': {},
            'key_concepts': [],
            'depth': depth
        }

        # Analyse des types de documents
        for doc in related_docs[:depth]:
            doc_type = doc['metadata'].get('type', 'UNKNOWN')
            context['document_types'][doc_type] = \
                context['document_types'].get(doc_type, 0) + 1

        # Cache du contexte
        context_key = f"{query}_{depth}"
        self._context_cache[context_key] = context

        return context

    def get_exploration_report(self) -> Dict:
        """Génère un rapport d'exploration"""
        return {
            "timestamp": datetime.now().isoformat(),
            "documents_indexed": len(self._document_index),
            "metrics": self._exploration_metrics.copy(),
            "document_types": self._analyze_document_types(),
            "recent_queries": self._query_history[-10:] if self._query_history else [],
            "exploration_mode": self.config.exploration_mode.value,
            "indexing_active": self._exploration_active
        }

    def _analyze_document_types(self) -> Dict:
        """Analyse la distribution des types de documents"""
        types = {}
        for doc_data in self._document_index.values():
            doc_type = doc_data['metadata'].get('type', 'UNKNOWN')
            types[doc_type] = types.get(doc_type, 0) + 1
        return types

    def natural_language_query(self, query: str) -> Dict:
        """
        Traite une requête en langage naturel

        Args:
            query: Requête naturelle

        Returns:
            Réponse structurée
        """
        # Analyse basique de l'intention
        intent = self._analyze_query_intent(query)

        # Recherche de documents
        search_results = self.search_documents(query)

        # Construction du contexte
        context = self.build_context(query, depth=2)

        # Génération de la réponse
        response = {
            'query': query,
            'intent': intent,
            'search_results': search_results,
            'context': context,
            'timestamp': datetime.now(),
            'response_type': 'documentary_repl'
        }

        # Ajout à l'historique
        self._query_history.append({
            'query': query,
            'results_count': len(search_results),
            'intent': intent,
            'timestamp': datetime.now()
        })

        # Limiter l'historique
        if len(self._query_history) > 100:
            self._query_history = self._query_history[-100:]

        return response

    def _analyze_query_intent(self, query: str) -> str:
        """Analyse l'intention d'une requête"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['adr', 'architectural', 'decision']):
            return 'ADR_EXPLORATION'
        elif any(word in query_lower for word in ['epic', 'project', 'feature']):
            return 'EPIC_TRACKING'
        elif any(word in query_lower for word in ['benchmark', 'performance', 'metrics']):
            return 'BENCHMARK_ANALYSIS'
        elif any(word in query_lower for word in ['how', 'what', 'why', 'explain']):
            return 'EXPLANATION'
        else:
            return 'GENERAL_SEARCH'

    def simulate_exploration_session(self, duration_seconds: int = 30):
        """Simule une session d'exploration pour démonstration"""
        print(f"Simulation d'exploration documentaire pendant {duration_seconds} secondes...")

        import random
        sample_queries = [
            "ADR architecture",
            "EPIC implementation",
            "performance benchmarks",
            "security policies",
            "quantum algorithms",
            "neural networks",
            "database optimization"
        ]

        start_time = datetime.now()
        query_count = 0

        while (datetime.now() - start_time).seconds < duration_seconds:
            query = random.choice(sample_queries)
            result = self.natural_language_query(query)
            query_count += 1

            status = f"[{datetime.now().strftime('%H:%M:%S')}] Query {query_count}: '{query}' -> {len(result['search_results'])} results"
            print(f"\r{status}", end="", flush=True)

            import time
            time.sleep(0.5)

        print("\nSimulation terminée.")
        print(f"Requêtes traitées: {query_count}")
        print(json.dumps(self.get_exploration_report(), indent=2, default=str))


# Instance globale pour faciliter l'accès
wiki_verse = WikiVerse()


if __name__ == "__main__":
    # Démonstration de base
    wv = WikiVerse()

    print("=== Démarrage WikiVerse ===")

    # Attendre un peu d'indexation
    import time
    time.sleep(2)

    # Simulation d'exploration
    wv.simulate_exploration_session(15)

    print("\n=== Rapport Final ===")
    report = wv.get_exploration_report()
    print(json.dumps(report, indent=2, default=str))

    # Arrêter l'indexation
    wv.stop_document_indexing()
    print("\nWikiVerse arrêté.")