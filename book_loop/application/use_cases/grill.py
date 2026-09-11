from __future__

from pydantic import BaseModel, Field

from book_loop.domain.models import BookState, GrillPersonality
from book_loop.domain.protocols import LLMProvider

MAX_TURNS = 8
MAX_HISTORY_MESSAGES = 12
MAX_MESSAGE_CHARS = 2000
MAX_CONTEXT_CHARS = 6000


class GrillResponse(BaseModel):
    reply: str = Field(min_length=1)
    question: str | None = None
    done: bool = False


class GrillMessage(BaseModel):
    role: str
    content: str = Field(min_length=1)


PERSONALITY_PROMPTS: dict[GrillPersonality, str] = {
    GrillPersonality.CHALLENGER: (
        "Tu es direct, exigeant et attentif aux failles narratives. "
        "Tu ne valides pas une idée simplement parce qu'elle est plausible en surface."
    ),
    GrillPersonality.EDITOR: (
        "Tu adoptes le regard d'un éditeur analytique. "
        "Tu cherches les problèmes de motivation, de structure, de causalité et d'enjeux."
    ),
    GrillPersonality.DEVILS_ADVOCATE: (
        "Tu es l'avocat du diable. Pour chaque réponse, cherche le contre-exemple "
        "ou l'hypothèse alternative qui met le choix narratif sous pression."
    ),
    GrillPersonality.DEMANDING_KIND: (
        "Tu es chaleureux dans la forme mais exigeant sur le fond. "
        "Tu peux reconnaître une bonne idée, puis immédiatement tester ce qui reste fragile."
    ),
}


class Grill:
    """Challenge an author without mutating canonical or creative state."""

    SYSTEM_PROMPT = """Tu es l'Œil critique de Book Loop, un sparring-partner narratif.

Ton rôle est de challenger l'auteur, pas d'écrire son histoire à sa place.
Identifie le point narratif le plus fragile, implicite ou intéressant dans ses réponses.
Tu peux remettre en cause les motivations, la causalité, les enjeux, les personnages,
les conflits, les conséquences, la crédibilité ou les facilités scénaristiques.

Ne cherche pas à être systématiquement encourageant. Si une réponse ne tient pas,
dis-le clairement et précisément.
Ne résous pas automatiquement le problème à la place de l'auteur : pousse-le à trouver
lui-même la réponse.

Pose UNE SEULE question à la fois. Évite les listes de questions.
N'invente pas de faits que l'auteur n'a pas fournis.
Ne transforme aucune réponse en fait canonique et ne modifie aucun état du livre.

Retourne uniquement le JSON correspondant au schéma demandé.
"""

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def execute(self, *, book: BookState, messages: list[GrillMessage], turn: int) -> GrillResponse:
        if turn < 1:
            raise ValueError("Grill turn must be at least 1")
        if turn > MAX_TURNS:
            return GrillResponse(
                reply="Nous avons assez creusé pour cette session. Reviens à ton histoire avec ces questions en tête.",
                question=None,
                done=True,
            )
        user_prompt = self._build_user_prompt(book=book, messages=messages)
        personality = PERSONALITY_PROMPTS[book.grill_personality]
        return self.llm.generate_structured(
            system_prompt=f"{self.SYSTEM_PROMPT}\n\nStyle de confrontation : {personality}",
            user_prompt=user_prompt,
            schema=GrillResponse,
            thinking_level="low",
            max_output_tokens=500,
        )

    @staticmethod
    def _build_user_prompt(*, book: BookState, messages: list[GrillMessage]) -> str:
        brief = book.creative_brief.model_dump(mode="json") if book.creative_brief else {}
        context = (
            f"TITRE: {book.title}\n"
            f"GENRE / THEME: {book.theme}\n"
            f"IDEE DE L'AUTEUR: {book.author_idea}\n"
            f"BRIEF: {brief}\n"
            f"UNIVERS / ELEMENTS: {book.lore}\n"
            f"CONTRAINTES: {book.constraints}"
        )[:MAX_CONTEXT_CHARS]
        history = messages[-MAX_HISTORY_MESSAGES:]
        rendered = "\n".join(f"{message.role.upper()}: {message.content[:MAX_MESSAGE_CHARS]}" for message in history)
        return f"CONTEXTE DU LIVRE:\n{context}\n\nCONVERSATION RECENTE:\n{rendered}"
