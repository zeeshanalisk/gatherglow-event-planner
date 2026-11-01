# GatherGlow — Celebration & Event Planner

**PromptWars Virtual · Challenge 5 · Celebration & Event Planner**

GatherGlow is an event-planning workspace for weddings, birthdays and community gatherings. It turns a short event brief into a practical plan covering creative direction, budget allocation, run-of-show, action checklist, vendor contacts, inclusion needs and contingency scenarios.

## What makes it useful

- **Personalised GenAI planning:** optional Google Gemini integration creates the creative direction, event ideas, inclusion notes and risk responses from the host's brief.
- **Reliable planning calculations:** category budgets, per-guest budget, date-aware run-of-show and checklist dates are calculated locally and are not delegated to an LLM.
- **Budget studio:** edit category allocations, see under/over-allocation immediately, and track real supplier quotes you enter.
- **Vendor desk:** manage user-entered vendor contacts and their current status without fabricating supplier recommendations.
- **What-if lab:** work through rain, heatwave, supplier cancellation, guest-count and budget-change scenarios.
- **Export:** download a shareable Markdown plan, complete JSON and run-of-show CSV.
- **Inclusive by design:** captures dietary and accessibility requirements and carries them into the plan.

## Run locally

Python 3.10+ is recommended. On Windows, double-click `run_windows.bat`; it creates a virtual environment, installs dependencies and starts the app. Or use the commands below.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The local planning engine works without an API key. To enable live Gemini generation, create a Google AI Studio API key and add it to `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-key"
GEMINI_MODEL = "gemini-3.8-flash"
```

The actual `secrets.toml` is excluded by `.gitignore`. Never paste an API key into source code, a README, a public issue or a GitHub commit. The dashboard notes that no Google Cloud credits are provided; API access, quotas and any charges depend on the Google AI Studio project/key you use. Check the current AI Studio limits before making requests. The app does not require a paid key to explore its local planning features, but local fallback must not be represented as a live GenAI response.

## Deploy on Streamlit Community Cloud

1. Push this project to a **public** GitHub repository with a single branch.
2. Sign in to Streamlit Community Cloud and choose **Create app**.
3. Select the repository, branch `main` and entrypoint `app.py`.
4. In **Advanced settings → Secrets**, add:

   ```toml
   GEMINI_API_KEY = "your-key"
   GEMINI_MODEL = "gemini-3.8-flash"
   ```

5. Deploy and open the app in a private/incognito window to confirm public access.

If you do not add a key, the deterministic local planning experience remains usable. Do not claim Gemini is active unless the app shows `Google Gemini` as its planning mode.

## Testing

Run the core test suite (no API key or network required):

```bash
python -m unittest discover -s tests -v
```

The 12 offline tests cover exact budget allocation, budget health states, schedule start-time handling, checklist generation, input validation (including non-finite budgets and past dates), required planner outputs, AI-output validation, prompt safety and Markdown export sections.

## Architecture

```text
app.py             Streamlit UI, session state, exports and user workflows
run_windows.bat    Windows setup and launch helper
planner.py         Pure planning logic, validation, budgets, dates and exports
ai_engine.py       Optional server-side Gemini integration + safe local fallback
tests/             Offline unit tests
.streamlit/        Visual theme and safe example secrets template
TECHNICAL_BLOG_DRAFT.md  Technical narrative draft for editing and publication
DEMO_VIDEO_SCRIPT.md    Real-screen demo outline (record the actual app)
ANTIGRAVITY_BUILD_PROMPT.md  Build/review prompt for your Antigravity session
PUSH_TO_GITHUB.md    Commands to publish on one public `main` branch
```

**Trust boundary:** Gemini is used for suggestions and narrative planning only. The app owns budget arithmetic, dates and checklist structure. AI output is validated and cannot overwrite these deterministic fields. API keys are read from environment variables or Streamlit secrets and are never sent to the browser intentionally.

## Evaluation-readiness notes

| Evaluation area | Implementation evidence |
|---|---|
| Problem statement alignment | Weddings, birthdays and community events; budgets, timelines, vendor/task checklist and tailored ideas |
| Code quality | UI, core logic and AI integration separated into focused modules |
| Security | Server-side secrets, input length limits, text sanitisation, no fabricated vendor listings |
| Efficiency | One generation call per plan build; deterministic local fallback; no database or background polling |
| Testing | Offline unit tests for budgets, budget status, timelines, checklists, event validation, output contract, prompt safety and Markdown exports |
| Accessibility | Explicit input labels, keyboard-operable Streamlit controls, status messages and responsive layout |

## Limitations and responsible use

- Budgets are planning allocations, not live market prices or vendor quotations.
- Vendor contacts must be entered and independently verified by the user.
- No venue availability, booking, permit, insurance or safety clearance is implied.
- Do not enter sensitive personal information. Event details may be sent to Gemini only when a key is configured and the user generates an AI plan or asks the copilot a question.
- Streamlit session state is not a permanent event database. Export the plan to keep a copy.

## GenAI disclosure

**Service:** Google Gemini API through the official `google-genai` Python SDK (default model `gemini-3.8-flash`; can be overridden through `GEMINI_MODEL`).

**Where it is used:** generating the event's creative direction, personal ideas, inclusive-planning suggestions, risk register and follow-up planning guidance. The AI is not used for deterministic budget arithmetic, schedule calculations or checklist date calculations. If no key is configured or the AI request fails, the app reports local mode and continues to work.

## walkthrough

1. Create a birthday, wedding or community event and enter its budget, guests, date and inclusion preferences.
2. Generate the plan and show the selected planning mode.
3. Open Budget Studio, change one category and demonstrate the over/under-budget warning.
4. Open Run of Show and show the time-aware schedule.
5. Mark checklist tasks complete and add one verified vendor contact.
6. In What-if Lab, choose Heavy rain or Guest count increases and explain the response plan.
7. Export the Markdown plan and JSON.

## Build-in-public post draft

I built **GatherGlow**, a Celebration & Event Planner for PromptWars Virtual Challenge 5.

The idea: event planning should be about the people and the moments—not juggling scattered budgets, timelines and vendor follow-ups.

GatherGlow brings together a personalised event concept, category-wise budget planning, a time-aware run-of-show, an actionable checklist, user-entered vendor contacts and practical what-if planning for changes like rain or a growing guest list.

I used Google Gemini for creative planning and tailored suggestions, while keeping budget calculations and date logic deterministic so the important numbers remain testable. Accessibility and dietary requirements are part of the event brief, not an afterthought.

This is a planning assistant—not a booking marketplace. It does not invent suppliers, prices or availability.


#PromptWars #GoogleAntigravity #BuildInPublic #GenerativeAI #EventPlanning

