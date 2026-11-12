# METATYA Self-Healing Engine V1

## Purpose
A bounded, evidence-first health monitor and repair-proposal system. V1 diagnoses; it does not autonomously repair.

## Components
1. Health Monitor: checks configured public endpoints and recent GitHub Actions runs.
2. Repair Planner: converts findings into structured proposals with evidence, confidence, risk, scope, approval requirement, and rollback plan.
3. Safe Repair Gate: validates policy. Passing means eligible for human review only; it never enables execution.
4. Recovery Verification: compares independently collected before/after snapshots and an externally supplied test result.
5. Evidence/Audit: workflow summary and JSON artifact retained for 14 days.

## Safety invariants
- Scheduled workflow is read-only; no GitHub writes.
- No automatic source edits, commits, merges, deployments, restarts, settings changes, deletions, or secret operations.
- Any future write proposal must use a dedicated non-main branch and explicit human approval.
- main and master are never accepted as repair targets.
- Startup failures do not justify application-source edits.
- Network/DNS failures trigger diagnostics only.
- Workflow execution failures require failed-job and failed-step log review before a scoped workflow-configuration proposal.
- Secrets and raw log contents are excluded from planner evidence.
- A passing gate is not authorization to execute a change.

## Run locally
    python -m unittest scripts.self_healing_v1.test_monitor -v
    python -m unittest scripts.self_healing_v1.test_planning -v

Live monitor (network required):
    python -m scripts.self_healing_v1.monitor --output out/self-healing-report.json

## Workflow triggers
The workflow supports manual dispatch, a six-hour schedule, and pull-request validation. It uses read-only contents/actions permissions and publishes a diagnostic artifact.

## Incident response
1. Preserve failed run ID, timestamp, workflow name, and failed step.
2. Distinguish runner startup failures from job execution failures.
3. Review exact failed job/step logs; redact credentials and personal data.
4. Generate a proposal; do not infer root cause from a status label alone.
5. Validate the proposal and obtain explicit approval.
6. If a separately authorized branch change is made, run tests and collect a fresh monitor snapshot.
7. Verify recovery and retain rollback readiness until a human reviewer accepts the evidence.

## V1 limitations
- Planner is deterministic and rule-based, not an AI diagnosis claim.
- Job-log review is represented only by sanitized metadata supplied by a human.
- Gate validates a proposal; it is not a GitHub permission boundary.
- Recovery verification trusts supplied snapshots and test boolean.
- No repair execution, merge, or deployment is implemented.
