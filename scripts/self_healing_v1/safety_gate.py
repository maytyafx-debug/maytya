"""Fail-closed policy validation for human-reviewed repair proposals."""
ALLOWED_SCOPES = {"diagnostics_only", "workflow_configuration", "application_source"}
FORBIDDEN_PATH_PARTS = {".github/workflows/deploy", "secrets", ".env", "credentials"}
FORBIDDEN_ACTIONS = {"merge", "deploy", "delete", "force_push", "write_main", "rotate_secret"}

def validate_repair_plan(plan: dict, *, human_approved: bool = False,
                         target_branch: str | None = None,
                         action: str = "propose") -> dict:
    """Validate policy only; this function never performs a repository mutation."""
    reasons = []
    if plan.get("allowed_scope") not in ALLOWED_SCOPES:
        reasons.append("scope_not_allowlisted")
    if plan.get("requires_approval") is not True:
        reasons.append("approval_requirement_missing")
    if not human_approved:
        reasons.append("human_approval_missing")
    if target_branch in {None, "", "main", "master"}:
        reasons.append("isolated_branch_required")
    if action in FORBIDDEN_ACTIONS:
        reasons.append("action_forbidden")
    path = str(plan.get("target_path", "")).lower()
    if any(part in path for part in FORBIDDEN_PATH_PARTS):
        reasons.append("sensitive_path_forbidden")
    if plan.get("status") != "proposal_only":
        reasons.append("plan_not_proposal_only")
    return {"accepted_for_review": not reasons, "execution_enabled": False,
            "repository_mutation_performed": False, "target_branch": target_branch,
            "reasons": reasons, "policy_version": "1.0"}
