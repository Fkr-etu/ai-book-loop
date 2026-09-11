# Critical Eye (Œil critique)

The Critical Eye is a narrative sparring capability for authors who are stuck or want an external challenge. It is intentionally separate from manuscript mutation and canonical knowledge management.

## Responsibilities

The Critical Eye may challenge:

- motivation and character logic;
- stakes and consequences;
- causality and scene logic;
- antagonist/opposition strength;
- unresolved assumptions and narrative holes;
- coherence between the author's stated intent and the proposed scene/story direction.

Its role is to question and challenge the author, not to write the manuscript for them.

## Personality

A book can configure one of four personalities:

- `challenger` — direct and demanding;
- `editor` — focused on structure and craft;
- `devils_advocate` — deliberately tests assumptions and weak points;
- `demanding_kind` — rigorous while remaining constructive.

The personality is persisted on the book and influences the system prompt used by the agent.

## Application contract

The use case exposes a minimal structured response:

```text
reply: string
question: string | null
done: boolean
```

The application enforces an eight-turn hard limit and bounds both conversation history and context size. The LLM provider is selected through the existing provider abstraction and can use a dedicated `GRILL_LLM_MODEL` setting.

## HTTP boundary

The authenticated endpoint is:

```text
POST /api/books/{book_id}/grill
```

The API accepts the current bounded conversation messages and the turn number. The backend returns the structured Critical Eye response.

## MVP boundaries

The Critical Eye does **not**:

- modify manuscript content;
- generate or promote Canon facts;
- mutate `BookState` during a conversation;
- persist the conversation transcript;
- build a CreativeSpec;
- silently decide that a proposed narrative interpretation is canonical.

The Studio keeps the active conversation client-side for the current session. A session is started explicitly after the author accepts the nudge, and dismissal prevents automatic relaunch for the current chapter.

## Product principle

The feature follows the product rule **AI proposes, author decides**. The value of the Critical Eye is therefore not the text it writes, but the quality of the questions and objections it raises before the author commits to a narrative choice.
