# Creative Brief

The creative brief is the structured representation of author intent used by the book workflow.

## Boundary

The brief is authored and approved as application state. It is not generated implicitly by an LLM and it does not become Canon.

```text
Author input
    ↓
CreativeBrief
    ↓
BookState
    ↓
Outline / Chapter Context
```

## Fields

- `premise`: required central story proposition.
- `audience`: intended readership, when known.
- `tone`: desired narrative voice or emotional register.
- `themes`: themes the work should explore.
- `must_include`: author-mandated elements.
- `must_avoid`: author constraints on content or treatment.

Empty optional fields are valid. The premise is required so a brief cannot silently become an empty intent object.

## Invariants

`SetCreativeBrief` is deterministic and persists the supplied validated `CreativeBrief`. It performs no LLM call and cannot approve Canon.

Chapter generation continues to expose the existing `author_idea`, `theme`, `lore`, and `constraints` fields for compatibility. The structured brief is additive and becomes an explicit context section when present.
