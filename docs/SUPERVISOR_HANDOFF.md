# Aletheia — Supervisor Handoff

## Current Milestone and Status

**Phase 1 — Dataset Selection and Data Audit.** Completed by Codex and pending
external supervisor review. This handoff is navigation evidence, not supervisor
approval. Architecture and every implementation milestone remain blocked.

Phase 0 and its repair are recorded as externally supervisor-approved because
the approved Phase 1 task explicitly establishes that starting state.

## Starting Repository State

- Latest commit at inspection: `9f9aae2 docs: repair Phase 0 planning governance`.
- The only starting working-tree change was the user-provided replacement of
  `docs/CURRENT_TASK.md` with the approved Phase 1 task.
- The tree contained planning/governance Markdown and `prompt.txt`; it contained
  no dataset, code, dependency, notebook, model, experiment, test, application,
  deployment, or approved architecture artifact.

## Dataset Decision

**Selected pending review:** South German Credit, UCI dataset 573, DOI
`10.24432/C5QG88`.

- Source: `https://archive.ics.uci.edu/dataset/573/south+german+credit`
- Official archive: `https://archive.ics.uci.edu/static/public/573/south+german+credit+update.zip`
- Licence: CC BY 4.0. Reuse and redistribution are allowed with attribution, a
  licence link, and an indication of changes. No raw data was added here.
- Retrieval date: 2026-09-09.
- Source file: `SouthGermanCredit.asc`, space-delimited text with a header;
  47,940 bytes; SHA-256
  `5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f`.
- Archive: 13,130 bytes; SHA-256
  `0b40d40eb7321693d559e247a556f88a6cc8df8489c3cb2ae084db7592584551`.

It passed the traceable-source, licence, target, observation-unit,
documentation/leakage-review, sample/minority support, laptop-size, provenance,
and constrained-counterfactual gates. This choice does not imply that any
future model will be accurate, stable, fair, causal, or suitable for lending.

Three alternatives were not selected: Default of Credit Card Clients has a
larger, better-timed target and stronger potential audit groups, but its useful
inputs are largely historical or lender-controlled and its raw codes contain
undocumented categories; the old Statlog German Credit entry has known code-
table errors and a corrected successor; Credit Approval anonymizes feature
meanings and does not define the `+`/`-` target mapping.

## Target, Observation Unit, and Computed Audit Facts

One row represents one granted credit contract/case from a 1973–1975 southern
German bank sample, not a random application or necessarily a unique customer.
`kredit=0` means bad/non-compliant and `kredit=1` means good/compliant according
to the distributed code table and reader. The future adverse event must be
mapped explicitly as raw `0`. The outcome is known after contract performance;
the intended research prediction moment is immediately before granting, after
proposed terms are known.

Actual inspection found:

- 1,000 rows × 21 columns: 20 predictors plus target;
- target `0=300` (30.00%) and `1=700` (70.00%); counts sum to 1,000;
- 0 missing cells in every column;
- 0 exact full-row duplicates and 0 predictor-only duplicates;
- no identifier or row date, so person uniqueness, repeated borrowers, and
  chronological ordering cannot be verified;
- all observed categorical codes are documented; purpose code 7 is documented
  but absent; no constant field; foreign-worker status is near-constant at
  37 yes and 963 no;
- legitimate source-defined subgroup counts include personal-status/sex groups
  of 50, 310, 548, and 92, and foreign-worker groups of 37 and 963. Only four
  bad outcomes occur in the 37-row foreign-worker group.

The correction report's extracted prose appears to reverse target codes in one
sentence. The exact archive's code table, R reader, and 300/700 distribution
agree on `0=bad`, `1=good`; the discrepancy is retained in the audit rather than
hidden.

## Leakage, Feature Roles, and Split Recommendation

No direct target-derived field or exact duplicate was found, but important risks
remain: the sample contains granted credits only; bad credits were oversampled
from an approximately 5% source prevalence to 30%; timestamps and entity IDs
are absent; concurrent-credit/history cutoffs are not explicit; `bishkred`
includes the current credit; amount uses an unknown monotonic transformation;
and coded categories are expert scores rather than continuous quantities.

Age, combined personal-status/sex, and foreign-worker status are proposed
audit-only candidates, not prediction features. Telephone is proposed excluded
as an obsolete socioeconomic proxy. `bishkred` remains unresolved. All other
prediction candidates remain provisional and require later approval; none was
selected by correlation or used for modelling.

Recommend a future fixed-seed **stratified random split**, with one final test
set isolated before learned preprocessing/model selection and cross-validation
inside training data. Dates and entity IDs do not support temporal or group-
aware splitting. This recommendation cannot eliminate undisclosed repeated-
borrower leakage or establish forward-time generalisation. No split was created.

## Fairness and Counterfactual Feasibility

No fairness analysis was performed. Fairness support is weak: the source combines
sex with personal status so sex cannot be recovered cleanly, the foreign-worker
comparison has only 37 rows/four bad outcomes, and age has no source-defined
grouping. Arbitrary regrouping and proxy inference are prohibited. These fields
may support only carefully justified audit work, not a claim of fairness.

No counterfactual was generated. A bounded proof of concept is feasible around
proposed amount, duration, instalment-rate band, and guarantor structure, with
joint constraints. Protected/demographic and historical fields are immutable or
non-actionable; purpose must not be changed to game a decision; the transformed
amount prevents literal currency-distance claims. Any later output would explain
model behaviour, not guaranteed real-world recourse.

## Files Changed

Codex changes:

- modified `AGENTS.md` with the authorized concise project-report clarification;
- created `docs/DATASET_AUDIT.md`;
- modified `docs/PROJECT_REPORT.md`;
- modified `docs/EXECUTION_PLAN.md`;
- rewrote `docs/SUPERVISOR_HANDOFF.md`.

Existing user change: `docs/CURRENT_TASK.md` remains modified because the user
installed this approved task; Codex did not replace or edit it.

Intentionally unchanged: `prompt.txt` and `docs/ARCHITECTURE.md`.

## Verification Performed and Exact Results

Authoritative UCI pages, DOI records, archive documentation, the linked South
German correction report, and CC BY 4.0 terms were inspected. Four official UCI
ZIPs were downloaded with `Invoke-WebRequest` to
`%TEMP%\aletheia-phase1-audit`, outside the repository. Python `zipfile`
extracted the archives; a temporary isolated environment used `xlrd 2.0.2` only
to inspect the legacy XLS candidate. No project dependency file was changed.

Tool versions: Windows PowerShell `5.1.26100.9278`, Git
`2.53.0.windows.1`, Python `3.12.10`, and temporary `xlrd 2.0.2`.

Executed identity/data checks included `Get-Item`, `Get-FileHash -Algorithm
SHA256`, and Python standard-library parsing with `csv`, `Counter`, and tuple
duplicate checks. Recheck result: header has the 21 documented names; rows
`1000`; columns `21`; target `{0: 300, 1: 700}`; target sum `1000`; missing
total `0`; full duplicates `0`; predictor duplicates `0`; file/archive sizes
and hashes match the values above. Per-column ranges/categories and subgroup-by-
target counts are preserved in `docs/DATASET_AUDIT.md`.

Repository checks completed after documentation edits:

- `git diff --check` → exit 0, no whitespace errors; only Git LF/CRLF warnings.
- `git diff -- prompt.txt docs/ARCHITECTURE.md` → no output; both unchanged.
- `rg --files` and extension/status inspection → no raw data, temporary audit
  environment, dependency file, notebook, source, model, experiment, API,
  frontend, database, Docker, MLflow, deployment, or future-task artifact.
- `git status --short` → the six paths listed in the final handoff/status only.
- final changed-file inspection → Phase 1 evidence/status is internally
  consistent; architecture and later implementation remain blocked.

No automated application/ML tests were applicable because neither application
nor ML implementation exists. No ML experiment or model metric was produced.

## Problems, Unresolved Questions, and Limitations

Temporary tooling issues: an initially guessed South German URL returned HTTP
404 before the official `+update` URL was used; Windows `Expand-Archive` could
not handle the BZIP2 ZIP entries, so Python's standard library extracted them.

Unresolved for future approved work: whether `bishkred` is safely available at
the prediction moment; exact cutoffs for concurrent/history fields; categorical
score treatment; dependent counterfactual constraints; fixed split seed/folds;
primary metric, threshold, and error-cost framing; and whether any fairness
analysis can be statistically and semantically justified.

Inherited limitations: small and old data, one region/bank, granted-only
selection bias, altered class prevalence, no dates/IDs, possible undisclosed
repeated customers, transformed amount, and weak protected-group support. The
data cannot validate modern lending deployment or population probabilities.

## Evidence the Supervisor Should Inspect

1. `docs/DATASET_AUDIT.md`: gates, candidate evidence, file identity, target,
   profiles, feature table, leakage, split, fairness/counterfactual feasibility,
   reproducibility, and sources.
2. `docs/PROJECT_REPORT.md`: concise Phase 1 learning/defence record and honest
   boundary between completed audit and planned modelling.
3. `docs/EXECUTION_PLAN.md`: Phase 1 gate/status and blocked later milestones.
4. `AGENTS.md`: only the authorized report-governance clarification.
5. Final Git diff/status, especially unchanged `prompt.txt` and
   `docs/ARCHITECTURE.md` and absence of raw data or implementation artifacts.

## Suggested Next Action

External supervisor review only. If satisfied, the user may commit and push the
working tree. Codex did not commit or push. No architecture, preprocessing,
model, XAI, fairness measurement, application, dependency, deployment, or next
milestone work began.
