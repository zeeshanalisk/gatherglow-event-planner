# GatherGlow validation report

**Project:** GatherGlow — PromptWars Virtual, Challenge 5
**Validation date:** 1 November 2026

## Checks completed in the preparation environment

- Python syntax compilation: `app.py`, `planner.py`, `ai_engine.py` and both test modules — passed.
- Offline unit tests: **12 passed**.
- Budget allocation totals are checked across multiple budget values.
- Budget status tests cover balanced, under-allocation and over-budget states.
- Event input tests cover empty names, invalid guest counts, non-finite budgets and past dates.
- Timeline tests confirm the first activity begins at the selected arrival time.
- Checklist tests confirm task count, stable IDs and overdue metadata.
- AI-output validation tests confirm model output cannot overwrite deterministic budget or schedule data.
- Prompt tests confirm structured JSON output and guardrails against invented suppliers and prompt-injection text in event fields.
- Markdown export tests confirm the core plan sections are included.
