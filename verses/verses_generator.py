#!/usr/bin/env python3
"""
Verses Generator Engine
Automated generation of VERSES based on patterns and ontology

IntentHash: 0xVERSES_GENERATOR_ENGINE_20260423
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class VersePattern(Enum):
    """Patterns for automated VERSE generation"""

    ETHICS_BASED = "ethics_based"
    STRUCTURE_BASED = "structure_based"
    DOMAIN_SPECIFIC = "domain_specific"
    VIOLATION_DRIVEN = "violation_driven"
    COMPLIANCE_ENHANCEMENT = "compliance_enhancement"


@dataclass
class GeneratedVerse:
    """Generated VERSE structure"""

    id: str
    name: str
    domain: str
    priority: str
    core_principle: str
    invariants: List[str]
    forbidden_patterns: List[str]
    required_patterns: List[str]
    examples_compliant: List[str]
    examples_violations: List[str]
    enforcement_rules: Dict[str, Any]
    confidence_score: float
    generated_from: str


class VersesGenerator:
    """Engine de génération automatique de VERSES"""

    def __init__(self, ontology_path: str = "ONTOLOGY/constitution_ontology_definitions.json"):
        self.ontology_path = Path(ontology_path)
        self.ontology = self._load_ontology()
        self.patterns_library = self._load_patterns()

    def _load_ontology(self) -> Dict[str, Any]:
        """Charge l'ontologie constitutionnelle"""
        if self.ontology_path.exists():
            with open(self.ontology_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Charge les patterns de génération"""

        return {
            "ethics_patterns": {
                "absolute_terms": [
                    "toujours", "jamais", "impossible", "parfait", "best", "worst",
                    "ultimate", "supreme", "definitively", "absolutely", "certainly"
                ],
                "unproven_claims": [
                    r"\b\d+x\s+performance\b", r"\bzero\s+\w+\b", r"\binfinite\s+\w+\b",
                    r"\beternal\s+\w+\b", r"\bquantum\s+supremacy\b"
                ],
                "missing_evidence": [
                    r"\b(fonctionne|performant|optimal)\b",
                    r"\b(améliore|augmente|réduit)\b.*\b(\d+%)?\b"
                ]
            },
            "structure_patterns": {
                "required_sections": ["Établi", "Visé", "Limites"],
                "evidence_markers": ["log", "benchmark", "test", "commit", "official"],
                "context_indicators": ["OS", "version", "hardware", "environment"]
            },
            "domain_patterns": {
                "hardware": {
                    "keywords": ["gpu", "cpu", "driver", "hardware", "crash", "performance"],
                    "required_context": ["machine", "OS", "driver version", "gpu model"],
                    "forbidden_claims": ["works everywhere", "no dependencies", "perfect stability"]
                },
                "security": {
                    "keywords": ["security", "encryption", "auth", "vulnerability", "breach"],
                    "required_context": ["threat model", "encryption type", "key management"],
                    "forbidden_claims": ["unbreakable", "perfect security", "zero risk"]
                },
                "performance": {
                    "keywords": ["performance", "latency", "throughput", "benchmark", "optimization"],
                    "required_context": ["baseline", "measurement method", "environment"],
                    "forbidden_claims": ["fastest", "ultimate performance", "infinite scale"]
                }
            }
        }

    def generate_verse_from_violations(self, violations: List[Dict[str, Any]],
                                     document_type: str = "general") -> GeneratedVerse:
        """Génère un VERSE basé sur des violations observées"""

        # Analyze violation patterns
        violation_patterns = self._analyze_violation_patterns(violations)

        # Determine domain
        domain = self._infer_domain_from_violations(violations, document_type)

        # Generate core principle
        core_principle = self._generate_core_principle(violation_patterns, domain)

        # Generate invariants
        invariants = self._generate_invariants(violation_patterns, domain)

        # Extract patterns
        forbidden_patterns = violation_patterns.get("forbidden", [])
        required_patterns = violation_patterns.get("required", [])

        # Generate examples
        examples_compliant = self._generate_compliant_examples(forbidden_patterns, domain)
        examples_violations = self._generate_violation_examples(forbidden_patterns, domain)

        # Determine confidence
        confidence = self._calculate_generation_confidence(violations, violation_patterns)

        verse_id = f"generated_{domain}_{int(datetime.now().timestamp())}"

        return GeneratedVerse(
            id=verse_id,
            name=f"Generated {domain.title()} Compliance",
            domain=domain,
            priority=self._determine_priority(violations),
            core_principle=core_principle,
            invariants=invariants,
            forbidden_patterns=forbidden_patterns,
            required_patterns=required_patterns,
            examples_compliant=examples_compliant,
            examples_violations=examples_violations,
            enforcement_rules=self._generate_enforcement_rules(domain),
            confidence_score=confidence,
            generated_from="violation_analysis"
        )

    def generate_domain_specific_verse(self, domain: str, requirements: Dict[str, Any]) -> GeneratedVerse:
        """Génère un VERSE spécifique à un domaine"""

        domain_patterns = self.patterns_library["domain_patterns"].get(domain, {})

        # Merge requirements with domain patterns
        all_requirements = {**domain_patterns, **requirements}

        core_principle = all_requirements.get("core_principle",
            f"Domain-specific compliance for {domain}")

        invariants = all_requirements.get("invariants", [
            f"Follow {domain} best practices",
            f"Include {domain} context information",
            f"Avoid {domain} hype claims"
        ])

        forbidden_patterns = all_requirements.get("forbidden_claims", [])
        required_patterns = all_requirements.get("required_context", [])

        # Generate examples based on domain
        examples_compliant = self._generate_domain_compliant_examples(domain, required_patterns)
        examples_violations = self._generate_domain_violation_examples(domain, forbidden_patterns)

        verse_id = f"domain_{domain}_{int(datetime.now().timestamp())}"

        return GeneratedVerse(
            id=verse_id,
            name=f"{domain.title()} Domain Compliance",
            domain=domain,
            priority="HIGH",
            core_principle=core_principle,
            invariants=invariants,
            forbidden_patterns=forbidden_patterns,
            required_patterns=required_patterns,
            examples_compliant=examples_compliant,
            examples_violations=examples_violations,
            enforcement_rules=self._generate_enforcement_rules(domain),
            confidence_score=0.85,
            generated_from="domain_requirements"
        )

    def generate_structure_enhancement_verse(self, structure_type: str) -> GeneratedVerse:
        """Génère un VERSE pour améliorer la structure documentaire"""

        structures = {
            "etabli_vise_limites": {
                "name": "Établi/Visé/Limites Structure",
                "core_principle": "La structure rigoureuse révèle la pensée rigoureuse",
                "invariants": [
                    "Établi/Visé/Limites structure obligatoire",
                    "Établi contient seulement des faits établis",
                    "Visé contient des objectifs mesurables",
                    "Limites liste explicitement les contraintes"
                ],
                "required_patterns": ["## Établi", "## Visé", "## Limites"],
                "forbidden_patterns": ["## Objectifs", "## Fonctionnalités", "## TODO"]
            },
            "evidence_based": {
                "name": "Evidence-Based Documentation",
                "core_principle": "Une affirmation technique = une preuve technique",
                "invariants": [
                    "Chaque affirmation a une source de preuve",
                    "Preuves sont vérifiables et actuelles",
                    "Manque de preuve = manque de fonctionnalité",
                    "Sources externes préférées aux affirmations internes"
                ],
                "required_patterns": ["log", "benchmark", "test", "commit"],
                "forbidden_patterns": ["je pense", "il semble", "probablement"]
            }
        }

        structure_config = structures.get(structure_type, structures["etabli_vise_limites"])

        verse_id = f"structure_{structure_type}_{int(datetime.now().timestamp())}"

        return GeneratedVerse(
            id=verse_id,
            name=structure_config["name"],
            domain="Documentation Structure",
            priority="HIGH",
            core_principle=structure_config["core_principle"],
            invariants=structure_config["invariants"],
            forbidden_patterns=structure_config["forbidden_patterns"],
            required_patterns=structure_config["required_patterns"],
            examples_compliant=self._generate_structure_examples(structure_type, "compliant"),
            examples_violations=self._generate_structure_examples(structure_type, "violations"),
            enforcement_rules={
                "require_structure": True,
                "auto_add_sections": True,
                "block_incomplete": True
            },
            confidence_score=0.95,
            generated_from="structure_template"
        )

    def _analyze_violation_patterns(self, violations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyse les patterns de violations"""

        patterns = {
            "forbidden": [],
            "required": [],
            "domains": set(),
            "severities": []
        }

        for violation in violations:
            rule_id = violation.get("rule_id", "")
            message = violation.get("message", "")
            severity = violation.get("severity", "")

            patterns["severities"].append(severity)

            # Extract forbidden terms
            if "forbidden" in rule_id or "absolute" in rule_id:
                # Extract terms from message or use rule knowledge
                if "absolute term" in message:
                    patterns["forbidden"].extend(["toujours", "jamais", "impossible"])

            # Extract missing requirements
            if "missing" in message.lower():
                if "section" in message:
                    patterns["required"].extend(["## Établi", "## Visé", "## Limites"])
                elif "evidence" in message:
                    patterns["required"].extend(["log", "benchmark", "test"])

            # Infer domain
            content = f"{rule_id} {message}"
            if any(word in content.lower() for word in ["gpu", "hardware", "driver"]):
                patterns["domains"].add("hardware")
            elif any(word in content.lower() for word in ["security", "auth", "encrypt"]):
                patterns["domains"].add("security")

        # Remove duplicates
        patterns["forbidden"] = list(set(patterns["forbidden"]))
        patterns["required"] = list(set(patterns["required"]))
        patterns["domains"] = list(patterns["domains"])

        return patterns

    def _infer_domain_from_violations(self, violations: List[Dict[str, Any]], doc_type: str) -> str:
        """Infère le domaine depuis les violations"""

        content = " ".join([str(v) for v in violations])

        if doc_type == "epic":
            return "Project Management"
        elif doc_type == "prd":
            return "Product Requirements"
        elif any(word in content.lower() for word in ["gpu", "hardware", "crash"]):
            return "Hardware Analysis"
        elif any(word in content.lower() for word in ["security", "auth", "encrypt"]):
            return "Security"
        elif any(word in content.lower() for word in ["performance", "latency", "benchmark"]):
            return "Performance"
        else:
            return "Documentation Ethics"

    def _generate_core_principle(self, patterns: Dict[str, List[str]], domain: str) -> str:
        """Génère un principe core basé sur les patterns"""

        domain_principles = {
            "hardware": "Analyser le hardware comme une scène de crime",
            "security": "La sécurité parfaite n'existe pas, seulement la sécurité suffisante",
            "performance": "La performance mesurée est la seule performance réelle",
            "documentation": "La documentation rigoureuse révèle la pensée rigoureuse"
        }

        return domain_principles.get(domain.lower(), "La rigueur technique est la base de la confiance")

    def _generate_invariants(self, patterns: Dict[str, List[str]], domain: str) -> List[str]:
        """Génère des invariants basés sur les patterns"""

        base_invariants = [
            "Éviter les termes absolus non prouvés",
            "Exiger des preuves pour les affirmations fortes",
            "Fournir un contexte technique complet"
        ]

        if domain.lower() == "hardware":
            base_invariants.extend([
                "Documenter l'environnement complet (OS, drivers, hardware)",
                "Fournir timeline détaillé pour les incidents",
                "Séparer observation de supposition"
            ])
        elif domain.lower() == "security":
            base_invariants.extend([
                "Spécifier le modèle de menaces",
                "Décrire les mécanismes de protection",
                "Admettre les limites de sécurité"
            ])

        return base_invariants

    def _generate_compliant_examples(self, forbidden_patterns: List[str], domain: str) -> List[str]:
        """Génère des exemples conformes"""

        examples = []

        if "toujours" in forbidden_patterns:
            examples.append("Hardware Detection: < 50ms (mesuré sur Quadro 4000)")
            examples.append("GPUCache Corruption: Réduit de 90% (test de stabilité 7 jours)")

        if domain.lower() == "hardware":
            examples.extend([
                "## Établi\n- Driver NVIDIA 525.60.13 testé (commit abc123)",
                "## Limites\n- Non compatible Windows XP"
            ])

        return examples[:5]  # Limit to 5 examples

    def _generate_violation_examples(self, forbidden_patterns: List[str], domain: str) -> List[str]:
        """Génère des exemples de violations"""

        examples = []

        if "toujours" in forbidden_patterns:
            examples.append("Fonctionne toujours parfaitement")
            examples.append("Jamais de crash")

        if domain.lower() == "hardware":
            examples.extend([
                "Zero dépendance hardware",
                "Performance ultime garantie",
                "Compatible partout"
            ])

        return examples[:5]

    def _calculate_generation_confidence(self, violations: List[Dict[str, Any]],
                                       patterns: Dict[str, List[str]]) -> float:
        """Calcule la confiance dans la génération"""

        base_confidence = 0.7

        # More violations = higher confidence
        violation_count = len(violations)
        if violation_count > 10:
            base_confidence += 0.1
        elif violation_count < 3:
            base_confidence -= 0.1

        # Clear patterns = higher confidence
        if patterns["forbidden"]:
            base_confidence += 0.1
        if patterns["required"]:
            base_confidence += 0.1

        # Domain specificity = higher confidence
        if patterns["domains"]:
            base_confidence += 0.1

        return min(base_confidence, 0.95)

    def _determine_priority(self, violations: List[Dict[str, Any]]) -> str:
        """Détermine la priorité du VERSE généré"""

        error_count = sum(1 for v in violations if v.get("severity") == "ERROR")
        critical_count = sum(1 for v in violations if v.get("severity") == "CRITICAL")

        if critical_count > 0 or error_count > 5:
            return "CRITICAL"
        elif error_count > 0:
            return "HIGH"
        else:
            return "MEDIUM"

    def _generate_enforcement_rules(self, domain: str) -> Dict[str, Any]:
        """Génère les règles d'enforcement"""

        base_rules = {
            "block_on_violation": True,
            "auto_correct": False,
            "require_review": True
        }

        if domain.lower() in ["hardware", "security"]:
            base_rules["auto_correct"] = False  # Never auto-correct critical domains
            base_rules["require_review"] = True

        return base_rules

    def _generate_domain_compliant_examples(self, domain: str, required_patterns: List[str]) -> List[str]:
        """Génère des exemples conformes pour un domaine"""

        examples = {
            "hardware": [
                "GPU: NVIDIA RTX 4070, Driver 525.60.13 (Ubuntu 22.04)",
                "CPU: Intel Xeon E5-2620, 32GB RAM",
                "Performance mesurée: 1450 FPS (1080p, ultra settings)"
            ],
            "security": [
                "Encryption: AES-256-GCM (clé 32 bytes)",
                "Auth: JWT RS256 avec expiration 1h",
                "Audit: Tous accès loggés avec timestamps"
            ],
            "performance": [
                "Latence moyenne: 45ms (p95: 120ms)",
                "Throughput: 1250 req/sec (load test 1h)",
                "Baseline: Version précédente 890 req/sec"
            ]
        }

        return examples.get(domain.lower(), ["Exemple conforme générique"])

    def _generate_domain_violation_examples(self, domain: str, forbidden_patterns: List[str]) -> List[str]:
        """Génère des exemples de violations pour un domaine"""

        examples = {
            "hardware": [
                "Fonctionne sur tous GPUs",
                "Zero dépendance driver",
                "Performance ultime garantie"
            ],
            "security": [
                "Chiffrement incassable",
                "Sécurité parfaite",
                "Jamais de faille"
            ],
            "performance": [
                "Fastest implementation ever",
                "Infinite scalability",
                "Zero latency guaranteed"
            ]
        }

        return examples.get(domain.lower(), ["Violation générique"])

    def _generate_structure_examples(self, structure_type: str, example_type: str) -> List[str]:
        """Génère des exemples de structure"""

        examples = {
            "etabli_vise_limites": {
                "compliant": [
                    "## Établi\n- API REST implémentée (commit abc123)\n- Tests unitaires passent (94% coverage)",
                    "## Visé\n- Atteindre 99% uptime\n- Supporter 1000 req/sec",
                    "## Limites\n- Non compatible IE11\n- Requiert HTTPS"
                ],
                "violations": [
                    "# Fonctionnalités\n- Authentification\n- API REST\n- Base de données",
                    "TODO: Implémenter sécurité\nTODO: Ajouter tests"
                ]
            },
            "evidence_based": {
                "compliant": [
                    "Latence réseau: <10ms (mesuré avec iperf, 1000 échantillons)",
                    "Sécurité: Résiste aux attaques connues (OWASP Top 10 testé)",
                    "Performance: 2.3x plus rapide (vs version précédente, bench.sql)"
                ],
                "violations": [
                    "Très performant",
                    "Sécurisé à 100%",
                    "Fonctionne parfaitement"
                ]
            }
        }

        structure_examples = examples.get(structure_type, examples["etabli_vise_limites"])
        return structure_examples.get(example_type, [])

    def export_generated_verses(self, verses: List[GeneratedVerse], output_path: str):
        """Exporte les VERSES générés"""

        verses_data = {
            "generated_at": datetime.now().isoformat(),
            "verses": []
        }

        for verse in verses:
            verse_dict = {
                "id": verse.id,
                "name": verse.name,
                "domain": verse.domain,
                "priority": verse.priority,
                "core_principle": verse.core_principle,
                "invariants": verse.invariants,
                "forbidden_patterns": verse.forbidden_patterns,
                "required_patterns": verse.required_patterns,
                "examples_compliant": verse.examples_compliant,
                "examples_violations": verse.examples_violations,
                "enforcement_rules": verse.enforcement_rules,
                "confidence_score": verse.confidence_score,
                "generated_from": verse.generated_from,
                "generated_at": datetime.now().isoformat()
            }
            verses_data["verses"].append(verse_dict)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(verses_data, f, indent=2, ensure_ascii=False)

    def generate_comprehensive_verses_suite(self) -> List[GeneratedVerse]:
        """Génère une suite complète de VERSES"""

        verses = []

        # Generate domain-specific verses
        for domain in ["hardware", "security", "performance", "networking"]:
            verse = self.generate_domain_specific_verse(domain, {})
            verses.append(verse)

        # Generate structure enhancement verses
        for structure in ["etabli_vise_limites", "evidence_based"]:
            verse = self.generate_structure_enhancement_verse(structure)
            verses.append(verse)

        # Generate ethics-based verse
        ethics_verse = GeneratedVerse(
            id=f"ethics_comprehensive_{int(datetime.now().timestamp())}",
            name="Comprehensive Ethics Compliance",
            domain="Ethics",
            priority="CRITICAL",
            core_principle="L'éthique technique est la base de la confiance durable",
            invariants=[
                "Admettre les imperfections",
                "Fournir des garanties réalistes",
                "Éviter les promesses impossibles",
                "Maintenir l'honnêteté intellectuelle"
            ],
            forbidden_patterns=[
                "parfait", "jamais", "toujours", "impossible", "best ever",
                "ultimate", "supreme", "zero risk", "infinite"
            ],
            required_patterns=[
                "limites", "contraintes", "hypothèses", "conditions"
            ],
            examples_compliant=[
                "Sécurité renforcée contre les attaques connues",
                "Performance améliorée de 40% dans les tests",
                "Compatible avec les environnements standardisés"
            ],
            examples_violations=[
                "Sécurité parfaite garantie",
                "Performance ultime atteinte",
                "Fonctionne partout sans exception"
            ],
            enforcement_rules={
                "block_on_violation": True,
                "require_ethics_review": True,
                "auto_correct_minor": True
            },
            confidence_score=0.90,
            generated_from="comprehensive_ethics_template"
        )
        verses.append(ethics_verse)

        return verses