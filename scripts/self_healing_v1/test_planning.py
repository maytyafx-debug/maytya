import unittest
from scripts.self_healing_v1.repair_planner import build_repair_plans
from scripts.self_healing_v1.safety_gate import validate_repair_plan
from scripts.self_healing_v1.recovery_verification import verify_recovery

class RepairPlannerTests(unittest.TestCase):
    def test_startup_failure_never_suggests_source_edit(self):
        plan = build_repair_plans({"workflow_runs":[{"run_id":585,"category":"runner_or_actions_startup_failure"}]})[0]
        self.assertEqual(plan["allowed_scope"], "diagnostics_only")
        self.assertIn("do not edit application code", plan["recommended_action"])
    def test_network_failure_is_diagnostics_only(self):
        plan = build_repair_plans({"site_checks":[{"url":"https://example.test/","ok":False,"finding":"network_error"}]})[0]
        self.assertEqual(plan["allowed_scope"], "diagnostics_only")
        self.assertEqual(plan["risk"], "low")
    def test_workflow_failure_requires_job_logs(self):
        plan = build_repair_plans({"workflow_runs":[{"run_id":42,"category":"workflow_execution_failure"}]})[0]
        self.assertEqual(plan["allowed_scope"], "diagnostics_only")
        self.assertIn("Review failed job/step", plan["recommended_action"])
    def test_reviewed_failure_gets_scoped_proposal(self):
        report = {"workflow_runs":[{"run_id":42,"category":"workflow_execution_failure"}]}
        plan = build_repair_plans(report, {"42":{"job_logs_reviewed":True,"failed_step":"Run unit tests"}})[0]
        self.assertEqual(plan["allowed_scope"], "diagnostics_only")
        self.assertTrue(plan["requires_approval"])

    def test_confirmed_workflow_root_cause_is_scoped(self):
        report = {"workflow_runs":[{"run_id":43,"category":"workflow_execution_failure"}]}
        evidence = {"43":{"job_logs_reviewed":True,"failed_step":"Build",
                          "root_cause_confirmed":True,
                          "affected_path":".github/workflows/build.yml"}}
        plan = build_repair_plans(report,evidence)[0]
        self.assertEqual(plan["allowed_scope"], "workflow_configuration")
    def test_provider_429_remains_diagnostics_only(self):
        report = {"workflow_runs":[{"run_id":44,"category":"workflow_execution_failure"}]}
        evidence = {"44":{"job_logs_reviewed":True,"failed_step":"Generate drafts",
                          "root_cause_confirmed":True,"affected_path":"scripts/content_engine_v2/providers.py",
                          "failure_signature":"provider_http_429"}}
        plan = build_repair_plans(report,evidence)[0]
        self.assertEqual(plan["allowed_scope"], "diagnostics_only")
        self.assertIn("rate limits", plan["recommended_action"])

    def test_healthy_findings_produce_no_plans(self):
        self.assertEqual(build_repair_plans({"site_checks":[{"ok":True}],"workflow_runs":[{"category":"healthy"}]}), [])

class SafetyGateTests(unittest.TestCase):
    def setUp(self):
        self.plan = {"allowed_scope":"diagnostics_only","requires_approval":True,"status":"proposal_only"}
    def test_missing_approval_fails_closed(self):
        result = validate_repair_plan(self.plan,target_branch="feat/repair")
        self.assertFalse(result["accepted_for_review"])
        self.assertIn("human_approval_missing",result["reasons"])
        self.assertFalse(result["execution_enabled"])
    def test_main_branch_rejected(self):
        result = validate_repair_plan(self.plan,human_approved=True,target_branch="main")
        self.assertFalse(result["accepted_for_review"])
        self.assertIn("isolated_branch_required",result["reasons"])
    def test_deploy_and_delete_forbidden(self):
        for action in ("deploy","delete"):
            result = validate_repair_plan(self.plan,human_approved=True,target_branch="feat/repair",action=action)
            self.assertFalse(result["accepted_for_review"])
            self.assertIn("action_forbidden",result["reasons"])
    def test_sensitive_paths_rejected(self):
        result = validate_repair_plan(dict(self.plan,target_path=".env.production"),human_approved=True,target_branch="feat/repair")
        self.assertFalse(result["accepted_for_review"])
        self.assertIn("sensitive_path_forbidden",result["reasons"])
    def test_non_isolated_branch_prefix_rejected(self):
        result = validate_repair_plan(self.plan,human_approved=True,target_branch="dev")
        self.assertFalse(result["accepted_for_review"])
        self.assertIn("isolated_branch_required",result["reasons"])
    def test_unrecognized_action_rejected(self):
        result = validate_repair_plan(self.plan,human_approved=True,target_branch="feat/repair",action="execute")
        self.assertFalse(result["accepted_for_review"])
        self.assertIn("action_forbidden",result["reasons"])
    def test_workflow_scope_requires_workflow_path(self):
        plan = dict(self.plan,allowed_scope="workflow_configuration",target_path="scripts/app.py")
        result = validate_repair_plan(plan,human_approved=True,target_branch="feat/repair")
        self.assertFalse(result["accepted_for_review"])
        self.assertIn("workflow_scope_path_mismatch",result["reasons"])
    def test_approved_proposal_still_does_not_execute(self):
        result = validate_repair_plan(self.plan,human_approved=True,target_branch="feat/repair")
        self.assertTrue(result["accepted_for_review"])
        self.assertFalse(result["execution_enabled"])
        self.assertFalse(result["repository_mutation_performed"])

class RecoveryVerificationTests(unittest.TestCase):
    def test_recovery_requires_tests_and_healthy_monitor(self):
        before={"overall_state":"attention_required","site_checks":[{"ok":False}]}
        after={"overall_state":"no_detected_failure","site_checks":[{"ok":True}]}
        result=verify_recovery(before,after,tests_passed=True)
        self.assertTrue(result["verified"])
        self.assertTrue(result["improved"])
    def test_failed_tests_block_verification(self):
        after={"overall_state":"no_detected_failure","site_checks":[{"ok":True}]}
        self.assertFalse(verify_recovery({},after,tests_passed=False)["verified"])
    def test_remaining_failure_blocks_verification(self):
        after={"overall_state":"attention_required","site_checks":[{"ok":False}]}
        self.assertFalse(verify_recovery({},after,tests_passed=True)["verified"])

if __name__ == "__main__":
    unittest.main()
