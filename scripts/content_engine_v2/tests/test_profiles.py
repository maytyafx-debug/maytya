import unittest
from scripts.content_engine_v2.profiles import build_prompt
from scripts.content_engine_v2.providers import parse_json, resolve_sources

class ProfileProviderTests(unittest.TestCase):
    def test_sport_profiles_are_distinct(self):
        beginner=build_prompt(domain="sport",tab="تمرین",audience="sport_beginner",source_pack=[])
        olympic=build_prompt(domain="sport",tab="تمرین",audience="sport_olympic",source_pack=[])
        self.assertNotEqual(beginner,olympic)
        with self.assertRaises(ValueError): build_prompt(domain="sport",tab="تمرین",audience="beginner",source_pack=[])
    def test_json_parser_accepts_fenced_json(self):
        fence=chr(96)*3
        raw=fence+"json\n{\"title\":\"نمونه\"}\n"+fence
        self.assertEqual(parse_json(raw)["title"],"نمونه")
    def test_unknown_source_is_rejected(self):
        with self.assertRaises(ValueError): resolve_sources(["missing"], [])
    def test_sources_resolve_from_pack_only(self):
        pack=[{"id":"nist","title":"NIST Framework","url":"https://www.nist.gov/"}]
        self.assertEqual(resolve_sources(["nist"],pack)[0]["title"],"NIST Framework")
    def test_malformed_json_is_rejected(self):
        with self.assertRaises(ValueError): parse_json("no structured content")

if __name__ == "__main__": unittest.main()
