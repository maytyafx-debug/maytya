import unittest
from unittest.mock import patch
from scripts.content_engine_v2.generator import generate_item

GOOD = {
    "title": "آموزش محاسبه نرخ تبدیل ارز",
    "body": "برای محاسبه ارزش تبدیل، مقدار ارز را در نرخ تبدیل ضرب می‌کنیم. برای نمونه ۱۰۰۰ یورو با نرخ ۱.۱۰۰۰ برابر ۱۱۰۰ دلار است. این مثال صرفاً آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "short_script": ["نرخ تبدیل را بشناس.", "مقدار ارز را در نرخ ضرب کن.", "واحدها را دوباره بررسی کن."],
    "source_ids": ["cftc"],
}
BAD = {**GOOD, "body": "برای محاسبه ارزش تبدیل، مقدار ارز را در نرخ تبدیل ضرب می‌کنیم. ۱۰۰۰ × ۱.۱۰۰۰ = ۱۱۰۰۰ دلار. این مثال صرفاً آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست."}

class GeneratorSelfRepairTests(unittest.TestCase):
    def setUp(self):
        self.source_pack = [{"id":"cftc","title":"CFTC Forex advisory","url":"https://www.cftc.gov/"}]

    @patch("scripts.content_engine_v2.generator.verify_source", return_value={"ok":True,"status":200,"content_type":"text/html","title":"CFTC"})
    def test_bad_math_is_regenerated_and_rechecked(self, _verify):
        outputs = iter([BAD, GOOD])
        prompts = []
        def provider(prompt):
            prompts.append(prompt)
            return next(outputs)
        item = generate_item(domain="forex",tab="آموزش",audience="beginner",
            source_pack=self.source_pack,provider=provider,max_revisions=1)
        self.assertEqual(item["status"],"review")
        self.assertEqual(item["repair"]["outcome"],"passed_after_revision")
        self.assertEqual(item["repair"]["attempts"],1)
        self.assertIn("محاسبه عددی ناسازگار",prompts[1])

    @patch("scripts.content_engine_v2.generator.verify_source", return_value={"ok":True,"status":200,"content_type":"text/html","title":"CFTC"})
    def test_still_bad_after_revisions_is_blocked(self, _verify):
        item = generate_item(domain="forex",tab="آموزش",audience="beginner",
            source_pack=self.source_pack,provider=lambda _prompt: BAD,max_revisions=1)
        self.assertEqual(item["status"],"draft")
        self.assertEqual(item["repair"]["outcome"],"blocked_after_revisions")
        self.assertFalse(item["quality"]["ok"])

    def test_revision_limit_is_bounded(self):
        with self.assertRaises(ValueError):
            generate_item(domain="forex",tab="آموزش",audience="beginner",
                source_pack=self.source_pack,provider=lambda _prompt: GOOD,max_revisions=99)

if __name__ == "__main__":
    unittest.main()
