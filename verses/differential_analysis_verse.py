# Differential Analysis Verse
# Verse pour méthodologie différentielle d'analyse corruption
# IntentHash: 0xDIFFERENTIAL_ANALYSIS_VERSE_20260420

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from skills.differential_analyzer import DifferentialAnalyzer


class DifferentialAnalysisVerse:
    """Verse pour analyse différentielle systématique des corruptions"""

    def __init__(self):
        self.analyzer = DifferentialAnalyzer()
        self.baselines = {}
        self.analysis_history = []
        self.load_state()

    def load_state(self):
        """Charge état persistant"""
        state_file = "differential_analysis_state.json"
        if os.path.exists(state_file):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    self.baselines = state.get("baselines", {})
                    self.analysis_history = state.get("history", [])
            except:
                pass

    def save_state(self):
        """Sauvegarde état"""
        state = {
            "baselines": self.baselines,
            "history": self.analysis_history[-50:],  # Garder 50 derniers
            "last_updated": datetime.now().isoformat(),
        }

        with open("differential_analysis_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def establish_corruption_baseline(self, target_type: str, target_path: str) -> dict:
        """Établit baseline pour type de corruption spécifique"""
        baseline_name = (
            f"{target_type}_baseline_{datetime.now().strftime('%Y%m%d_%H%M')}"
        )

        result = self.analyzer.establish_baseline(target_path, baseline_name)

        if result["success"]:
            self.baselines[target_type] = {
                "name": baseline_name,
                "path": target_path,
                "created": datetime.now().isoformat(),
                "structure_summary": result["structure_summary"],
            }
            self.save_state()

        return result

    def analyze_corruption_incident(
        self, incident_type: str, corrupted_path: str
    ) -> dict:
        """Analyse incident de corruption via méthodologie différentielle"""
        if incident_type not in self.baselines:
            return {
                "success": False,
                "error": f"No baseline established for {incident_type}. Run establish_corruption_baseline first.",
            }

        baseline_name = self.baselines[incident_type]["name"]

        # Calcul diff
        diff_result = self.analyzer.compute_deep_diff(baseline_name, corrupted_path)

        if not diff_result["success"]:
            return diff_result

        # Diagnostic causal
        causal_patterns = self.analyzer.identify_causal_patterns(diff_result)

        # Plan remédiation
        remediation_plan = self.analyzer.generate_remediation_plan(causal_patterns)

        analysis_record = {
            "incident_type": incident_type,
            "corrupted_path": corrupted_path,
            "timestamp": datetime.now().isoformat(),
            "baseline_used": baseline_name,
            "diff_analysis": diff_result,
            "causal_patterns": causal_patterns,
            "remediation_plan": remediation_plan,
            "severity_assessment": self._assess_incident_severity(
                diff_result, causal_patterns
            ),
        }

        self.analysis_history.append(analysis_record)
        self.save_state()

        return {
            "success": True,
            "analysis_id": f"analysis_{len(self.analysis_history)}",
            "summary": self._generate_analysis_summary(analysis_record),
            "recommendations": remediation_plan,
            "severity": analysis_record["severity_assessment"],
        }

    def get_corruption_patterns_report(
        self, incident_type: Optional[str] = None
    ) -> dict:
        """Génère rapport des patterns de corruption identifiés"""
        relevant_analyses = [
            a
            for a in self.analysis_history
            if incident_type is None or a["incident_type"] == incident_type
        ]

        if not relevant_analyses:
            return {"success": False, "error": "No analyses found"}

        # Agréger patterns
        pattern_stats = {}
        for analysis in relevant_analyses:
            patterns = analysis.get("causal_patterns", {}).get("patterns_detected", {})
            for pattern_type, pattern_data in patterns.items():
                if pattern_type not in pattern_stats:
                    pattern_stats[pattern_type] = {
                        "occurrences": 0,
                        "total_confidence": 0,
                        "evidences": [],
                    }

                pattern_stats[pattern_type]["occurrences"] += 1
                pattern_stats[pattern_type]["total_confidence"] += pattern_data.get(
                    "confidence", 0
                )
                pattern_stats[pattern_type]["evidences"].extend(
                    pattern_data.get("evidence", [])
                )

        # Calculer moyennes
        for pattern_type, stats in pattern_stats.items():
            stats["average_confidence"] = (
                stats["total_confidence"] / stats["occurrences"]
            )
            stats["unique_evidences"] = len(set(str(e) for e in stats["evidences"]))

        return {
            "success": True,
            "incident_type": incident_type or "all",
            "total_analyses": len(relevant_analyses),
            "pattern_statistics": pattern_stats,
            "most_common_pattern": max(
                pattern_stats.items(), key=lambda x: x[1]["occurrences"]
            )[0]
            if pattern_stats
            else None,
        }

    def predict_corruption_risk(self, target_path: str) -> dict:
        """Prédit risque de corruption basé sur historique"""
        # Analyse structure actuelle
        try:
            current_structure = self.analyzer._analyze_structure(target_path)
        except:
            return {"success": False, "error": f"Cannot analyze {target_path}"}

        # Comparer avec baselines similaires
        risk_factors = []

        for baseline_type, baseline_info in self.baselines.items():
            if os.path.exists(baseline_info["path"]):
                try:
                    baseline_structure = self.analyzer._analyze_structure(
                        baseline_info["path"]
                    )

                    # Calculer différences structurelles
                    size_diff = abs(
                        current_structure["total_size"]
                        - baseline_structure["total_size"]
                    )
                    file_count_diff = abs(
                        len(current_structure["files"])
                        - len(baseline_structure["files"])
                    )

                    if size_diff > 100 * 1024 * 1024:  # 100MB diff
                        risk_factors.append(
                            {
                                "type": baseline_type,
                                "factor": "size_anomaly",
                                "severity": min(
                                    100, size_diff / (1024 * 1024)
                                ),  # Points par MB
                                "description": f"Size difference: {size_diff / (1024 * 1024):.1f}MB vs baseline",
                            }
                        )

                    if file_count_diff > 10:
                        risk_factors.append(
                            {
                                "type": baseline_type,
                                "factor": "file_count_anomaly",
                                "severity": file_count_diff * 2,
                                "description": f"File count difference: {file_count_diff} vs baseline",
                            }
                        )

                except:
                    continue

        total_risk = sum(f["severity"] for f in risk_factors)
        risk_level = (
            "low" if total_risk < 50 else "medium" if total_risk < 150 else "high"
        )

        return {
            "success": True,
            "target_path": target_path,
            "risk_level": risk_level,
            "total_risk_score": total_risk,
            "risk_factors": risk_factors,
            "recommendations": self._generate_risk_recommendations(
                risk_level, risk_factors
            ),
        }

    def _assess_incident_severity(
        self, diff_result: dict, causal_patterns: dict
    ) -> dict:
        """Évalue sévérité de l'incident"""
        base_severity = diff_result.get("severity_score", 0)
        pattern_confidence = causal_patterns.get("confidence", 0)

        # Ajuster selon type de corruption
        dominant_pattern = causal_patterns.get("dominant_pattern", "")
        severity_multiplier = {
            "gpu_cache_corruption": 1.5,  # Risque crash système
            "file_corruption": 2.0,  # Perte de données
            "config_corruption": 0.8,  # Facilement réparable
            "data_corruption": 2.5,  # Impact business élevé
        }.get(dominant_pattern, 1.0)

        final_severity = min(100, base_severity * severity_multiplier)

        severity_level = (
            "low"
            if final_severity < 30
            else "medium"
            if final_severity < 70
            else "high"
        )

        return {
            "score": final_severity,
            "level": severity_level,
            "factors": {
                "base_diff_severity": base_severity,
                "pattern_confidence": pattern_confidence,
                "type_multiplier": severity_multiplier,
                "dominant_pattern": dominant_pattern,
            },
        }

    def _generate_analysis_summary(self, analysis_record: dict) -> dict:
        """Génère résumé d'analyse"""
        return {
            "incident_type": analysis_record["incident_type"],
            "severity": analysis_record["severity_assessment"]["level"],
            "dominant_pattern": analysis_record["causal_patterns"]["dominant_pattern"],
            "confidence": analysis_record["causal_patterns"]["confidence"],
            "key_changes": {
                "structure_changes": len(
                    analysis_record["diff_analysis"]["structure_diff"]["modified_files"]
                ),
                "content_changes": len(
                    analysis_record["diff_analysis"]["content_diff"]["modified_content"]
                ),
                "new_files": len(
                    analysis_record["diff_analysis"]["content_diff"]["new_files"]
                ),
            },
            "recommendations_count": len(
                analysis_record["remediation_plan"]["actions"]
            ),
        }

    def _generate_risk_recommendations(
        self, risk_level: str, risk_factors: list
    ) -> list:
        """Génère recommandations selon niveau de risque"""
        recommendations = []

        if risk_level == "high":
            recommendations.extend(
                [
                    "Immediate backup required",
                    "Schedule maintenance window",
                    "Consider system isolation",
                    "Prepare rollback procedures",
                ]
            )
        elif risk_level == "medium":
            recommendations.extend(
                [
                    "Monitor closely for changes",
                    "Plan preventive maintenance",
                    "Review recent system changes",
                    "Consider incremental backups",
                ]
            )
        else:  # low
            recommendations.extend(
                [
                    "Continue normal monitoring",
                    "Regular maintenance schedule sufficient",
                    "No immediate action required",
                ]
            )

        # Recommandations spécifiques selon facteurs
        for factor in risk_factors:
            if factor["factor"] == "size_anomaly":
                recommendations.append(
                    "Investigate large size changes - possible data accumulation"
                )
            elif factor["factor"] == "file_count_anomaly":
                recommendations.append(
                    "Review file additions/deletions for unauthorized changes"
                )

        return recommendations


# Fonctions d'interface pour intégration système
def establish_corruption_baseline(target_type: str, target_path: str) -> dict:
    """Interface pour établir baseline corruption"""
    verse = DifferentialAnalysisVerse()
    return verse.establish_corruption_baseline(target_type, target_path)


def analyze_corruption_incident(incident_type: str, corrupted_path: str) -> dict:
    """Interface pour analyser incident corruption"""
    verse = DifferentialAnalysisVerse()
    return verse.analyze_corruption_incident(incident_type, corrupted_path)


def get_corruption_patterns_report(incident_type: Optional[str] = None) -> dict:
    """Interface pour rapport patterns corruption"""
    verse = DifferentialAnalysisVerse()
    return verse.get_corruption_patterns_report(incident_type)


def predict_corruption_risk(target_path: str) -> dict:
    """Interface pour prédiction risque corruption"""
    verse = DifferentialAnalysisVerse()
    return verse.predict_corruption_risk(target_path)
