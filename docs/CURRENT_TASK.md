# MILESTONE

Phase 2 — System Architecture, Technology Selection, and Implementation Roadmap

# GOAL

Design the proposed system architecture for Aletheia, select and justify only the technologies needed for the upcoming research implementation, and establish a detailed evidence-driven milestone roadmap.

This milestone must define how Aletheia will eventually support:

* reproducible dataset acquisition and verification;
* schema and semantic validation;
* feature-role enforcement;
* leakage-safe splitting and preprocessing;
* baseline and comparator training;
* model evaluation;
* experiment traceability;
* global and local explanations;
* constrained counterfactuals;
* explanation-stability analysis;
* conditional fairness analysis;
* later API and reviewer-interface integration.

This is a system-design milestone. Do not implement the architecture.

# WHY THIS MILESTONE EXISTS

Phase 0 established the research scope.

Phase 1 selected and audited South German Credit and established:

* target semantics;
* observation unit;
* feature meanings;
* leakage risks;
* audit-only and excluded-feature candidates;
* split constraints;
* fairness limitations;
* counterfactual limitations;
* reproducibility requirements.

Architecture can now be based on actual dataset evidence instead of assumptions.

The system design must keep research validity independent from frontend, API, database, and deployment concerns.

# CURRENT STATE AND PREREQUISITES

At the start of this task:

* Phase 0 and its repair are externally supervisor-approved.
* Phase 1 is externally supervisor-approved.
* South German Credit is the selected dataset.
* No raw dataset is tracked.
* No project architecture has been approved.
* No dependencies, source code, notebooks, tests, models, experiments, API, database, frontend, or deployment files exist.
* `docs/ARCHITECTURE.md` still contains only an unapproved placeholder.
* `docs/CURRENT_TASK.md` is the sole current authorization.
* Codex must not commit or push.

If repository evidence materially contradicts this state, stop and report it before editing.

# FILES TO READ FIRST

Read completely:

* `AGENTS.md`
* `prompt.txt`
* `docs/CURRENT_TASK.md`
* `docs/DATASET_AUDIT.md`
* `docs/PROJECT_REPORT.md`
* `docs/ARCHITECTURE.md`
* `docs/EXECUTION_PLAN.md`
* `docs/SUPERVISOR_HANDOFF.md`

Also inspect:

* current Git status;
* recent Git history;
* repository tree;
* Phase 1 commit and diff;
* all existing documentation constraints.

Treat repository evidence as authoritative.

# BEFORE CHANGING FILES

Provide a concise working update explaining:

1. the verified repository state;
2. the architectural problems that must now be solved;
3. the proposed decision process;
4. architecture alternatives to evaluate;
5. technologies that require selection now;
6. technologies that should remain deferred;
7. expected files to change;
8. major ML, XAI, reproducibility, coupling, and overengineering risks;
9. acceptance criteria.

Do not begin editing if Phase 1 evidence is missing or contradictory.

# IN SCOPE

## 1. Record the Phase 1 approval

Update the relevant status sections so they truthfully record:

* Phase 1 is externally supervisor-approved;
* South German Credit is approved for the Research MVP;
* approval is limited to dataset suitability for an academic research prototype;
* approval does not establish model performance, fairness, stability, calibration, production suitability, or modern-lending validity.

Update the status line in `docs/DATASET_AUDIT.md` without rewriting its evidence.

## 2. Architecture principles

Evaluate and document the principles that should govern Aletheia:

* research-first design;
* modular monolith;
* separation of ML research logic from HTTP/UI concerns;
* explicit dependency direction;
* small understandable modules;
* testable data and model boundaries;
* reproducible artifacts;
* configuration separate from execution logic;
* no hidden notebook-only core logic;
* no premature database or distributed infrastructure;
* platform components added only after research evidence exists.

A modular monolith is the expected default. Choose something else only if repository evidence provides a compelling reason.

Do not introduce artificial Clean Architecture layers, interfaces, repositories, or dependency-injection frameworks merely for appearance.

## 3. System context and delivery stages

Document the system at three levels:

### Research MVP

The evidence-producing core that:

* verifies and loads the selected dataset;
* applies approved feature policy;
* creates reproducible split membership;
* fits training-only preprocessing;
* trains approved model candidates;
* evaluates them;
* generates audit evidence;
* records experiment metadata and artifacts.

### Semester application

A later thin delivery layer that may:

* expose approved model artifacts through an API;
* provide a reviewer-facing interface;
* display experiment, prediction, explanation, and counterfactual evidence;
* record minimal audit events.

It must reuse the research core and must not duplicate preprocessing or model logic.

### Enterprise extensions

Keep production infrastructure, microservices, Kubernetes, RBAC, workflow engines, monitoring platforms, and cloud architecture deferred.

## 4. Component responsibilities

Define proposed component boundaries for:

* dataset acquisition and integrity verification;
* raw-data loading;
* schema validation;
* target mapping;
* feature-role policy;
* split management;
* preprocessing;
* model definitions;
* training orchestration;
* cross-validation and bounded tuning;
* final held-out evaluation;
* experiment metadata;
* artifact storage;
* global explanations;
* local explanations;
* counterfactual generation and constraint validation;
* explanation-stability analysis;
* conditional fairness evaluation;
* reporting or presentation adapters;
* future API;
* future reviewer interface.

For each component document:

* responsibility;
* inputs;
* outputs;
* dependencies;
* components that call it;
* prohibited responsibilities;
* important failure modes;
* tests that will eventually verify it.

Avoid creating a separate service or abstraction where a small module or function would be sufficient.

## 5. Dependency direction

Define and diagram the allowed dependency direction.

At minimum:

* domain/data contracts must not depend on API or UI code;
* ML research logic must not depend on FastAPI, React, databases, or deployment systems;
* future API and UI layers may call stable application/research interfaces;
* external libraries should be wrapped only where doing so provides real testability or compatibility value;
* experiment-report generation should consume recorded results rather than rerun training implicitly;
* the UI must never implement preprocessing or model logic.

Explain how this prevents coupling and training/inference inconsistency.

## 6. Dataset-specific invariants

The architecture must encode these Phase 1 constraints:

* raw `kredit=0` means bad/non-compliant;
* raw `kredit=1` means good/compliant;
* the future adverse-event target should be derived explicitly;
* the raw target must remain traceable;
* age, personal-status/sex, and foreign-worker status are audit-only candidates;
* telephone is excluded;
* `bishkred` is unresolved and must not silently become a model input;
* categorical integer codes must not automatically be treated as continuous;
* no raw 30% adverse-class frequency may be presented as population prevalence;
* the amount transformation prevents literal currency interpretation;
* no temporal or group split is possible with the current source;
* a fixed stratified split is currently recommended;
* all learned transformations must fit on training data only.

Specify where these invariants will eventually be validated and tested.

## 7. Training data flow

Design and diagram the future training flow:

Official source
→ download and checksum verification
→ raw immutable file
→ schema and semantic validation
→ explicit target mapping
→ feature-role enforcement
→ reproducible split assignment
→ training-only preprocessing
→ cross-validation and bounded model selection
→ final model fit on approved training data
→ one held-out evaluation
→ XAI and audit analysis
→ versioned experiment artifacts
→ human-readable report.

Explain:

* where leakage could occur;
* where each control belongs;
* which steps learn from data;
* which steps may see the held-out test set;
* how split membership remains reproducible;
* how audit-only attributes remain aligned without entering the model.

## 8. Future inference data flow

Design and diagram the future inference flow:

Validated raw request
→ schema validation
→ approved feature policy
→ fitted preprocessing artifact
→ fitted model
→ prediction or score
→ optional explanation
→ optional constrained counterfactual
→ audit record
→ response.

Clarify that:

* inference must use the exact fitted preprocessing artifact;
* it must not refit preprocessing;
* audit-only attributes must not be silently passed to the model;
* explanations must correspond to the exact model and transformed representation;
* application code must not independently reinterpret raw feature codes.

## 9. Experiment and artifact design

Define the minimum local artifact contract for the Research MVP.

Consider:

* run identifier;
* dataset identity and SHA-256;
* target mapping;
* feature-policy version;
* split seed and membership identity;
* preprocessing configuration;
* fitted preprocessing/model artifact;
* algorithm and hyperparameters;
* library versions;
* validation results;
* final-test results;
* explanation configuration;
* counterfactual constraints;
* timestamps;
* limitations.

Choose a lightweight local artifact approach for the Research MVP unless evidence justifies MLflow or a database immediately.

Explain:

* directory or manifest concept;
* immutability expectations;
* how reports reference a particular run;
* how later APIs consume approved artifacts;
* how accidental overwrites or result drift will be prevented.

Do not implement artifact storage.

## 10. XAI architecture

Design how Aletheia will keep explanation methodology consistent across models.

Address:

* native versus post-hoc explanations;
* global versus local explanations;
* original feature names versus transformed columns;
* one-hot-encoded feature grouping;
* training-only background/reference data;
* held-out case selection;
* explanation configuration and reproducibility;
* exact model/preprocessor association;
* limitations under correlated features;
* distinction between association and causality.

Do not select SHAP merely because it is popular. Compare appropriate alternatives and state what should be selected now, deferred, or evaluated experimentally.

## 11. Counterfactual architecture

Design the future counterfactual boundary.

It must separate:

* immutable features;
* audit-only features;
* non-actionable historical features;
* mutable features;
* constrained mutable features;
* dependent feature rules;
* categorical validity;
* permitted directions and ranges;
* model-class change;
* plausibility validation;
* cost/distance calculation;
* failure to find a valid candidate.

Account for:

* transformed credit amount;
* dependence between amount, duration, and instalment-rate band;
* prohibited changes to purpose merely to game a result;
* guarantor practicality;
* difference between immediate and long-term change;
* model recourse versus real-world guarantees.

Compare a small custom constrained approach with a library such as DiCE, but do not finalize a dependency without compatibility and methodological justification.

## 12. Explanation-stability architecture

Design the later stability experiment without implementing it.

Specify the future boundary for:

* held-out case selection;
* valid perturbation generation;
* immutable-feature protection;
* prediction-boundary crossings;
* background/reference data;
* top-k overlap;
* rank correlation;
* normalized attribution change;
* random seeds;
* repeated runs;
* artifact recording;
* limitations.

Do not invent thresholds or claim stability has been measured.

## 13. Conditional fairness architecture

Fairness must be an optional audit path, disabled unless evidence supports it.

Design how the system would:

* keep audit-only attributes outside prediction inputs;
* preserve row alignment;
* compute subgroup counts before metrics;
* enforce minimum-support warnings or refusal;
* report selection and error-rate measurements;
* represent uncertainty;
* avoid binary “fair/unfair” conclusions;
* record limitations and subgroup definitions.

For South German Credit, record that no fairness experiment is currently authorized because the available group structure is weak.

## 14. Technology decisions

Create a technology decision matrix covering:

* core language and supported Python version;
* tabular data handling;
* classical ML;
* configuration;
* schema validation;
* serialization;
* testing;
* static analysis and formatting;
* plotting/report generation;
* XAI candidates;
* counterfactual candidates;
* experiment metadata;
* future API;
* future frontend;
* future persistence;
* containerization.

For each decision document:

* problem;
* realistic alternatives;
* selected, provisional, or deferred status;
* why;
* trade-offs;
* Windows and Python 3.12 compatibility;
* 8 GB laptop implications;
* licence considerations where material;
* when to reconsider.

Prefer the smallest defensible dependency set.

Do not install anything or create dependency files.

Do not finalize FastAPI, React/Next, PostgreSQL, MLflow, Docker, SHAP, or DiCE unless the decision is genuinely required now and supported by evidence. Later delivery technologies may remain provisional.

Avoid XGBoost or deep-learning dependencies unless they answer a distinct research question that scikit-learn alternatives cannot.

## 15. Planned repository structure

Propose, but do not create, an understandable future repository structure.

It should identify likely locations for:

* source package;
* configuration;
* dataset manifest or acquisition logic;
* tests;
* experiment outputs;
* model artifacts;
* reports;
* documentation;
* optional notebooks;
* future API;
* future frontend.

Explain which directories are needed for the next implementation milestone and which remain future-only.

Core logic must not live only in notebooks.

## 16. Testing strategy

Define future tests for:

* dataset checksum;
* exact schema;
* target mapping;
* forbidden feature roles;
* categorical handling;
* split reproducibility;
* absence of train/test overlap;
* preprocessing fit boundaries;
* transformed feature consistency;
* model interface;
* metric correctness;
* artifact/model compatibility;
* explanation/model association;
* counterfactual constraint enforcement;
* fairness support guards;
* API validation later;
* end-to-end research flow later.

Distinguish unit, integration, ML/data, and end-to-end tests.

Do not target meaningless 100% coverage.

## 17. Error handling and observability

Define appropriate future handling for:

* checksum mismatch;
* schema drift;
* undocumented category;
* missing or malformed values;
* forbidden feature entering prediction;
* unresolved feature policy;
* invalid target mapping;
* failed model loading;
* incompatible preprocessing artifact;
* unsupported explanation method;
* no valid counterfactual;
* insufficient fairness support;
* corrupt or incomplete experiment artifacts.

Choose simple structured logging and clear errors. Do not introduce a monitoring platform.

## 18. Security and privacy boundaries

Document only architecture-relevant constraints:

* no credentials in the repository;
* no unnecessary sensitive logging;
* no claim that public historical data makes the system production-safe;
* safe model-artifact loading;
* input validation;
* future API authorization deferred until an application milestone;
* no real-person lending decisions.

Do not design authentication or RBAC now.

## 19. Detailed milestone roadmap

Update `docs/EXECUTION_PLAN.md` with the proposed post-architecture milestone sequence.

The roadmap must:

* remain research-first;
* separate data foundation, baseline modelling, comparator evaluation, XAI, counterfactuals, stability, conditional fairness, research synthesis, and later application work;
* identify dependencies between milestones;
* give each milestone a bounded goal;
* state key in-scope and out-of-scope work;
* define measurable completion evidence;
* require external review before progression;
* avoid authorizing any milestone merely because it appears in the roadmap.

The next implementation milestone should be small and should establish the reproducible data foundation before model training.

Do not create its executable `CURRENT_TASK.md`.

## 20. Architecture decision record

Create one ADR:

`docs/decisions/0001-research-first-modular-monolith.md`

It must record:

* context;
* decision;
* alternatives;
* reasons;
* trade-offs;
* consequences;
* deferred decisions;
* when to reconsider.

Do not create multiple ADRs for minor decisions.

# ARCHITECTURE DOCUMENT REQUIREMENTS

Rewrite `docs/ARCHITECTURE.md` as the proposed Phase 2 architecture.

It must include:

* status and approval boundary;
* architecture principles;
* system context;
* delivery stages;
* component responsibilities;
* dependency direction;
* training flow;
* future inference flow;
* dataset-specific invariants;
* experiment/artifact design;
* XAI design;
* counterfactual design;
* stability design;
* conditional fairness design;
* technology decisions;
* planned repository structure;
* testing strategy;
* error handling;
* security/privacy boundaries;
* deferred decisions;
* architecture risks and limitations.

Use compact Mermaid diagrams where they materially clarify component relationships or data flow. Do not add decorative diagrams.

The document must say “proposed pending external supervisor review,” not “approved.”

# PROJECT_REPORT REQUIREMENTS

Update `docs/PROJECT_REPORT.md` as a concise study and defence guide for Phase 2.

Document:

* why architecture followed dataset audit;
* the selected architectural style;
* research-core versus delivery-layer separation;
* major components and their responsibilities;
* dependency direction;
* training and inference flows;
* dataset-specific invariants;
* experiment artifact strategy;
* important XAI/counterfactual/fairness boundaries;
* selected versus deferred technologies;
* alternatives and trade-offs;
* failure modes;
* planned tests;
* files the user should inspect;
* interview/viva questions and concise answers.

Do not copy the entire architecture document into the report.

Do not describe planned components as implemented.

# EXECUTION PLAN REQUIREMENTS

Update `docs/EXECUTION_PLAN.md` to:

* record Phase 1 as externally supervisor-approved;
* record Phase 2 as completed by Codex and pending external review only if all criteria are met;
* include the bounded post-architecture milestone roadmap;
* keep every implementation milestone blocked;
* require a future replacement `CURRENT_TASK.md` before implementation.

# DATASET AUDIT REQUIREMENT

Update only the status/approval wording in `docs/DATASET_AUDIT.md`.

Do not rewrite or expand the completed Phase 1 evidence unless a genuine factual error is discovered. If an error is discovered, stop and explain it before changing the audit.

# SUPERVISOR HANDOFF REQUIREMENTS

Rewrite `docs/SUPERVISOR_HANDOFF.md` for Phase 2.

Include:

* milestone and status;
* verified starting state;
* architecture summary;
* key component boundaries;
* training and inference flow;
* dataset invariants;
* selected and deferred technologies;
* artifact strategy;
* XAI/counterfactual/stability/fairness boundaries;
* roadmap summary;
* ADR created;
* exact files changed;
* checks actually run and exact results;
* unresolved decisions;
* risks and limitations;
* confirmation that no implementation or dependencies were introduced;
* evidence the supervisor should inspect;
* next action limited to external review.

# OUT OF SCOPE

Do not:

* download or commit dataset files;
* perform further EDA unless verifying a suspected Phase 1 factual error;
* create source-code directories or package files;
* create Python modules;
* create notebooks;
* create tests;
* install dependencies;
* create `pyproject.toml`, requirements files, lock files, or environment files;
* create split files;
* preprocess data;
* train models;
* generate metrics;
* implement explanations or counterfactuals;
* perform fairness or stability experiments;
* create an API, database, frontend, Docker configuration, CI/CD, deployment, or cloud infrastructure;
* create more than one ADR;
* modify `prompt.txt`;
* replace `docs/CURRENT_TASK.md` with a later task;
* commit, push, merge, mutate branches, or rewrite Git history;
* begin the next implementation milestone.

# ANTI-OVERENGINEERING RULES

* Prefer a modular monolith.
* Keep the research core independent from delivery layers.
* Do not create microservices.
* Do not introduce Kubernetes, CQRS, event sourcing, service meshes, workflow engines, or distributed queues.
* Do not create generic repository frameworks.
* Do not add interfaces for components that have only one simple implementation unless a real boundary requires one.
* Do not force every SOLID principle into every module.
* Do not select infrastructure before it solves an approved problem.
* Do not create code during a design milestone.
* Keep the architecture explainable by a CSE student.

# VERIFICATION

At minimum:

1. inspect the complete final diff;
2. run `git diff --check`;
3. run `git status --short`;
4. inspect the final changed-file list;
5. confirm only authorized files changed;
6. confirm `prompt.txt` and `AGENTS.md` are unchanged;
7. confirm no raw data, source code, notebooks, tests, dependency files, models, experiment outputs, API, frontend, database, Docker, CI/CD, or deployment artifacts were introduced;
8. verify every architecture component has a clear responsibility and dependency direction;
9. verify training and inference use the same fitted preprocessing contract;
10. verify target mapping and feature-role constraints appear in the architecture;
11. verify audit-only features cannot silently enter model inputs;
12. verify no population-probability claim is made;
13. verify fairness remains conditional and disabled;
14. verify future application layers depend on the research core rather than duplicating it;
15. verify the roadmap does not authorize implementation;
16. verify `ARCHITECTURE.md`, `EXECUTION_PLAN.md`, `PROJECT_REPORT.md`, `DATASET_AUDIT.md`, the ADR, and the handoff are consistent;
17. verify Phase 2 is described as pending external supervisor review;
18. verify Codex performed no Git commit or push.

Report every check actually run and its exact result.

# ACCEPTANCE CRITERIA / DEFINITION OF DONE

Phase 2 is complete by Codex only if:

* [ ] Phase 1 is recorded as supervisor-approved.
* [ ] `ARCHITECTURE.md` contains a coherent proposed architecture.
* [ ] Research core and delivery layers are separated.
* [ ] Component responsibilities and prohibited responsibilities are clear.
* [ ] Dependency direction is explicit.
* [ ] Training and inference flows are documented.
* [ ] Dataset-specific invariants are enforced by design.
* [ ] Audit-only attributes cannot silently enter prediction features.
* [ ] Target mapping is explicit and testable.
* [ ] Oversampling limitations prevent population-probability claims.
* [ ] Experiment metadata and artifact contracts are defined.
* [ ] XAI architecture respects preprocessing and model identity.
* [ ] Counterfactual constraints are represented.
* [ ] Stability methodology has a future architectural boundary without fabricated results.
* [ ] Fairness remains optional and guarded by evidence.
* [ ] Technology decisions distinguish selected, provisional, and deferred choices.
* [ ] The proposed repository structure is understandable and not created.
* [ ] Testing, errors, security, and configuration boundaries are documented.
* [ ] One justified modular-monolith ADR exists.
* [ ] The execution roadmap has bounded milestones and approval gates.
* [ ] `PROJECT_REPORT.md` contains concise learning and defence material.
* [ ] `SUPERVISOR_HANDOFF.md` accurately reports the design milestone.
* [ ] No implementation, dataset, persistent dependency, or infrastructure artifact was introduced.
* [ ] No Git commit or push was performed by Codex.

If any mandatory criterion fails, report Phase 2 as incomplete.

# EXPECTED GIT STATUS BEFORE USER COMMIT

Expected modified files:

* `docs/CURRENT_TASK.md`
* `docs/DATASET_AUDIT.md`
* `docs/ARCHITECTURE.md`
* `docs/EXECUTION_PLAN.md`
* `docs/PROJECT_REPORT.md`
* `docs/SUPERVISOR_HANDOFF.md`

Expected new file:

* `docs/decisions/0001-research-first-modular-monolith.md`

Explanation:

* `CURRENT_TASK.md` is modified because the user replaced Phase 1 with this approved Phase 2 task.
* `DATASET_AUDIT.md` should receive only the Phase 1 approval-status update.
* `ARCHITECTURE.md` is rewritten as the proposed design.
* No other file should change.

Must remain unchanged:

* `AGENTS.md`
* `prompt.txt`
* `README.md`
* `.gitignore`

No source, test, dataset, dependency, model, experiment, API, frontend, database, Docker, CI/CD, or deployment file should appear.

If Git status includes anything else, stop and explain it before recommending a commit.

# FINAL CODEX RESPONSE

Report:

1. milestone status;
2. architecture summary;
3. why this architecture was chosen;
4. alternatives considered;
5. component boundaries;
6. dependency direction;
7. training flow;
8. inference flow;
9. dataset invariants;
10. artifact strategy;
11. XAI architecture;
12. counterfactual architecture;
13. stability architecture;
14. fairness boundary;
15. selected technologies;
16. provisional or deferred technologies;
17. proposed repository structure;
18. testing strategy;
19. roadmap;
20. ADR created;
21. files created;
22. files modified;
23. files intentionally unchanged;
24. checks actually run;
25. exact results;
26. unresolved decisions;
27. risks and limitations;
28. what the user should understand;
29. confirmation that no implementation began;
30. confirmation that Codex did not commit or push;
31. actual final `git status --short`;
32. recommended commit message.

Recommend:

`docs: design Aletheia system architecture`

Do not claim external supervisor approval.

# STOP RULE

Stop after completing and verifying Phase 2.

Do not begin the reproducible-data-foundation milestone or any other implementation work.

Do not create source code, tests, dependencies, datasets, models, experiments, APIs, databases, frontends, containers, CI/CD, or deployment files.

Do not replace `docs/CURRENT_TASK.md` again.

Do not commit or push.

The user will inspect Git status, commit and push the completed attempt, and return it for independent external supervisor review.
