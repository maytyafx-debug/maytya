"""Read-only before/after verification for an independently run recovery check."""
def verify_recovery(before: dict, after: dict, *, tests_passed: bool) -> dict:
    """Compare supplied snapshots; does not run tests or change any system."""
    before_state, after_state = before.get("overall_state", "unknown"), after.get("overall_state", "unknown")
    before_bad = sum(1 for x in before.get("site_checks", []) if not x.get("ok", False))
    after_bad = sum(1 for x in after.get("site_checks", []) if not x.get("ok", False))
    monitor_ok = after_state == "no_detected_failure" and after_bad == 0
    improved = after_bad < before_bad or (before_state == "attention_required" and after_state == "no_detected_failure")
    verified = bool(tests_passed and monitor_ok)
    return {"verified": verified, "tests_passed": bool(tests_passed),
            "monitor_healthy_after": monitor_ok, "site_failures_before": before_bad,
            "site_failures_after": after_bad, "improved": improved,
            "mode": "read_only_comparison",
            "next_step": "Human review of evidence; no merge or deployment is authorized."
            if verified else "Recovery is not verified; inspect remaining failures and retain rollback readiness."}
