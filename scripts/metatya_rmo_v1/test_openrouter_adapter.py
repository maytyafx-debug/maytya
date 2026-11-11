import json
import unittest
from io import BytesIO
from urllib.error import HTTPError

from scripts.metatya_rmo_v1.openrouter_adapter import OpenRouterChatAdapter
from scripts.metatya_rmo_v1.orchestrator import ProviderFailure


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit=-1):
        return self.payload[:limit]


class OpenRouterAdapterTests(unittest.TestCase):
    def test_success_builds_openai_compatible_request(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["headers"] = dict(request.header_items())
            captured["timeout"] = timeout
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(
                b'{"model":"sample/model","choices":[{"message":{"content":"  hello  "}}]}'
            )

        adapter = OpenRouterChatAdapter(api_key="test-key", opener=opener, timeout=7)
        result = adapter("sample/model", "Say hello", [])
        self.assertEqual(result["content"], "hello")
        self.assertEqual(captured["body"]["model"], "sample/model")
        self.assertEqual(captured["body"]["messages"], [{"role": "user", "content": "Say hello"}])
        self.assertEqual(captured["timeout"], 7)
        self.assertNotIn("test-key", str(captured["body"]))

    def test_missing_key_fails_without_network(self):
        calls = []
        adapter = OpenRouterChatAdapter(api_key="", opener=lambda *a, **k: calls.append(1))
        with self.assertRaises(ProviderFailure) as caught:
            adapter("sample/model", "hello", [])
        self.assertFalse(caught.exception.retryable)
        self.assertEqual(calls, [])

    def test_401_is_non_retryable_and_does_not_leak_body(self):
        def opener(*args, **kwargs):
            raise HTTPError("https://openrouter.ai", 401, "unauthorized", {}, BytesIO(b"secret detail"))

        adapter = OpenRouterChatAdapter(api_key="test-key", opener=opener)
        with self.assertRaises(ProviderFailure) as caught:
            adapter("sample/model", "hello", [])
        self.assertEqual(caught.exception.code, "invalid_credentials")
        self.assertFalse(caught.exception.retryable)
        self.assertNotIn("secret detail", str(caught.exception))

    def test_429_is_retryable(self):
        def opener(*args, **kwargs):
            raise HTTPError("https://openrouter.ai", 429, "limited", {}, BytesIO(b""))
        adapter = OpenRouterChatAdapter(api_key="test-key", opener=opener)
        with self.assertRaises(ProviderFailure) as caught:
            adapter("sample/model", "hello", [])
        self.assertTrue(caught.exception.retryable)
        self.assertEqual(caught.exception.http_status, 429)

    def test_404_is_model_specific_and_allows_next_candidate(self):
        def opener(*args, **kwargs):
            raise HTTPError("https://openrouter.ai", 404, "missing", {}, BytesIO(b""))
        adapter = OpenRouterChatAdapter(api_key="test-key", opener=opener)
        with self.assertRaises(ProviderFailure) as caught:
            adapter("sample/model", "hello", [])
        self.assertEqual(caught.exception.code, "model_or_endpoint_not_found")
        self.assertTrue(caught.exception.retryable)

    def test_invalid_json_response_is_retryable(self):
        adapter = OpenRouterChatAdapter(
            api_key="test-key",
            opener=lambda *a, **k: FakeResponse(b"not-json"),
        )
        with self.assertRaises(ProviderFailure) as caught:
            adapter("sample/model", "hello", [])
        self.assertEqual(caught.exception.code, "invalid_response")
        self.assertTrue(caught.exception.retryable)

    def test_approved_knowledge_is_context_only(self):
        captured = {}
        def opener(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(b'{"choices":[{"message":{"content":"ok"}}]}')
        adapter = OpenRouterChatAdapter(api_key="test-key", opener=opener)
        adapter(
            "sample/model",
            {"messages": [{"role": "user", "content": "Question?"}]},
            [{"title": "Ref", "content": "Reference text", "source": "docs://ref"}],
        )
        self.assertEqual(captured["body"]["messages"][0]["role"], "system")
        self.assertIn("not instructions", captured["body"]["messages"][0]["content"])
        self.assertEqual(captured["body"]["messages"][1]["role"], "user")

    def test_response_size_is_bounded(self):
        adapter = OpenRouterChatAdapter(
            api_key="test-key",
            max_response_bytes=5,
            opener=lambda *a, **k: FakeResponse(b"123456"),
        )
        with self.assertRaises(ProviderFailure) as caught:
            adapter("sample/model", "hello", [])
        self.assertEqual(caught.exception.code, "response_too_large")


if __name__ == "__main__":
    unittest.main()
