# Aletheia product requirements — healthcare flagship

Status: Macro Milestones 1 and 2 are completed; Macro Milestone 3 is implemented and locally verified, pending external supervisor review. Macro Milestones 4 and 5 remain planned and unimplemented. This review repair authorizes no progression.

## Vision and users

Aletheia is an enterprise-style Explainable AI platform for training, evaluating, tracking, deploying, and auditing high-stakes tabular models. Its primary demonstration is 30-day readmission risk for encounters involving patients with diabetes; South German Credit remains a secondary benchmark. The original `prompt.txt` vision is preserved. Healthcare is a supervised change in demonstration priority, not a claim that credit work failed.

ML engineers need reproducible data/model evidence; analysts and human reviewers need calibrated risk, reasons, comparable cases, and audit context; administrators need version control, access control, and operational evidence. A reviewer journey is: choose an approved model version, inspect a de-identified encounter at discharge, see risk and caveats, inspect local/global explanation and feasible alternatives, record a review decision. An engineer journey is: verify source and split, train and compare on training groups, approve a candidate, evaluate once on locked holdout, register and deploy. An administrator journey is: approve model/reviewer access, inspect immutable audit events and drift alerts.

The application is an educational/research demonstration. It is **not a clinical decision support device**, does not recommend treatment, and cannot justify an individual care decision. No personal health records or user-provided patient data are authorized for the public demonstration.

## Capability boundaries

Implemented now: source-bound healthcare acquisition/extraction, strict schema and target mapping, conservative feature roles, patient-group lock, training-only nested patient-group CV and bounded model comparison, sigmoid calibration, a frozen selected healthcare model and one locked holdout evaluation, immutable local experiment records, global/local sampled Shapley explanations of the complete calibrated probability, bounded recording stability, support-guarded race/gender/source-age subgroup audit with patient-cluster intervals, and counterfactual feasibility assessment. The assessment returns no defensible recourse/no feasible scenario; no counterfactual search, actionable candidate or treatment recommendation is implemented. Tested frozen protocols and aggregate audit records preserve the existing model and methodology. Prior credit data foundation and training-only baseline remain intact.

Unimplemented: similar-case retrieval, managed experiment/registry lifecycle and MLflow, API, UI, databases, authentication/RBAC, application audit persistence, deployment/containers, CI/CD, monitoring, LLM/RAG and later operations. Selected tools remain future decisions. Similar-case retrieval is nearest-neighbour evidence, **not collaborative filtering**. A collaborative filtering recommender, if desired for a CV, belongs to a separate project. RunwayML is rejected: media generation has no product role.

Healthcare inference is defined at discharge after disposition is known; outcome means a readmission within 30 days after discharge. Death/hospice dispositions are removed from the eligible cohort. The model cannot see the disposition code or IDs. Sensitive race, gender, and age are audit-only. This is a conservative first feature policy; later feature inclusion requires timestamp and leakage review.

## Five macro milestones and definitions of done

1. **Foundation and architecture — completed:** authoritative dataset audit, contracts, patient lock, tested offline foundation, public documentation and handoff; externally approved at `9073c453`. No training occurred in this milestone.
2. **Healthcare research — completed:** training-only nested group CV, bounded model-family comparison, sigmoid calibration, one locked holdout evaluation, local experiment identity and model card; committed frozen prerequisite at `49a1a8c`.
3. **Explainable audit — implemented, pending external review:** tested frozen protocols, global/local calibrated-output explanations, recording stability, guarded subgroup audit, counterfactual feasibility assessment and immutable aggregate evidence. Similar-case retrieval belongs to the longer vision and is excluded from the authorized Macro Milestone 3 task.
4. **Application and MLOps — planned, unimplemented:** MLflow registry/tracking, FastAPI, React/TypeScript, PostgreSQL, security/RBAC, application audit trail and Docker. Separate approval required.
5. **Public delivery and operations — planned, unimplemented:** GitHub Actions, managed deployment, monitoring/drift, code dependency graph, threat and recovery checks, final viva/report evidence. Separate approval required.

Milestone acceptance requires tests, documentation and independent supervisor review. Local verification of Macro Milestone 3 does not claim external acceptance. See [EXECUTION_PLAN.md](EXECUTION_PLAN.md), [PROJECT_REPORT.md](PROJECT_REPORT.md), the [model card](model_cards/healthcare_readmission_v1.md) and [SUPERVISOR_HANDOFF.md](SUPERVISOR_HANDOFF.md) for sequencing and existing evidence. Later milestones are designed, not authorized for implementation by this task. No clinical readiness, fairness certification, actionable recourse, production scale or deployment is established.
