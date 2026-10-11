# Aletheia product requirements — healthcare flagship

Status: Macro Milestones 1–3 are completed; CURRENT_TASK.md records Macro
Milestone 3 external approval at `ff9dce291f63a6d4241360997ef0aff2308597f9`.
Macro Milestone 4 Stage 0 prepares a documentation contract for review only.
Application implementation and Macro Milestone 5 remain unimplemented.

## Vision and users

Aletheia is an enterprise-style Explainable AI platform for training, evaluating, tracking, deploying, and auditing high-stakes tabular models. Its primary demonstration is 30-day readmission risk for encounters involving patients with diabetes; South German Credit remains a secondary benchmark. The original `prompt.txt` vision is preserved. Healthcare is a supervised change in demonstration priority, not a claim that credit work failed.

ML engineers need reproducible model evidence; reviewers need calibrated risk,
explanations and audit context; administrators need version and access control.
The longer vision includes comparable cases and defensible scenarios. The first
application deliberately uses the narrower journeys below. Existing research
training/evaluation is completed history, not an online user action.

The application is an educational/research demonstration. It is **not a clinical decision support device**, does not recommend treatment, and cannot justify an individual care decision. No personal health records or user-provided patient data are authorized for the public demonstration.

## Capability boundaries

Implemented now: source-bound healthcare acquisition/extraction, strict schema and target mapping, conservative feature roles, patient-group lock, training-only nested patient-group CV and bounded model comparison, sigmoid calibration, a frozen selected healthcare model and one locked holdout evaluation, immutable local experiment records, global/local sampled Shapley explanations of the complete calibrated probability, bounded recording stability, support-guarded race/gender/source-age subgroup audit with patient-cluster intervals, and counterfactual feasibility assessment. The assessment returns no defensible recourse/no feasible scenario; no counterfactual search, actionable candidate or treatment recommendation is implemented. Tested frozen protocols and aggregate audit records preserve the existing model and methodology. Prior credit data foundation and training-only baseline remain intact.

Unimplemented: similar-case retrieval, managed experiment/registry lifecycle and MLflow, API, UI, databases, authentication/RBAC, application audit persistence, deployment/containers, CI/CD, monitoring, LLM/RAG and later operations. Selected tools remain future decisions. Similar-case retrieval is nearest-neighbour evidence, **not collaborative filtering**. A collaborative filtering recommender, if desired for a CV, belongs to a separate project. RunwayML is rejected: media generation has no product role.

Healthcare inference is defined at discharge after disposition is known; outcome means a readmission within 30 days after discharge. Death/hospice dispositions are removed from the eligible cohort. The model cannot see the disposition code or IDs. Sensitive race, gender, and age are audit-only. This is a conservative first feature policy; later feature inclusion requires timestamp and leakage review.

## Five macro milestones and definitions of done

1. **Foundation and architecture — completed:** authoritative dataset audit, contracts, patient lock, tested offline foundation, public documentation and handoff; externally approved at `9073c453`. No training occurred in this milestone.
2. **Healthcare research — completed:** training-only nested group CV, bounded model-family comparison, sigmoid calibration, one locked holdout evaluation, local experiment identity and model card; committed frozen prerequisite at `49a1a8c`.
3. **Explainable audit — completed, externally approved at `ff9dce291`:** tested frozen protocols, global/local calibrated-output explanations, recording stability, guarded subgroup audit, counterfactual feasibility assessment and immutable aggregate evidence. Similar-case retrieval remains outside the first application.
4. **Application and MLOps — Stage 0 documentation contract only:** MLflow import/lifecycle, FastAPI, React/TypeScript, PostgreSQL, OIDC/RBAC, synthetic application audit and local Docker. Implementation requires a replacement CURRENT_TASK.md.
5. **Public delivery and operations — planned, unimplemented:** GitHub Actions, managed deployment, monitoring/drift, code dependency graph, threat and recovery checks, final viva/report evidence. Separate approval required.

Milestone acceptance requires checks, documentation and independent supervisor
review. The Macro Milestone 3 approval comes from CURRENT_TASK.md; the model
card's earlier pending-review statement is historical and is not rewritten by
this task. See [EXECUTION_PLAN.md](EXECUTION_PLAN.md), [PROJECT_REPORT.md](PROJECT_REPORT.md),
the [model card](model_cards/healthcare_readmission_v1.md) and
[SUPERVISOR_HANDOFF.md](SUPERVISOR_HANDOFF.md). No clinical readiness, fairness
certification, actionable recourse, production scale or deployment is established.

## First application journeys — planned contract v1

| User | Supported journey after implementation approval | Explicit boundary |
|---|---|---|
| Public portfolio visitor | overview → model card → aggregate global/stability/subgroup evidence → fixed synthetic local example and no-recourse explanation | read only; no identity, patient submission, real case retrieval or POST prediction |
| ML engineer | inspect exact approved model and evidence → authenticated fixed-case prediction → inspect own prediction/audit history; operator import existing release into MLflow | import is a private operator workflow; no training, holdout access, model upload or promotion authority from engineer role alone |
| Reviewer | inspect model caveats → request the fixed synthetic encounter prediction → compare saved signed explanation → record coded evidence-review decision → inspect authorized prediction/review revisions and their associated audit events | only events for predictions/reviews the reviewer may access; no release, entitlement, bootstrap or system-wide history; no treatment decision, editable record or unrestricted note |
| Administrator | inspect model versions and release events → privately approve/promote/rollback already verified package → grant/revoke subject roles → inspect release, entitlement and system-wide audit history and service status | first administrator uses the explicit one-time post-migration operator bootstrap; no public write/admin endpoint or custom passwords; reviewer permission is separate |

Research evidence is already implemented. Synthetic demonstration and all
authenticated application workflows above are planned. Future clinical/production
intake would require contemporary validation, lawful data handling, clinical
review, threshold/harm analysis and a separately approved retention/security
contract. Public application will not accept or persist identifiable patient
information; v1 accepts only server-owned `synthetic-discharge-v1` IDs, not even
arbitrary de-identified feature vectors. Only that fixed case has both approved
precomputed local evidence and a specified synthetic inference parity check.

## React/TypeScript route and component map — planned

Use a static React/TypeScript SPA, same-origin API proxy and client-side routes.
Browser guards improve navigation; the API enforces all permissions. Preserve
model/version/hash context across every screen; stale context disables submission
and asks for refresh. No ML transforms, derived fairness metrics or model files
in the browser. Charts consume saved values and keep the full numeric data in
accessible tables. Token state and synthetic response state stay in memory.

| Route | Screen/components and API contract | Access |
|---|---|---|
| `/` | project/evidence overview, capability-status panel, methodology links, limitation banner; current metadata | public |
| `/model-card` | readable model-card document, provenance, threshold/recall caveat; current card/metadata | public |
| `/demo` | fixed synthetic encounter field list and source badge, sign-in prompt or predict button; cases/predictions | public read; E/R/A submit |
| `/evidence/local` | synthetic signed contribution chart, baseline/probability equation, 13-field table, calibration and method caveats; fixed local endpoint | public |
| `/predictions/:id` | persisted synthetic prediction, exact explanation reference, event link, review summary; prediction/reviews endpoints | owner E; R/A all |
| `/evidence/global` | sorted horizontal field chart, repeat-range markers with explicit non-CI caption; global endpoint | public |
| `/evidence/stability` | metrics/table, flag counts, recording-only interpretation, undefined/crossed-empty state; stability endpoint | public |
| `/evidence/subgroups` | support-aware table, metric selector, intervals, missing groups and zero-event caveat; subgroup endpoint | public |
| `/predictions/:id/review` | evidence checklist, coded decision/reason, revision/conflict state and prior decisions; review POST/GET | reviewer |
| `/audit-history` | paginated timeline/table of actual committed events, hash links, scope and read-only detail; audit endpoints; filtered views do not verify the full chain | E own; R authorized prediction/review events only; A all including release/entitlement/system-wide |
| `/admin/models` and `/admin/models/:version` | version/provenance/runtime/approval history, service-status panel; admin model endpoints | administrator |
| `/auth/callback` | provider callback/PKCE exchange and controlled return navigation | OIDC flow; no open redirect |

Visual direction: an editorial research workbench with calm off-white surfaces,
dark ink typography and restrained teal accents. Use system UI sans-serif,
monospace only for hashes, a consistent 4/8-pixel spacing scale, readable line
lengths and a clear page title/caveat/evidence hierarchy. Do not imply a live
clinical dashboard. Desktop has a narrow navigation column and evidence content;
mobile stacks content with an accessible navigation button. Charts use labelled
axes, consistent probability units and color plus text/sign, never color alone.
Target WCAG 2.2 AA contrast, keyboard/focus/skip-link navigation, explicit form
labels, table captions and screen-reader summaries. Keep subgroup uncertainty
and the extremely low 0.5 recall visible, not in hidden tooltips alone.

Each screen specifies skeleton/loading state, no-data/unsupported state,
sanitized error with request ID/retry, offline/service-unready notice and stale
version state. Review submits retain the same idempotency key on retry and clear
only after confirmed success; show 409 conflicts without overwriting history.
Micro-interactions are short focus/hover/transitional feedback (120–180ms), no
fake realtime events, autoplay, decorative 3D, pervasive glass or gradients.
`prefers-reduced-motion` removes optional transitions; responsiveness and chart
accessibility are tested, not claimed implemented. See the
[HTTP/RBAC contract](ARCHITECTURE.md), [runtime](DEPLOYMENT_ARCHITECTURE.md) and
[test gates](EXECUTION_PLAN.md).
