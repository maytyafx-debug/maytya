import unittest
from unittest.mock import Mock, patch
from scripts.content_engine_v2.source_registry import verify_source

class SourceRegistryTests(unittest.TestCase):
    def test_rejects_non_allowlisted_domain_before_request(self):
        session=Mock()
        result=verify_source({"url":"https://example.com/a","title":"x"},allowlist={"nist.gov"},session=session)
        self.assertFalse(result["ok"]); session.get.assert_not_called()
    def test_rejects_http_and_localhost(self):
        for url in ("http://nist.gov/a","https://127.0.0.1/a","https://user@nist.gov/a"):
            self.assertFalse(verify_source({"url":url},allowlist={"nist.gov"})["ok"])
    def test_redirect_is_followed_only_inside_allowlist(self):
        redirect=Mock()
        redirect.status_code=301
        redirect.headers={"Location":"https://www.nist.gov/final"}
        redirect.close=Mock()
        final=Mock()
        final.status_code=200
        final.headers={"Content-Type":"text/html"}
        final.iter_content.return_value=[b"<title>Final</title>"]
        final.close=Mock()
        session=Mock(); session.get.side_effect=[redirect,final]
        with patch("scripts.content_engine_v2.source_registry.socket.getaddrinfo", return_value=[(None,None,None,None,("8.8.8.8",443))]):
            result=verify_source({"url":"https://www.nist.gov/start"},allowlist={"nist.gov"},session=session)
        self.assertTrue(result["ok"]); self.assertEqual(result["redirects"],1)
    def test_redirect_outside_allowlist_is_rejected(self):
        redirect=Mock()
        redirect.status_code=302
        redirect.headers={"Location":"https://example.com/out"}
        redirect.close=Mock()
        session=Mock(); session.get.return_value=redirect
        with patch("scripts.content_engine_v2.source_registry.socket.getaddrinfo", return_value=[(None,None,None,None,("8.8.8.8",443))]):
            result=verify_source({"url":"https://www.nist.gov/start"},allowlist={"nist.gov"},session=session)
        self.assertFalse(result["ok"]); self.assertIn("allowlist",result["reason"])
        session.get.assert_called_once()
    def test_reads_allowed_html_title(self):
        response=Mock()
        response.status_code=200
        response.headers={"Content-Type":"text/html; charset=utf-8"}
        response.iter_content.return_value=[b"<html><title>NIST Framework</title></html>"]
        response.close=Mock()
        session=Mock(); session.get.return_value=response
        with patch("scripts.content_engine_v2.source_registry.socket.getaddrinfo", return_value=[(None,None,None,None,("8.8.8.8",443))]):
            result=verify_source({"url":"https://www.nist.gov/example","title":"NIST"},allowlist={"nist.gov"},session=session)
        self.assertTrue(result["ok"]); self.assertEqual(result["title"],"NIST Framework")
        session.get.assert_called_once()

if __name__ == "__main__": unittest.main()
