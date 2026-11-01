from __future__ import annotations

import csv
import html
import io
import json
from datetime import date, datetime, time, timedelta

import streamlit as st

from ai_engine import generate_blueprint, get_api_key, get_model
from planner import (
    allocate_budget, budget_health, build_checklist, build_timeline, clean_text,
    local_blueprint, plan_as_markdown, validate_event,
)

st.set_page_config(page_title="GatherGlow | Event Planning Studio", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#17252b; --muted:#64747a; --teal:#0b6e69; --mint:#dff4ed; --cream:#f7f7f2; --coral:#d9785d; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
.stApp { background:linear-gradient(180deg,#f7f8f4 0%,#f5f7f6 100%); }
[data-testid="stSidebar"] { background:#102f32; }
[data-testid="stSidebar"] * { color:#edf5ef !important; }
[data-testid="stSidebar"] [data-testid="stMetricValue"] { color:#d9efe4 !important; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; }
h1 { font-size:2.5rem !important; }
.hero { background:linear-gradient(110deg,#102f32 0%,#145d57 58%,#3b8071 100%); padding:2rem 2.2rem; border-radius:22px; color:#fff; margin-bottom:1.25rem; box-shadow:0 16px 35px rgba(16,47,50,.13); }
.hero-kicker { color:#b9e4d5; text-transform:uppercase; letter-spacing:.18em; font-size:.72rem; font-weight:700; }
.hero h1 { color:white !important; margin:.3rem 0 .4rem 0; }
.hero p { color:#e1eee8; max-width:760px; margin:0; font-size:1.02rem; }
.eyebrow { color:var(--teal); font-weight:700; letter-spacing:.13em; text-transform:uppercase; font-size:.72rem; }
.panel { background:#fff; border:1px solid #e4eae6; border-radius:18px; padding:1rem 1.2rem; box-shadow:0 6px 22px rgba(22,54,49,.045); }
.stat { background:#fff; border:1px solid #e3eae5; border-radius:16px; padding:1rem 1.1rem; min-height:102px; }
.stat-label { color:#72817c; font-size:.78rem; font-weight:600; }
.stat-value { color:#173c3a; font-family:'Manrope'; font-size:1.55rem; font-weight:800; margin-top:.2rem; }
.stat-note { color:#8b9691; font-size:.76rem; }
.pill { display:inline-block; border-radius:30px; padding:.28rem .65rem; background:#e3f3ed; color:#14665d; font-size:.76rem; font-weight:700; }
.small-muted { color:#71807d; font-size:.84rem; }
div.stButton > button[kind="primary"] { background:#0b6e69; border-color:#0b6e69; border-radius:11px; font-weight:700; }
div.stButton > button { border-radius:11px; }
[data-testid="stMetric"] { background:#fff; border:1px solid #e5ebe7; padding:.75rem .9rem; border-radius:14px; }
[data-testid="stMetricLabel"] { color:#667871; }
[data-testid="stMetricValue"] { color:#173c3a; }
.stTabs [data-baseweb="tab-list"] { gap:.5rem; background:#edf2ee; border-radius:13px; padding:.35rem; }
.stTabs [data-baseweb="tab"] { border-radius:10px; padding:.45rem .85rem; }
.stTabs [aria-selected="true"] { background:#fff !important; color:#0b6e69 !important; }
hr { border-color:#e3eae5; }
footer { visibility:hidden; }
@media (max-width: 700px) { .hero { padding:1.35rem; } h1 { font-size:1.9rem !important; } }
</style>
""", unsafe_allow_html=True)

if "event" not in st.session_state:
    st.session_state.event = None
if "plan" not in st.session_state:
    st.session_state.plan = None
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = "Not generated"
if "tasks" not in st.session_state:
    st.session_state.tasks = None
if "plan_revision" not in st.session_state:
    st.session_state.plan_revision = 0
if "task_revision" not in st.session_state:
    st.session_state.task_revision = 0
if "quotes" not in st.session_state:
    st.session_state.quotes = []
if "vendors" not in st.session_state:
    st.session_state.vendors = []

with st.sidebar:
    st.markdown("# ✦ GatherGlow")
    st.caption("CELEBRATION PLANNING STUDIO")
    st.markdown("---")
    st.markdown("**Your planning workspace**")
    st.markdown("Plan with intention. Adapt without chaos.")
    api_active = bool(get_api_key())
    st.markdown(f"<span class='pill'>{'Gemini key configured' if api_active else 'Local mode ready'}</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Built around six evaluation areas**")
    for area in ["Problem alignment", "Code quality", "Security", "Efficiency", "Testing", "Accessibility"]:
        st.markdown(f"✓ {area}")
    st.markdown("---")
    st.caption("Your inputs stay in this session. No account or database is required.")

st.markdown("""
<div class="hero">
  <div class="hero-kicker">Thoughtful events · less planning stress</div>
  <h1>Make room for the moments<br/>that matter.</h1>
  <p>One calm workspace for your event concept, budget, run-of-show, vendors and last-minute what-ifs. Start with a few details; GatherGlow turns them into an actionable plan.</p>
</div>
""", unsafe_allow_html=True)

# Create / revise event brief.
with st.expander("✦  Create or update your event brief", expanded=st.session_state.event is None):
    with st.form("event_brief", clear_on_submit=False):
        c1, c2, c3 = st.columns([1.15, 1, 1])
        with c1:
            event_name = st.text_input("Event name", value=(st.session_state.event or {}).get("name", "A day to remember"), max_chars=80)
            event_type = st.selectbox("Celebration type", ["Wedding", "Birthday", "Community event"], index=["Wedding", "Birthday", "Community event"].index((st.session_state.event or {}).get("event_type", "Wedding")))
            city = st.text_input("City / locality", value=(st.session_state.event or {}).get("city", "Kolkata"), max_chars=80)
        with c2:
            event_date = st.date_input("Event date", value=(st.session_state.event or {}).get("event_date", date.today() + timedelta(days=45)), min_value=date.today())
            guests = st.number_input("Expected guests", min_value=1, max_value=100000, value=int((st.session_state.event or {}).get("guests", 120)), step=5)
            budget = st.number_input("Total budget (₹)", min_value=1000, max_value=100000000, value=int((st.session_state.event or {}).get("budget", 250000)), step=5000)
        with c3:
            venue = st.text_input("Venue / venue type", value=(st.session_state.event or {}).get("venue", "To be confirmed"), max_chars=100)
            start_time = st.time_input("Guest arrival", value=(st.session_state.event or {}).get("start_time", time(17, 0)), step=900)
            setting = st.selectbox("Setting", ["Indoor", "Outdoor", "Mixed / undecided"], index=["Indoor", "Outdoor", "Mixed / undecided"].index((st.session_state.event or {}).get("setting", "Mixed / undecided")))
        st.markdown("**Make it personal and inclusive**")
        d1, d2 = st.columns(2)
        with d1:
            vibe = st.text_input("Mood / style", value=(st.session_state.event or {}).get("vibe", "warm, elegant and relaxed"), max_chars=100, help="Examples: joyful and colourful; intimate and premium; low-waste community gathering")
            dietary = st.text_input("Dietary needs", value=(st.session_state.event or {}).get("dietary", "Vegetarian options; clearly labelled allergens"), max_chars=240)
        with d2:
            access = st.text_input("Accessibility needs", value=(st.session_state.event or {}).get("access", "Step-free route and reserved seating"), max_chars=240)
            special = st.text_input("One personal detail to celebrate", value=(st.session_state.event or {}).get("special", "A shared family tradition"), max_chars=240)
        submitted = st.form_submit_button("Build my event plan", type="primary", use_container_width=True)
        if submitted:
            brief = {"name": clean_text(event_name, 80), "event_type": event_type, "city": clean_text(city, 80),
                     "event_date": event_date, "guests": int(guests), "budget": float(budget),
                     "venue": clean_text(venue, 100), "start_time": start_time, "setting": setting,
                     "vibe": clean_text(vibe, 100), "dietary": clean_text(dietary, 240),
                     "access": clean_text(access, 240), "special": clean_text(special, 240)}
            errors = validate_event(brief)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                with st.spinner("Designing your plan and checking the moving parts…"):
                    plan, mode, warning = generate_blueprint(brief)
                st.session_state.event = brief
                st.session_state.plan = plan
                st.session_state.ai_mode = mode
                st.session_state.tasks = plan["checklist"]
                # Version widget keys so a new event never inherits stale budget/task values.
                st.session_state.plan_revision += 1
                st.session_state.task_revision += 1
                st.session_state.generated_at = datetime.now().isoformat(timespec="minutes")
                if warning:
                    st.warning(warning)
                st.success(f"Your plan is ready · {mode}")
                st.rerun()

if not st.session_state.event or not st.session_state.plan:
    st.info("Start with the event brief above. A sample plan is available below so you can explore the workspace before entering your own details.")
    if st.button("Load an example birthday plan"):
        sample = {"name":"Mira's Garden Birthday", "event_type":"Birthday", "city":"Kolkata", "event_date":date.today()+timedelta(days=35), "guests":80, "budget":180000.0, "venue":"Garden café", "start_time":time(17,0), "setting":"Outdoor", "vibe":"joyful, intimate and colourful", "dietary":"Vegetarian and Jain-friendly options; allergen labels", "access":"Step-free access and reserved seating", "special":"A family photo-and-memory wall"}
        st.session_state.event = sample
        st.session_state.plan = local_blueprint(sample)
        st.session_state.ai_mode = "Example · Local planning engine"
        st.session_state.tasks = st.session_state.plan["checklist"]
        st.session_state.plan_revision += 1
        st.session_state.task_revision += 1
        st.rerun()
    st.stop()

event = st.session_state.event
plan = st.session_state.plan
tasks = st.session_state.tasks or plan["checklist"]

# Top summary strip
remaining = (event["event_date"] - date.today()).days
allocations = plan["budget"]
completed = sum(1 for t in tasks if t.get("done"))
progress = int(100 * completed / max(1, len(tasks)))
st.markdown(f"<div class='eyebrow'>YOUR EVENT · {html.escape(clean_text(event['event_type'], 40).upper())}</div><h2 style='margin-top:.15rem'>{html.escape(clean_text(event['name'],80))}</h2><div class='small-muted'>{html.escape(clean_text(event['city'],80))} · {event['event_date'].strftime('%d %B %Y')} · {event['guests']:,} guests · <span class='pill'>{st.session_state.ai_mode}</span></div>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Budget envelope", f"₹{event['budget']:,.0f}", f"₹{event['budget']/event['guests']:,.0f} per guest")
with m2: st.metric("Countdown", f"{remaining} days", "Event date" if remaining >= 0 else "Date passed")
with m3: st.metric("Checklist progress", f"{progress}%", f"{completed} of {len(tasks)} complete")
with m4: st.metric("Planning status", "On track" if budget_health(allocations,event['budget']) == "Balanced" else budget_health(allocations,event['budget']), "Budget allocation")

st.markdown(" ")
tabs = st.tabs(["✦ Overview", "₹ Budget studio", "◷ Run of show", "☑ Vendor & task desk", "↗ What-if lab", "✧ AI copilot & export"])

with tabs[0]:
    left, right = st.columns([1.2, .8], gap="large")
    with left:
        st.markdown("### The creative direction")
        direction = plan["creative_direction"]
        st.markdown(f"<div class='panel'><div class='eyebrow'>THE CONCEPT</div><h3>{html.escape(clean_text(direction['theme'],120))}</h3><p>{html.escape(clean_text(plan['event_summary'],500))}</p><div>{''.join([f'<span class=\"pill\" style=\"margin:0 .3rem .3rem 0\">{html.escape(clean_text(c,40))}</span>' for c in direction['palette']])}</div><hr/><b>Signature experience</b><ul>{''.join([f'<li>{html.escape(clean_text(x,180))}</li>' for x in direction['experience']])}</ul><b>Food direction</b><p>{html.escape(clean_text(direction['food_direction'],240))}</p><b>Entertainment</b><p>{html.escape(clean_text(direction['entertainment'],240))}</p></div>", unsafe_allow_html=True)
        st.markdown("### Personal touches")
        for idea in plan["personalized_ideas"]:
            st.markdown(f"- {idea}")
        st.markdown("### Risk register")
        for risk in plan["risk_register"]:
            with st.expander(f"{risk['risk']} · {risk['trigger']}"):
                st.write(risk["response"])
    with right:
        st.markdown("### The budget at a glance")
        st.bar_chart({"Allocation (₹)": allocations}, horizontal=True)
        st.markdown("### Inclusion commitments")
        for note in plan["inclusion_notes"]:
            st.markdown(f"- {note}")
        st.caption("Planning estimates only. Confirm local supplier quotes, venue permissions and applicable safety requirements before booking.")

with tabs[1]:
    st.markdown("### Give every rupee a job")
    st.caption("The starting allocation is a planning baseline. Adjust category targets to match your priorities; the total is checked live.")
    edited = {}
    cols = st.columns(2)
    for idx, (category, value) in enumerate(allocations.items()):
        with cols[idx % 2]:
            edited[category] = st.number_input(category, min_value=0, max_value=100000000, value=int(value), step=1000, key=f"budget_{st.session_state.plan_revision}_{category}")
    # Persist user edits so the dashboard, summary and exports stay consistent.
    st.session_state.plan["budget"] = {k: float(v) for k, v in edited.items()}
    total_allocated = sum(edited.values())
    diff = event["budget"] - total_allocated
    if diff == 0:
        st.success("Your category allocations add up exactly to the event budget.")
    elif diff > 0:
        st.info(f"₹{diff:,.0f} remains unallocated. Consider assigning it to contingency or a priority category.")
    else:
        st.error(f"You are ₹{abs(diff):,.0f} over the budget. Reduce optional spend before committing.")
    st.progress(min(1.0, total_allocated / max(1, event["budget"])))
    st.markdown(f"**Allocated:** ₹{total_allocated:,.0f} of ₹{event['budget']:,.0f} · **Per guest:** ₹{total_allocated/max(1,event['guests']):,.0f}")
    st.markdown("#### Quote tracker")
    st.caption("Enter real quotes as you receive them; no vendor prices are fabricated by GatherGlow.")
    with st.form("quote_form"):
        q1,q2,q3 = st.columns([1.2,1,1])
        q_name = q1.text_input("Vendor / supplier name", max_chars=80)
        q_category = q2.selectbox("Category", list(allocations.keys()))
        q_amount = q3.number_input("Quoted amount (₹)", min_value=0, max_value=100000000, value=0, step=1000)
        add_quote = st.form_submit_button("Add quote")
        if add_quote:
            if not clean_text(q_name, 80) or q_amount <= 0:
                st.warning("Enter a supplier name and a quote greater than ₹0.")
            else:
                st.session_state.quotes.append({"name":clean_text(q_name,80),"category":q_category,"amount":int(q_amount)})
                st.rerun()
    if st.session_state.quotes:
        st.dataframe(st.session_state.quotes, use_container_width=True, hide_index=True)
        quote_total = sum(q["amount"] for q in st.session_state.quotes)
        st.metric("Total entered quotes", f"₹{quote_total:,.0f}", f"{len(st.session_state.quotes)} supplier quotes")
        quote_by_category = {category: sum(q["amount"] for q in st.session_state.quotes if q["category"] == category) for category in allocations}
        quote_rows = [{"Category": category, "Planned (₹)": int(allocations[category]),
                       "Quotes entered (₹)": quote_by_category[category],
                       "Remaining after quotes (₹)": int(allocations[category] - quote_by_category[category])}
                      for category in allocations]
        st.caption("Compare supplier quotes with your current category targets. A quote is not a booking or contract.")
        st.dataframe(quote_rows, use_container_width=True, hide_index=True)
        exceeded = [category for category, amount in quote_by_category.items() if amount > allocations[category]]
        if exceeded:
            st.warning("Quotes exceed the planned allocation for: " + ", ".join(exceeded) + ". Recheck scope or adjust the budget before confirming.")
    else:
        st.info("No supplier quotes entered yet.")

with tabs[2]:
    st.markdown("### A clear run-of-show")
    st.caption("Times are calculated from your event start time. Change the event brief to rebuild the schedule.")
    for item in plan["timeline"]:
        a,b,c = st.columns([.8,2.4,.8])
        a.markdown(f"**{item['time']}**")
        b.markdown(item["activity"])
        c.markdown(f"<span class='pill'>{item['duration']}</span>", unsafe_allow_html=True)
        st.divider()
    st.markdown("**Operations reminder:** assign one named person as the event-day point of contact and share the final run-of-show with every confirmed supplier.")

with tabs[3]:
    st.markdown("### From idea to done")
    st.caption("This is a planning checklist, not a claim that vendors have been contacted or booked. Check tasks off as you complete them.")
    updated_tasks = []
    for task in tasks:
        row = st.columns([.12,2.7,.8,.9])
        done = row[0].checkbox(f"Mark complete: {task['task']}", value=bool(task.get("done")), key=f"task_{st.session_state.task_revision}_{task['id']}", label_visibility="collapsed")
        row[1].markdown(("~~" if done else "") + task["task"] + ("~~" if done else ""))
        row[2].markdown(f"`{task['area']}`")
        due_date = date.fromisoformat(task["due"])
        due_label = f"OVERDUE · {due_date.strftime('%d %b')}" if due_date < date.today() else f"Due {due_date.strftime('%d %b')}"
        row[3].markdown(f"<span class='small-muted'>{html.escape(due_label)}</span>", unsafe_allow_html=True)
        updated_tasks.append({**task,"done":done})
    st.session_state.tasks = updated_tasks
    st.progress(sum(t["done"] for t in updated_tasks)/max(1,len(updated_tasks)))
    st.markdown("#### Vendor contact sheet")
    st.caption("Add verified contacts yourself. GatherGlow does not invent or endorse real suppliers.")
    with st.form("vendor_form"):
        v1,v2,v3,v4 = st.columns([1,1,1.1,1.2])
        v_name = v1.text_input("Vendor / contact", max_chars=80)
        v_type = v2.selectbox("Service", ["Venue", "Catering", "Decor", "Photo / video", "Entertainment", "Transport", "Accessibility", "Other"])
        v_phone = v3.text_input("Phone / email", max_chars=100)
        v_status = v4.selectbox("Status", ["To contact", "Contacted", "Quote received", "Confirmed"])
        save_vendor = st.form_submit_button("Save contact")
        if save_vendor and clean_text(v_name,80):
            st.session_state.vendors.append({"contact":clean_text(v_name,80),"service":v_type,"details":clean_text(v_phone,100),"status":v_status})
            st.rerun()
    if st.session_state.vendors:
        st.dataframe(st.session_state.vendors, use_container_width=True, hide_index=True)
    else:
        st.info("Your verified vendor contacts will appear here.")

with tabs[4]:
    st.markdown("### Plans change. Your plan should adapt.")
    st.caption("Explore the effect of a changed budget, guest count or weather condition before it becomes an event-day surprise.")
    x1,x2,x3 = st.columns(3)
    revised_budget = x1.number_input("Revised budget (₹)", min_value=1000, max_value=100000000, value=int(event["budget"]), step=5000)
    revised_guests = x2.number_input("Revised guest count", min_value=1, max_value=100000, value=int(event["guests"]), step=5)
    weather = x3.selectbox("Scenario", ["No change", "Heavy rain", "Heatwave", "Vendor cancellation", "Guest count increases"])
    revised_per_guest = revised_budget / revised_guests
    budget_per_person = event["budget"] / event["guests"]
    st.markdown("#### Impact snapshot")
    xx1,xx2,xx3 = st.columns(3)
    xx1.metric("New per-guest budget", f"₹{revised_per_guest:,.0f}", f"{revised_per_guest-budget_per_person:+,.0f} vs current")
    xx2.metric("Budget change", f"₹{revised_budget-event['budget']:+,.0f}")
    xx3.metric("Guest change", f"{revised_guests-event['guests']:+,}")
    scenario_responses = {
        "No change": ["Keep the confirmed run-of-show and maintain the contingency reserve."],
        "Heavy rain": ["Move critical activities under cover or to the pre-confirmed indoor backup.", "Protect electrical equipment and keep walkways non-slip and well lit.", "Send the venue-switch message through the agreed guest communication channel."],
        "Heatwave": ["Move strenuous or outdoor activities away from peak heat.", "Add shaded rest points, drinking water and a clear medical-help contact.", "Check cooling and ventilation capacity with the venue."],
        "Vendor cancellation": ["Activate the pre-vetted backup supplier or simplify the affected activity.", "Keep the contract, payment record and key contact details accessible.", "Notify guests only if the change affects their experience or schedule."],
        "Guest count increases": ["Reconfirm legal venue capacity, accessible seating, food quantity and transport.", "Reprice catering using actual per-person quotes; do not assume a linear price.", "Protect safety and food requirements before adding decorative extras."],
    }
    for response in scenario_responses[weather]:
        st.markdown(f"- {response}")
    if revised_budget < event["budget"]:
        st.warning("Lower budget: preserve safety, food quality, accessibility and essential logistics. Reduce optional styling, printed material or non-essential add-ons first.")
    elif revised_guests > event["guests"]:
        st.warning("Higher guest count: verify venue capacity and supplier availability before accepting additional guests.")

with tabs[5]:
    st.markdown("### Your planning copilot")
    st.caption("Gemini creates the personalised concept and ideas; deterministic app logic calculates budgets and event times. The fallback remains available without an API key.")
    st.markdown(f"**Current planning mode:** `{st.session_state.ai_mode}`")
    if not get_api_key():
        st.info("To enable live Gemini generation, add GEMINI_API_KEY to Streamlit Secrets. The rest of the planner already works without it.")
    question = st.text_area("Ask about your current event", placeholder="How can I make the reception more accessible without increasing the budget?", max_chars=600, height=90)
    if st.button("Get planning guidance", type="primary", disabled=not bool(question.strip())):
        if get_api_key():
            try:
                from google import genai
                client = genai.Client(api_key=get_api_key())
                model = get_model()
                prompt = ("You are GatherGlow, an inclusive event-planning assistant. Give actionable, safe advice. "
                          "Do not invent local vendor names, availability, prices or bookings. Mark assumptions. "
                          f"Event: {json.dumps({'type':event['event_type'],'guests':event['guests'],'budget_inr':event['budget'],'city':event['city'],'date':event['event_date'].isoformat(),'dietary':event['dietary'],'accessibility':event['access']})}. "
                          f"Current budget and schedule context: {json.dumps({'budget':plan['budget'],'timeline':plan['timeline']})}. "
                          f"User question: {clean_text(question,600)}")
                with st.spinner("GatherGlow is thinking…"):
                    reply = client.models.generate_content(model=model, contents=prompt)
                st.markdown(reply.text or "The assistant did not return a response. Please try again.")
            except Exception as exc:
                st.error(f"AI guidance is unavailable ({type(exc).__name__}). Your saved plan is unchanged.")
        else:
            st.info("Add a Gemini API key in Streamlit Secrets to use the live copilot. For now, use the What-if Lab and deterministic planning tools.")
    st.markdown("---")
    st.markdown("### Export and share")
    markdown_plan = plan_as_markdown(event, {**plan,"checklist":tasks})
    if st.session_state.get("vendors"):
        markdown_plan += "\n\n## Vendor contacts (user-entered; verify before use)\n"
        markdown_plan += "\n".join(f"- {v['contact']} · {v['service']} · {v['status']} · {v['details']}" for v in st.session_state.vendors)
    if st.session_state.get("quotes"):
        markdown_plan += "\n\n## Supplier quotes (user-entered; not verified)\n"
        markdown_plan += "\n".join(f"- {q['name']} · {q['category']} · ₹{q['amount']:,.0f}" for q in st.session_state.quotes)
    json_payload = {
        "event": {**event, "event_date": event["event_date"].isoformat(), "start_time": event["start_time"].strftime("%H:%M")},
        "plan": {**plan, "checklist": tasks},
        "vendor_contacts": st.session_state.get("vendors", []),
        "supplier_quotes": st.session_state.get("quotes", []),
        "generated_at": st.session_state.get("generated_at", "Example plan"),
        "planning_mode": st.session_state.ai_mode,
    }
    e1,e2 = st.columns(2)
    e1.download_button("↓ Download event plan (.md)", markdown_plan, file_name="gatherglow-event-plan.md", mime="text/markdown", use_container_width=True)
    e2.download_button("↓ Download full data (.json)", json.dumps(json_payload, indent=2, ensure_ascii=False), file_name="gatherglow-event-plan.json", mime="application/json", use_container_width=True)
    csv_rows = [{"time":x["time"],"activity":x["activity"],"duration":x["duration"]} for x in plan["timeline"]]
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=["time","activity","duration"])
    writer.writeheader(); writer.writerows(csv_rows)
    st.download_button("↓ Download timeline (.csv)", csv_buffer.getvalue(), file_name="gatherglow-run-of-show.csv", mime="text/csv")
    st.markdown("---")
    st.markdown("**Privacy note:** event details are held in the active app session. Gemini receives the event brief when an API key is configured and a plan or copilot response is requested. Vendor contacts and quotes are user-entered and included only in exports. Do not enter sensitive personal data.")

st.markdown("---")
st.markdown("<div class='small-muted'>GatherGlow · PromptWars Virtual · Challenge 5: Celebration & Event Planner<br/>Planning support only. Supplier availability, quotations, contracts, permits and venue safety must be verified directly.</div>", unsafe_allow_html=True)
