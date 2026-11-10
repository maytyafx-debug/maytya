import json, tempfile, unittest
from pathlib import Path
from scripts.content_engine_v2.history import load_v1_history

class HistoryTests(unittest.TestCase):
    def test_reads_all_legacy_domains_without_mutating_source(self):
        payload={"sections":{"forex":{"items":[{"title":"الف","body":"متن","tab":"آموزش","date":"2026-01-01"}]},
            "sport":{"items":[{"title":"ب","body":"متن دوم","tab":"تمرین"}]}}}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"content.json"; original=json.dumps(payload,ensure_ascii=False)
            path.write_text(original,encoding="utf-8")
            history=load_v1_history(path)
            self.assertEqual(len(history),2)
            self.assertEqual({x["domain"] for x in history},{"forex","sport"})
            self.assertEqual(path.read_text(encoding="utf-8"),original)
    def test_live_archive_contains_all_metatya_domains(self):
        history=load_v1_history("docs/content.json")
        self.assertGreater(len(history),400)
        self.assertEqual({x["domain"] for x in history},
            {"forex","crypto","bourse","income","business","finance","education","psychology","law","ai","privacy","sport","health"})
    def test_missing_archive_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(load_v1_history(Path(tmp)/"missing.json"),[])

if __name__=="__main__": unittest.main()
