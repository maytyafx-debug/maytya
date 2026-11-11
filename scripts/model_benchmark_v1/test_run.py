import unittest

from scripts.model_benchmark_v1.run import evaluate, parse_json


class BenchmarkTests(unittest.TestCase):
    def valid_output(self):
        return {
            "title": "آموزش سواد هوش مصنوعی",
            "body": "هوش مصنوعی می‌تواند در تصمیم‌گیری به انسان کمک کند، اما خروجی آن باید با توجه به زمینه و محدودیت‌های سامانه بررسی شود. نظارت انسانی و ارزیابی ریسک به استفاده مسئولانه کمک می‌کنند.",
            "short_script": ["هوش مصنوعی ابزار است.", "خروجی را بررسی کن.", "نظارت انسانی را حفظ کن."],
            "source_ids": ["nist"],
        }

    def test_parse_json_with_code_fence(self):
        value = parse_json('```json\n{"title":"آزمون"}\n```')
        self.assertEqual(value["title"], "آزمون")

    def test_valid_structured_output(self):
        report = evaluate(self.valid_output(), ["nist"])
        self.assertEqual(report["format_guardrail_score"], 100)
        self.assertTrue(all(report["checks"].values()))

    def test_empty_sources_are_rejected(self):
        output = self.valid_output()
        output["source_ids"] = []
        report = evaluate(output, ["nist"])
        self.assertFalse(report["checks"]["sources_nonempty"])
        self.assertFalse(report["checks"]["sources_are_allowed"])

    def test_unknown_source_is_rejected(self):
        output = self.valid_output()
        output["source_ids"] = ["invented"]
        report = evaluate(output, ["nist"])
        self.assertFalse(report["checks"]["sources_are_allowed"])

    def test_extra_keys_are_rejected(self):
        output = self.valid_output()
        output["unsupported_claim"] = "anything"
        report = evaluate(output, ["nist"])
        self.assertFalse(report["checks"]["exact_required_keys"])

    def test_wrong_script_shape_is_rejected(self):
        output = self.valid_output()
        output["short_script"] = ["فقط یک خط"]
        report = evaluate(output, ["nist"])
        self.assertFalse(report["checks"]["three_script_lines"])

    def test_invalid_json_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_json("not json")


if __name__ == "__main__":
    unittest.main()
