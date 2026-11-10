import unittest
from scripts.content_engine_v2.similarity import similarity, find_near_duplicates

class SimilarityTests(unittest.TestCase):
    def test_rephrased_persian_titles_are_similar(self):
        a="اهرم مالی و تفاوت وجه تضمین با اندازه تعهد"
        b="تفاوت اندازه قرارداد و وجه تضمین در معاملات اهرمی"
        self.assertGreater(similarity(a,b),0.2)
    def test_unrelated_titles_are_not_identical(self):
        self.assertLess(similarity("چارچوب ارزیابی هوش مصنوعی","ریکاوری ورزشکاران حرفه‌ای"),0.72)
    def test_duplicate_finder_returns_ranked_match(self):
        item={"title":"آموزش مدیریت ریسک","body":"شناخت ریسک و کنترل آن"}
        old=[{"id":"x","title":"مدیریت ریسک در آموزش","body":"کنترل ریسک و شناخت آن"}]
        self.assertTrue(find_near_duplicates(item,old,threshold=0.1))

if __name__ == "__main__": unittest.main()
