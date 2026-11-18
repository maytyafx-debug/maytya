"""Deterministic, evidence-only repair plan generation. Plans are proposals only."""
from __future__ import annotations
from datetime import datetime, timezone

def _finding_id(kind: str, key: object) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(key)).strip("-")
    return f"{kind}-{safe or 'unknown'}"[:96]

def build_repair_plans(report: dict, job_evidence: dict | None = None) -> list[dict]:
    """Build bounded plans from monitor findings and optional sanitized job metadata."""
    evidence_map = job_evidence or {}
    plans: list[dict] = []
    for item in report.get("site_checks", []):
        if item.get("ok"):
            continue
        finding, url = item.get("finding", "site_check_failed"), str(item.get("url", "unknown"))
        if finding == "network_error":
            action = "Repeat the bounded health check and inspect network/DNS availability; do not edit source."
            scope, confidence, risk = "diagnostics_only", "low", "low"
        else:
            action = "Inspect HTTP status, response-size limit, and hosting response before proposing a scoped fix."
            scope, confidence, risk = "diagnostics_only", "medium", "low"
        plans.append({"finding_id": _finding_id("site", url),
            "evidence": {"source": "site_check", "finding": finding,
                         "status_code": item.get("status_code"), "url": url},
            "confidence": confidence, "risk": risk, "recommended_action": action,
            "requires_approval": True, "allowed_scope": scope,
            "rollback_plan": "No change has been made; discard this proposal if evidence changes.",
            "status": "proposal_only"})
    for item in report.get("workflow_runs", []):
        category = item.get("category")
        if category in {"healthy", "in_progress", "not_checked"}:
            continue
        run_id = item.get("run_id")
        supplied = evidence_map.get(str(run_id), {}) if run_id is not None else {}
        if category == "runner_or_actions_startup_failure":
            action = "Inspect GitHub Actions service/runner initialization and perform one controlled rerun; do not edit application code."
            scope, confidence, risk = "diagnostics_only", "medium", "low"
        elif category == "workflow_execution_failure":
            if supplied.get("failure_signature") == "provider_http_429":
                action = ("Review provider rate limits and benchmarked fallback-model availability; "
                          "OPENROUTER_MODELS was empty in the observed run. "
                          "Do not infer a source-code defect from HTTP 429.")
                scope, confidence, risk = "diagnostics_only", "medium", "low"
            elif not all((supplied.get("job_logs_reviewed"), supplied.get("failed_step"),
                          supplied.get("root_cause_confirmed"), supplied.get("affected_path"))):
                action = "Review failed job/step evidence and confirm root cause plus affected path; no source repair is justified yet."
                scope, confidence, risk = "diagnostics_only", "low", "low"
            elif str(supplied.get("affected_path", "")).startswith(".github/workflows/"):
                action = "Prepare a minimal branch-only workflow proposal limited to the confirmed affected file."
                scope, confidence, risk = "workflow_configuration", "medium", "medium"
            elif str(supplied.get("affected_path", "")).startswith("scripts/"):
                action = "Prepare a minimal branch-only source proposal limited to the confirmed affected module."
                scope, confidence, risk = "application_source", "medium", "medium"
            else:
                action = "The confirmed affected path is outside allowlisted code scopes; keep this diagnostic-only."
                scope, confidence, risk = "diagnostics_only", "low", "low"
        elif category in {"actions_api_error", "actions_api_unavailable"}:
            action = "Recheck API connectivity and read permissions; do not modify repository source."
            scope, confidence, risk = "diagnostics_only", "low", "low"
        else:
            action = "Gather additional run and job evidence before proposing any repair."
            scope, confidence, risk = "diagnostics_only", "low", "low"
        plans.append({"finding_id": _finding_id("workflow", run_id or item.get("workflow", "unknown")),
            "evidence": {"source": "github_actions", "run_id": run_id,
                         "workflow": item.get("workflow"), "category": category,
                         "html_url": item.get("html_url"),
                         "job_logs_reviewed": bool(supplied.get("job_logs_reviewed")),
                         "failed_step": supplied.get("failed_step"),
                         "root_cause_confirmed": bool(supplied.get("root_cause_confirmed")),
                         "affected_path": supplied.get("affected_path"),
                         "failure_signature": supplied.get("failure_signature")},
            "confidence": confidence, "risk": risk, "recommended_action": action,
            "requires_approval": True, "allowed_scope": scope,
            "rollback_plan": "Keep all work on an isolated branch; revert the proposal commit if approved changes fail verification.",
            "status": "proposal_only"})
    return plans

def planner_metadata() -> dict:
    return {"generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": "proposal_only", "automatic_repairs": False}
