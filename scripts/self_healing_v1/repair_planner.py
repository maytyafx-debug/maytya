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
            if not supplied.get("job_logs_reviewed") or not supplied.get("failed_step"):
                action = "Collect and review the failed job and step logs; no source repair is justified yet."
                scope, confidence, risk = "diagnostics_only", "low", "low"
            else:
                action = "Prepare a minimal branch-only proposal limited to the confirmed failed workflow step."
                scope, confidence, risk = "workflow_configuration", "medium", "medium"
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
                         "failed_step": supplied.get("failed_step")},
            "confidence": confidence, "risk": risk, "recommended_action": action,
            "requires_approval": True, "allowed_scope": scope,
            "rollback_plan": "Keep all work on an isolated branch; revert the proposal commit if approved changes fail verification.",
            "status": "proposal_only"})
    return plans

def planner_metadata() -> dict:
    return {"generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": "proposal_only", "automatic_repairs": False}
