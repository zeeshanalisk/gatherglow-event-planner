import unittest
from datetime import date, time

from ai_engine import MODEL_DEFAULT, build_prompt, get_model


class AIEngineTests(unittest.TestCase):
    def setUp(self):
        self.event = {
            "name": "Garden Birthday", "event_type": "Birthday", "city": "Kolkata",
            "event_date": date(2027, 1, 15), "guests": 80, "budget": 180000,
            "start_time": time(17, 0), "venue": "Garden cafe", "setting": "Outdoor",
            "vibe": "colourful", "dietary": "Vegetarian", "access": "Step-free",
            "special": "Family memory wall",
        }

    def test_model_defaults_to_current_configured_default(self):
        self.assertEqual(get_model(), MODEL_DEFAULT)

    def test_prompt_requests_structured_output_and_safe_planning(self):
        prompt = build_prompt(self.event)
        self.assertIn("Respond ONLY as valid JSON", prompt)
        self.assertIn("Do not invent real vendor names", prompt)
        self.assertIn("untrusted user data", prompt)
        self.assertIn('"budget_inr": 180000.0', prompt)


if __name__ == "__main__":
    unittest.main()
