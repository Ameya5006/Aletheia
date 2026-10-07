# Healthcare 30-day readmission model card — experiment v1

## Intended use and status

This is an educational retrospective model for studying discharge-time
readmission prediction and audit discipline. It is not clinically validated,
approved for care decisions, a treatment recommendation, or a patient-facing
service. There is no deployed API or clinical workflow. The fitted artifact is
local and ignored by Git. This card describes the protocol and its measured
result; the machine-readable source of truth is the immutable local run under
`artifacts/healthcare-model-v1/`.

## Data and target

Source: UCI Diabetes 130-US Hospitals for Years 1999–2008, dataset 296, DOI
10.24432/C5230J, CC BY 4.0. The source raw SHA-256 is
`0689e7ec031237dc63031b938805c48377748761a3b26acab621567afa24df97`.
An observation is one inpatient encounter. Death/hospice discharges are
excluded, leaving 99,343 encounters. The positive target is source `<30`
readmission; `>30` and `NO` are negative. The prediction point is discharge.
The training side has 79,808 encounters from 56,178 patients (9,074 positive);
the locked holdout has 19,535 encounters from 13,812 patients (2,240 positive).
Membership checksum:
`6879c9e652887c4a8b59797dd2260ad79795958fb3eebff1b22c3fe33b075316`.

## Inputs and processing

The frozen 13-field policy uses eight quantitative fields: time in hospital,
lab procedure count, procedure count, medication count, prior outpatient,
emergency and inpatient counts, and diagnosis count. It uses five categorical
fields: admission type and source codes, maximum glucose serum result, A1C
result and diabetes medication flag. Quantitative fields receive fold-fitted
median imputation and standardization. Categorical fields receive constant
missing imputation and one-hot encoding; unseen values map to zero indicators.
Identifiers, outcome, disposition, sensitive audit fields and excluded fields
are not model inputs. The 13 fields are a conservative baseline policy, not a
claim that no richer clinically reviewed set could improve performance.

## Study design

Five outer and three inner shuffled, seeded `StratifiedGroupKFold` folds keep
patients disjoint and preprocessing local to training. Inner folds tune bounded
dummy, L2 Logistic Regression, Random Forest and Histogram Gradient Boosting
grids. Outer folds compare raw and sigmoid-calibrated outputs. Sigmoid uses
out-of-fold predictions from patient-disjoint calibration folds. Average
precision is primary; alternatives within 0.005 AP use Brier, ROC-AUC, log
loss and stable name tie-breakers. The model and calibration method are frozen
before one held-out evaluation. Threshold 0.5 is descriptive, not clinically
chosen. The holdout uses 500 seeded patient-cluster bootstrap resamples for
95% intervals. All measurements are encounter-level except that uncertainty
resamples whole patients.

## Measured result

The two complete training-only calculations agreed. Outer-fold mean AP was
0.113698 for the prior dummy, 0.197312 for Logistic Regression, 0.196374 for
Random Forest and 0.199591 for Histogram Gradient Boosting. Histogram plus
group-OOF sigmoid had mean Brier 0.097624 and ROC-AUC 0.635554. It won the
predeclared AP and near-tie Brier rule. Final training-only tuning selected
15 leaves, 30 iterations and minimum leaf size 40. Forest training AP
0.235960 versus validation AP 0.196374 suggests more fitting to training
patients than the chosen histogram (0.215586 versus 0.199591).

The single holdout evaluation used 19,535 encounters from 13,812 patients,
including 2,240 positives. Intervals below use 500 patient-cluster bootstrap
replications, seed 4242; they are not external-validation intervals.

| Metric | Estimate | 95% patient-cluster interval |
|---|---:|---:|
| Average precision | 0.202633 | 0.184091–0.221497 |
| ROC-AUC | 0.639473 | 0.626640–0.653593 |
| Balanced accuracy | 0.502418 | 0.500125–0.505621 |
| Recall | 0.005357 | 0.000452–0.012309 |
| Specificity | 0.999480 | 0.998931–0.999858 |
| Precision | 0.571429 | 0.200000–0.693429 |
| F1 | 0.010615 | 0.000902–0.024124 |
| Log loss | 0.342237 | 0.331423–0.352035 |
| Brier score | 0.098255 | 0.094170–0.101733 |

The descriptive 0.5 confusion matrix is TN 17,286, FP 9, FN 2,228 and TP
12. The model therefore misses almost all positive encounters at this cutoff.
No clinical threshold has been chosen. The holdout calibration intercept is
0.133640 and slope 1.058929; six populated calibration bins are saved in the
immutable local evaluation record. These diagnostics do not prove prospective
or cross-hospital calibration.

Frozen selection SHA-256:
`85db5e79faacc80d9818b235c4e8338be0aeb10fbcf89da2f3bc56e87172e9a7`.
Fitted local artifact SHA-256:
`8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a`.
An exclusive holdout claim and evaluation record exist. The CLI refuses an
existing experiment directory before rerunning any data work.

## Limitations and risks

The data are historical and lack hospital and encounter dates, so this is
neither temporal nor external validation. The source does not establish exact
clinical workflow availability for every field. Unknown categories receive a
safe but lossy zero encoding. The cohort excludes some discharge outcomes and
therefore does not represent all admissions. The split is patient-disjoint but
not hospital-disjoint. Class imbalance and prevalence affect average precision,
precision, calibration and usefulness. The local joblib file is executable
serialization and must be loaded only after checksum, protocol and software
checks from this project; untrusted user files are prohibited. No subgroup
fairness, explanation, causal or prospective assessment is part of this card.

## Reproduction and evidence

Use `python -m aletheia.domains.healthcare model` from the repository root in
the pinned Python environment with the verified source archive in ignored
`data/raw/healthcare`. The command refuses an existing run directory. Do not
delete a completed run and repeat holdout evaluation to improve a result.
Inspect `configs/experiments/healthcare_model_v1.toml`,
`docs/decisions/0006-healthcare-model-selection-protocol.md`, the ignored
`nested_cv.json`, `selection.json`, `artifact.json`, `holdout.claim` and
`holdout.json`, plus `docs/SUPERVISOR_HANDOFF.md` for exact result summaries.
