# Google Antigravity build/review prompt

Open this folder as the Antigravity workspace, then paste the following as the initial build/review task. Keep the resulting build history truthful and retain your own screenshots of the workflow if the organizers ask for proof.

---

You are working on **GatherGlow**, a submission for PromptWars Virtual Challenge 5: Celebration & Event Planner.

First inspect the existing repository and README. Do not replace working modules without a reason. Your job is to review and improve the implementation as a senior product engineer, while keeping it lightweight and suitable for a public GitHub repository under 10 MB with exactly one branch.

## Problem statement
Build a GenAI-powered planning assistant for weddings, birthdays and community events. It must help users organize budgets, timelines, vendor checklists and personalized ideas.

## Evaluation dimensions
Optimize for all six visible Hack2Skill dimensions: Code Quality, Security, Efficiency, Testing, Accessibility and Problem Statement Alignment. Do not assume undisclosed weights.

## Product acceptance criteria
1. A host can create and revise an event brief with event type, date, city, venue, guests, budget, start time, indoor/outdoor setting, vibe, dietary needs, accessibility needs and a personal detail.
2. Gemini adds meaningful personalised concept direction, ideas, inclusive planning notes and risk responses. AI is not decorative: it must materially improve the plan.
3. A deterministic Python planner calculates category budgets, per-guest cost, run-of-show times and checklist due dates. Never let an LLM override arithmetic or schedule calculations.
4. The budget studio flags under-allocation and over-budget totals and lets the user track actual supplier quotes.
5. The task desk supports completion tracking and user-entered, explicitly unverified vendor contacts.
6. The what-if lab gives safe, practical actions for rain, heat, cancellation, budget change and guest-count change.
7. Users can export Markdown, JSON and CSV.
8. The app remains useful without a Gemini API key and clearly labels local fallback mode.

## Engineering constraints
- Keep API credentials server-side only (Streamlit secrets or environment variables); never expose or commit secrets.
- Validate and length-limit external/user text. Escape untrusted text before inserting it into HTML.
- Validate model JSON and ignore AI-supplied budget/timeline values.
- Do not invent real vendors, local prices, availability, bookings or regulatory approvals.
- Keep imports and dependencies minimal. No unnecessary external services, analytics trackers or database requirement.
- Make keyboard navigation, labels, focus states, contrast and mobile layouts usable.
- Keep code split into focused files; comments should explain non-obvious choices, not narrate every line.

## Your tasks
1. Run `python -m unittest discover -s tests -v` and `python -m py_compile app.py planner.py ai_engine.py`.
2. Fix all reproducible defects and add tests for any new critical logic.
3. Run the Streamlit app and test all user flows end-to-end when dependencies are available.
4. Review the app for XSS, leaked secrets, unsafe AI output, unhandled API failure and incorrect budget/time calculations.
5. Check that no generated caches, virtual environment, credentials or large files are in the repository.
6. Update README with only features verified in the implementation. Do not claim deployment or Gemini use until verified.
7. Summarise files changed, tests run, test outcomes and known limitations. Do not invent test results.