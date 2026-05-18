#!/usr/bin/env python3
"""BonSensPython - Reasoning au niveau token pour LLM"""

import re
import json
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TokenSense:
    token: str
    part_of_speech: str
    semantic_role: str
    context_score: float


class BonSensPython:
    """Reasoning token-level inspiré de l'approche intuitive"Bon Sens" """

    def __init__(self):
        self.stop_words = {"le", "la", "les", "un", "une", "des", "de", "du", "au", "aux"}

    def tokenize_with_sense(self, text: str) -> List[TokenSense]:
        """Tokeniser avec sens sémantique"""
        tokens = text.lower().split()
        senses = []
        
        for i, token in enumerate(tokens):
            if token in self.stop_words:
                pos = "STOP"
            elif token in {"est", "sont", "étaient", "été"}:
                pos = "VERB"
            elif token.endswith("tion") or token.endswith("sion"):
                pos = "NOUN"
            elif token.startswith("http"):
                pos = "URL"
            else:
                pos = "CONTENT"
            
            role = self._infer_role(token, i, len(tokens))
            
            senses.append(TokenSense(
                token=token,
                part_of_speech=pos,
                semantic_role=role,
                context_score=1.0 - (abs(i - len(tokens)/2) / len(tokens))
            ))
        
        return senses

    def _infer_role(self, token: str, position: int, total: int) -> str:
        """Inférer rôle sémantique"""
        if position == 0:
            return "subject"
        if position == total - 1:
            return "predicate"
        return "modifier"

    def reason_missing(self, tokens: List[TokenSense]) -> List[str]:
        """Raisonner pour tokens manquants"""
        missing = []
        
        for i, ts in enumerate(tokens):
            if ts.context_score < 0.3:
                missing.append(f"Token '{ts.token}' faible contexte")
        
        return missing

    def score_coherence(self, tokens: List[TokenSense]) -> float:
        """Score de cohérence textuelle"""
        if not tokens:
            return 0.0
        
        avg_score = sum(ts.context_score for ts in tokens) / len(tokens)
        content_ratio = len([t for t in tokens if t.part_of_speech == "CONTENT"]) / len(tokens)
        
        return (avg_score * 0.6 + content_ratio * 0.4)


if __name__ == "__main__":
    reasoner = BonSensPython()
    senses = reasoner.tokenize_with_sense("Le système Diamond est intelligent.")
    print(json.dumps([s.__dict__ for s in senses], indent=2))