import unittest
from scripts.content_engine_v2.quality import evaluate

class QualitySimilarityIntegrationTests(unittest.TestCase):
    def item(self,title,body):
        return {"domain":"ai","tab":"آموزش","audience":"beginner","title":title,"body":body,
            "short_script":["این یک نکته مهم است.","معیارها را دقیق و مستقل بررسی کن.","نتیجه را با منبع معتبر بسنج."],
            "sources":[{"title":"NIST","url":"https://www.nist.gov/"}],"formats":["website"]}
    def test_near_duplicate_is_blocked(self):
        current=self.item("ارزیابی خروجی هوش مصنوعی","برای سنجش پاسخ مدل باید ادعاها را با منبع معتبر بررسی کرد و محدودیت‌ها را شناخت.")
        old=self.item("چگونه خروجی هوش مصنوعی را ارزیابی کنیم","برای بررسی پاسخ مدل ادعاها را با منابع معتبر بسنجید و محدودیت‌ها را بشناسید.")
        result=evaluate(current,existing_items=[old])
        self.assertFalse(result["checks"]["near_duplicate"])
        self.assertTrue(result["near_duplicates"])
    def test_source_is_mandatory(self):
        current=self.item("عنوان آموزشی مستقل","متن آموزشی که منبع معتبر برای آن مشخص نشده است.")
        current["sources"]=[]
        result=evaluate(current)
        self.assertFalse(result["checks"]["sources"])
    def test_unrelated_content_passes_similarity_gate(self):
        current=self.item("ارزیابی خروجی هوش مصنوعی","برای سنجش پاسخ مدل باید ادعاها را با منبع معتبر بررسی کرد و محدودیت‌ها را شناخت.")
        old=self.item("ریکاوری در ورزش قهرمانی","ثبت خواب و خستگی می‌تواند گفت‌وگو با کادر تخصصی را بهتر کند.")
        result=evaluate(current,existing_items=[old])
        self.assertTrue(result["checks"]["near_duplicate"])

if __name__=="__main__": unittest.main()
