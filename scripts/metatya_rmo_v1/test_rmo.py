import unittest

from scripts.metatya_rmo_v1.knowledge import prepare_knowledge
from scripts.metatya_rmo_v1.orchestrator import (
    ModelCandidate,
    ProviderFailure,
    ResilientModelOrchestrator,
)


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.models = [
            ModelCandidate("model-a", "provider-a"),
            ModelCandidate("model-b", "provider-b"),
            ModelCandidate("model-c", "provider-c"),
        ]

    def test_fallback_after_rate_limit_and_accepts_valid_result(self):
        calls = []

        def provider(model_id, request, knowledge):
            calls.append(model_id)
            if model_id == "model-a":
                raise ProviderFailure("rate_limited", http_status=429)
            return {"answer": "valid"}

        runner = ResilientModelOrchestrator(self.models, provider, lambda value: value.get("answer") == "valid")
        result = runner.run({"question": "test"})
        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.selected_model, "model-b")
        self.assertEqual(calls, ["model-a", "model-b"])

    def test_invalid_output_falls_through(self):
        def provider(model_id, request, knowledge):
            return {"answer": "bad"} if model_id == "model-a" else {"answer": "ok"}

        runner = ResilientModelOrchestrator(self.models, provider, lambda value: value.get("answer") == "ok")
        result = runner.run({})
        self.assertEqual(result.selected_model, "model-b")
        self.assertEqual(result.attempts[0].status, "invalid_output")

    def test_non_retryable_error_stops_without_quota_waste(self):
        calls = []

        def provider(model_id, request, knowledge):
            calls.append(model_id)
            raise ProviderFailure("invalid_credentials", retryable=False, http_status=401)

        runner = ResilientModelOrchestrator(self.models, provider, lambda value: True)
        result = runner.run({})
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.reason, "non_retryable_provider_error")
        self.assertEqual(calls, ["model-a"])

    def test_attempts_are_bounded(self):
        calls = []

        def provider(model_id, request, knowledge):
            calls.append(model_id)
            raise TimeoutError()

        runner = ResilientModelOrchestrator(self.models, provider, lambda value: True, max_attempts=2)
        result = runner.run({})
        self.assertEqual(result.reason, "all_candidates_exhausted")
        self.assertEqual(calls, ["model-a", "model-b"])

    def test_empty_candidate_list_fails_closed(self):
        runner = ResilientModelOrchestrator([], lambda *args: {}, lambda value: True)
        self.assertEqual(runner.run({}).reason, "no_eligible_models")


class KnowledgeBridgeTests(unittest.TestCase):
    def test_only_approved_unique_records_are_exposed(self):
        records = [
            {"id": "a", "title": "Approved", "content": "Useful content", "source": "doc://a", "review_status": "approved"},
            {"id": "b", "title": "Draft", "content": "Not approved", "source": "doc://b", "review_status": "draft"},
            {"id": "a", "title": "Duplicate", "content": "Duplicate", "source": "doc://a2", "review_status": "approved"},
        ]
        result = prepare_knowledge(records)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "a")

    def test_missing_fields_are_ignored(self):
        self.assertEqual(prepare_knowledge([{"id": "incomplete"}]), [])

    def test_max_records_is_enforced(self):
        records = [
            {"id": str(i), "title": "T", "content": "C", "source": "S", "review_status": "approved"}
            for i in range(3)
        ]
        self.assertEqual(len(prepare_knowledge(records, max_records=2)), 2)


if __name__ == "__main__":
    unittest.main()
