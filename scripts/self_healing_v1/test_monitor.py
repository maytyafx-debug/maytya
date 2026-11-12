import unittest
from unittest.mock import patch
from scripts.self_healing_v1.monitor import classify_run, build_report


class ClassifyRunTests(unittest.TestCase):
    def test_startup_failure_is_not_misclassified_as_code_failure(self):
        result = classify_run({"name": "pages-build-deployment", "status": "completed",
                               "conclusion": "startup_failure", "id": 585})
        self.assertEqual(result["category"], "runner_or_actions_startup_failure")
        self.assertIn("do not change application code", result["recommended_action"])

    def test_failed_job_requires_logs_before_repair(self):
        result = classify_run({"name": "Build", "status": "completed", "conclusion": "failure"})
        self.assertEqual(result["category"], "workflow_execution_failure")
        self.assertIn("failed job and step logs", result["recommended_action"])

    def test_running_job_is_not_a_failure(self):
        result = classify_run({"status": "in_progress", "conclusion": None})
        self.assertEqual(result["category"], "in_progress")

    @patch("scripts.self_healing_v1.monitor.check_site", return_value=[{"url":"/", "ok":True}])
    @patch("scripts.self_healing_v1.monitor.fetch_recent_runs", return_value=[{"category":"healthy"}])
    def test_healthy_report_is_read_only(self, _runs, _site):
        report = build_report("owner/repo", "https://example.test")
        self.assertEqual(report["overall_state"], "no_detected_failure")
        self.assertFalse(report["repair_policy"]["automatic_mutations"])
        self.assertFalse(report["repair_policy"]["main_branch_writes"])

    @patch("scripts.self_healing_v1.monitor.check_site", return_value=[{"url":"/", "ok":False}])
    @patch("scripts.self_healing_v1.monitor.fetch_recent_runs", return_value=[])
    def test_site_failure_requires_attention(self, _runs, _site):
        report = build_report("owner/repo", "https://example.test")
        self.assertEqual(report["overall_state"], "attention_required")

    @patch("scripts.self_healing_v1.monitor.check_site", return_value=[{"url":"/", "ok":True}])
    @patch("scripts.self_healing_v1.monitor.fetch_recent_runs", return_value=[{
        "category":"workflow_execution_failure", "created_at":"2020-01-01T00:00:00Z"
    }])
    def test_old_failure_does_not_keep_current_health_red_forever(self, _runs, _site):
        report = build_report("owner/repo", "https://example.test")
        self.assertEqual(report["overall_state"], "no_detected_failure")


if __name__ == "__main__":
    unittest.main()
