#!/usr/bin/env python3
"""QwenPlayground - Exploration modèles open-source"""

import json
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelInfo:
    name: str
    size_b: float
    quantizations: List[str]
    tasks: List[str]
    performance_score: float


class QwenPlayground:
    """Exploration modèles Qwen open-source"""

    def __init__(self):
        self.models = {
            "qwen-7b": ModelInfo("Qwen-7B", 7, ["int8", "int4", "fp16"], 
                               ["chat", "reasoning", "code"], 0.85),
            "qwen-14b": ModelInfo("Qwen-14B", 14, ["int8", "int4", "fp16"],
                                ["chat", "reasoning", "code", "translation"], 0.88),
            "qwen-72b": ModelInfo("Qwen-72B", 72, ["int8", "fp16"],
                                ["chat", "reasoning", "code", "translation", "summarization"], 0.92)
        }

    def list_models(self) -> List[ModelInfo]:
        """Lister modèles disponibles"""
        return list(self.models.values())

    def recommend_model(self, task: str, constraints: Dict = None) -> Optional[ModelInfo]:
        """Recommander modèle selon tâche"""
        matching = [m for m in self.models.values() if task in m.tasks]
        
        if not matching:
            return None
        
        # Filtrer par contraintes
        if constraints:
            max_size = constraints.get("max_size_b")
            if max_size:
                matching = [m for m in matching if m.size_b <= max_size]
        
        # Retourner meilleur score
        return max(matching, key=lambda m: m.performance_score)

    def get_quantization_recommendation(self, model_name: str, memory_limit: str = "8GB") -> str:
        """Recommander quantification selon mémoire disponible"""
        memory_map = {"4GB": "int4", "8GB": "int4", "16GB": "int8", "32GB+": "fp16"}
        return memory_map.get(memory_limit, "int4")


if __name__ == "__main__":
    playground = QwenPlayground()
    rec = playground.recommend_model("reasoning", {"max_size_b": 14})
    print(json.dumps(rec.__dict__ if rec else None, indent=2))