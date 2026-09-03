from __future__ import annotations

import json

from book_loop.domain.models import CreativeBrief, Outline
from book_loop.domain.protocols import LLMProvider


class OutlineAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def generate(
        self,
        *,
        theme: str,
        author_idea: str,
        lore: str,
        constraints: list[str],
        creative_brief: CreativeBrief | None = None,
    ) -> Outline:
        system_prompt = (
            "You are a developmental fiction editor. Create a concise global book outline "
            "that preserves the author's intent. Treat the structured creative brief as authoritative "
            "author direction. Do not invent constraints that contradict it. "
            "Return valid JSON only, with this exact shape: "
            '{"chapters":[{"number":1,"title":"...","objective":"...","synopsis":"..."}]}.'
        )
        brief_context = "No structured creative brief provided."
        if creative_brief is not None:
            lines = [f"Premise: {creative_brief.premise}"]
            if creative_brief.audience:
                lines.append(f"Audience: {creative_brief.audience}")
            if creative_brief.tone:
                lines.append(f"Tone: {creative_brief.tone}")
            if creative_brief.themes:
                lines.append(f"Themes: {', '.join(creative_brief.themes)}")
            if creative_brief.must_include:
                lines.append(f"Must include: {', '.join(creative_brief.must_include)}")
            if creative_brief.must_avoid:
                lines.append(f"Must avoid: {', '.join(creative_brief.must_avoid)}")
            brief_context = "\n".join(lines)
        user_prompt = (
            f"CREATIVE BRIEF:\n{brief_context}\n\n"
            f"THEME:\n{theme}\n\nAUTHOR IDEA:\n{author_idea}\n\nLORE:\n{lore}\n\n"
            f"CONSTRAINTS:\n{chr(10).join('- ' + c for c in constraints)}\n\n"
            "Create the chapter-by-chapter outline. Numbers must start at 1 and be consecutive."
        )
        raw = self.llm.generate(system_prompt=system_prompt, user_prompt=user_prompt).strip()
        if raw.startswith("```"):
            raw = raw.removeprefix("```").removeprefix("json").removesuffix("```").strip()
        try:
            return Outline.model_validate(json.loads(raw))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError("The outline provider returned invalid structured JSON") from exc
