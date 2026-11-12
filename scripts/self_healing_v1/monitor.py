"""Read-only health monitor and evidence-based repair planner for METATYA.

This module never writes to GitHub, changes settings, restarts deployments, or
edits project files. It gathers public site checks and recent Actions run state,
then emits a bounded diagnosis report for human review.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

USER_AGENT = "METATYA-Self-Healing-Engine/1.0"
DEFAULT_SITE = "https://maytyafx-debug.github.io/maytya"
ENDPOINTS = ("/", "/content.json", "/data/latest.json")


def classify_run(run: dict) -> dict:
    """Classify a GitHub Actions run without assuming a code defect."""
    status = str(run.get("status", "unknown"))
    conclusion = run.get("conclusion")
    workflow = str(run.get("name") or run.get("path") or "unknown")
    if status != "completed":
        category, action = "in_progress", "Wait for completion; do not repair yet."
    elif conclusion == "startup_failure":
        category, action = "runner_or_actions_startup_failure", (
            "Inspect GitHub Actions service/runner initialization and rerun once; "
            "do not change application code based on this signal alone."
        )
    elif conclusion in {"failure", "timed_out", "action_required"}:
        category, action = "workflow_execution_failure", (
            "Inspect failed job and step logs, then propose a minimal branch-only fix."
        )
    elif conclusion == "cancelled":
        category, action = "cancelled", "Check concurrency and cancellation context."
    elif conclusion == "success":
        category, action = "healthy", "No repair indicated by this run."
    else:
        category, action = "unknown_conclusion", "Collect more evidence before proposing repair."
    return {"workflow": workflow, "run_id": run.get("id"), "status": status,
            "conclusion": conclusion, "category": category, "recommended_action": action,
            "html_url": run.get("html_url"), "created_at": run.get("created_at")}


def _request(url: str, token: str | None = None, timeout: int = 15) -> tuple[int, bytes]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(1_000_001)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(4096)


def check_site(site_url: str) -> list[dict]:
    results = []
    for path in ENDPOINTS:
        url = site_url.rstrip("/") + path
        try:
            status, body = _request(url)
            ok = 200 <= status < 300 and len(body) <= 1_000_000
            results.append({"url": url, "status_code": status, "ok": ok,
                            "bytes_read": len(body),
                            "finding": "healthy" if ok else "http_or_size_failure"})
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            results.append({"url": url, "ok": False,
                            "finding": "network_error", "error_type": type(exc).__name__})
    return results


def fetch_recent_runs(repo: str, token: str | None) -> list[dict]:
    if not token:
        return [{"category": "not_checked", "recommended_action":
                 "Configure the built-in GITHUB_TOKEN permissions for Actions read access."}]
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=30"
    try:
        status, body = _request(url, token=token)
        if status != 200:
            return [{"category": "actions_api_unavailable", "http_status": status,
                     "recommended_action": "Check token permissions and GitHub Actions API availability."}]
        payload = json.loads(body.decode("utf-8"))
        return [classify_run(item) for item in payload.get("workflow_runs", [])]
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return [{"category": "actions_api_error", "error_type": type(exc).__name__,
                 "recommended_action": "Retry monitoring and inspect API connectivity."}]


def build_report(repo: str, site_url: str, token: str | None = None) -> dict:
    site = check_site(site_url)
    runs = fetch_recent_runs(repo, token)
    failures = [item for item in site if not item.get("ok", False)]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    run_alerts = []
    for item in runs:
        if item.get("category") in {"healthy", "in_progress", "not_checked"}:
            continue
        created_at = item.get("created_at")
        if not created_at:
            run_alerts.append(item)
            continue
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            run_alerts.append(item)
            continue
        if created >= cutoff:
            run_alerts.append(item)
    if failures or run_alerts:
        state = "attention_required"
    else:
        state = "no_detected_failure"
    return {
        "schema_version": "1.0",
        "engine": "METATYA Self-Healing Engine V1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "read_only_diagnosis",
        "repository": repo,
        "site_url": site_url,
        "overall_state": state,
        "site_checks": site,
        "workflow_runs": runs,
        "repair_policy": {
            "automatic_mutations": False,
            "production_deployments": False,
            "main_branch_writes": False,
            "human_approval_required_for_repairs": True,
            "note": "A failed check is evidence for diagnosis, not permission to mutate the repository."
        },
        "recommended_next_step": (
            "Inspect the specific failed endpoint or workflow job logs; prepare a minimal isolated repair proposal."
            if state == "attention_required" else
            "Continue scheduled monitoring; no repair is justified by current evidence."
        )
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", "maytyafx-debug/maytya"))
    parser.add_argument("--site-url", default=os.getenv("SITE_URL", DEFAULT_SITE))
    parser.add_argument("--output", default="out/self-healing-report.json")
    args = parser.parse_args(argv)
    report = build_report(args.repo, args.site_url, os.getenv("GITHUB_TOKEN"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("METATYA Self-Healing Engine V1:", report["overall_state"])
    print("Site checks:", sum(x.get("ok", False) for x in report["site_checks"]), "/", len(report["site_checks"]))
    print("Workflow runs inspected:", len(report["workflow_runs"]))
    print("Report:", output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
