# Aletheia — Project Report

## Project Overview

Aletheia is a proposed Explainable AI (XAI) decision-auditing project for
structured classification in high-stakes contexts. Credit/loan risk is the
reference use case: it makes individual decisions and recourse understandable,
but does not make this a banking product. Intended users are an ML engineer or
data scientist comparing experiments and a risk analyst reviewing a prediction;
an administrator role is a later extension.

This is not a normal prediction dashboard. A dashboard can show a class and
probability. Aletheia's purpose is to compare predictive models using
performance *and* auditable evidence: global/local explanations, constrained
counterfactuals, explanation stability, and, only when valid data exists,
measured subgroup differences. It will not certify lending decisions, prove
causality, prove fairness, replace a human reviewer, or claim a new XAI method.

## Problem Statement

Aggregate metrics can conceal opaque decision logic, unstable explanations, and
different error patterns across groups. A high-stakes prediction alone does not
show a reviewer what inputs influenced it, whether a feasible change could
alter it, or whether observed subgroups have materially different outcomes.
Accuracy alone is especially weak when classes or false-positive/false-negative
costs are imbalanced.

Aletheia will investigate performance-versus-auditability trade-offs. An
explanation is evidence about a fitted model output, not a causal or human
reason. A counterfactual changes the model output, not reality. Fairness metrics
measure selected properties, not legal compliance or universal fairness.

## Scope, Users, and Assumptions

**Established scope:** South German Credit is the selected public tabular
classification dataset, pending external review of Phase 1. It supports a small
laptop-feasible classical-model study and evidence-backed model audit. No model,
experiment, metric, application, architecture, or deployment exists yet. Deep
learning is optional, not central.

**Assumptions requiring validation:** the selected data must have a clear
target, source/licence, data dictionary, sufficient observations/minority-class
support, and feature semantics adequate for realistic counterfactual constraints.
Fairness is possible only where legitimate audit attributes and adequate
subgroup support exist; protected attributes must not be inferred from proxies.
The positive class, threshold, and decision/error-cost framing cannot be chosen
before the dataset is understood.

### Permanent Vision and Current Authorization

`prompt.txt` preserves Aletheia's permanent original vision. It describes the
complete platform ambition, not permission to implement every feature now.
`docs/CURRENT_TASK.md` authorizes exactly one bounded task and cannot override
the project's safety, ML-validity, evidence, or governance rules. At this point
the authorized work is Phase 1 dataset selection/audit; architecture and all
later work remain blocked pending external review. This distinction prevents a
broad vision from being mistaken for an approved implementation plan.

## Functional Requirements

The planned research prototype must:

1. preserve an approved dataset's source, licence, version, schema, and data
   dictionary;
2. validate data and create reproducible training-only preprocessing;
3. train a small predeclared model set under common split rules;
4. compare class-aware metrics, confusion matrices, and validation evidence
   without tuning on final test data;
5. produce global and selected-case local explanations, labelling native and
   post-hoc methods;
6. generate valid constrained counterfactual candidates;
7. run a predeclared explanation-stability study for selected held-out cases;
8. perform subgroup analysis only when defensible; and
9. record data version, seed, split, preprocessing, feature schema, algorithm,
   hyperparameters, environment where practical, and metrics.

An API, dashboard, database, and audit log may later present this evidence, but
are not prerequisites for answering the research question.

## Non-Functional Requirements

- **Reproducibility:** fixed seeds where supported, reproducible/recorded split
  membership, and all learned transforms fitted on training partitions only.
- **Validity and traceability:** each result names its data version, model,
  partition, metric definitions, and explanation configuration; leakage control
  takes priority.
- **Interpretability:** reports must not imply causal, stable, or fair behaviour
  that was not measured.
- **Efficiency:** work must run locally on a normal student laptop; no high-end
  GPU, cloud service, or distributed infrastructure is required.
- **Safety and privacy:** public/de-identified data only; no credentials; no
  representation that the prototype is suitable for real lending.
- **Testability:** later transformations, metrics, constraints, and experiment
  metadata should be independently testable.

## Research Questions

**Primary:** For a documented tabular credit-risk classification dataset, how do
selected model families trade predictive performance against interpretability,
local-explanation stability, and—where valid subgroup data exists—measured
group disparities needed for a human-auditable workflow?

**Secondary:**

- Does a complex model make a material, consistent validation/held-out
  improvement over an interpretable baseline?
- For identical held-out cases, how do local explanations differ in important
  features and direction across models?
- Under small valid perturbations, how do predictions and explanations change?
- How far must mutable, bounded features move to alter a model class, and are
  those candidates plausible under documented constraints?
- If a defensible audit attribute exists, what selection-rate, error-rate,
  precision/recall, and calibration differences are measured by subgroup?

These are planning questions, not empirical conclusions.

## Dataset Requirements

Before selection, assess source/licence, observation unit, target meaning,
collection period, feature semantics, missingness, class distribution,
duplicates, leakage-prone/post-outcome columns, and temporal/entity structure.
The data needs adequate minority and, if applicable, subgroup support for a
defensible held-out study; the threshold for adequacy must follow inspection,
not be invented now. Synthetic data could later test software mechanics but
cannot support the study's empirical claims. Reject data with unclear
provenance/target, unusable feature semantics, likely leakage, or inadequate
support.

### Phase 1 Dataset Decision

South German Credit was selected after comparing four official UCI candidates.
It passed the gates for traceable provenance, CC BY 4.0 usage, explicit contract-
compliance target, corrected feature meanings, modest minority-class support,
laptop size, and constrained counterfactual semantics. The official raw file
has 1,000 granted credit contracts, 20 predictors, and target `kredit` (`0=bad`
contract compliance, `1=good`); 300 cases are bad and 700 good. The adverse
event for future evaluation is the raw `0` value and must be mapped explicitly.

Dataset audit came before architecture because the data determines target
semantics, observable feature timing, leakage controls, split feasibility,
audit-only attributes, counterfactual constraints, and the kind of XAI evidence
that can be defended. Detailed sources, hashes, computed profiles, candidate
rejections, and feature roles are in `docs/DATASET_AUDIT.md`.

The alternatives were Default of Credit Card Clients (larger and better for
potential subgroup study, but dominated by historical/lender-controlled inputs
and undocumented raw codes), the older Statlog German Credit entry (known
code-table defects), and Credit Approval (anonymized features and undefined
label meaning). For the selected data, age, combined personal-status/sex, and
foreign-worker status are proposed audit-only—not prediction—attributes;
telephone is proposed excluded, and the current-credit count remains unresolved.

A future stratified random split is recommended because no dates or entity IDs
support temporal or group splitting. It cannot control undisclosed repeated
borrowers or test forward-time generalisation. Only constrained contract terms
make a limited counterfactual proof possible; immutable and historical fields
must not become recourse. Fairness analysis is not yet justified because sex is
not recoverable cleanly and the foreign-worker group has only 37 observations,
including four bad outcomes.

## Planned ML and Evaluation Strategy

**Candidate models:** Regularised Logistic Regression is the required,
interpretable baseline: fast, reproducible, and directly inspectable through
coefficients. A shallow constrained Decision Tree is an optional native
baseline: rule-like but vulnerable to instability/overfitting. Random Forest
and Gradient Boosting are principal nonlinear tabular comparators: they test
whether added flexibility is worth reduced direct interpretability. A dummy
classifier may provide a class-imbalance sanity reference. SVM, k-NN, AdaBoost,
and a small MLP are not commitments; an ANN belongs only in a later
strong-semester comparison if data and runtime justify it.

**Baseline and selection:** Complex models face the logistic baseline with the
same split and preprocessing discipline. The model cannot be chosen by accuracy
alone. After target/error costs are known, predeclare a primary class-aware
metric (possibly F1, recall, or PR-AUC), supported by ROC-AUC, precision,
recall, confusion matrices, calibration where feasible, and inference cost.

**Evaluation:** The default is a reproducible stratified train/test split with
the test set untouched until final comparison. Use stratified cross-validation
inside training data for candidate selection and only a bounded predeclared
search. Fit imputation, encoding, scaling, selection, and resampling within
each training fold. If review finds chronology or repeated entities, use
temporal or group-aware splits instead. Record seed, folds, schema,
preprocessing, algorithms, hyperparameters, library versions, and metric
definitions. This protects against target, temporal, preprocessing, duplicate,
and entity leakage.

## Explainability and Audit Requirements

**Global vs local:** Global explanations ask which inputs generally influence a
model over a stated population; native coefficients/tree structure and
permutation importance or SHAP summary evidence are candidates. They do not
explain one decision, prove causality, or prove fairness. Local explanations ask
which inputs are associated with raising/lowering output for one record relative
to a stated reference. Prefer native evidence where faithful; SHAP is a
candidate common post-hoc method. LIME is unnecessary unless it serves a defined
comparison. Post-hoc evidence depends on background data, correlation,
preprocessing, and settings.

**Counterfactual strategy:** A counterfactual is a valid, minimally changed
input that changes the *fitted model's* class. Future constraint specifications
must label features immutable (such as age/protected attributes), mutable, or
constrained mutable with ranges, categories, direction, and dependency rules.
Cost should prefer sparse, scaled-small changes. Outputs are model-recourse
candidates—not financial advice or an approval guarantee. Custom constrained
search versus a library such as DiCE remains open until licence, constraints,
reproducibility, and testing are evaluated.

**Explanation stability:** For selected held-out cases, create small valid and
plausible perturbations, recompute prediction/explanation, and report both
prediction changes and explanation similarity. Predeclare measures such as
top-k overlap/rank correlation and normalized attribution change. Cases crossing
a decision boundary are separate because identical explanations are not
expected. Perturbation size, eligible features, background data, and samples
await dataset review. This is a strong-semester feature after core MVP evidence.

**Fairness:** Only with valid audit attributes and adequate group support,
report counts, selection/positive-prediction rates, false-positive and
false-negative rates, precision/recall, and calibration where meaningful, with
uncertainty or warnings for small groups. Do not infer sensitive identity, add a
protected feature for convenience, remove one and call the model fair, or issue
a binary fairness claim. Conflicting fairness definitions and data limitations
must be explicit.

## Risks and Controls

ML risks: target/temporal/post-outcome leakage; transforms fitted outside
training data; repeated-entity leakage; class imbalance; public data not
representing real lending; misleading explanations; implausible
counterfactuals; and fragile subgroup results. Controls: semantic/source review,
leakage checks, pipeline isolation, appropriate splitting, class-aware metrics,
documented limitations, feature constraints, and conditional fairness analysis.

Engineering risks: premature dashboards/APIs/databases/MLflow/Docker,
unnecessary microservices/abstractions, experiment-result drift, XAI dependency
compatibility, misleading visuals, and future sensitive-data logging. Controls:
research-first sequencing, minimal dependencies, recorded runs, clear caveats,
and later privacy-conscious audit design.

## Scope Boundaries

**Research MVP:** the minimum evidence-producing ML/XAI prototype: one approved
documented dataset; leakage-safe reproducible preprocessing and splitting; an
interpretable baseline and justified nonlinear comparators; cross-validated
selection within training data; untouched held-out evaluation; global/local
explanation evidence; a constrained counterfactual proof of concept; traceable
experiment metadata; and a concise research comparison or prediction-inspection
presentation. Fairness remains conditional on legitimate audit attributes,
adequate subgroup support, and appropriate methodology.

Explanation stability remains part of Aletheia's complete research question but
is not required to complete the initial Research MVP. It is required before
claiming that the complete research question, including stability, has been
answered. Its perturbation rules, eligible features, sample selection,
background/reference data, similarity metrics, and boundary-crossing treatment
must follow dataset inspection; it is not implemented, measured, or validated.

**Semester application/demo scope:** a later usable application built only after
reliable Research MVP evidence exists. Subject to separate approval and
justification, it may add a minimal API, reviewer-facing interface, experiment
tracking or appropriate persistence, targeted tests, audit records, and local
reproducibility/containerization. FastAPI, MLflow, PostgreSQL, React/Next, and
Docker are unselected technologies. Finishing the Research MVP neither completes
the original platform vision nor automatically completes this application scope;
application features must present verified research evidence rather than conceal
weak methodology.

**Enterprise extensions:** explicitly deferred are unnecessary early
microservices, Kubernetes, RBAC, CI/CD, cloud infrastructure, approval
workflows, production monitoring, scheduled retraining, production registry,
drift/explanation-drift monitoring, real-lender integration, large deep
learning, and local LLMs.

## Decisions to Finalize Before Implementation

Phase 1 selects the dataset and raw adverse label, but does not finalize a
business threshold, primary model metric, future pipeline, or application
architecture. Before modelling, later approved work must resolve the exact
prediction feature set, treatment of categorical expert scores, observation
cutoffs for concurrent-credit fields, counterfactual dependencies, folds/seed,
and final-test protocol. XAI/counterfactual libraries, MLP inclusion,
visualisation, FastAPI, MLflow, PostgreSQL, React/Next, Docker, and deployment
remain unselected. Reproducible research still precedes platform infrastructure.

## System Architecture

Not finalized. No module layout, public API, database schema, technology stack,
deployment design, or infrastructure commitment has been approved.

## Data Flow

No implemented flow exists. The future analytical flow is: documented dataset
→ schema/leakage review → training-only preprocessing → cross-validated
candidate evaluation → one held-out evaluation → defined explanation,
counterfactual, stability, and conditional fairness analysis → traceable report.
The separation prevents inflated results from unavailable prediction-time data.

## Implementation Timeline

### Phase 0 — Project Analysis and Scope Validation

The broad enterprise proposal was narrowed before architecture/tool commitments
because dataset validity and research design must govern later work. Established:
users, requirements, research questions, data/model criteria, evaluation/XAI
boundaries, risks, MVP, and deferred work. Concepts: supervised tabular
classification, held-out evaluation, cross-validation, leakage,
intrinsic/post-hoc interpretability, counterfactuals, stability, and subgroup
measurement. Result: a coherent research scope was documented without
implementation. Phase 0 is externally supervisor-approved.

### Phase 0 Repair — Documentation and Governance Consistency Repair

This repair followed an external `FAIL — FIX BEFORE CONTINUING` finding on the
first Phase 0 attempt. It reconciles scope terminology, research-first order,
stability status, task authority, Git authority, and the measurable Phase 0
record. A Definition of Done and external approval gate matter because written
planning is only trustworthy when it names the evidence needed to advance and
does not silently authorize later work. The repair is externally
supervisor-approved.

### Phase 1 — Dataset Selection and Data Audit

**What was accomplished:** Four official UCI candidates were compared using
explicit gates, their permitted raw files were inspected outside the repository,
and South German Credit was selected pending supervisor review. Its identity,
structure, target, feature roles, leakage risks, split direction, and conditional
fairness/counterfactual feasibility were documented.

**Why this came now:** Dataset evidence is needed before architecture or
modelling so later decisions use the actual target, semantics, chronology, and
constraints rather than guesses.

**Concepts involved:** provenance and licensing, observation unit, selection
bias, outcome timing, audit-only versus prediction features, leakage review,
stratified splitting, subgroup support, and counterfactual feasibility.

**Result:** Phase 1 is completed by Codex and pending external supervisor review;
architecture and implementation remain blocked.

## Technical Decisions

**Research-first, not platform-first:** Data and ML/XAI evidence precede APIs,
dashboards, persistence, tracking, and deployment. Trade-off: a full-stack demo
is postponed; reconsider after reproducible results exist.

**Credit-risk tabular reference:** supports understandable audits and local
classical ML, while conclusions remain dataset-bound and not production lending
validation. Reconsider if no dataset meets the criteria.

**Logistic baseline plus limited nonlinear models:** provides a real
performance/transparency comparison without an algorithm catalogue; extend only
when another family answers a distinct question.

**Conditional fairness:** avoids proxy-based or underpowered claims, but the
first study may have no fairness result.

## ML Experiments

No ML experiments, model metrics, or model results exist. Phase 1 performed a
structural dataset audit only; its class and subgroup counts are data facts, not
model-performance metrics.

## Important Problems Encountered

No implementation problem has occurred. During Phase 1, Windows
`Expand-Archive` could not extract BZIP2 entries, so Python's standard `zipfile`
was used in the temporary audit directory. An initially guessed South German
archive URL returned 404 before the official `+update` URL was used. More
importantly, one sentence in the linked report appears to reverse the target
codes; UCI's distributed code table, R reader, and observed 300/700 counts agree
on `0=bad`, `1=good`. The lesson is to cross-check narrative documentation
against the exact distributed artifact rather than silently choosing a label.

## Concepts Learned Through This Project

**Intrinsic vs post-hoc interpretability:** coefficients/rules expose model
structure directly; feature attribution estimates influence for a fitted model.
Neither proves causality. Planned in the comparison.

**Data leakage:** training gets unavailable future/target information and
evaluation becomes falsely optimistic. Prevent with training-only transforms,
untouched tests, and time/group splits where appropriate.

**Global vs local explanation:** global evidence describes general model
patterns; local evidence concerns one prediction. A global ranking cannot
explain an individual decision.

**Counterfactual:** constrained feature changes that alter a model class; not a
guarantee of a real-world outcome.

**Dataset selection before architecture:** the selected data fixes what one row
and the target mean and exposes timing, feature, fairness, and recourse limits.
Architecture designed earlier could encode the wrong target or unsupported
capabilities. Phase 1 uses this ordering without designing architecture.

**Prediction feature versus audit-only attribute:** a field may be retained to
measure subgroup behaviour without being supplied to the classifier. In this
audit, age, combined personal-status/sex, and foreign-worker status are proposed
audit-only candidates; that does not make their fairness use automatically valid.

## Project Defence and Interview Preparation

**Why is this not a prediction dashboard?** It compares performance with
explanation, constrained recourse, stability, and conditional subgroup evidence;
the interface is secondary.

**Why not highest accuracy?** Accuracy can hide class/error-cost trade-offs;
model choice needs a context-aware primary metric and audit trade-offs.

**How will leakage be prevented?** Review source semantics, split before
learned preprocessing, fit transforms only within training folds, and reserve
test data for final evaluation.

**Can it prove fairness or causality?** No; it reports bounded, dataset-specific
measurements and model-output explanations with limitations.

**Why choose South German Credit over the larger Taiwanese default dataset?**
The Taiwanese data has stronger sample and target chronology, but most useful
financial variables are historical at prediction time and its raw codes contain
undocumented categories. South German Credit has corrected, human-readable
contract features that better support the XAI and constrained-counterfactual
Research MVP, accepting age and representativeness limitations.

**What does one selected row represent?** One granted credit contract from a
1973–1975 southern German bank sample. It is not a rejected application, so the
data has historical screening/selection bias.

**Why recommend stratified random splitting?** The target is 70/30, but the file
has no dates or entity identifiers needed for temporal/group-aware splitting.
Stratification preserves class support; it cannot solve undisclosed repeated-
borrower or forward-time generalisation risks.

## Semester Viva Preparation

**Basic:** Why can accuracy be insufficient? What is leakage?

**Intermediate:** Why Logistic Regression as a baseline? How do global/local
explanations differ? Why constrain counterfactuals?

**Difficult:** Why can explanations vary near a decision boundary? Why can
fairness metrics conflict? When is temporal/group-aware splitting necessary?

## Resume Evidence

Verified evidence: four official dataset candidates compared; one selected raw
file audited at 1,000 rows × 21 columns; zero model comparisons, implemented
XAI techniques, application tests, or deployments.

## Limitations

South German Credit is old (1973–1975), geographically narrow, contains only
granted credits, oversamples bad contracts, has no row dates or identifiers,
and uses an unknown monotonic transformation for amount. Sex cannot be recovered
cleanly from its combined field, and only 37 rows are foreign workers, so robust
fairness analysis is not currently justified. Future results remain dataset- and
method-bound. No model, architecture approval, or production validation exists.

## Future Work

**Useful next step, subject to approval:** external supervisor review of Phase 1
and `docs/DATASET_AUDIT.md`. Architecture remains blocked unless a later current
task explicitly authorizes it.

**Later extensions:** richer fairness/robustness methodology, monitoring,
deployment workflows, multi-user controls, integrations, and cloud operations.
