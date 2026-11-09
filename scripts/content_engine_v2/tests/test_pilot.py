import json
import unittest
from pathlib import Path
from scripts.content_engine_v2.quality import evaluate

class PilotSampleTests(unittest.TestCase):
    def test_all_pilot_samples_pass_automated_gate(self):
        fixture=Path(__file__).resolve().parents[1] / "examples" / "pilot-review.json"
        items=json.loads(fixture.read_text(encoding="utf-8"))["items"]
        self.assertEqual({x["domain"] for x in items},{"forex","ai","sport"})
        for item in items:
            with self.subTest(title=item["title"]):
                report=evaluate(item)
                self.assertTrue(report["ok"], report["errors"])

    def test_sport_pilot_keeps_distinct_audience_levels(self):
        fixture=Path(__file__).resolve().parents[1] / "examples" / "pilot-review.json"
        items=json.loads(fixture.read_text(encoding="utf-8"))["items"]
        sports=[x for x in items if x["domain"]=="sport"]
        self.assertEqual({x["audience"] for x in sports},{"sport_beginner","sport_olympic"})

if __name__ == "__main__": unittest.main()
