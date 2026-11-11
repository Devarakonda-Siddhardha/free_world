# EPISODIC_MEMORY.md - What Happened

Memories are stored in `EPISODIC_MEMORY.jsonl`, one JSON object per line with fields `timestamp`, `summary`, and `detail`.

- Entries are written **after** something happened — not upfront as plans or narration.
- The goal is to remember **what was done**, not every low-level micro-step.
- **Not what you learned** — learnings, physical techniques, and mistakes belong in `SEMANTIC_MEMORY.md`.
- `summary` field: **one short sentence**, past tense, describing what happened. Easily scannable by extracting just this field across entries.
- `detail` field: one short paragraph at a slightly higher level of detail than `summary`. Skip repetitive coordinate dumps.
- Never rewrite or delete old entries in `EPISODIC_MEMORY.jsonl`. Always append.
