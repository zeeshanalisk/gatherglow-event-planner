# GatherGlow: Designing an Event Planner That Keeps the Important Decisions Grounded

*PromptWars Virtual · Challenge 5 — Celebration & Event Planner*

> Draft for editing and publication. Before publishing, run the app, use Google Antigravity as required by the event, verify the live Gemini mode if you claim it, and replace the link placeholders with real URLs.

## The problem

Planning a wedding, birthday or community event is not one task. A host has to translate an idea into a budget, a sequence of activities, a practical checklist, supplier follow-ups and contingency plans. Dietary and accessibility needs must be part of the first brief instead of being treated as last-minute additions.

GatherGlow brings those pieces into one workspace. The goal is not to pretend that an AI assistant can book a venue or know a supplier's current price. The goal is to help the host make better decisions, see the operational consequences and keep their plan organised.

## The product approach

The host begins with an event brief: celebration type, date, city, venue or venue type, guest count, total budget, arrival time, setting, style, dietary requirements, accessibility needs and a personal detail. The app turns that brief into a concept and a working plan.

The workspace has six connected areas:

1. **Overview:** creative direction, tailored ideas, inclusion commitments and a risk register.
2. **Budget studio:** editable category allocations, per-guest spend and a supplier-quote tracker that flags category overruns.
3. **Run of show:** a schedule calculated from the host's selected start time.
4. **Vendor and task desk:** a dated action checklist and user-entered supplier contacts.
5. **What-if lab:** practical response steps for heavy rain, heat, supplier cancellation and changes to budget or guest count.
6. **AI copilot and export:** follow-up planning guidance and downloadable Markdown, JSON and CSV files.

## Why the application uses two planning layers

The most important design decision is to separate creative assistance from calculations.

**Gemini handles language-heavy work:** a tailored event concept, theme, palette, experience ideas, food direction, entertainment suggestions, inclusion notes and risk responses. The application sends only the event details needed for the requested plan or copilot response when a Gemini API key has been configured.

**Python handles deterministic work:** budget allocation, per-guest arithmetic, run-of-show times and checklist due dates. Those values are calculated locally. A model response cannot replace the app's budget, schedule or checklist fields. This keeps the AI useful without making it the source of truth for amounts or timings.

If Gemini is unavailable or no key is configured, GatherGlow falls back to a clearly labelled local planning mode. The fallback is useful for exploring the application, but it must not be described as a live GenAI response.

## Trust, safety and inclusion

GatherGlow does not generate fake supplier names, live prices, availability, bookings or legal approvals. Hosts enter their own supplier contacts and quotations, and the interface labels them as user-entered information. Venue capacity, contracts, permits, local rules and safety requirements must be checked with the responsible providers.

Dietary and accessibility requirements are captured in the original event brief. Recommendations include practical checks such as ingredient and allergen labels, separate serving tools, step-free routes, reserved seating and accessible facilities. These are planning prompts, not a substitute for a venue or professional assessment.

The application keeps its API key in environment variables or Streamlit Secrets rather than source code. User text is length-limited and cleaned before entering the AI prompt or HTML-rendered areas. Model output is validated, and calculation fields are restored from deterministic local results.

## How it is tested

The offline unit tests cover budget totals, balanced/under/over budget states, valid and invalid event details, start-time handling, checklist creation, AI-output validation, prompt safety and Markdown export sections. The suite can be run without a Gemini key or network connection:

```bash
python -m unittest discover -s tests -v
```

The browser workflow should also be checked after installation: build a plan, adjust category allocations, add a supplier quote, complete a task, test a what-if scenario and download all three export formats. A live Gemini response should be claimed only after the app visibly reports the Gemini model rather than local fallback mode.

## Limitations and next steps

GatherGlow is a planning assistant, not a booking marketplace, supplier directory or event-management database. Its starting allocations are editable planning assumptions, not market benchmarks. Streamlit session state is temporary, so the host should export the plan to keep a copy. A production version could add secure accounts, encrypted persistence, team collaboration and verified supplier integrations, but those features are intentionally outside this lightweight competition build.
