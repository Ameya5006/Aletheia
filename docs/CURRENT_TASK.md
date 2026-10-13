# CURRENT TASK — MACRO MILESTONE 4, STAGE 2

## Stage

Implement the production-quality Aletheia frontend and integrate it with the completed Stage 1 backend.

This is an implementation milestone. Spend approximately 95% of effort on implementation, integration, testing and verification, and no more than 5% on concise documentation.

Do not begin Stage 3 deployment/CI/CD work.

## Required starting state

Before editing:

1. Read `AGENTS.md` and this file completely.
2. Confirm branch `main`.
3. Confirm `HEAD` equals local `origin/main`.
4. Confirm the latest completed milestone includes:

   `feat: implement Aletheia backend and MLOps foundation`

5. Confirm `git status --short --untracked-files=all` contains only the user-owned modification to:

   `docs/CURRENT_TASK.md`

6. Record the starting commit and stash list.
7. Do not apply, drop, modify or inspect the contents of the existing credit-research stash beyond confirming that it remains present.
8. If the starting state differs materially, stop and report the discrepancy without editing anything.

## Required reading

Read the relevant implementation contracts before coding:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/DEPLOYMENT_ARCHITECTURE.md`
- `docs/EXECUTION_PLAN.md`
- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`
- `docs/decisions/0008-application-mlops-contract.md`
- Stage 1 FastAPI routes, schemas, authentication, registry and persistence code
- Stage 1 application tests
- healthcare model card and responsible-audit documentation

Inspect the actual FastAPI/OpenAPI contract. Do not invent endpoints, fields, roles, metrics or lifecycle states.

## UI reference

Use the supplied “Aletheia Healthcare AI Platform” Figma/exported ZIP only as a visual and interaction reference.

The reference defines the desired overall direction:

- restrained healthcare/governance visual language;
- professional typography;
- clean information hierarchy;
- responsive sidebar and mobile navigation;
- subtle motion;
- accessible charts;
- clear empty, loading, unavailable and restricted states;
- Overview;
- Case Analysis;
- Explanation;
- Reliability;
- Review;
- Audit Trail;
- Model Card.

Do not copy its hardcoded fixture values, fake model versions, fake hashes, fake approval states, fake service states or invented API contracts.

The repository, Stage 1 API and verified research artifacts are the source of truth.

## Product boundary

The frontend is a decision-auditing application for Aletheia’s fixed synthetic healthcare demonstration.

It must not provide:

- arbitrary patient submission;
- real patient uploads;
- editable clinical inputs;
- diagnosis;
- treatment recommendations;
- clinical intervention recommendations;
- unrestricted model training;
- threshold tuning;
- new holdout evaluation;
- new research-audit execution;
- fabricated predictions, explanations, subgroup results or metrics.

The interface must state important limitations naturally without filling every page with repetitive disclaimers.

## Required implementation

### 1. Frontend foundation

Create the architecture-approved React and TypeScript frontend using the repository’s selected tooling.

Requirements:

- strict TypeScript;
- production build;
- environment-based API base URL;
- routing;
- reusable UI components;
- centralized design tokens;
- responsive desktop, tablet and mobile layouts;
- accessible focus states and keyboard navigation;
- reduced-motion support;
- light and dark appearance;
- no giant monolithic component;
- no copied Figma-generated single-file application;
- no unnecessary frontend framework or state-management dependency.

Use libraries only when they provide clear value. Pin dependencies reproducibly and verify licences and Python dependency compatibility are unaffected.

### 2. API client and contracts

Integrate with the real Stage 1 FastAPI application.

Implement:

- typed request and response boundaries;
- authentication token/session handling compatible with the approved OIDC/JWT contract;
- request correlation where supported;
- timeout and cancellation handling;
- normalized API errors;
- 401, 403, 404, 409, 422, 429 and 5xx states where applicable;
- loading, empty, unavailable and revoked-model handling;
- no silent fallback from failed backend requests to fabricated fixture results.

Reuse or generate contracts safely from the real OpenAPI schema where appropriate. Detect contract drift in tests.

A clearly labelled local demo/fixture mode may be provided for frontend development, but it must never be confused with backend data and must be disabled or visibly identified in production configuration.

### 3. Application shell and access control

Implement:

- organization sign-in entry point compatible with the authentication contract;
- authenticated application shell;
- current role display;
- role-aware controls;
- sign-out/session-expired behavior;
- forbidden-access state;
- Viewer;
- Clinical Reviewer;
- Model-Risk Auditor;
- any administrator-only capability only where Stage 1 explicitly supports it.

UI visibility is not authorization. The backend remains authoritative.

### 4. Overview

Display backend-derived:

- model/release state;
- model family/version;
- service readiness;
- fixed demonstration case;
- prediction probability and configured threshold;
- audit integrity summary;
- review readiness;
- clear synthetic/demo provenance.

Do not label a model Approved or Active unless returned by the registry-backed API.

### 5. Case Analysis

Implement the fixed, read-only synthetic case workflow:

- case identifier;
- permitted case context;
- model prediction;
- risk threshold;
- model version;
- prediction timestamp;
- link to explanation evidence.

Do not create editable patient input fields.

### 6. Explanation

Display the actual available explanation evidence:

- local explanation;
- baseline/raw score where supported;
- contribution direction and magnitude;
- transformed-to-source feature grouping where supplied;
- calibrated probability relationship without incorrectly treating calibration as an additive feature;
- global explanation evidence when available;
- explicit unavailable state when evidence is genuinely not published.

Charts must have text alternatives and must not imply causality.

### 7. Reliability

Implement the three approved areas:

- explanation stability;
- subgroup/fairness evidence;
- counterfactual feasibility.

Use the real evidence contract.

Show sample sizes and uncertainty where supplied. Preserve the distinction between observed subgroup differences and fairness certification.

Support the valid `no feasible scenario` counterfactual result without presenting it as an error.

Never generate treatment advice.

### 8. Human review workflow

Implement the Stage 1 review contract:

- evidence checklist;
- permitted decisions;
- required comment validation;
- expected revision;
- idempotency;
- successful submission;
- conflict response;
- unavailable/retry state;
- review history;
- role restrictions;
- resulting audit linkage.

Do not simulate successful persistence when the backend request failed.

### 9. Audit trail

Implement:

- backend audit-event listing;
- filtering supported by the API;
- event-detail view;
- actor role;
- event type;
- resource visibility according to role;
- timestamp;
- integrity status;
- hash/previous-hash visibility where permitted;
- pagination or bounded loading if required by the API;
- honest distinction between backend-verified events and local/demo fixtures.

Chain-break simulation may exist only in an explicitly enabled development mode, never in the normal application.

### 10. Model card and release state

Implement:

- current model metadata;
- model family and version;
- calibration method and published metrics;
- feature and dataset boundaries;
- validation design;
- known limitations;
- lifecycle state;
- release/approval evidence;
- revoked and unavailable states;
- links to relevant audit evidence where supported.

Do not invent missing fields.

### 11. UX quality

The result must feel deliberately designed rather than template-generated.

Require:

- consistent spacing and typography;
- restrained colour palette;
- subtle functional animations;
- no animation-heavy landing experience;
- no excessive glassmorphism;
- readable chart labels;
- responsive navigation;
- proper empty/loading/error states;
- semantic HTML;
- accessible forms;
- useful mobile layout;
- no horizontal overflow at supported sizes.

## Integration and testing

Add meaningful tests covering at minimum:

- production build and TypeScript checking;
- API contract mapping;
- authentication/session states;
- role-based rendering;
- route navigation;
- overview rendering;
- fixed-case rendering;
- prediction and explanation rendering;
- missing evidence states;
- stability/subgroup/counterfactual states;
- review success;
- review conflict;
- review validation;
- unauthorized review;
- backend unavailable behavior;
- audit filtering/detail;
- revoked/unavailable model state;
- accessibility-critical interactions;
- responsive smoke coverage;
- prevention of fixture fallback after API failure.

Use mocks only at the frontend boundary. Include at least one integration path against the real Stage 1 FastAPI application or its generated OpenAPI contract.

Do not alter Stage 1 behavior merely to make frontend tests pass unless a genuine contract defect is demonstrated. If a backend defect is found, document it and implement the smallest verified repair within the established architecture.

## Verification

Run all relevant checks that exist after implementation, including:

- frontend dependency consistency;
- frontend lint;
- formatting check;
- TypeScript check;
- frontend unit/component tests;
- production build;
- frontend integration/contract tests;
- relevant Stage 1 application tests;
- complete offline Python test suite;
- Python dependency check;
- Ruff lint;
- Ruff formatting check;
- `git diff --check`;
- repository status inspection;
- confirmation that generated build output, caches, coverage output, environment files and secrets are ignored;
- confirmation that no raw healthcare or credit data appears in Git status.

If browser automation is added, keep it bounded and laptop-conscious.

## Documentation policy

Implementation is the priority.

Update only:

- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`

Update `README.md` only if required for accurate setup or frontend commands.

Keep updates concise but preserve:

- what was implemented;
- frontend-to-backend flow;
- major design decisions;
- important problems encountered and their fixes;
- tests and exact results;
- remaining limitations;
- interview/viva explanation;
- actual unimplemented work.

Do not expand unrelated planning documents or rewrite historical sections.

Do not modify `docs/CURRENT_TASK.md`.

## Protected boundaries

Do not:

- retrain or reselect the model;
- access or reevaluate held-out data;
- rerun the responsible research audit;
- modify frozen research artifacts;
- restore the existing stash;
- add LLM, LangChain, tool calling, vector storage, Redis, Kafka, Kubernetes or unrelated databases;
- add cloud deployment;
- begin Stage 3;
- commit or push.

## Stop conditions

Stop and report immediately if:

- starting Git state is unauthorized;
- existing backend contracts materially contradict the approved application contract;
- required secrets or external identity-provider access are necessary for local implementation;
- protected research evidence would need modification;
- an unexplained generated or raw-data file enters Git status;
- a destructive migration or irreversible operation would be required.

## Final response

Report:

1. Stage status.
2. Starting commit and repository state.
3. Frontend architecture implemented.
4. Screens and workflows implemented.
5. Real API endpoints integrated.
6. Authentication and RBAC behavior.
7. Prediction/explanation/reliability behavior.
8. Review and audit behavior.
9. Responsive and accessibility work.
10. Dependencies added and why.
11. Tests and commands run.
12. Exact results.
13. Problems encountered and fixes.
14. Files created.
15. Files modified.
16. Files intentionally unchanged.
17. Remaining limitations.
18. Confirmation that model training, holdout access and audit reruns did not occur.
19. Confirmation that Stage 3 did not begin.
20. Confirmation that Codex did not commit or push.
21. Exact final `git status --short --untracked-files=all`.
22. Recommended commit message.

If successful, recommend:

`feat: implement Aletheia frontend application`

Stop after Stage 2 and wait for external supervisor review.