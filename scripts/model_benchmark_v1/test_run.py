import unittest

from run import evaluate, parse_json


class BenchmarkTests(unittest.TestCase):
    def test_parse_json_with_code_fence(self):
        value = parse_json('```json\n{"title":"آزمون"}\n```')
        self.assertEqual(value["title"], "آزمون")

    def test_evaluate_valid_structured_output(self):
        output = {
            "title": "آموزش سواد هوش مصنوعی",
            "body": "هوش مصنوعی می‌تواند در تصمیم‌گیری به انسان کمک کند، اما خروجی آن باید با توجه به زمینه و محدودیت‌های سامانه بررسی شود. نظارت انسانی و ارزیابی ریسک به استفاده مسئولانه کمک می‌کنند.",
            "short_script": ["هوش مصنوعی ابزار است.", "خروجی را بررسی کن.", "نظارت انسانی را حفظ کن."],
            "source_ids": ["nist"],
        }
        report = evaluate(output, ["nist"])
        self.assertEqual(report["score"], 100)
        self.assertTrue(all(report["checks"].values()))

    def test_unknown_source_is_rejected_by_format_gate(self):
        output = {
            "title": "آموزش سواد هوش مصنوعی",
            "body": "هوش مصنوعی می‌تواند در تصمیم‌گیری به انسان کمک کند، اما خروجی آن باید با توجه به زمینه و محدودیت‌های سامانه بررسی شود. نظارت انسانی و ارزیابی ریسک به استفاده مسئولانه کمک می‌کنند.",
            "short_script": ["هوش مصنوعی ابزار است.", "خروجی را بررسی کن.", "نظارت انسانی را حفظ کن."],
            "source_ids": ["invented"],
        }
        report = evaluate(output, ["nist"])
        self.assertFalse(report["checks"]["sources_are_allowed"])
        self.assertEqual(report["score"], 85)

    def test_invalid_json_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_json("not json")


if __name__ == "__main__":
    unittest.main()
