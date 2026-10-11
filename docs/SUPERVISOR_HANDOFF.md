# Supervisor Handoff — Macro Milestone 4 Stage 0 contract repair

Documentation-only supervisor repair completed for review; implementation remains
unimplemented and unauthorized. No new documentation file was created in this repair.

## Changed decisions

- Three executable stages after Stage 0: backend foundation/packaging/MLflow/
  migrations/FastAPI/OIDC/RBAC/atomic audit and backend tests; React/TypeScript and
  complete API integration; Compose, E2E/security/accessibility/resource checks
  and release readiness. Internal dependency order and every original gate remain.
  Future milestones use 95% implementation/testing and 5% concise documentation.
- Configurable maximum access-JWT lifetime must be validated against the selected
  issuer. Strict issuer/audience/signature/expiry/skew/algorithm validation remains;
  no public OIDC provider selected.
- Initial administrator: explicit one-time post-migration operator command using
  configured identity; grant and system-attributed append-only event commit
  together. Only this administrator grant permits NULL granted_by; all later
  grants require an active administrator actor. Permanent unique bootstrap marker,
  constraints and serialized conflict checks reject repetition, including after
  revocation. No passwords, public endpoint or automatic startup bootstrap.
- Reviewers see only events associated with authorized predictions/reviews;
  administrators may inspect release/entitlement/system-wide events; engineers
  remain own-only. Endpoint table, RBAC matrix and journey/route agree.
- The Vector databases/tool calling line already occurred once at repair start
  and still occurs once; no duplicate deletion was necessary.

Exact invariants and gates: [architecture](ARCHITECTURE.md),
[execution plan](EXECUTION_PLAN.md), [ADR 0008](decisions/0008-application-mlops-contract.md).

## Verification evidence

Starting and final branch: main. HEAD = origin/main =
ff9dce291f63a6d4241360997ef0aff2308597f9. Stash remains
c6b91a13bf4338e559dfaad49f850dd719f5ca47. Staged file list is empty.
Starting repair inventory already contained the Stage 0 docs and existing
untracked ADR below; docs/CURRENT_TASK.md remains user-owned and unchanged.

Read-only local-link/fence checker: exit 0, no missing local targets or unbalanced
fences; Mermaid blocks counted, not rendered. Contradiction searches: no stale
eight-stage, Stage 4–8, five-minute lifetime or unrestricted reviewer-event rules
in repaired contracts. CURRENT_TASK.md's original eight-item planning instructions
remain unchanged; this supervisor repair consolidates them without losing gates.
git diff --check: exit 0. SHA-256 comparison: all 87 protected files unchanged,
including AGENTS.md, prompt.txt, user-owned CURRENT_TASK.md, source/config/tests/
dependencies, attributes and ten frozen model/audit files; README.md also unchanged
during this repair. No implementation tests or ML experiments executed.

Actually modified in this repair: docs/ARCHITECTURE.md,
docs/DEPLOYMENT_ARCHITECTURE.md, docs/EXECUTION_PLAN.md,
docs/PRODUCT_REQUIREMENTS.md, docs/PROJECT_REPORT.md,
docs/SUPERVISOR_HANDOFF.md, docs/decisions/0008-application-mlops-contract.md.
README.md and the untracked ADR's creation are prior Stage 0 work.

## Unresolved issues and limitations

Contract only: bootstrap/constraint enforcement, provider compatibility, all
backend/UI/security/accessibility/runtime tests and laptop resource budgets remain
unverified until separately authorized implementation. Public provider/tenant,
hosting/region/retention and package/image versions remain later review gates.
Diagrams were not rendered. No services, installs, holdout access, retraining,
audit freeze/run, commit, push or branch/history changes occurred. Stop for review;
only a new approved task authorizes Stage 1.

Exact final Git status (nothing staged):

```text
 M README.md
 M docs/ARCHITECTURE.md
 M docs/CURRENT_TASK.md
 M docs/DEPLOYMENT_ARCHITECTURE.md
 M docs/EXECUTION_PLAN.md
 M docs/PRODUCT_REQUIREMENTS.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
?? docs/decisions/0008-application-mlops-contract.md
```

Recommended user-performed commit message:
`docs: repair Stage 0 application contract`.
