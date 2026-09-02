from __future__ import annotations

import json
from book_loop.domain.protocols import LLMProvider


class FakeLLMProvider(LLMProvider):
    """Fake LLM Provider for local development and offline testing."""

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        sys_lower = system_prompt.lower()
        if "review" in sys_lower:
            return json.dumps({
                "score": 9,
                "approved": True,
                "issues": [],
                "suggestions": ["Excellent style scholastique."]
            })
        if "summary" in sys_lower or "summarize" in sys_lower:
            return "Résumé canonique du chapitre."
        if "outline" in sys_lower:
            return (
                "1. Le Murmure du Parchemin — Découverte de la tablette\n"
                "2. La Cité Suspendue — Voyage vers le pont de verre\n"
                "3. L'Éclipse du Codex — Sacrifice du premier souvenir"
            )

        return "Texte généré par l'assistant IA en mode offline."
