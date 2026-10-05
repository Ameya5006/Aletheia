# Aletheia product requirements — healthcare flagship

Status: approved design for Macro Milestone 1; delivery features below remain planned.

## Vision and users

Aletheia is an enterprise-style Explainable AI platform for training, evaluating, tracking, deploying, and auditing high-stakes tabular models. Its primary demonstration is 30-day readmission risk for encounters involving patients with diabetes; South German Credit remains a secondary benchmark. The original `prompt.txt` vision is preserved. Healthcare is a supervised change in demonstration priority, not a claim that credit work failed.

ML engineers need reproducible data/model evidence; analysts and human reviewers need calibrated risk, reasons, comparable cases, and audit context; administrators need version control, access control, and operational evidence. A reviewer journey is: choose an approved model version, inspect a de-identified encounter at discharge, see risk and caveats, inspect local/global explanation and feasible alternatives, record a review decision. An engineer journey is: verify source and split, train and compare on training groups, approve a candidate, evaluate once on locked holdout, register and deploy. An administrator journey is: approve model/reviewer access, inspect immutable audit events and drift alerts.

The application is an educational/research demonstration. It is **not a clinical decision support device**, does not recommend treatment, and cannot justify an individual care decision. No personal health records or user-provided patient data are authorized for the public demonstration.

## Capability boundaries

Implemented now: source-bound healthcare acquisition/extraction, strict schema and target mapping, conservative feature roles, patient-group lock and offline tests; prior credit data foundation and training-only baseline remain intact. Planned: healthcare baselines and group CV, model comparison and calibration, global/local XAI, constrained counterfactuals, stability, conditional subgroup fairness, similar-case retrieval, experiment/registry lifecycle, API, UI, persistence, deployment, CI/CD, monitoring, security. Similar-case retrieval is nearest-neighbour evidence, **not collaborative filtering**. A collaborative filtering recommender, if desired for a CV, belongs to a separate project. RunwayML is rejected: media generation has no product role.

Healthcare inference is defined at discharge after disposition is known; outcome means a readmission within 30 days after discharge. Death/hospice dispositions are removed from the eligible cohort. The model cannot see the disposition code or IDs. Sensitive race, gender, and age are audit-only. This is a conservative first feature policy; later feature inclusion requires timestamp and leakage review.

## Five macro milestones and definitions of done

1. **Foundation and architecture (current):** authoritative audit, contracts, patient lock, tested offline foundation, public documentation and handoff. No model training.
2. **Healthcare research:** training-only group CV, multiple model families, calibration, one locked holdout evaluation under approved protocol, experiment identity and model cards. Approval required before work.
3. **Explainable audit:** global/local methods, constrained counterfactuals, stability, conditional fairness and similar cases with honest limitations. Approval required.
4. **Application and MLOps:** MLflow registry/tracking, FastAPI, React/TypeScript, PostgreSQL, security/RBAC, immutable audit trail, Docker and cards. Approval required.
5. **Public delivery and operations:** GitHub Actions, managed deployment, monitoring/drift, code dependency graph, threat and recovery checks, final viva/report evidence. Approval required.

Milestone completion requires tests, documentation and independent supervisor review. Later milestones are designed, not authorized for implementation by this task.
