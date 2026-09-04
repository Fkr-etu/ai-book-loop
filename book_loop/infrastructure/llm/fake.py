from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel

from book_loop.domain.protocols import LLMProvider

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


class FakeLLMProvider(LLMProvider):
    """Fake LLM Provider for local development and offline testing."""

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        sys_lower = system_prompt.lower()
        if "assertion" in sys_lower or "extract" in sys_lower:
            source = user_prompt.split("SOURCE CHUNK:\n", 1)[-1].strip()
            statement = re.split(r"(?<=[.!?])(?:\s+|$)", source, maxsplit=1)[0].strip()
            return json.dumps({
                "assertions": [
                    {
                        "statement": statement,
                        "subject": "Valerius",
                        "predicate": "fact",
                        "object": statement,
                        "confidence": 0.95,
                    }
                ]
            })
        if "review" in sys_lower:
            return json.dumps({
                "score": 9,
                "approved": True,
                "issues": [],
                "suggestions": ["Excellent style scholastique."],
            })
        if "summary" in sys_lower or "summarize" in sys_lower:
            return "Résumé canonique du chapitre."
        if "outline" in sys_lower:
            return json.dumps({
                "chapters": [
                    {
                        "number": 1,
                        "title": "Le Murmure du Parchemin",
                        "objective": "Découverte de la tablette",
                        "synopsis": "Le protagoniste découvre la tablette dans les archives.",
                    },
                    {
                        "number": 2,
                        "title": "La Cité Suspendue",
                        "objective": "Voyage vers le pont de verre",
                        "synopsis": "Le voyage révèle les premiers enjeux de la cité.",
                    },
                    {
                        "number": 3,
                        "title": "L'Éclipse du Codex",
                        "objective": "Sacrifice du premier souvenir",
                        "synopsis": "Le secret du codex est révélé au prix d'un souvenir.",
                    },
                ]
            })

        return "Texte généré par l'assistant IA en mode offline."

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[StructuredModel],
        thinking_level: str = "medium",
        max_output_tokens: int | None = None,
    ) -> StructuredModel:
        del thinking_level, max_output_tokens
        return schema.model_validate_json(
            self.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        )
