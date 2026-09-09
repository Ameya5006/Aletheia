# Aletheia — Phase 1 Dataset Selection and Data Audit

## Status and Evidence Labels

**Decision (externally supervisor-approved):** **South German Credit** is
approved as suitable for Aletheia's academic Research MVP. This approval is
limited to dataset suitability and does not validate any model or modern-lending
use.

This document uses three evidence labels:

- **Source-reported:** stated by UCI or the associated correction report.
- **Computed:** obtained from the downloaded official file on 2026-09-09.
- **Interpretation:** a project decision or limitation derived from those facts.

Selection does not assert that a future model will be accurate, explainable,
stable, fair, causal, or suitable for real lending.

## Mandatory Selection Gates

| Gate | South German Credit | Default of Credit Card Clients | Statlog German Credit | Credit Approval |
|---|---|---|---|---|
| Authoritative, traceable source | Pass: UCI DOI | Pass: UCI DOI | Pass: UCI DOI | Pass: UCI DOI |
| Clear lawful usage | Pass: CC BY 4.0 | Pass: CC BY 4.0 | Pass: CC BY 4.0 | Pass: CC BY 4.0 |
| Defined classification target | Pass | Pass | Pass | Fail: `+`/`-` meanings are not defined in official metadata |
| Understandable observation unit | Pass with selection-bias caveat | Pass | Pass with weak background | Fail for risk study: application label meaning/timing is unclear |
| Documentation supports leakage review | Pass: corrected code table and background report | Pass with undocumented raw codes | Fail: UCI/correction report identifies severe coding errors | Fail: feature meanings deliberately removed |
| Adequate observations/minority support | Pass for modest study: 1,000/300 adverse | Pass: 30,000/6,636 defaults | Pass numerically: 1,000/300 bad | Pass numerically: 690/307 `+`, but target meaning fails |
| Student-laptop size | Pass: 47,940-byte data file | Pass: 5.54 MB workbook | Pass: 79,793-byte data file | Pass: 32,218-byte data file |
| No fatal provenance/target ambiguity | Pass | Pass | Fail due corrected successor and known code-table defects | Fail |
| Semantics support constrained counterfactual proof | Pass with constraints | Fail for selection: most useful fields are historical or lender-controlled | Fail because meanings/codings are unreliable | Fail because meanings are anonymized |
| **Overall** | **Pass / selected** | **Not selected** | **Rejected** | **Rejected** |

Fairness support was not a pass/fail gate.

## Candidate Comparison

### 1. South German Credit — Selected

- **Authoritative source:** UCI Machine Learning Repository, dataset 573,
  DOI `10.24432/C5QG88`.
- **Associated documentation:** Ulrike Grömping, *South German Credit Data:
  Correcting a Widely Used Data Set*, Report 04/2019 (29 November 2019).
- **Licence:** UCI states CC BY 4.0: sharing and adaptation are allowed for any
  purpose with attribution. Redistribution is therefore allowed subject to the
  licence conditions; Aletheia does not commit the raw file in this milestone.
- **Access/file:** official ZIP download; `SouthGermanCredit.asc`,
  space-delimited text with header.
- **Source-reported size:** 1,000 credits, 20 predictors plus a binary response;
  1973–1975, southern German regional bank; 700 good and 300 bad credits; bad
  credits heavily oversampled; no missing values.
- **Computed:** 1,000 rows × 21 columns including target; 700 good/300 bad; no
  missing cells; zero exact full-row or predictor-only duplicates.
- **Semantics:** detailed corrected variable names and level meanings. Contract
  duration, proposed amount/terms, purpose, and guarantor status provide a
  constrained counterfactual starting point.
- **Audit attributes:** age, combined personal-status/sex, and foreign-worker
  status exist, but their limitations make fairness support weak rather than a
  selection reason.
- **Key risks:** only previously approved/granted credits are sampled; old and
  geographically narrow; bad outcomes are oversampled; row chronology and
  customer identifiers are absent; amounts underwent an unknown monotonic
  transformation.

### 2. Default of Credit Card Clients — Not Selected

- **Authoritative source:** UCI dataset 350, DOI `10.24432/C55S3H`.
- **Paper:** I.-C. Yeh and C.-H. Lien (2009), *The comparisons of data mining
  techniques for the predictive accuracy of probability of default of credit
  card clients*, DOI `10.1016/j.eswa.2007.12.020`.
- **Licence/access:** CC BY 4.0; official ZIP containing legacy XLS.
- **Source-reported:** 30,000 Taiwanese credit-card clients, 23 predictors,
  six months of payment/bill history (April–September 2005), and default payment
  next month (`1=yes`, `0=no`); no missing values.
- **Computed:** workbook data sheet contains 30,000 rows × 25 columns (ID + 23
  predictors + target); target `0=23,364` (77.88%), `1=6,636` (22.12%); no empty cells; ID values
  1–30,000 are unique; zero exact duplicates including ID and 35 duplicate
  predictor/target vectors after excluding ID.
- **Computed schema concerns:** `EDUCATION` includes undocumented codes 0 (14),
  5 (280), and 6 (51); `MARRIAGE` includes undocumented 0 (54); repayment-status
  fields contain common `-2` and `0` codes not explained in UCI's stated scale.
- **Observation/audit interpretation:** one row is a credit-card client with a
  unique source ID; no repeated ID is present. Sex, education, marriage, and age
  are documented potential audit attributes with ample broad-category support,
  though the undocumented categories prohibit casual regrouping. The 5.54 MB
  file is laptop-suitable. Payment, bill, and prior-payment fields precede the
  next-month target according to UCI, but their exact cutoff would still need to
  be enforced.
- **Why not selected:** target timing, sample size, and fairness attributes are
  stronger than South German Credit, but most behavioural inputs are historical
  at the prediction moment and `LIMIT_BAL` is lender-controlled. This weakens a
  defensible applicant-facing counterfactual proof of concept. Undocumented
  codes also require an additional semantic investigation.

### 3. Statlog (German Credit Data) — Rejected

- **Authoritative source:** UCI dataset 144, DOI `10.24432/C5NC77`.
- **Licence/access:** CC BY 4.0; official ZIP; inspected symbolic
  `german.data` text file.
- **Source-reported:** 1,000 records, 20 predictors, labels `1=good`, `2=bad`, no
  missing values, and an asymmetric cost matrix.
- **Computed:** 1,000 rows × 21 fields; target `1=700`, `2=300`; no missing
  markers; target distribution 70.00% good/30.00% bad; zero exact full-row or
  predictor-only duplicates. No identifier or row date is present, so repeated
  people and chronology cannot be checked directly.
- **Observation/audit interpretation:** the records are credit cases from the
  same historical source later corrected as South German Credit. Age,
  personal-status/sex, and foreign-worker fields exist, but their supplied
  category meanings are among the reasons the correction was required. Feature
  timing and counterfactual roles inherit the same uncertainties as the
  corrected data with less reliable documentation. The text file is
  laptop-suitable.
- **Why rejected:** the official South German entry and correction report state
  that the old entry has severe code-table errors and insufficient background.
  The corrected successor is a strictly more defensible choice for XAI, where
  feature meanings are central.

### 4. Credit Approval — Rejected

- **Authoritative source:** UCI dataset 27, DOI `10.24432/C5FS30`;
  J. R. Quinlan (1987).
- **Licence/access:** CC BY 4.0; official ZIP; inspected `crx.data` CSV-like file
  and `crx.names` documentation.
- **Source-reported:** 690 credit-card applications, 15 anonymized predictors,
  37 cases with missing data, target symbols `+` and `-`.
- **Computed:** 690 rows × 16 fields; target `+=307`, `-=383`; no exact full-row
  duplicates; class shares are 44.49% `+` and 55.51% `-`. No identifier or
  chronology is documented. Missing counts match the source: A1 12, A2 12, A4 6, A5 6, A6
  9, A7 9, A14 13; other fields 0.
- **Observation/audit interpretation:** one row is an application, but the
  collection period and predictor meanings—including any sensitive attributes,
  identifiers, timing, and post-decision fields—are unavailable. The file is
  laptop-suitable, but anonymization prevents legitimate fairness groups or
  realistic counterfactual constraints.
- **Why rejected:** official feature names/values were intentionally made
  meaningless, and the official metadata does not define which target symbol
  means approval. It cannot support defensible leakage, fairness, or
  counterfactual analysis.

## Selected Dataset Identity and Reacquisition

| Item | Verified value |
|---|---|
| Dataset | South German Credit |
| Repository record | https://archive.ics.uci.edu/dataset/573/south+german+credit |
| DOI | https://doi.org/10.24432/C5QG88 |
| Official download | https://archive.ics.uci.edu/static/public/573/south+german+credit+update.zip |
| Retrieval date | 2026-09-09 |
| UCI donation/release date | 2020-06-19; no separate version number stated |
| Archive identity | `south-german-credit.zip`, 13,130 bytes, SHA-256 `0b40d40eb7321693d559e247a556f88a6cc8df8489c3cb2ae084db7592584551` |
| Selected raw file | `SouthGermanCredit.asc`, space-delimited text with header |
| Raw file identity | 47,940 bytes, SHA-256 `5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f` |
| Shape | 1,000 observations × 21 columns: 20 predictors + target |
| Licence | CC BY 4.0; attribute UCI/dataset creator, link the licence, and indicate changes |
| Redistribution | Allowed under CC BY 4.0 conditions; raw data is intentionally not stored here |

To reacquire, download the official ZIP URL, verify the archive hash, extract
`SouthGermanCredit.asc`, and verify the raw-file hash. The ZIP uses BZIP2
compression; Python's `zipfile` extracted it when Windows PowerShell's
`Expand-Archive` could not.

## Target and Observation Unit

**Source-reported:** the data are a stratified sample of 1,000 credit contracts
from 1973–1975 at a large regional bank in southern Germany. All debtors had
passed creditworthiness checks and received credit. A good case complied with
the contract; a bad case did not.

**Operational interpretation:** one row is one granted credit contract/case,
not a random loan application and not necessarily a unique customer. The raw
target `kredit` uses `0=bad/non-compliant` and `1=good/compliant` according to
the distributed code table and R reader. For later classification reporting,
the adverse/positive event should be derived explicitly as `kredit == 0`; the
raw file must not be silently relabelled.

The linked correction report's extracted prose appears to reverse the numeric
codes in one sentence, while UCI's archive `codetable.txt`, its R reader, and
the observed 300/700 counts consistently map `0=bad`, `1=good`. This
documentation discrepancy must remain visible.

The intended research prediction moment is immediately before granting the
credit, after proposed contract terms are known. The repayment target becomes
known only after contract performance. The source does not give per-field
timestamps, so application-time availability is a reasoned interpretation, not
a verified operational fact. This is not approval prediction: rejected
applicants are absent, creating selection bias.

## Structural Audit

- **Physical schema:** header plus 1,000 data lines; all 21 raw fields contain
  integer tokens. Semantic types are three genuinely quantitative predictors
  (`duration`, transformed `amount`, `age`), several ordinal/discretized fields,
  nominal categories stored as integer scores, and a binary target.
- **Missingness:** every column has 0 missing values (0.00%).
- **Duplicates:** 0 exact full-row duplicates; 0 predictor-only duplicates.
- **Identifier uniqueness:** no identifier column exists. Duplicate checks
  cannot establish unique people or accounts.
- **Repeated entities:** unresolved; source provides no customer/account ID.
- **Chronology:** collection period is 1973–1975, but no row-level date exists.
- **Target arithmetic:** 300 bad + 700 good = 1,000; 30.00% bad and 70.00% good.
- **Schema consistency:** every observed categorical code is documented. Purpose
  code 7 (`education`) is documented but unobserved; this is an empty level, not
  an invalid row. No constant fields exist. `foreign_worker=no` has 963/1,000
  rows and is near-constant for subgroup analysis.

### Per-Feature Computed Profile and Proposed Roles

All missing counts below are `0 (0.00%)`.
Column names, meanings, units, and categorical definitions come from the UCI
archive's `codetable.txt` and the linked correction report; observed values and
counts are computed from `SouthGermanCredit.asc`. Timing and proposed roles are
project interpretations unless the row explicitly states a source definition.

| Source / meaning | Semantic type; observed values | Timing | Proposed role | Leakage concern | Counterfactual category and reason |
|---|---|---|---|---|---|
| `laufkont` / checking-account status | Nominal score; 1:274, 2:269, 3:63, 4:394 | Application snapshot (interpreted) | Prediction candidate | No direct target derivation; timing not explicitly timestamped | Constrained mutable; balance/account status may change over time, not instantly |
| `laufzeit` / duration | Quantitative months; 4–72, 33 values | Proposed contract term | Prediction candidate | Must be fixed before outcome | Constrained mutable; term can be proposed within product rules |
| `moral` / credit history | Nominal score 0–4; 40/49/530/88/293 | Prior/concurrent history | Prediction candidate | Concurrent-credit cutoff needs clarification | Non-actionable historical fact |
| `verw` / purpose | Nominal 0–10; counts 234/103/181/280/12/22/50/0/9/97/12 | Application | Prediction candidate | None evident | Non-actionable for recourse; changing stated purpose may be deceptive |
| `hoehe` / amount | Quantitative-looking; 250–18,424, 923 values | Proposed contract | Prediction candidate | Source says unknown monotonic transformation, so magnitude is not literal | Constrained mutable but exact distance/cost unresolved |
| `sparkont` / savings | Nominal score 1–5; 603/103/63/48/183 | Application snapshot | Prediction candidate | None evident | Constrained mutable over time, not immediate |
| `beszeit` / employment duration | Ordinal 1–5; 62/172/339/174/253 | Accumulated before application | Prediction candidate | None evident | Non-actionable historical duration |
| `rate` / instalment-rate band | Ordered 1–4; 136/231/157/476 | Proposed contract | Prediction candidate | Depends on terms/income; joint constraints required | Constrained mutable jointly with amount/duration |
| `famges` / personal status and sex | Nominal 1–4; 50/310/548/92 | Application | Audit-only candidate | Mixed categories cannot recover sex reliably | Immutable/unresolved; never recourse |
| `buerge` / other debtor or guarantor | Nominal 1–3; 907/41/52 | Application | Prediction candidate | None evident | Constrained mutable; adding a party has legal/practical constraints |
| `wohnzeit` / residence duration | Ordered 1–4; 130/308/149/413 | Historical | Prediction candidate | None evident | Non-actionable historical duration |
| `verm` / most valuable property | Ordered 1–4; 282/232/332/154 | Application snapshot | Prediction candidate | Socioeconomic proxy risk | Non-actionable for immediate recourse |
| `alter` / age | Quantitative years; 19–75, 53 values | Application | Audit-only candidate | None evident | Immutable; never recourse |
| `weitkred` / other instalment plans | Nominal 1–3; 139/47/814 | Existing at application | Prediction candidate | Cutoff for concurrent plan must be fixed | Non-actionable historical/current obligation |
| `wohn` / housing | Nominal 1–3; 179/714/107 | Application | Prediction candidate | Socioeconomic proxy risk | Non-actionable for immediate recourse |
| `bishkred` / number of credits at bank | Ordered 1–4; 633/333/28/6 | Includes current credit | Unresolved prediction candidate | Definition includes current contract; availability/coding moment must be fixed | Non-actionable historical count |
| `beruf` / job category | Ordinal 1–4; 22/200/630/148 | Application | Prediction candidate | Coarse source scoring embeds historical judgement | Non-actionable for immediate recourse |
| `pers` / people financially dependent | Binary 1–2; 155/845 | Application | Prediction candidate | None evident | Non-actionable household circumstance |
| `telef` / registered landline | Binary 1–2; 596/404 | Application | Excluded candidate | Obsolete 1970s socioeconomic proxy with little modern meaning | Non-actionable; should not drive recourse |
| `gastarb` / foreign-worker status | Binary 1–2; 37/963 | Application | Audit-only candidate | Sensitive/nationality proxy; highly imbalanced | Immutable; never recourse |
| `kredit` / contract compliance | Binary; 0 bad:300, 1 good:700 | Known after repayment performance | Target | Direct outcome; never a predictor | Non-actionable target |

“Prediction candidate” is provisional. It does not approve a future feature;
Phase 1 records semantics and risk only.

## Leakage, Timing, and Repeated-Entity Review

No field is visibly derived from `kredit`, and the exact-duplicate checks found
none. Nevertheless:

- there are no row timestamps, so a temporal split cannot be constructed even
  though collection spans three years;
- there is no customer/account ID, so repeated borrowers cannot be detected or
  kept in one partition;
- `bishkred` includes the current credit, so the future pipeline must confirm
  that its value is fixed at the chosen prediction moment;
- credit-history and other-instalment-plan fields need a strict observation
  cutoff so future/concurrent information is not accidentally included;
- the sample contains granted credits only, so it cannot directly model the
  full applicant population and may encode the bank's historical screening;
- bad credits were deliberately oversampled from an approximately 5% source
  prevalence to 30%, so raw probabilities and calibration cannot be presented
  as population default probabilities;
- categorical integer values are expert scores, not equal-distance measurements;
  treating all of them as continuous would be a semantic modelling error; and
- the amount uses an unknown monotonic transformation, preventing literal DM
  interpretation or direct real-world counterfactual costs.

None is a proven target leak in the file, but each is a required future control.

## Recommended Future Split Family

Recommend a **stratified random split**, not yet implemented, because the file
has a binary 70/30 target but no row dates or entity identifiers needed for
temporal/group-aware splitting. Use a fixed reproducible seed, isolate one final
test set before any learned preprocessing or model selection, and perform
cross-validation only within training data.

This choice preserves adverse-class support and prevents test-set tuning, but it
cannot prevent same-person leakage if undisclosed repeated borrowers exist and
cannot simulate forward-in-time generalisation. Reconsider the split if an
authoritative dated or identified version is later found.

## Fairness Feasibility (No Fairness Analysis Performed)

Potential audit-only attributes and computed support are:

| Raw audit candidate | Group | Total | Bad (`0`) | Good (`1`) | Feasibility concern |
|---|---:|---:|---:|---:|---|
| `famges` | 1 male divorced/separated | 50 | 20 | 30 | Small |
| `famges` | 2 female non-single **or** male single | 310 | 109 | 201 | Sex is not recoverable |
| `famges` | 3 male married/widowed | 548 | 146 | 402 | Mixes sex and status |
| `famges` | 4 female single | 92 | 25 | 67 | Small and incomplete female taxonomy |
| `gastarb` | 1 foreign worker | 37 | 4 | 33 | Far too few bad cases for stable error-rate analysis |
| `gastarb` | 2 not foreign worker | 963 | 296 | 667 | Severe imbalance against comparison group |

`age` is available (19–75), but no source-defined fairness groups exist;
arbitrary bins were not created. The combined `famges` field cannot support a
clean male/female comparison, and `foreign_worker` support is too weak for
reliable subgroup error metrics. Fairness analysis is therefore **technically
limited and not yet justified**. Later work may investigate carefully defined
age analysis or raw-category descriptive audit, but must not claim the dataset
or model is fair/unfair or representative of modern lending.

## Counterfactual Feasibility (No Counterfactuals Generated)

The dataset passes the minimum semantic gate for a proof of concept because
contract duration, amount, instalment-rate band, and guarantor structure can be
treated as proposed-application variables with joint constraints. Savings or
checking status might support longer-horizon hypothetical recourse.

Constraints must prohibit changes to age, foreign-worker status, personal
status/sex, and the target. Credit history, employment duration, residence
duration, existing-credit count, dependants, property, housing, job, telephone,
and past obligations are historical or impractical as immediate recourse.
Purpose must not be changed merely to game a decision. Amount, duration, and
instalment rate are dependent; independent changes may create impossible loan
terms. The unknown amount transformation prevents claiming literal currency
distance. These rules make a bounded model-behaviour demonstration possible,
not financial advice or guaranteed recourse.

## Why South German Credit Was Selected

It is the best fit among these candidates because XAI requires correct human
meanings. It retains interpretable credit-contract features, supplies a
corrected code table and background, has an explicit outcome, includes enough
adverse cases for modest held-out work, fits easily on a student laptop, and
permits at least a constrained counterfactual proof. The trade-off is accepting
small, old, selected, oversampled data and weak fairness support instead of the
larger Taiwanese dataset's stronger target/fairness sample.

Reconsider selection if the target code cannot be resolved from authoritative
artifacts, a source version with dates/identifiers invalidates duplicate/split
assumptions, counterfactual dependencies cannot be made defensible, or a better
licensed dataset offers equally clear semantics with representative modern
coverage.

## Reproducibility and Commands Executed

Temporary location (outside repository):
`%TEMP%\aletheia-phase1-audit`. No raw file is tracked.

Tool versions: Windows PowerShell 5.1.26100.9278; Python 3.12.10; temporary
isolated `xlrd` 2.0.2 only for the legacy XLS candidate. `xlrd` is not a
selected project dependency.

Downloads used this PowerShell pattern with each official URL:

```powershell
$auditDir = Join-Path ([System.IO.Path]::GetTempPath()) 'aletheia-phase1-audit'
New-Item -ItemType Directory -Force -Path $auditDir
Invoke-WebRequest -Uri '<official UCI ZIP URL>' -OutFile (Join-Path $auditDir '<local-name>.zip')
```

The exact official ZIP URLs were:

```text
https://archive.ics.uci.edu/static/public/573/south+german+credit+update.zip
https://archive.ics.uci.edu/static/public/144/statlog+german+credit+data.zip
https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip
https://archive.ics.uci.edu/static/public/27/credit+approval.zip
```

South German extraction and file identity were checked with:

```powershell
python -c "import zipfile; zipfile.ZipFile(r'$auditDir\south-german-credit.zip').extractall(r'$auditDir\south-german-credit')"
Get-Item (Join-Path $auditDir 'south-german-credit\SouthGermanCredit.asc')
Get-FileHash (Join-Path $auditDir 'south-german-credit\SouthGermanCredit.asc') -Algorithm SHA256
```

The following inline audit was executed for the selected file. It reproduces
shape, target arithmetic, per-column missingness, duplicates, and every observed
range/category count in the feature table without creating a script file:

```powershell
$raw = Join-Path $auditDir 'south-german-credit\SouthGermanCredit.asc'
$profileCode = @'
import collections,csv,sys
with open(sys.argv[1], encoding='ascii') as f:
    source=list(csv.reader(f, delimiter=' ', skipinitialspace=True))
header=source[0]
rows=[tuple(r) for r in source[1:] if r]
missing={'', '?', 'NA', 'N/A'}
print('shape', len(rows), len(header))
print('target', dict(sorted(collections.Counter(r[-1] for r in rows).items())))
print('missing', {header[i]:sum(r[i] in missing for r in rows)
                  for i in range(len(header))})
print('duplicates', len(rows)-len(set(rows)),
      'predictor_duplicates', len(rows)-len(set(r[:-1] for r in rows)))
for i,name in enumerate(header):
    values=[r[i] for r in rows]
    numbers=[int(v) for v in values]
    result=(min(numbers),max(numbers),len(set(numbers))) if len(set(values))>40 \
           else dict(sorted(collections.Counter(values).items()))
    print(name,result)
'@
python -c $profileCode $raw
```

The source-supported audit groups were checked separately rather than inferred
from proxies:

```powershell
$groupCode = @'
import collections,csv,sys
with open(sys.argv[1], encoding='ascii') as f:
    rows=list(csv.DictReader(f, delimiter=' ', skipinitialspace=True))
for field in ('famges', 'gastarb'):
    table=collections.Counter((r[field],r['kredit']) for r in rows)
    for group in sorted({r[field] for r in rows}):
        bad,good=table[group,'0'],table[group,'1']
        print(field,group,'total',bad+good,'bad',bad,'good',good)
'@
python -c $groupCode $raw
```

For the two remaining delimited candidates, this executed command reproduced
shape, target, missingness, and both duplicate checks:

```powershell
$delimitedCode = @'
import collections,csv,sys
path,mode=sys.argv[1],sys.argv[2]
with open(path,encoding='utf-8') as f:
    rows=[tuple(r) for r in csv.reader(f,delimiter=' ' if mode=='space' else ',',
                                      skipinitialspace=True) if r]
missing={'', '?', 'NA', 'N/A'}
print(path,'shape',len(rows),len(rows[0]),
      'target',dict(sorted(collections.Counter(r[-1] for r in rows).items())),
      'missing_by_column',[sum(r[i] in missing for r in rows)
                           for i in range(len(rows[0]))],
      'duplicates',len(rows)-len(set(rows)),
      'predictor_duplicates',len(rows)-len(set(r[:-1] for r in rows)))
'@
python -c $delimitedCode (Join-Path $auditDir 'statlog-german-credit\german.data') space
python -c $delimitedCode (Join-Path $auditDir 'credit-approval\crx.data') comma
```

The legacy XLS was read in an isolated temporary environment, then inspected
with the following exact command. The output supplied its shape, missingness,
target/ID/duplicate results, undocumented code counts, and sex-by-target counts:

```powershell
python -m venv "$env:TEMP\aletheia-phase1-audit\audit-venv"
& "$env:TEMP\aletheia-phase1-audit\audit-venv\Scripts\python.exe" -m pip install xlrd
$xlsCode = @'
import collections,sys,xlrd
sheet=xlrd.open_workbook(sys.argv[1]).sheet_by_index(0)
header=[str(sheet.cell_value(1,c)).strip() for c in range(sheet.ncols)]
rows=[tuple(sheet.cell_value(r,c) for c in range(sheet.ncols))
      for r in range(2,sheet.nrows)]
print('sheet_shape',sheet.nrows,sheet.ncols,'data_shape',len(rows),len(header))
print('missing_by_column',{header[i]:sum(v in ('','?','NA','N/A')
      for v in (r[i] for r in rows)) for i in range(len(header))})
print('target',dict(sorted(collections.Counter(int(r[-1]) for r in rows).items())),
      'id_unique',len({r[0] for r in rows}),
      'duplicates',len(rows)-len(set(rows)),
      'without_id_duplicates',len(rows)-len(set(r[1:] for r in rows)))
for name in ('SEX','EDUCATION','MARRIAGE','PAY_0','PAY_2','PAY_3',
             'PAY_4','PAY_5','PAY_6'):
    i=header.index(name)
    print(name,dict(sorted(collections.Counter(int(r[i]) for r in rows).items())))
sex=header.index('SEX')
print('sex_target',dict(sorted(collections.Counter(
      (int(r[sex]),int(r[-1])) for r in rows).items())))
'@
& "$env:TEMP\aletheia-phase1-audit\audit-venv\Scripts\python.exe" -c $xlsCode `
  (Join-Path $auditDir 'default-credit-card-clients\default of credit card clients.xls')
```

The initial South German URL guessed without `+update` returned HTTP 404; the
official page-linked archive URL above succeeded. `Expand-Archive` reported an
unsupported compression method for its BZIP2 entries; Python `zipfile` extracted
all three official files. These were temporary tooling issues, not data changes.

## Evidence Sources

- UCI South German Credit: https://archive.ics.uci.edu/dataset/573/south+german+credit
- Official correction report: https://www1.beuth-hochschule.de/FB_II/reports/Report-2019-004.pdf
- CC BY 4.0 terms: https://creativecommons.org/licenses/by/4.0/
- UCI Default of Credit Card Clients: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
- Original default paper DOI: https://doi.org/10.1016/j.eswa.2007.12.020
- UCI Statlog German Credit: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
- UCI Credit Approval: https://archive.ics.uci.edu/dataset/27/credit+approval

The downloaded UCI archives' own code tables/readers were also inspected. Facts
not explicitly labelled computed or interpretation above are source-reported.
