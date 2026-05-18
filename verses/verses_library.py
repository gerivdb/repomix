#!/usr/bin/env python3
"""
Verses Library Engine
Programmatic access to ECOS Verses for automated governance

IntentHash: 0xVERSES_LIBRARY_ENGINE_20260423
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Verse:
    """Représentation programmatique d'un VERSE"""

    id: str
    name: str
    domain: str
    priority: str
    status: str
    core_principle: str
    invariants: List[str]
    forbidden_patterns: List[str]
    required_patterns: List[str]
    examples_compliant: List[str]
    examples_violations: List[str]
    enforcement_rules: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    def is_active(self) -> bool:
        """Vérifie si le VERSE est actif"""
        return self.status == "ACTIVE"

    def get_forbidden_patterns(self) -> List[str]:
        """Retourne les patterns interdits"""
        return self.forbidden_patterns

    def get_required_patterns(self) -> List[str]:
        """Retourne les patterns requis"""
        return self.required_patterns

    def validate_text(self, text: str) -> Dict[str, Any]:
        """Valide un texte contre ce VERSE"""
        violations = []
        compliances = []

        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern.lower() in text.lower():
                violations.append({
                    "type": "forbidden_pattern",
                    "pattern": pattern,
                    "message": f"Found forbidden pattern: {pattern}"
                })

        # Check required patterns
        for pattern in self.required_patterns:
            if pattern.lower() not in text.lower():
                violations.append({
                    "type": "missing_required",
                    "pattern": pattern,
                    "message": f"Missing required pattern: {pattern}"
                })
            else:
                compliances.append(pattern)

        return {
            "verse_id": self.id,
            "compliant": len(violations) == 0,
            "violations": violations,
            "compliances": compliances,
            "score": len(compliances) / (len(self.required_patterns) + len(self.forbidden_patterns)) if (len(self.required_patterns) + len(self.forbidden_patterns)) > 0 else 0
        }


class VersesLibrary:
    """Bibliothèque centralisée des VERSES ECOS"""

    def __init__(self, library_path: str = "verses"):
        self.library_path = Path(library_path)
        self.verses: Dict[str, Verse] = {}
        self.load_verses()

    def load_verses(self):
        """Charge tous les VERSES depuis les fichiers"""

        # Load from markdown files
        if self.library_path.exists():
            for md_file in self.library_path.glob("VERSE.*.md"):
                verse = self._parse_verse_from_md(md_file)
                if verse:
                    self.verses[verse.id] = verse

        # Load from programmatic definitions
        self._load_programmatic_verses()

    def _parse_verse_from_md(self, file_path: Path) -> Optional[Verse]:
        """Parse un VERSE depuis un fichier Markdown"""

        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Extract metadata from header
            metadata = {}
            in_header = False
            for line in lines[:20]:  # Check first 20 lines
                if line.startswith('**IntentHash:**'):
                    metadata['intent_hash'] = line.split('`')[1] if '`' in line else line.split(':')[1].strip()
                elif line.startswith('**Status:**'):
                    status_line = line.split(':')[1].strip()
                    metadata['status'] = status_line.split('|')[0].strip()
                    metadata['priority'] = status_line.split('|')[1].split(':')[1].strip() if '|' in line else 'MEDIUM'
                elif line.startswith('**Domain:**'):
                    metadata['domain'] = line.split(':')[1].strip().split('|')[0].strip()
                elif '**"' in line and '"' in line:
                    metadata['core_principle'] = line.split('"')[1]

            # Extract verse ID from filename
            verse_id = file_path.stem.replace('VERSE.', '')

            # Extract invariants and patterns
            invariants = []
            forbidden = []
            required = []
            examples_compliant = []
            examples_violations = []

            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('### ') and 'Invariant' in line:
                    current_section = 'invariants'
                elif line.startswith('### ✅ ACCEPTABLE'):
                    current_section = 'compliant'
                elif line.startswith('### ❌ UNACCEPTABLE'):
                    current_section = 'violations'
                elif line.startswith('### Absolute Requirements') or line.startswith('### Invariants'):
                    current_section = 'invariants'
                elif line.startswith('- **') and current_section == 'invariants':
                    invariants.append(line.replace('- **', '').replace('**', ''))
                elif line.startswith('```') and current_section in ['compliant', 'violations']:
                    # Extract code blocks
                    pass  # Simplified parsing

            # Create verse object
            return Verse(
                id=verse_id,
                name=verse_id.replace('-', ' ').title(),
                domain=metadata.get('domain', 'General'),
                priority=metadata.get('priority', 'MEDIUM'),
                status=metadata.get('status', 'ACTIVE'),
                core_principle=metadata.get('core_principle', ''),
                invariants=invariants,
                forbidden_patterns=forbidden,
                required_patterns=required,
                examples_compliant=examples_compliant,
                examples_violations=examples_violations,
                enforcement_rules={},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        except Exception as e:
            print(f"Error parsing verse {file_path}: {e}")
            return None

    def _load_programmatic_verses(self):
        """Charge les VERSES définis programmatiquement"""

        # Sobriety-First Verse
        if "sobriety-first" not in self.verses:
            self.verses["sobriety-first"] = Verse(
                id="sobriety-first",
                name="Sobriety First",
                domain="Documentation Ethics",
                priority="CRITICAL",
                status="ACTIVE",
                core_principle="Ce qui n'est pas mesuré objectivement n'existe pas. Ce qui n'est pas démontré empiriquement n'est pas vrai.",
                invariants=[
                    "No Surpromising - Every claim must be backed by measurable evidence",
                    "No Bullshit-Talk - Avoid hyperbolic language that cannot be verified",
                    "Measurable Claims Only - All benefits must have quantitative metrics",
                    "Source Citations - Every technical fact must reference official sources",
                    "Limitation Disclosure - Explicitly state what is NOT implemented"
                ],
                forbidden_patterns=[
                    "toujours", "jamais", "impossible", "parfait", "best", "worst", "ultimate", "supreme",
                    "definitively", "absolutely", "certainly", "quantum supremacy", "infinite", "eternal",
                    "zero hardware dependency", "transcending physical limitations"
                ],
                required_patterns=[
                    "Établi", "Visé", "Limites", "sobriety-first, rigor-writing"
                ],
                examples_compliant=[
                    "Hardware Detection: < 50ms (measured on Quadro 4000)",
                    "GPUCache Corruption: Reduced by 90% (7-day stability test)"
                ],
                examples_violations=[
                    "Quantum Supremacy Graphics Breakthrough",
                    "6,250,000 FPS Performance",
                    "Zero Hardware Dependency Rendering"
                ],
                enforcement_rules={
                    "block_on_violation": True,
                    "auto_correct": True,
                    "require_review": True
                },
                created_at=datetime(2026, 4, 23),
                updated_at=datetime(2026, 4, 23)
            )

        # Rigor-Writing Verse
        if "rigor-writing" not in self.verses:
            self.verses["rigor-writing"] = Verse(
                id="rigor-writing",
                name="Rigor Writing",
                domain="Documentation Structure",
                priority="HIGH",
                status="ACTIVE",
                core_principle="La structure rigoureuse révèle la pensée rigoureuse",
                invariants=[
                    "Établi/Visé/Limites structure obligatoire",
                    "Une affirmation = une preuve",
                    "Contexte obligatoire (Qui/Quoi/Quand/Où)",
                    "Limites explicitement documentées"
                ],
                forbidden_patterns=[
                    "sans précision", "approximativement", "environ", "probablement"
                ],
                required_patterns=[
                    "## Établi", "## Visé", "## Limites", "T0", "T1", "T2"
                ],
                examples_compliant=[
                    "## Établi\n- Fonction X implémentée (commit abc123)",
                    "## Limites\n- Ne fonctionne pas sous Windows XP"
                ],
                examples_violations=[
                    "Fonctionne bien",
                    "Performant"
                ],
                enforcement_rules={
                    "require_structure": True,
                    "validate_evidence": True,
                    "block_incomplete": True
                },
                created_at=datetime(2026, 4, 23),
                updated_at=datetime(2026, 4, 23)
            )

    def get_verse(self, verse_id: str) -> Optional[Verse]:
        """Récupère un VERSE par ID"""
        return self.verses.get(verse_id)

    def get_verses_by_domain(self, domain: str) -> List[Verse]:
        """Récupère les VERSES par domaine"""
        return [v for v in self.verses.values() if v.domain == domain]

    def get_active_verses(self) -> List[Verse]:
        """Récupère les VERSES actifs"""
        return [v for v in self.verses.values() if v.is_active()]

    def validate_text_against_verses(self, text: str, verse_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Valide un texte contre plusieurs VERSES"""

        if verse_ids is None:
            verses_to_check = self.get_active_verses()
        else:
            verses_to_check = [self.get_verse(vid) for vid in verse_ids if self.get_verse(vid)]

        results = {}
        overall_score = 0
        total_violations = 0

        for verse in verses_to_check:
            validation = verse.validate_text(text)
            results[verse.id] = validation
            overall_score += validation['score']
            total_violations += len(validation['violations'])

        overall_score = overall_score / len(verses_to_check) if verses_to_check else 0

        return {
            "overall_compliant": total_violations == 0,
            "overall_score": overall_score,
            "total_violations": total_violations,
            "verse_results": results,
            "recommendations": self._generate_recommendations(results)
        }

    def _generate_recommendations(self, results: Dict[str, Dict]) -> List[str]:
        """Génère des recommandations basées sur les résultats"""

        recommendations = []

        for verse_id, result in results.items():
            if not result['compliant']:
                verse = self.get_verse(verse_id)
                if verse:
                    if result['violations']:
                        recommendations.append(f"Fix {len(result['violations'])} violations in {verse.name}")
                    if not result['compliances']:
                        recommendations.append(f"Add required patterns for {verse.name}")

        return recommendations

    def get_applicable_verses(self, document_type: str, content: str = "") -> List[Verse]:
        """Détermine les VERSES applicables selon le type de document"""

        applicable = []

        # Domain-based selection
        if document_type in ["epic", "prd", "brain-doc"]:
            applicable.extend(self.get_verses_by_domain("Documentation Ethics"))
            applicable.extend(self.get_verses_by_domain("Documentation Structure"))

        elif document_type in ["incident", "forensic", "crash"]:
            applicable.extend(self.get_verses_by_domain("Hardware Analysis"))

        elif document_type in ["performance", "benchmark"]:
            applicable.extend(self.get_verses_by_domain("Documentation Ethics"))

        # Content-based hints (simplified)
        if content:
            content_lower = content.lower()
            if any(word in content_lower for word in ["gpu", "hardware", "driver", "crash"]):
                applicable.extend([v for v in self.get_active_verses() if "hardware" in v.domain.lower()])

        # Remove duplicates
        seen_ids = set()
        unique_applicable = []
        for verse in applicable:
            if verse.id not in seen_ids:
                unique_applicable.append(verse)
                seen_ids.add(verse.id)

        return unique_applicable

    def apply_verse_corrections(self, text: str, verse_ids: Optional[List[str]] = None) -> str:
        """Applique des corrections automatiques basées sur les VERSES"""

        if verse_ids is None:
            verses_to_apply = self.get_active_verses()
        else:
            verses_to_apply = [self.get_verse(vid) for vid in verse_ids if self.get_verse(vid)]

        corrected_text = text

        for verse in verses_to_apply:
            if verse.id == "sobriety-first":
                # Add VERSES citation if missing
                citation = "**VERSES:** sobriety-first, rigor-writing"
                if citation not in corrected_text:
                    # Add after frontmatter or at top
                    lines = corrected_text.split('\n')
                    insert_pos = 0

                    # Skip frontmatter
                    if lines and lines[0].startswith('---'):
                        for i, line in enumerate(lines[1:], 1):
                            if line.startswith('---'):
                                insert_pos = i + 1
                                break

                    lines.insert(insert_pos, citation)
                    lines.insert(insert_pos + 1, "")
                    corrected_text = '\n'.join(lines)

            elif verse.id == "rigor-writing":
                # Add basic structure if missing
                if "## Établi" not in corrected_text:
                    corrected_text += "\n\n## Établi\nTODO: Add established facts\n"
                if "## Visé" not in corrected_text:
                    corrected_text += "\n## Visé\nTODO: Add objectives\n"
                if "## Limites" not in corrected_text:
                    corrected_text += "\n## Limites\nTODO: Add limitations\n"

        return corrected_text

    def export_verses_to_json(self, output_path: str):
        """Exporte la bibliothèque vers JSON"""

        verses_data = {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "verses": {}
        }

        for verse_id, verse in self.verses.items():
            verses_data["verses"][verse_id] = {
                "id": verse.id,
                "name": verse.name,
                "domain": verse.domain,
                "priority": verse.priority,
                "status": verse.status,
                "core_principle": verse.core_principle,
                "invariants": verse.invariants,
                "forbidden_patterns": verse.forbidden_patterns,
                "required_patterns": verse.required_patterns,
                "examples_compliant": verse.examples_compliant,
                "examples_violations": verse.examples_violations,
                "enforcement_rules": verse.enforcement_rules,
                "created_at": verse.created_at.isoformat(),
                "updated_at": verse.updated_at.isoformat()
            }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(verses_data, f, indent=2, ensure_ascii=False)

    def get_verse_statistics(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les VERSES"""

        total_verses = len(self.verses)
        active_verses = len(self.get_active_verses())
        domains = {}
        priorities = {}

        for verse in self.verses.values():
            domains[verse.domain] = domains.get(verse.domain, 0) + 1
            priorities[verse.priority] = priorities.get(verse.priority, 0) + 1

        return {
            "total_verses": total_verses,
            "active_verses": active_verses,
            "inactive_verses": total_verses - active_verses,
            "domains": domains,
            "priorities": priorities,
            "verses_list": list(self.verses.keys())
        }