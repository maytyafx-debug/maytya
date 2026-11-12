import unittest
from scripts.content_engine_v2.promote import prepare_promotion

class PromotionTests(unittest.TestCase):
    def approved_item(self):
        return {"id":"new-1","domain":"ai","tab":"آموزش","title":"راهنمای سنجش پاسخ سامانه","body":"برای سنجش پاسخ سامانه، ادعاها را با منابع معتبر بررسی کنید. معیارهای کیفیت را پیش از استفاده مشخص کنید و محدودیت‌ها را ثبت کنید. در تصمیم‌های حساس، بازبینی انسانی را حفظ کنید.","audience":"beginner","formats":["website","telegram"],"short_script":["پاسخ روان همیشه درست نیست.","ادعاها را با منبع معتبر بررسی کن.","محدودیت‌ها را ثبت کن و بازبینی انسانی داشته باش."],"sources":[{"title":"NIST","url":"https://www.nist.gov/"}],"disclaimer":"این محتوا آموزشی است؛ خروجی هوش مصنوعی ممکن است خطا داشته باشد و باید با منابع معتبر و بازبینی انسانی بررسی شود.","status":"approved","quality":{"ok":True}}
    def test_promotion_is_additive_and_keeps_old_history(self):
        old={"sections":{"ai":{"name":"هوش مصنوعی","items":[{"title":"مطلب قبلی","body":"متن قدیمی"}]}}}
        v2={"items":[self.approved_item()]}
        result,summary=prepare_promotion(v2,old,{"new-1"})
        self.assertEqual(len(result["sections"]["ai"]["items"]),2)
        self.assertEqual(result["sections"]["ai"]["items"][1]["title"],"مطلب قبلی")
        self.assertEqual(summary["approved"],1)
        self.assertEqual(result["sections"]["ai"]["items"][0]["v2_id"],"new-1")
    def test_unapproved_item_cannot_be_promoted(self):
        item=self.approved_item(); item["status"]="review"
        with self.assertRaises(ValueError):
            prepare_promotion({"items":[item]},{"sections":{}},{"new-1"})
    def test_failed_quality_gate_cannot_be_promoted(self):
        item=self.approved_item(); item["quality"]={"ok":False}
        with self.assertRaises(ValueError):
            prepare_promotion({"items":[item]},{"sections":{}},{"new-1"})

if __name__=="__main__": unittest.main()
