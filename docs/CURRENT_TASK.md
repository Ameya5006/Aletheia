# MILESTONE

Phase 1 — Dataset Selection and Data Audit

# GOAL

Select one technically defensible public tabular credit-risk classification dataset for Aletheia and produce an evidence-based audit establishing whether it can support the planned Research MVP.

The milestone must determine:

* provenance and licence;
* dataset version and file identity;
* target semantics;
* observation unit;
* feature meanings;
* class distribution;
* missingness and duplicates;
* chronology and repeated-entity risks;
* potential leakage;
* prediction, audit-only, identifier, target, and excluded feature roles;
* candidate split strategy;
* fairness-analysis feasibility;
* counterfactual feasibility;
* important dataset limitations.

Do not train a model or design the application architecture.

# WHY THIS MILESTONE EXISTS

Phase 0 and its documentation repair have passed external supervisor review.

Dataset evidence must now be established before architecture or implementation because it determines:

* what Aletheia predicts;
* what information is available at prediction time;
* how leakage must be prevented;
* which split strategy is valid;
* what preprocessing will eventually be required;
* which attributes may be used for prediction or auditing;
* whether meaningful counterfactual constraints can be created;
* whether fairness analysis is legitimate;
* and which later ML/XAI components are actually justified.

# CURRENT STATE AND PREREQUISITES

At the start of this task:

* Phase 0 and its repair are externally supervisor-approved.
* The approved direction is research-first.
* `prompt.txt` remains the permanent original vision.
* No dataset has been selected.
* No EDA, model training, architecture, dependency selection, application implementation, API, database, frontend, or deployment exists.
* `docs/ARCHITECTURE.md` remains unapproved.
* `docs/CURRENT_TASK.md` is the only currently authorized task.
* The user, not Codex, performs Git commits and pushes.

If the repository materially differs from this state, stop and report the discrepancy.

# FILES TO READ FIRST

Read completely:

* `AGENTS.md`
* `prompt.txt`
* `docs/CURRENT_TASK.md`
* `docs/PROJECT_REPORT.md`
* `docs/ARCHITECTURE.md`
* `docs/EXECUTION_PLAN.md`
* `docs/SUPERVISOR_HANDOFF.md`

Also inspect:

* `git status --short`;
* recent Git history;
* the repository tree;
* any currently tracked dataset, code, dependency, or experiment artifacts.

Treat repository evidence as authoritative.

# BEFORE CHANGING FILES

Provide a concise working update explaining:

1. the verified repository state;
2. the Phase 1 methodology;
3. the candidate-selection gates;
4. the files you expect to change;
5. any temporary tools required;
6. risks such as unclear licensing, target ambiguity, leakage, weak feature semantics, small samples, or poor subgroup support;
7. the measurable acceptance criteria.

Do not select a dataset merely because it is popular or convenient.

# IN SCOPE

## 1. Permanent PROJECT_REPORT clarification

Add one concise governance clarification to `AGENTS.md` stating that `docs/PROJECT_REPORT.md` must eventually function as an evidence-backed engineering, learning, interview, viva, and project-defence guide.

For each meaningful implemented component or method, where applicable, the report must explain:

* purpose and project location;
* data or request flow;
* important callers and dependencies;
* chosen approach and alternatives;
* trade-offs and assumptions;
* failure modes and meaningful bugs;
* relevant tests;
* important code/files to inspect;
* technical or ML concepts involved;
* limitations;
* concise interview/viva explanations and likely follow-up questions.

The report must remain structured and concise. It must never describe planned work as implemented or invent evidence to make the guide appear complete.

Do not otherwise restructure `AGENTS.md`.

## 2. Candidate dataset comparison

Identify at least three credible public tabular credit-risk or loan-risk classification datasets.

Use authoritative primary sources wherever possible:

* official dataset repositories;
* official data documentation;
* original dataset papers;
* official licence pages.

For every candidate, record:

* exact dataset name;
* authoritative source URL;
* original paper or documentation where available;
* licence or usage terms;
* access method;
* file format;
* approximate and verified row/column counts;
* target variable and label meaning;
* observation unit;
* collection period or chronology, if documented;
* missing-value information;
* class distribution where data access permits verification;
* identifiers or possible repeated entities;
* sensitive or potential audit attributes;
* feature-semantic quality;
* potential post-outcome or leakage-prone fields;
* counterfactual suitability;
* fairness-analysis feasibility;
* laptop/runtime suitability;
* major limitations and rejection risks.

Distinguish:

* facts stated by the source;
* facts computed from the downloaded data;
* interpretations or unresolved questions.

Do not use an arbitrary composite score. Apply transparent pass/fail gates and a qualitative comparison.

## 3. Mandatory dataset-selection gates

A selected dataset must have:

* an authoritative, traceable source;
* sufficiently clear lawful usage or licence terms;
* a defined classification target;
* an understandable observation unit;
* enough feature documentation for leakage analysis;
* enough observations and minority-class support for meaningful evaluation;
* manageable size for the user’s normal student laptop;
* no unresolved fatal target or provenance ambiguity;
* sufficient feature semantics for at least a defensible counterfactual proof of concept.

Fairness support is desirable but not mandatory. Never choose or reject a dataset solely to force fairness analysis.

If no candidate passes these gates, do not force a selection. Report `INVESTIGATE` with the exact missing evidence.

## 4. Inspect the actual candidate data

Where licensing and access permit, inspect the real candidate files rather than relying only on webpage summaries.

Temporary raw files must remain outside the repository or in an ignored temporary location. Do not commit raw candidate datasets during this milestone.

If temporary audit tooling is necessary:

* prefer already available tools;
* an isolated temporary environment outside the repository may be used;
* explain why it is needed;
* record relevant tool versions;
* do not treat temporary audit packages as selected Aletheia dependencies;
* do not create or modify project dependency files.

If the actual data cannot be inspected, clearly mark which claims remain source-reported rather than independently verified.

## 5. Selected dataset identity and reproducibility evidence

For the selected dataset, record:

* exact source and download URL;
* retrieval date;
* version or release information where available;
* original filename;
* file format;
* file size;
* SHA-256 checksum;
* row and column count;
* source licence and attribution requirements;
* whether redistribution is allowed;
* instructions for reacquiring the same data.

Do not commit the raw dataset.

## 6. Target and observation-unit audit

Document:

* what one row represents;
* what event or condition the target represents;
* the target label values;
* which label represents the adverse/positive event for future classification analysis;
* when the target becomes known;
* the intended prediction moment;
* whether every feature would exist at that moment;
* whether the dataset describes applications, customers, accounts, or outcomes;
* any ambiguity between credit risk, default prediction, approval prediction, and repayment outcome.

Do not invent a business threshold or production-lending interpretation.

## 7. Structural data audit

Compute and record:

* shape;
* column names;
* data types;
* representative value ranges or categories;
* missing-value count and percentage per feature;
* exact duplicate-row count;
* identifier uniqueness;
* possible repeated-entity evidence;
* target counts and percentages;
* invalid or undocumented values;
* constant or near-constant fields where relevant;
* obvious schema inconsistencies;
* chronology fields and their coverage.

All numerical findings must come from actual executed inspection and must be reproducible from recorded commands.

Check arithmetic consistency, such as class counts summing to the audited observation count.

## 8. Feature dictionary and feature roles

Create a feature-level table containing:

* source column name;
* plain-language meaning;
* data type;
* important values or units;
* timing relative to the target;
* proposed role:

  * target;
  * identifier;
  * prediction candidate;
  * audit-only candidate;
  * excluded;
  * unresolved;
* leakage concern;
* counterfactual category:

  * immutable;
  * mutable;
  * constrained mutable;
  * non-actionable;
  * unresolved;
* reason and source evidence.

Do not finalize a prediction feature merely because it correlates with the target.

Protected or sensitive attributes must not automatically become prediction features. If potentially useful for auditing, keep the prediction and audit roles conceptually separate.

## 9. Leakage and temporal review

Investigate:

* target-derived fields;
* post-outcome information;
* information created after the intended prediction time;
* duplicated records;
* repeated customers or accounts;
* chronology;
* aggregate fields that may use future information;
* identifiers that accidentally encode outcomes;
* source preprocessing that may already contain leakage;
* unclear feature timing.

For every suspicious field, record the concern, evidence, proposed treatment, and unresolved questions.

If a fatal leakage or target-validity problem is discovered, reject the dataset rather than hiding it.

## 10. Candidate split strategy

Recommend, but do not implement, the appropriate future split family:

* stratified random;
* temporal;
* group-aware;
* or another justified approach.

Explain:

* why the strategy matches the observation unit and chronology;
* what leakage it prevents;
* what evidence is still missing;
* how the final test set must remain isolated later.

Do not generate train/test files or begin preprocessing.

## 11. Fairness feasibility audit

Do not perform fairness analysis yet.

Determine only whether the dataset may support it by documenting:

* available legitimate audit attributes;
* provenance and meaning of those attributes;
* subgroup counts;
* positive and negative target counts within candidate groups where definitions are source-supported;
* very small or unsupported groups;
* whether categories were encoded or combined by the source;
* risks of arbitrary regrouping;
* whether an attribute should be audit-only;
* limitations of treating the public dataset as representative of real lending.

Do not infer protected identities from proxy features.

Do not claim the dataset or a future model is fair or unfair.

## 12. Counterfactual feasibility audit

Do not generate counterfactuals yet.

Assess whether the feature semantics permit realistic future constraints:

* immutable attributes;
* non-actionable historical attributes;
* mutable financial variables;
* directionally constrained variables;
* categorical constraints;
* allowed ranges;
* relationships between dependent features;
* changes that could be mathematically valid but practically impossible.

Mark uncertain classifications as unresolved instead of guessing.

## 13. Dataset decision

Select one dataset only if the evidence clearly supports it.

Document:

* why it passed the mandatory gates;
* why it is the best fit for Aletheia’s Research MVP;
* why each realistic alternative was not selected;
* trade-offs accepted;
* limitations inherited;
* conditions that would require reconsidering the choice.

Dataset selection is not evidence that the later model will be accurate, explainable, stable, fair, or suitable for real lending.

# REQUIRED ARTIFACT

Create:

* `docs/DATASET_AUDIT.md`

It must contain:

1. candidate comparison;
2. selection gates;
3. final selection or explicit investigation result;
4. provenance, licence, and version evidence;
5. actual data-inspection results;
6. target and observation-unit analysis;
7. structural audit;
8. feature dictionary and roles;
9. leakage review;
10. split recommendation;
11. fairness feasibility;
12. counterfactual feasibility;
13. limitations;
14. reproducibility instructions;
15. evidence sources.

Keep detailed dataset tables in this file rather than overloading `PROJECT_REPORT.md`.

# PROJECT_REPORT REQUIREMENTS

Update `docs/PROJECT_REPORT.md` with a concise, technically accurate learning and defence record covering:

* which dataset was selected, if any;
* why dataset selection came before architecture;
* alternatives considered;
* target semantics;
* observation unit;
* important feature-role distinctions;
* major leakage risks;
* recommended split family;
* fairness feasibility;
* counterfactual feasibility;
* assumptions and limitations;
* what evidence is in `docs/DATASET_AUDIT.md`;
* what files the user should inspect;
* concise interview/viva questions and model answers based on completed Phase 1 work.

The report must remain a study guide rather than a raw dump of audit output.

Do not document future modelling as though it exists.

# EXECUTION PLAN REQUIREMENTS

Update `docs/EXECUTION_PLAN.md` to record:

* Phase 0 and its repair as externally supervisor-approved;
* Phase 1 as completed by Codex and pending external supervisor review only if all acceptance criteria are met;
* otherwise, Phase 1 as incomplete or investigate;
* actual Phase 1 scope, evidence, and measurable Definition of Done;
* architecture and all implementation milestones as still blocked.

Do not authorize architecture or create the next executable milestone.

# SUPERVISOR HANDOFF REQUIREMENTS

Rewrite `docs/SUPERVISOR_HANDOFF.md` for Phase 1.

Include:

* current milestone and status;
* exact selected dataset, or explicit failure to select;
* source and licence;
* target and observation unit;
* actual computed audit facts;
* important leakage findings;
* feature-role conclusions;
* split recommendation;
* fairness and counterfactual feasibility;
* exact files changed;
* exact commands or checks run and results;
* unresolved questions;
* limitations;
* confirmation that no model, preprocessing pipeline, architecture, application, or later milestone began;
* evidence the external supervisor should inspect;
* suggested next action limited to supervisor review.

The handoff is navigation evidence, not proof.

# OUT OF SCOPE

Do not:

* design system architecture or module boundaries;
* modify `docs/ARCHITECTURE.md`;
* modify `prompt.txt`;
* select the permanent application technology stack;
* create project dependency files;
* install persistent project dependencies;
* create notebooks or permanent analysis scripts;
* commit raw or processed datasets;
* preprocess data for modelling;
* create train, validation, or test datasets;
* train or tune models;
* choose model hyperparameters;
* produce model metrics;
* implement SHAP, LIME, counterfactual generation, stability, or fairness analysis;
* create APIs, databases, frontends, Docker files, MLflow configuration, or deployment files;
* fabricate missing documentation, licence terms, counts, metrics, or findings;
* begin architecture planning;
* create the next `CURRENT_TASK.md`;
* commit, push, merge, mutate branches, or rewrite Git history.

# ANTI-OVERENGINEERING RULES

* Produce one focused dataset-audit document.
* Do not create a data-catalogue system.
* Do not create database schemas.
* Do not add DVC, MLflow, Docker, orchestration, or cloud storage.
* Do not create abstractions for a pipeline that does not exist.
* Do not evaluate unnecessary datasets once a sufficiently broad and credible comparison exists.
* Prefer verified evidence over document length.

# VERIFICATION

At minimum, perform and report:

1. authoritative source and licence verification;
2. actual file download or documented access attempt;
3. SHA-256 calculation for the selected raw file;
4. schema and shape inspection;
5. missing-value calculations;
6. duplicate-row check;
7. identifier and repeated-entity check where possible;
8. target-count and percentage calculation;
9. arithmetic consistency checks;
10. subgroup-support counts only where definitions are legitimate;
11. feature-timing and leakage review;
12. comparison of computed facts with source documentation;
13. `git diff --check`;
14. `git status --short`;
15. final changed-file inspection;
16. confirmation that no raw dataset or temporary audit artifact is tracked;
17. confirmation that `prompt.txt` and `docs/ARCHITECTURE.md` are unchanged;
18. confirmation that no model, application, architecture, dependency, or future-task work was introduced.

Record exact commands, tool versions where relevant, and exact results.

If actual data access, provenance, licensing, or target semantics cannot be verified, do not fabricate completion. Return `INVESTIGATE`.

# ACCEPTANCE CRITERIA / DEFINITION OF DONE

Phase 1 is complete by Codex only if:

* [ ] At least three credible candidate datasets were compared.
* [ ] Candidate facts use authoritative sources where available.
* [ ] Source-reported and independently computed facts are distinguished.
* [ ] Mandatory selection gates are explicit.
* [ ] One dataset passes the gates and is selected, or an honest `INVESTIGATE` result explains why none can be selected.
* [ ] The selected file has recorded identity, retrieval information, size, and SHA-256.
* [ ] Licence and redistribution conditions are documented without guessing.
* [ ] Target semantics and observation unit are clear.
* [ ] Actual shape, schema, missingness, duplicates, and class distribution were computed.
* [ ] Feature meanings and proposed roles are documented.
* [ ] Leakage, chronology, and repeated-entity risks were investigated.
* [ ] A future split family is recommended with evidence.
* [ ] Fairness feasibility is assessed without performing fairness analysis.
* [ ] Counterfactual feasibility is assessed without generating counterfactuals.
* [ ] Dataset limitations and rejection conditions are explicit.
* [ ] `docs/DATASET_AUDIT.md` contains reproducibility evidence.
* [ ] `PROJECT_REPORT.md` contains concise learning and defence material based only on completed work.
* [ ] `EXECUTION_PLAN.md` records the correct gate and Phase 1 status.
* [ ] `SUPERVISOR_HANDOFF.md` accurately reports repository evidence.
* [ ] No raw data, models, application code, architecture, persistent dependencies, or future task was added.
* [ ] No Git commit or push was performed by Codex.

If any mandatory criterion fails, report Phase 1 as incomplete or `INVESTIGATE`.

# EXPECTED GIT STATUS BEFORE USER COMMIT

The expected changed files are:

* Modified: `AGENTS.md`
* Modified: `docs/CURRENT_TASK.md`
* Modified: `docs/EXECUTION_PLAN.md`
* Modified: `docs/PROJECT_REPORT.md`
* Modified: `docs/SUPERVISOR_HANDOFF.md`
* New untracked file: `docs/DATASET_AUDIT.md`

Notes:

* `docs/CURRENT_TASK.md` is modified because the user replaced the previous task with this approved Phase 1 task. Codex must not replace it again.
* No raw dataset should appear.
* Temporary scripts, environments, downloaded archives, spreadsheets, CSV files, or generated outputs must not appear in repository status.
* `prompt.txt` must remain unchanged.
* `docs/ARCHITECTURE.md` must remain unchanged.
* No dependency, notebook, source-code, API, frontend, database, Docker, MLflow, or deployment file should appear.

If Git status contains additional files, stop and explain them before recommending a commit.

# FINAL CODEX RESPONSE

Report:

1. milestone status;
2. dataset selected or investigation outcome;
3. why;
4. candidates considered;
5. authoritative sources and licence;
6. target and observation unit;
7. important computed audit results;
8. leakage findings;
9. feature-role conclusions;
10. split recommendation;
11. fairness feasibility;
12. counterfactual feasibility;
13. files created;
14. files modified;
15. files intentionally unchanged;
16. commands and checks actually run;
17. exact results;
18. unresolved issues;
19. limitations;
20. what the user should understand;
21. confirmation that architecture and modelling did not begin;
22. confirmation that Codex did not commit or push;
23. actual final `git status --short`;
24. recommended commit message.

If Phase 1 completes successfully, recommend:

`docs: select and audit Aletheia dataset`

If no dataset can defensibly be selected, recommend:

`docs: investigate Aletheia dataset candidates`

Do not claim external supervisor approval.

# STOP RULE

Stop after completing and verifying Phase 1.

Do not begin:

* architecture;
* technology selection;
* preprocessing implementation;
* model training;
* explainability implementation;
* counterfactual generation;
* fairness measurement;
* API or frontend development;
* experiment tracking;
* deployment;
* or another milestone.

Do not modify `docs/CURRENT_TASK.md` again.

Do not commit or push.

The user will inspect Git status, commit and push the completed attempt, and return it for independent external supervisor review.
