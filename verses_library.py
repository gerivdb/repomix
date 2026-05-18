"""
Verses Library - NEXUS Advanced Ecosystem
Management system for quantum verses and creative content
"""

import json
import os
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
from verses_creative_foundation import (
    BaseQuantumVerse,
    QuantumPoetryVerse,
    AnticipatoryNarrativeVerse,
    ArchitectureVerse,
    DebugVerse,
    TeamHarmonyVerse,
    CodeEleganceVerse,
    AlgorithmicSonnetVerse,
    DatabaseSymphonyVerse,
    APISerenadeVerse,
    QuantumFractalVerse,
    BlockchainBalladVerse,
    MachineLearningOdeVerse,
    CybersecuritySonataVerse,
    DevOpsRhapsodyVerse,
    QuantumEntanglementVerse,
    DataVisualizationWaltzVerse,
    CloudComputingConcertoVerse,
    IoTIntermezzoVerse,
    AugmentedRealityAriaVerse,
    NaturalLanguageOperaVerse,
    RoboticSymphonyVerse,
    QuantumCryptographyCantataVerse,
    SwarmIntelligenceChorusVerse,
    VirtualRealityFantasiaVerse,
    EdgeComputingEtudeVerse,
    GeneticAlgorithmRondoVerse,
    BlockchainConsensusCapriceVerse,
    NeuralNetworkNocturneVerse,
    ContainerOrchestrationOvertureVerse,
    QuantumSupremacySonataVerse,
    HumanComputerInteractionMinuetVerse,
    BioinformaticsBalletVerse,
    AutonomousSystemsSymphonyVerse,
    DigitalTwinConcertoVerse,
    EthicalAICantataVerse,
    MetaverseOperaVerse,
    SustainableTechSerenadeVerse,
    CognitiveComputingChorusVerse,
    VerseResult,
    CreationContext,
)


class VersesLibrary:
    """Comprehensive library for managing quantum verses and creative content."""

    def __init__(self, library_path: str = "verses_library.json"):
        self.library_path = library_path
        self.verses: Dict[
            str, Dict[str, VerseResult]
        ] = {}  # verse_type -> verse_id -> verse_result
        self.verse_classes: Dict[str, Type[BaseQuantumVerse]] = {
            "quantum_poetry": QuantumPoetryVerse,
            "anticipatory_narrative": AnticipatoryNarrativeVerse,
            "architecture_verse": ArchitectureVerse,
            "debug_verse": DebugVerse,
            "team_harmony": TeamHarmonyVerse,
            "code_elegance": CodeEleganceVerse,
            "algorithmic_sonnet": AlgorithmicSonnetVerse,
            "database_symphony": DatabaseSymphonyVerse,
            "api_serenade": APISerenadeVerse,
            "quantum_fractal": QuantumFractalVerse,
            "blockchain_ballad": BlockchainBalladVerse,
            "ml_ode": MachineLearningOdeVerse,
            "cybersecurity_sonata": CybersecuritySonataVerse,
            "devops_rhapsody": DevOpsRhapsodyVerse,
            "quantum_entanglement": QuantumEntanglementVerse,
            "data_viz_waltz": DataVisualizationWaltzVerse,
            "cloud_concerto": CloudComputingConcertoVerse,
            "iot_intermezzo": IoTIntermezzoVerse,
            "ar_aria": AugmentedRealityAriaVerse,
            "nlp_opera": NaturalLanguageOperaVerse,
            "robotic_symphony": RoboticSymphonyVerse,
            "quantum_crypto_cantata": QuantumCryptographyCantataVerse,
            "swarm_chorus": SwarmIntelligenceChorusVerse,
            "vr_fantasia": VirtualRealityFantasiaVerse,
            "edge_etude": EdgeComputingEtudeVerse,
            "ga_rondo": GeneticAlgorithmRondoVerse,
            "blockchain_caprice": BlockchainConsensusCapriceVerse,
            "neural_nocturne": NeuralNetworkNocturneVerse,
            "container_overture": ContainerOrchestrationOvertureVerse,
            "quantum_supremacy_sonata": QuantumSupremacySonataVerse,
            "hci_minuet": HumanComputerInteractionMinuetVerse,
            "bioinformatics_ballet": BioinformaticsBalletVerse,
            "autonomous_symphony": AutonomousSystemsSymphonyVerse,
            "digital_twin_concerto": DigitalTwinConcertoVerse,
            "ethical_ai_cantata": EthicalAICantataVerse,
            "metaverse_opera": MetaverseOperaVerse,
            "sustainable_tech_serenade": SustainableTechSerenadeVerse,
            "cognitive_chorus": CognitiveComputingChorusVerse,
        }
        self._load_library()

    def _load_library(self):
        """Load verses library from persistent storage."""
        if os.path.exists(self.library_path):
            try:
                with open(self.library_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for verse_type, verses in data.items():
                        self.verses[verse_type] = {}
                        for verse_id, verse_dict in verses.items():
                            # Convert back to VerseResult
                            self.verses[verse_type][verse_id] = VerseResult(
                                **verse_dict
                            )
            except (json.JSONDecodeError, KeyError) as e:
                print(
                    f"Warning: Failed to load verses library: {e}. Starting with empty library."
                )
                self.verses = {}

    def _save_library(self):
        """Save verses library to persistent storage."""
        data = {}
        for verse_type, verses in self.verses.items():
            data[verse_type] = {}
            for verse_id, verse_result in verses.items():
                # Convert VerseResult to dict
                data[verse_type][verse_id] = {
                    "verse_content": verse_result.verse_content,
                    "verse_type": verse_result.verse_type,
                    "resonance_score": verse_result.resonance_score,
                    "harmony_metrics": verse_result.harmony_metrics,
                    "metadata": verse_result.metadata,
                    "created_at": verse_result.created_at,
                }

        with open(self.library_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def register_verse_type(self, verse_type: str, verse_class: Type[BaseQuantumVerse]):
        """Register a new verse type."""
        self.verse_classes[verse_type] = verse_class

    async def create_verse(
        self, verse_type: str, context: CreationContext, verse_id: Optional[str] = None
    ) -> Optional[VerseResult]:
        """Create a new verse and add it to the library."""
        if verse_type not in self.verse_classes:
            print(f"Unknown verse type: {verse_type}")
            return None

        if verse_id is None:
            verse_id = f"{verse_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            verse_class = self.verse_classes[verse_type]
            verse_instance = verse_class(f"test_{verse_type}")

            result = await verse_instance.compose_quantum_verse(context)

            # Store in library
            if verse_type not in self.verses:
                self.verses[verse_type] = {}

            self.verses[verse_type][verse_id] = result
            self._save_library()

            print(f"Created verse: {verse_id} ({verse_type})")
            return result

        except Exception as e:
            print(f"Failed to create verse: {e}")
            return None

    def get_verse(self, verse_type: str, verse_id: str) -> Optional[VerseResult]:
        """Retrieve a specific verse."""
        if verse_type in self.verses and verse_id in self.verses[verse_type]:
            return self.verses[verse_type][verse_id]
        return None

    def search_verses(
        self,
        verse_type: Optional[str] = None,
        min_resonance: float = 0.0,
        tags: Optional[List[str]] = None,
        content_query: Optional[str] = None,
    ) -> List[VerseResult]:
        """Search verses with various filters."""
        results = []

        search_space = self.verses.items()
        if verse_type:
            if verse_type in self.verses:
                search_space = [(verse_type, self.verses[verse_type])]
            else:
                return []

        for v_type, verses in search_space:
            for verse_id, verse_result in verses.items():
                # Filter by resonance
                if verse_result.resonance_score < min_resonance:
                    continue

                # Filter by tags
                if tags:
                    verse_tags = verse_result.metadata.get("tags", [])
                    if not any(tag in verse_tags for tag in tags):
                        continue

                # Filter by content
                if content_query:
                    if content_query.lower() not in verse_result.verse_content.lower():
                        continue

                results.append(verse_result)

        return results

    def get_verse_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the verses library."""
        total_verses = sum(len(verses) for verses in self.verses.values())
        verse_types = list(self.verses.keys())

        type_distribution = {}
        resonance_scores = []
        creation_dates = []

        for verse_type, verses in self.verses.items():
            type_distribution[verse_type] = len(verses)

            for verse_result in verses.values():
                resonance_scores.append(verse_result.resonance_score)
                if verse_result.created_at:
                    try:
                        creation_dates.append(
                            datetime.fromisoformat(verse_result.created_at)
                        )
                    except ValueError:
                        pass

        avg_resonance = (
            sum(resonance_scores) / len(resonance_scores) if resonance_scores else 0
        )

        # Calculate creation frequency
        if creation_dates:
            creation_dates.sort()
            if len(creation_dates) > 1:
                time_span = (creation_dates[-1] - creation_dates[0]).total_seconds()
                creation_frequency = (
                    len(creation_dates) / (time_span / 86400) if time_span > 0 else 0
                )
            else:
                creation_frequency = 0
        else:
            creation_frequency = 0

        return {
            "total_verses": total_verses,
            "verse_types": verse_types,
            "type_distribution": type_distribution,
            "average_resonance": avg_resonance,
            "creation_frequency_per_day": creation_frequency,
            "library_health": self._assess_library_health(),
        }

    def _assess_library_health(self) -> str:
        """Assess the overall health of the verses library."""
        if not self.verses:
            return "empty"

        total_verses = sum(len(verses) for verses in self.verses.values())

        if total_verses < 5:
            return "developing"
        elif total_verses < 20:
            return "growing"
        else:
            return "mature"

    def export_verses(self, file_path: str, verse_type: Optional[str] = None):
        """Export verses to a JSON file."""
        export_data = {}

        if verse_type:
            if verse_type in self.verses:
                export_data[verse_type] = {}
                for verse_id, verse_result in self.verses[verse_type].items():
                    export_data[verse_type][verse_id] = {
                        "content": verse_result.verse_content,
                        "resonance": verse_result.resonance_score,
                        "metadata": verse_result.metadata,
                    }
        else:
            # Export all
            for v_type, verses in self.verses.items():
                export_data[v_type] = {}
                for verse_id, verse_result in verses.items():
                    export_data[v_type][verse_id] = {
                        "content": verse_result.verse_content,
                        "resonance": verse_result.resonance_score,
                        "metadata": verse_result.metadata,
                    }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def import_verses(self, file_path: str):
        """Import verses from a JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            import_data = json.load(f)

        for verse_type, verses in import_data.items():
            if verse_type not in self.verses:
                self.verses[verse_type] = {}

            for verse_id, verse_data in verses.items():
                # Create VerseResult from imported data
                verse_result = VerseResult(
                    verse_content=verse_data["content"],
                    verse_type=verse_type,
                    resonance_score=verse_data["resonance"],
                    harmony_metrics={},  # Not preserved in export
                    metadata=verse_data["metadata"],
                )

                self.verses[verse_type][verse_id] = verse_result

        self._save_library()

    def cleanup_old_verses(self, days_old: int = 30, min_resonance: float = 0.3):
        """Clean up old or low-resonance verses."""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)

        removed_count = 0

        for verse_type in list(self.verses.keys()):
            for verse_id in list(self.verses[verse_type].keys()):
                verse_result = self.verses[verse_type][verse_id]

                # Remove if too old and low resonance
                should_remove = False

                if verse_result.created_at:
                    try:
                        created_timestamp = datetime.fromisoformat(
                            verse_result.created_at
                        ).timestamp()
                        if (
                            created_timestamp < cutoff_date
                            and verse_result.resonance_score < min_resonance
                        ):
                            should_remove = True
                    except ValueError:
                        pass

                if should_remove:
                    del self.verses[verse_type][verse_id]
                    removed_count += 1

        if removed_count > 0:
            self._save_library()

        return removed_count


# Global verses library instance
verses_library = VersesLibrary()
