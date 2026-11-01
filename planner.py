"""Core planning logic for GatherGlow: Celebration & Event Planner.

Pure functions live here so budget math, timeline generation and validation can
be tested without Streamlit or network access.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any
import math
import re


CATEGORY_WEIGHTS = {
    "Venue & setup": 0.22,
    "Food & beverage": 0.30,
    "Decor & experience": 0.14,
    "Photography & media": 0.10,
    "Entertainment": 0.09,
    "Logistics & accessibility": 0.07,
    "Contingency": 0.08,
}

EVENT_PROFILES = {
    "Wedding": {
        "title": "A day that feels unmistakably yours",
        "theme": "Modern heritage garden celebration",
        "palette": ["Warm ivory", "Sage", "Champagne"],
        "moments": ["A welcome ritual", "A story-led couple entrance", "A shared family toast"],
        "food_style": "A balanced regional menu with clearly labelled dietary alternatives",
        "entertainment": "Acoustic welcome set followed by a DJ or culturally relevant live music",
    },
    "Birthday": {
        "title": "A joyful celebration built around the guest of honour",
        "theme": "Colour-pop memory lane",
        "palette": ["Coral", "Butter yellow", "Midnight blue"],
        "moments": ["A memory wall", "A short surprise video", "A relaxed cake-and-photo moment"],
        "food_style": "Easy-to-serve favourites, one signature dessert and labelled alternatives",
        "entertainment": "A playlist-led party with one interactive game or activity",
    },
    "Community event": {
        "title": "A welcoming gathering where everyone can participate",
        "theme": "Neighbourhood together",
        "palette": ["Terracotta", "Leaf green", "Cream"],
        "moments": ["A community welcome", "A shared activity or showcase", "A thank-you circle"],
        "food_style": "Simple buffet or refreshment stations with allergen labels and inclusive options",
        "entertainment": "Local performers, open-mic slots or facilitated group activities",
    },
}

TASK_TEMPLATES = [
    ("Confirm venue, capacity and accessibility", "Venue", 30),
    ("Set the guest list and send invitations", "Guests", 24),
    ("Shortlist and confirm food partners", "Food", 21),
    ("Confirm photography / media coverage", "Media", 18),
    ("Approve decor, layout and signage", "Design", 14),
    ("Confirm entertainment and run-through", "Experience", 10),
    ("Collect dietary and access requirements", "Guests", 7),
    ("Reconfirm vendors, timings and contacts", "Operations", 3),
    ("Prepare emergency kit and final checklist", "Operations", 1),
]


def clean_text(value: Any, limit: int = 160) -> str:
    """Normalize user text and cap length before it enters prompts/UI exports."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(value or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def validate_event(event: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not clean_text(event.get("name"), 80):
        errors.append("Add an event name.")
    if event.get("event_type") not in EVENT_PROFILES:
        errors.append("Choose Wedding, Birthday or Community event.")
    try:
        budget = float(event.get("budget", 0))
        if not math.isfinite(budget) or not 1000 <= budget <= 100_000_000:
            errors.append("Budget must be a finite amount between ₹1,000 and ₹10 crore.")
    except (TypeError, ValueError):
        errors.append("Enter a valid budget.")
    try:
        guests = int(event.get("guests", 0))
        if not 1 <= guests <= 100_000:
            errors.append("Guest count must be between 1 and 100,000.")
    except (TypeError, ValueError):
        errors.append("Enter a valid guest count.")
    if not isinstance(event.get("event_date"), date):
        errors.append("Choose a valid event date.")
    elif event["event_date"] < date.today():
        errors.append("The event date cannot be in the past.")
    return errors


def allocate_budget(total: float, guests: int) -> dict[str, float]:
    """Return rounded category allocations that add up exactly to total."""
    total = max(0.0, float(total))
    result: dict[str, float] = {}
    remaining = round(total, 2)
    keys = list(CATEGORY_WEIGHTS)
    for category in keys[:-1]:
        value = round(total * CATEGORY_WEIGHTS[category], 2)
        result[category] = value
        remaining -= value
    result[keys[-1]] = round(remaining, 2)
    return result


def build_timeline(event_date: date, start_time: time, event_type: str) -> list[dict[str, str]]:
    """Create a practical run-of-show using the event date and start time."""
    if event_type == "Wedding":
        items = [("Guest arrival & welcome", 0, 45), ("Ceremony / key ritual", 45, 60),
                 ("Photos & refreshments", 105, 45), ("Meal service", 150, 75),
                 ("Speeches / family moments", 225, 35), ("Music & celebration", 260, 90),
                 ("Farewell & guest departures", 350, 30)]
    elif event_type == "Birthday":
        items = [("Guest arrival & welcome", 0, 30), ("Icebreaker / activity", 30, 35),
                 ("Guest-of-honour moment", 65, 20), ("Food & refreshments", 85, 55),
                 ("Cake, photos & wishes", 140, 35), ("Games / music", 175, 60),
                 ("Thank-you & departures", 235, 25)]
    else:
        items = [("Welcome desk & registration", 0, 30), ("Opening remarks", 30, 15),
                 ("Community activity / showcase", 45, 60), ("Refreshments & networking", 105, 45),
                 ("Open participation / performances", 150, 60), ("Closing thanks & clean-up brief", 210, 20)]
    base = datetime.combine(event_date, start_time)
    return [{"time": (base + timedelta(minutes=offset)).strftime("%I:%M %p"),
             "activity": title, "duration": f"{duration} min"}
            for title, offset, duration in items]


def build_checklist(event_date: date) -> list[dict[str, Any]]:
    today = date.today()
    tasks = []
    for index, (title, area, days_before) in enumerate(TASK_TEMPLATES, 1):
        due = event_date - timedelta(days=days_before)
        tasks.append({"id": index, "task": title, "area": area,
                      "due": due.isoformat(), "overdue": due < today, "done": False})
    return tasks


def local_blueprint(event: dict[str, Any]) -> dict[str, Any]:
    """Deterministic fallback: the core planner works even without an API key."""
    profile = EVENT_PROFILES[event["event_type"]]
    total = float(event["budget"])
    guests = int(event["guests"])
    allocations = allocate_budget(total, guests)
    event_date = event["event_date"]
    start = event.get("start_time", time(17, 0))
    city = clean_text(event.get("city", "your city"), 80) or "your city"
    vibe = clean_text(event.get("vibe", "welcoming"), 100) or "welcoming"
    access = clean_text(event.get("access", ""), 240)
    dietary = clean_text(event.get("dietary", ""), 240)
    special = clean_text(event.get("special", ""), 240)
    return {
        "event_summary": f"{profile['title']} in {city}, designed for {guests:,} guests with a {vibe.lower()} feel.",
        "creative_direction": {"theme": profile["theme"], "palette": profile["palette"],
                               "experience": profile["moments"], "food_direction": profile["food_style"],
                               "entertainment": profile["entertainment"]},
        "budget": allocations,
        "timeline": build_timeline(event_date, start, event["event_type"]),
        "checklist": build_checklist(event_date),
        "personalized_ideas": [
            f"Create a {vibe.lower()} welcome moment that reflects the host's story and local character.",
            f"Set up one low-pressure shared activity suitable for a group of {guests:,}.",
            f"Use a simple photo corner with a reusable backdrop to create a keepsake without excess waste.",
        ] + ([f"Plan around this personal detail: {special}."] if special else []),
        "inclusion_notes": [x for x in [
            f"Dietary planning: {dietary}. Label ingredients and keep serving tools separate." if dietary else "Label food clearly and provide a vegetarian option.",
            f"Accessibility planning: {access}. Confirm step-free routes, seating and accessible facilities with the venue." if access else "Confirm step-free routes, seating and accessible facilities with the venue.",
        ]],
        "risk_register": [
            {"risk": "Weather disruption", "trigger": "Rain or high wind for an outdoor event", "response": "Confirm an indoor backup or covered area and communicate the switch plan."},
            {"risk": "Vendor delay", "trigger": "A supplier misses the agreed arrival window", "response": "Assign one point of contact and keep a backup contact for critical services."},
            {"risk": "Budget pressure", "trigger": "Quotes exceed the planned category allocation", "response": "Protect food, access and safety first; reduce optional decor or add-ons before contingency."},
        ],
        "assumptions": [f"Budget is ₹{total:,.0f} for {guests:,} guests (₹{total / guests:,.0f} per guest).",
                        f"The plan is a starting estimate for {city}; obtain written local vendor quotes before booking."],
    }


def validate_blueprint(data: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    """Validate model output and restore required fields with safe fallbacks."""
    fallback = local_blueprint(event)
    if not isinstance(data, dict):
        return fallback
    clean = dict(fallback)
    for key in ("event_summary",):
        if isinstance(data.get(key), str) and data[key].strip():
            clean[key] = clean_text(data[key], 500)
    if isinstance(data.get("creative_direction"), dict):
        direction = data["creative_direction"]
        for field in ("theme", "food_direction", "entertainment"):
            if isinstance(direction.get(field), str) and direction[field].strip():
                clean["creative_direction"][field] = clean_text(direction[field], 240)
        for field in ("palette", "experience"):
            if isinstance(direction.get(field), list):
                vals = [clean_text(x, 80) for x in direction[field][:6] if clean_text(x, 80)]
                if vals:
                    clean["creative_direction"][field] = vals
    if isinstance(data.get("personalized_ideas"), list):
        vals = [clean_text(x, 240) for x in data["personalized_ideas"][:8] if clean_text(x, 240)]
        if vals:
            clean["personalized_ideas"] = vals
    if isinstance(data.get("inclusion_notes"), list):
        vals = [clean_text(x, 240) for x in data["inclusion_notes"][:8] if clean_text(x, 240)]
        if vals:
            clean["inclusion_notes"] = vals
    if isinstance(data.get("risk_register"), list):
        vals = []
        for item in data["risk_register"][:6]:
            if isinstance(item, dict) and all(isinstance(item.get(k), str) for k in ("risk", "trigger", "response")):
                vals.append({k: clean_text(item[k], 240) for k in ("risk", "trigger", "response")})
        if vals:
            clean["risk_register"] = vals
    if isinstance(data.get("assumptions"), list):
        vals = [clean_text(x, 240) for x in data["assumptions"][:6] if clean_text(x, 240)]
        if vals:
            clean["assumptions"] = vals
    # Never accept AI-generated budget math or event times: deterministic logic owns them.
    clean["budget"] = fallback["budget"]
    clean["timeline"] = fallback["timeline"]
    clean["checklist"] = fallback["checklist"]
    return clean


def budget_health(allocations: dict[str, float], total: float) -> str:
    actual = sum(float(v) for v in allocations.values())
    if abs(actual - total) < 0.02:
        return "Balanced"
    if actual > total:
        return "Over budget"
    return "Unallocated funds"


def plan_as_markdown(event: dict[str, Any], plan: dict[str, Any]) -> str:
    direction = plan["creative_direction"]
    lines = [f"# {clean_text(event['name'], 80)}", "", f"**{event['event_type']} · {event['event_date'].isoformat()} · {clean_text(event.get('city',''),80)}**",
             "", "## The concept", plan["event_summary"], f"**Theme:** {direction['theme']}",
             f"**Palette:** {', '.join(direction['palette'])}", "", "## Budget (INR)"]
    lines += [f"- {k}: ₹{v:,.0f}" for k, v in plan["budget"].items()]
    lines += ["", "## Run of show"]
    lines += [f"- {x['time']} — {x['activity']} ({x['duration']})" for x in plan["timeline"]]
    lines += ["", "## Action checklist"]
    lines += [f"- [{'x' if x.get('done') else ' '}] {x['task']} — due {x['due']}" for x in plan["checklist"]]
    lines += ["", "## Personal touches"] + [f"- {x}" for x in plan["personalized_ideas"]]
    lines += ["", "## Inclusion"] + [f"- {x}" for x in plan["inclusion_notes"]]
    lines += ["", "## Risks & responses"]
    lines += [f"- **{x['risk']}** ({x['trigger']}): {x['response']}" for x in plan["risk_register"]]
    lines += ["", "## Assumptions"] + [f"- {x}" for x in plan["assumptions"]]
    lines += ["", "---", "Generated with GatherGlow. Estimates are planning aids, not vendor quotes or guarantees."]
    return "\n".join(lines)
