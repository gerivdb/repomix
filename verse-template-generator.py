#!/usr/bin/env python3
"""
Verse Template Generator Automatique
Génère automatiquement des templates de verses à partir de sources académiques validées

Usage: python verse-template-generator.py --sources sources/schmidhuber-2003-godel-machines.yaml
"""

import yaml
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerseTemplateGenerator:
    """
    Générateur automatique de templates de verses depuis sources académiques
    """

    def __init__(self):
        # Mappings concepts NEXUS vers primitives
        self.nexus_mappings = self._load_nexus_mappings()

        # Templates par type de verse
        self.templates = self._load_templates()

    def _load_nexus_mappings(self) -> Dict[str, Any]:
        """Charge les mappings concepts NEXUS existants"""
        # Simulation mappings (en production, charger depuis ontologie)
        return {
            "self-improvement": {
                "primitives": ["get_concept_sources", "validate_concept"],
                "engines": ["reasoning_engine"],
                "categories": ["cognitive_enhancement"],
            },
            "universal_search": {
                "primitives": ["search_knowledge", "optimize_search"],
                "engines": ["search_engine"],
                "categories": ["algorithmic_search"],
            },
            "machine_learning": {
                "primitives": ["train_model", "predict_outcome"],
                "engines": ["ml_engine"],
                "categories": ["supervised_learning"],
            },
            "optimization": {
                "primitives": ["optimize_parameters", "evaluate_performance"],
                "engines": ["optimization_engine"],
                "categories": ["mathematical_optimization"],
            },
        }

    def _load_templates(self) -> Dict[str, str]:
        """Charge les templates de verses"""
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)

        # Template par défaut si aucun fichier trouvé
        default_template = """# VERSE: {VERSE_NAME}
## IntentHash: 0x{VERSE_HASH}
## Generated: {GENERATION_DATE}

Applies VERSES: {APPLIED_VERSES}

---

## ÉTABLI

Concepts issus de {SOURCE_TITLE} ({SOURCE_YEAR}):
{ESTABLISHED_CONTENT}

## VISÉ

Implémentation opérationnelle:
{VISION_CONTENT}

## LIMITES

{LIMITATIONS_CONTENT}

### 🎯 Objectif
{OBJECTIVE_CONTENT}

---

### 📋 Plan d'exécution

| Phase | Durée | Livrable |
|---|---|---|
{EXECUTION_PLAN}

---

### ✅ Caractéristiques fondamentales

{CHARACTERISTICS_CONTENT}

---

### 📋 Architecture

{ARCHITECTURE_CONTENT}

---

### ✅ Critères d'acceptation

{ACCEPTANCE_CRITERIA}

---

### ⚠️ Contraintes d'implémentation

{CONSTRAINTS_CONTENT}

---

### 🎯 Score final visé: 19.5 / 20

{DESCRIPTION_CONTENT}

---

### 📝 Sign-off
| Rôle | Nom | Date | Statut |
|---|---|---|---|
| Générateur | VerseTemplateGenerator | {GENERATION_DATE} | ✅ GENERATED |
"""

        return {"default": default_template}

    def generate_verse_template(
        self, source_files: List[str], output_dir: str = "verses/generated"
    ) -> List[Dict[str, Any]]:
        """
        Génère templates de verses depuis sources

        Args:
            source_files: Liste fichiers sources YAML
            output_dir: Répertoire sortie

        Returns:
            Liste résultats génération
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = []

        for source_file in source_files:
            try:
                source_path = Path(source_file)
                if not source_path.exists():
                    logger.error(f"Source introuvable: {source_file}")
                    continue

                # Charger source
                with open(source_path, "r", encoding="utf-8") as f:
                    source_data = yaml.safe_load(f)

                if not source_data:
                    logger.error(f"Source vide: {source_file}")
                    continue

                # Générer template
                verse_template = self._generate_single_template(source_data)

                # Sauvegarder
                verse_id = source_data.get("id", "unknown").replace("-", "_").upper()
                output_file = output_path / f"VERSE_{verse_id}_GENERATED.md"

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(verse_template)

                result = {
                    "source_file": source_file,
                    "verse_file": str(output_file),
                    "verse_id": verse_id,
                    "status": "success",
                    "concepts_extracted": len(source_data.get("concepts", [])),
                    "primitives_mapped": verse_template.count(
                        "get_concept_sources"
                    ),  # Rough count
                }

                results.append(result)
                logger.info(f"Template généré: {output_file}")

            except Exception as e:
                logger.error(f"Erreur génération template {source_file}: {e}")
                results.append(
                    {"source_file": source_file, "status": "error", "error": str(e)}
                )

        return results

    def _generate_single_template(self, source_data: Dict[str, Any]) -> str:
        """Génère un template verse depuis une source"""
        # Extraire informations clés
        source_id = source_data.get("id", "unknown")
        title = source_data.get("title", "Unknown Title")
        authors = source_data.get("authors", [])
        year = source_data.get("year", "Unknown Year")
        abstract = source_data.get("abstract", "")
        keywords = source_data.get("keywords", [])
        concepts = source_data.get("concepts", [])
        contributions = source_data.get("contributions", {})

        # Générer nom verse
        verse_name = self._generate_verse_name(source_id, concepts)

        # Extraire concepts clés et mappings
        key_concepts, primitives, engines, categories = (
            self._extract_concepts_and_mappings(concepts, keywords)
        )

        # Générer contenu template
        template_vars = {
            "VERSE_NAME": verse_name,
            "VERSE_HASH": self._generate_intent_hash(source_id),
            "GENERATION_DATE": datetime.now().strftime("%d/%m/%Y"),
            "APPLIED_VERSES": self._select_applied_verses(concepts),
            "SOURCE_TITLE": title,
            "SOURCE_YEAR": year,
            "ESTABLISHED_CONTENT": self._generate_established_content(
                concepts, contributions
            ),
            "VISION_CONTENT": self._generate_vision_content(key_concepts, primitives),
            "LIMITATIONS_CONTENT": self._generate_limitations_content(concepts),
            "OBJECTIVE_CONTENT": self._generate_objective_content(
                key_concepts, engines
            ),
            "EXECUTION_PLAN": self._generate_execution_plan(key_concepts),
            "CHARACTERISTICS_CONTENT": self._generate_characteristics_content(
                key_concepts
            ),
            "ARCHITECTURE_CONTENT": self._generate_architecture_content(
                primitives, engines
            ),
            "ACCEPTANCE_CRITERIA": self._generate_acceptance_criteria(primitives),
            "CONSTRAINTS_CONTENT": self._generate_constraints_content(categories),
            "DESCRIPTION_CONTENT": self._generate_description_content(title, concepts),
        }

        # Appliquer template
        template = self.templates.get("default", "")
        for key, value in template_vars.items():
            template = template.replace(f"{{{key}}}", str(value))

        return template

    def _generate_verse_name(self, source_id: str, concepts: List[str]) -> str:
        """Génère nom verse intelligent"""
        # Prendre premiers mots significatifs du source_id
        parts = source_id.replace("-", " ").split()
        if len(parts) >= 2:
            return f"{parts[0].upper()} {parts[1].upper()}"
        elif concepts:
            return concepts[0].upper().replace("_", " ")
        else:
            return "GENERATED_VERSE"

    def _generate_intent_hash(self, source_id: str) -> str:
        """Génère IntentHash simple"""
        # Hash simplifié pour template
        import hashlib

        hash_obj = hashlib.md5(source_id.encode())
        return f"VERSE_{hash_obj.hexdigest()[:8].upper()}"

    def _select_applied_verses(self, concepts: List[str]) -> str:
        """Sélectionne verses applicables"""
        # Mapping simple concepts -> verses
        verse_mapping = {
            "self-improvement": "sobriety-first",
            "optimization": "rigor-writing",
            "learning": "precision",
            "reasoning": "logic",
        }

        applied = []
        for concept in concepts:
            concept_lower = concept.lower()
            for key, verse in verse_mapping.items():
                if key in concept_lower and verse not in applied:
                    applied.append(verse)

        return ", ".join(applied) if applied else "rigor-writing"

    def _extract_concepts_and_mappings(
        self, concepts: List[str], keywords: List[str]
    ) -> tuple:
        """Extrait concepts et mappings NEXUS"""
        key_concepts = []
        primitives = []
        engines = []
        categories = []

        # Analyser concepts et keywords
        all_terms = concepts + keywords
        term_text = " ".join(all_terms).lower()

        for term, mapping in self.nexus_mappings.items():
            if term in term_text:
                key_concepts.extend([term] if term not in key_concepts else [])
                primitives.extend(mapping.get("primitives", []))
                engines.extend(mapping.get("engines", []))
                categories.extend(mapping.get("categories", []))

        # Déduplication
        primitives = list(set(primitives))
        engines = list(set(engines))
        categories = list(set(categories))

        # Concepts par défaut si aucun mapping
        if not key_concepts and concepts:
            key_concepts = concepts[:3]  # Prendre 3 premiers concepts
            primitives = [
                "get_concept_sources",
                "validate_concept",
            ]  # Primitives par défaut
            engines = ["reasoning_engine"]
            categories = ["general_cognition"]

        return key_concepts, primitives, engines, categories

    def _generate_established_content(
        self, concepts: List[str], contributions: Dict[str, Any]
    ) -> str:
        """Génère contenu ÉTABLI"""
        content = "- Concepts identifiés:\n"
        for concept in concepts[:5]:  # Max 5 concepts
            content += f"  - {concept}\n"

        if contributions:
            content += "\n- Contributions principales:\n"
            for category, items in contributions.items():
                if isinstance(items, list):
                    for item in items[:2]:  # Max 2 par catégorie
                        content += f"  - {category}: {item}\n"

        return content

    def _generate_vision_content(
        self, key_concepts: List[str], primitives: List[str]
    ) -> str:
        """Génère contenu VISÉ"""
        content = "- Implémentation concepts clés:\n"
        for concept in key_concepts:
            content += f"  - {concept}\n"

        content += "\n- Primitives opérationnelles:\n"
        for primitive in primitives:
            content += f"  - {primitive}\n"

        return content

    def _generate_limitations_content(self, concepts: List[str]) -> str:
        """Génère contenu LIMITES"""
        content = "- Complexité concepts avancés\n"
        content += "- Dépendance qualité données d'entraînement\n"
        content += "- Limitation contexte computationnel"

        return content

    def _generate_objective_content(
        self, key_concepts: List[str], engines: List[str]
    ) -> str:
        """Génère contenu OBJECTIF"""
        concept_str = ", ".join(key_concepts) if key_concepts else "concepts extraits"
        engine_str = ", ".join(engines) if engines else "engines génériques"

        content = f"Implémenter opérationnellement les {concept_str} "
        content += f"via {engine_str} intégrés dans l'écosystème NEXUS."

        return content

    def _generate_execution_plan(self, key_concepts: List[str]) -> str:
        """Génère plan d'exécution"""
        phases = [
            ("1", "2h", f"Extraction {len(key_concepts)} concepts clés"),
            ("2", "3h", "Développement primitives"),
            ("3", "2h", "Intégration engines"),
            ("4", "1h", "Tests et validation"),
        ]

        plan_lines = []
        for phase, duration, deliverable in phases:
            plan_lines.append(f"| {phase} | {duration} | {deliverable} |")

        return "\n".join(plan_lines)

    def _generate_characteristics_content(self, key_concepts: List[str]) -> str:
        """Génère caractéristiques"""
        chars = [
            ("🧠", "Intelligent", f"Implémentation {len(key_concepts)} concepts"),
            ("⚡", "Performant", "Optimisation temps réel"),
            ("🔗", "Intégré", "Compatible écosystème NEXUS"),
            ("🎯", "Précis", "Validation concepts >95%"),
        ]

        content_lines = []
        for icon, title, desc in chars:
            content_lines.append(f"| {icon} **{title}** | {desc} |")

        return "\n".join(content_lines)

    def _generate_architecture_content(
        self, primitives: List[str], engines: List[str]
    ) -> str:
        """Génère architecture"""
        content = "```mermaid\ngraph TD\n"
        content += "    A[Input Data] --> B[Primitives]\n"

        for i, primitive in enumerate(primitives):
            content += f"    B --> C{i}[{primitive}]\n"

        for i, engine in enumerate(engines):
            content += f"    C{i} --> D[Engine: {engine}]\n"

        content += "    D --> E[Output Results]\n```"

        return content

    def _generate_acceptance_criteria(self, primitives: List[str]) -> str:
        """Génère critères d'acceptation"""
        criteria = [
            f"- [ ] {len(primitives)} primitives opérationnelles",
            "- [ ] Tests automatiques passant",
            "- [ ] Performance >90% baseline",
            "- [ ] Intégration écosystème réussie",
        ]

        return "\n".join(criteria)

    def _generate_constraints_content(self, categories: List[str]) -> str:
        """Génère contraintes"""
        constraints = [
            "- ⚠️ Respect limites computationnelles",
            "- ⚠️ Validation sécurité avant déploiement",
            "- ⚠️ Compatibilité versions existantes",
        ]

        return "\n".join(constraints)

    def _generate_description_content(self, title: str, concepts: List[str]) -> str:
        """Génère description"""
        concept_str = ", ".join(concepts[:3]) if concepts else "concepts académiques"
        content = f"Implémentation opérationnelle des {concept_str} "
        content += f"extrait de '{title}' dans l'écosystème NEXUS."

        return content


def main():
    parser = argparse.ArgumentParser(
        description="Générateur automatique templates de verses"
    )
    parser.add_argument(
        "--sources", nargs="+", required=True, help="Fichiers sources YAML"
    )
    parser.add_argument(
        "--output-dir", default="verses/generated", help="Répertoire sortie"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbose")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    generator = VerseTemplateGenerator()

    print("[GENERATOR] Generating verse templates...")
    results = generator.generate_verse_template(args.sources, args.output_dir)

    print("\n[RESULTS] Generation Summary:")
    success_count = sum(1 for r in results if r.get("status") == "success")
    print(f"[SUCCESS] Generated: {success_count}/{len(results)}")

    for result in results:
        if result["status"] == "success":
            print(f"  [OK] {result['source_file']} -> {result['verse_file']}")
            print(
                f"    Concepts: {result['concepts_extracted']}, Primitives: {result['primitives_mapped']}"
            )
        else:
            print(
                f"  [ERROR] {result['source_file']}: {result.get('error', 'Erreur inconnue')}"
            )


if __name__ == "__main__":
    main()
