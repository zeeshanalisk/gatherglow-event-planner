import unittest
from datetime import date, time

from planner import (
    allocate_budget, budget_health, build_checklist, build_timeline, clean_text,
    local_blueprint, plan_as_markdown, validate_blueprint, validate_event,
)


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.event = {
            "name": "Test Celebration", "event_type": "Birthday", "city": "Kolkata",
            "event_date": date(2027, 1, 15), "guests": 100, "budget": 200000,
            "start_time": time(17, 30), "vibe": "warm and joyful", "setting": "Indoor",
            "dietary": "Vegetarian", "access": "Step-free", "special": "Memory wall",
        }

    def test_budget_allocations_sum_exactly(self):
        for amount in (1000, 99999, 200000, 10000000):
            allocations = allocate_budget(amount, 100)
            self.assertAlmostEqual(sum(allocations.values()), amount, places=2)
            self.assertTrue(all(v >= 0 for v in allocations.values()))

    def test_timeline_starts_at_user_time(self):
        timeline = build_timeline(date(2027, 1, 15), time(17, 30), "Birthday")
        self.assertEqual(timeline[0]["time"], "05:30 PM")
        self.assertGreaterEqual(len(timeline), 5)

    def test_validation_rejects_empty_name_and_invalid_guests(self):
        event = dict(self.event, name=" ", guests=0)
        errors = validate_event(event)
        self.assertTrue(any("event name" in e.lower() for e in errors))
        self.assertTrue(any("guest count" in e.lower() for e in errors))

    def test_validation_rejects_non_finite_budget_and_past_date(self):
        event = dict(self.event, budget=float("nan"), event_date=date(2000, 1, 1))
        errors = validate_event(event)
        self.assertTrue(any("finite amount" in e.lower() for e in errors))
        self.assertTrue(any("past" in e.lower() for e in errors))

    def test_local_blueprint_contains_required_deliverables(self):
        plan = local_blueprint(self.event)
        for key in ("creative_direction", "budget", "timeline", "checklist", "personalized_ideas", "risk_register", "inclusion_notes"):
            self.assertIn(key, plan)
        self.assertAlmostEqual(sum(plan["budget"].values()), self.event["budget"])

    def test_ai_output_cannot_override_budget_or_schedule(self):
        malicious = {"budget": {"Venue": 1}, "timeline": [], "event_summary": "A new concept"}
        result = validate_blueprint(malicious, self.event)
        self.assertAlmostEqual(sum(result["budget"].values()), self.event["budget"])
        self.assertGreater(len(result["timeline"]), 0)
        self.assertEqual(result["event_summary"], "A new concept")

    def test_clean_text_removes_control_characters_and_caps_length(self):
        self.assertEqual(clean_text("  hello\x00   world ", 11), "hello world")
        self.assertEqual(len(clean_text("x" * 500, 20)), 20)

    def test_budget_health_distinguishes_balanced_under_and_over(self):
        self.assertEqual(budget_health({"A": 60, "B": 40}, 100), "Balanced")
        self.assertEqual(budget_health({"A": 50}, 100), "Unallocated funds")
        self.assertEqual(budget_health({"A": 110}, 100), "Over budget")

    def test_checklist_has_nine_ordered_tasks_and_overdue_flags(self):
        checklist = build_checklist(date(2027, 1, 15))
        self.assertEqual(len(checklist), 9)
        self.assertEqual([task["id"] for task in checklist], list(range(1, 10)))
        self.assertTrue(all("overdue" in task and task["done"] is False for task in checklist))

    def test_markdown_export_contains_core_sections(self):
        plan = local_blueprint(self.event)
        markdown = plan_as_markdown(self.event, plan)
        for heading in ("## The concept", "## Budget (INR)", "## Run of show", "## Action checklist", "## Inclusion", "## Risks & responses"):
            self.assertIn(heading, markdown)


if __name__ == "__main__":
    unittest.main()
