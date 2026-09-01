from __future__ import annotations

from book_loop.domain.protocols import LLMProvider


class FakeLLMProvider(LLMProvider):
    """Fake LLM Provider for local development and offline testing."""

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        if "outline" in system_prompt.lower() or "outline" in user_prompt.lower():
            return (
                "1. Le Murmure du Parchemin — Découverte de la tablette\n"
                "2. La Cité Suspendue — Voyage vers le pont de verre\n"
                "3. L'Éclipse du Codex — Sacrifice du premier souvenir"
            )
        if "review" in system_prompt.lower() or "critique" in user_prompt.lower():
            return (
                "SCORE: 9\n"
                "APPROVED: true\n"
                "ISSUES: none\n"
                "SUGGESTIONS: Excellent style scholastique."
            )
        if "summary" in system_prompt.lower() or "summarize" in user_prompt.lower():
            return "Résumé canonique du chapitre."

        return "Texte généré par l'assistant IA en mode offline."
