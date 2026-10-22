# ADR 0007 — Frozen healthcare explanation and responsible-audit protocol

Status: implemented and locally verified for Macro Milestone 3. Exclusive
protocol freezing preceded the completed empirical audit; independent technical
review is pending. Model and original experiment bindings remained unchanged.

Canonical protocol SHA-256:
`fae9acd4c95da774faa1e20a84129146faeeeef1ac866d809ac95df77a7aa04f`.
Result SHA-256:
`2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8`.
The report/model card record results and uncertainty; the handoff records checks.

## Context and decision

The preserved Milestone 2 artifact is a discharge-time Histogram Gradient
Boosting pipeline followed by a separately fitted group-OOF sigmoid. Explaining
only tree scores would omit the probability conversion that reviewers see.
`configs/audit/healthcare_audit_v1.toml` therefore specifies a model-agnostic,
paired permutation Monte Carlo interventional Shapley estimator of the complete
calibrated probability callable. This is a small custom sampled estimator, not
the SHAP package or an assertion of exact Shapley values. Numeric fields and
whole original categorical fields are the players; fitted one-hot categories
provide transformed-to-source lineage without splitting clinical fields.

For each case, 32 seeded random orders and their reverses successively replace
reference fields with the case's values. One training reference row is sampled
per pair from a fixed 64-encounter training background. Average signed increments
sum to the case probability minus the average path-reference probability. A
different path seed can change that sampled baseline; every reported baseline
is retained. Three fixed samples of 128 training encounters and different path
seeds yield global mean absolute contributions and repeat ranges. These ranges
mix case-sampling and path-sampling variation and are not confidence intervals.
Training XAI is descriptive of the fitted model, not unseen-patient performance.
Local values are published only for the protocol-fixed synthetic encounter.
Real-case values and per-case probabilities/attributions stay in memory.

Stability uses 16 seeded training cases and five +/-1 recording perturbations
of lab/procedure counts, bounded by training-observed integer ranges. Every
other field remains fixed, including care, demographics and prior utilization.
These small count corrections are a plausible recording-sensitivity probe in
the source domain, not evidence that a clinical intervention is feasible.
Identical paths/reference seed before and after perturbation reduce Monte Carlo
noise. Absolute attribution rank correlation, top-3 overlap and L1 change
normalized by original attribution L1 are reported, with undefined cases,
unchanged-at-bound cases and 0.5 class crossings recorded. Overlap below 2/3 or
normalized change above 0.25 are descriptive flags, not clinical standards.

The separately guarded holdout audit compares original race, gender and ten
source age bands, retaining missing/unknown categories. There are no invented
age bins, intersections or inferred identities. Inclusion requires 200
encounters, 100 patients, 20 positives and 20 negatives. Unsupported groups
have no performance estimates. Each supported group reports prevalence, AP,
ROC-AUC, Brier, recall, specificity, FPR, FNR and positive prediction rate at
the unchanged descriptive threshold 0.5. Two hundred bootstrap draws resample
patients within each subgroup, retaining all their encounters in that subgroup;
95% percentile intervals count valid/undefined replicates. They are marginal
within-group intervals, not paired disparity intervals or multiple-comparison
significance tests. Missingness, group support and historical ascertainment
limit interpretation. No discrimination, legal or clinical certification follows.

All care/history fields are immutable for recourse at discharge; demographics
and identifiers are immutable, and targets/excluded fields are forbidden.
No conditionally mutable field has a reviewed intervention, time horizon or
joint feasibility constraint. Implement the authorized feasibility assessment
and explicit no-scenario result. A distance/cost objective is undefined because
there is no admissible intervention set. Do not invent medication advice or
reduce prior visits to manufacture recourse.

## Evidence gates and privacy

The `audit` research module has separate `freeze`, `run` and read-only `inspect`
commands. Freeze binds configuration, code/tests, dataset/feature/split configs,
split lock and every preserved model-run file, software versions, starting Git
HEAD and timestamp before outcomes. Run validates source bytes and actual split
membership, performs training-only explanations, then exclusively creates an
audit holdout claim before holdout prediction/subgroup metrics. The original
Milestone 2 holdout claim is preserved. The new audit claim survives failure;
there is no automatic retry or alternative production run path. No fitting,
model search, calibration fit or threshold tuning occurs in the audit.

Protocol, claim, aggregate result and manifest are exclusively created under
ignored `artifacts/healthcare-audit-v1`. Persisted-byte hashes bind these records.
The schema allowlists aggregates and the fixed synthetic local example; exact
subgroup counts below 20 are suppressed. No raw record, patient ID, row key,
real local values or unrestricted prediction vector is published. This is
bounded aggregate publication, not differential privacy, physical WORM storage
or a defence against a malicious local administrator deleting files.

## Alternatives, costs and reconsideration

Tree-specific SHAP was rejected as the primary probability explanation because
its tree output would require a separate treatment of this external nonlinear
sigmoid. The [SHAP permutation explainer documentation](https://shap.readthedocs.io/en/latest/generated/shap.PermutationExplainer.html)
supports model-agnostic permutation paths and identity-link additivity. Installing
SHAP would add compatibility and dependency work to a bounded calculation that
can be tested with existing NumPy/pandas/scikit-learn. The custom estimator trades
library optimizations and richer diagnostics for readable, directly tested paths;
it does not claim the package's full implementation or performance.

[Permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)
would be a valid global alternative but measures performance loss and does not
provide signed additive local contributions. LIME needs surrogate-fit fidelity
checks and does not guarantee telescoping additivity. Exact coalition enumeration
has exponential cost. Conditional attribution could avoid unlikely marginal
combinations but requires a justified conditional distribution model. Unbounded
counterfactual search and DiCE were rejected without defensible clinical
mutability. Row bootstrap was rejected because encounters share patients.

No new package, hosted service, dataset or training dependency is installed.
Thread limiting uses the already locked scikit-learn runtime dependency
`threadpoolctl`; no GPU or service is required. Reconsider with externally
validated contemporary data, clinician-reviewed interventions, a larger
pre-registered sampling budget, or independently tested library compatibility.
Any model development requires a new independent test population and approval.

## Verification required before empirical use

`test_audit.py` covers mapping, calibrated-versus-base outputs, exact additive
toy behavior, local/global determinism, forbidden fields, stability metrics and
bounds, subgroup support/alignment/undefined metrics/patient resampling,
immutable recourse and the exclusive claim. `test_audit_integration.py` runs
the real audit composition using synthetic source/model providers, verifies
manifest hashes, privacy refusals, overwrite refusal, and existing-claim refusal
before prediction. Source-loading and trusted model identity are separately
covered by foundation/model tests and verified against the preserved real run.
