import unittest
from scripts.content_engine_v2.schema import make_item, to_v1
from scripts.content_engine_v2.quality import evaluate, DISCLAIMERS
from scripts.content_engine_v2.render import render_all

class EngineV2Tests(unittest.TestCase):
    def sample(self):
        return make_item(domain="ai", tab="آموزش", title="چگونه خروجی هوش مصنوعی را ارزیابی کنیم؟",
            body="برای ارزیابی خروجی هوش مصنوعی، معیار موفقیت را پیش از استفاده مشخص کنید. پاسخ را با منبع معتبر مقایسه کنید، محدودیت‌ها را ثبت کنید و در تصمیم‌های مهم بازبینی انسانی داشته باشید.",
            audience="beginner", formats=["website","telegram","instagram_reel","instagram_carousel"],
            short_script=["هر پاسخ هوش مصنوعی را درست فرض نکن.","ادعاها را با منبع معتبر و معیار روشن بسنج.","پیش از استفاده مهم، بازبینی انسانی انجام بده."],
            sources=[{"title":"NIST AI Risk Management Framework","url":"https://www.nist.gov/itl/ai-risk-management-framework"}])
    def test_valid_item_and_renderers(self):
        item=self.sample(); report=evaluate(item)
        self.assertTrue(report["ok"], report["errors"])
        rendered=render_all(item, "https://example.test/article")
        self.assertIn("telegram", rendered); self.assertEqual(len(rendered["instagram_carousel"]), 3)
    def test_financial_disclaimer_required(self):
        item=self.sample(); item["domain"]="forex"
        report=evaluate(item)
        self.assertFalse(report["ok"]); self.assertFalse(report["checks"]["disclaimer"])
    def test_duplicate_title_rejected(self):
        item=self.sample(); self.assertFalse(evaluate(item, existing_titles={item["title"]})["ok"])
    def test_v1_adapter(self):
        item=self.sample(); legacy=to_v1(item, date="2026-11-10")
        self.assertEqual(legacy["date"], "2026-11-10"); self.assertEqual(len(legacy["short_script"]), 3)

if __name__ == "__main__": unittest.main()
