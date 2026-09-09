# MILESTONE

Phase 0 Documentation and Governance Consistency Repair

# GOAL

Repair the planning and governance inconsistencies identified during the external supervisor’s review of Phase 0.

The repository must end with one internally consistent account of:

- the proposed Aletheia scope;
- the milestone sequence;
- the meanings of Research MVP, semester application scope, and enterprise extensions;
- the status of explanation stability;
- the measurable Phase 0 Definition of Done;
- external approval status;
- the role and authority boundaries of `docs/CURRENT_TASK.md`;
- and responsibility for Git commits and pushes.

This is a documentation and governance repair only.

# WHY THIS MILESTONE EXISTS

The first Phase 0 attempt contained technically promising ML/XAI planning, but it received:

`FAIL — FIX BEFORE CONTINUING`

The failure was caused by planning inconsistencies:

1. conflicting execution order;
2. conflicting meanings of MVP;
3. explanation stability being described as both mandatory and optional;
4. no measurable Phase 0 Definition of Done;
5. wording that slightly overstated approval status;
6. no permanent governance for `docs/CURRENT_TASK.md`;
7. no permanent record that Codex must not commit or push.

These problems must be repaired before dataset selection or any later work begins.

# CURRENT STATE AND PREREQUISITES

At the start of this task:

- Phase 0 has been attempted but has not passed external supervisor review.
- The proposed direction is research-first.
- No dataset has been selected or downloaded.
- No EDA has been conducted.
- No architecture has been approved.
- No dependencies have been installed.
- No application code, ML experiment, model artifact, API, frontend, database, or deployment exists.
- `prompt.txt` is the permanent original Aletheia specification.
- `docs/CURRENT_TASK.md` contains the only currently authorized task.
- `docs/ARCHITECTURE.md` must remain unapproved.
- Phase 1 is blocked pending completion, user commit/push, and external supervisor review of this repair.

If repository evidence materially contradicts this state, stop and report the discrepancy before editing files.

# FILES TO INSPECT

Before making changes, read completely:

- `AGENTS.md`
- `prompt.txt`
- `docs/CURRENT_TASK.md`
- `docs/PROJECT_REPORT.md`
- `docs/ARCHITECTURE.md`
- `docs/EXECUTION_PLAN.md`
- `docs/SUPERVISOR_HANDOFF.md`

Also inspect:

- current Git status;
- the latest relevant commit;
- the current uncommitted diff;
- the repository file tree for evidence of work outside the claimed scope.

Treat repository evidence as authoritative. Do not assume that a statement is correct merely because it appears in `SUPERVISOR_HANDOFF.md`.

# BEFORE EDITING

Before changing files, provide a concise working update that explains:

1. what currently exists;
2. each inconsistency confirmed from the repository;
3. what files you plan to modify;
4. why each modification is necessary;
5. what must remain unchanged;
6. risks of making the governance too complex;
7. the acceptance criteria you will use.

Do not pause for approval unless you discover a material contradiction, missing prerequisite, or required scope expansion.

# IN SCOPE

## 1. Integrate `docs/CURRENT_TASK.md` into governance

Update `AGENTS.md` with the minimum rules necessary to establish that:

- `docs/CURRENT_TASK.md` contains exactly one currently approved Codex milestone or repair task;
- Codex must read it before beginning project work;
- its contents are replaced when the external supervisor approves a different task;
- it may narrow the current work but cannot override permanent safety, ML-correctness, testing, evidence-integrity, or governance rules;
- it cannot silently redefine `prompt.txt`;
- completing it does not authorize the next milestone;
- work must stop at its stated boundary;
- external supervisor review is required before progression;
- Codex must not commit, push, merge, create or move branches, rewrite Git history, or perform equivalent remote Git mutations unless the user explicitly changes this policy;
- Codex must recommend a commit message, while the user performs commit and push operations.

Do not create a new governance framework, policy hierarchy document, or ADR unless an unavoidable contradiction proves one is necessary.

## 2. Reconcile repository-document responsibilities

Ensure the documentation consistently reflects:

- `AGENTS.md`: permanent operating and engineering rules;
- `prompt.txt`: permanent original project specification and vision;
- `docs/CURRENT_TASK.md`: exactly one currently approved task;
- `docs/PROJECT_REPORT.md`: actual completed work, decisions, evidence, learning, and limitations;
- `docs/ARCHITECTURE.md`: currently approved architecture and architectural constraints;
- `docs/EXECUTION_PLAN.md`: approved milestone sequence, dependencies, scope, and Definitions of Done;
- `docs/SUPERVISOR_HANDOFF.md`: concise current-state evidence for external review.

Do not modify `prompt.txt`.

## 3. Reconcile the execution order

The current report and handoff recommend dataset selection and data audit before architecture, while the execution plan currently places architecture and technology selection first.

Adopt and document this research-first order:

1. Phase 0 — Project Analysis and Scope Validation
2. Phase 0 Repair — Documentation and Governance Consistency Repair
3. Phase 1 — Dataset Selection and Data Audit
4. Architecture, technology, and detailed implementation-roadmap planning
5. Reproducible ML and later implementation milestones

The execution plan may identify Phase 1 and its purpose as a future blocked milestone, but must not turn this task into Phase 1 or authorize its execution.

Explain why dataset evidence must inform:

- target semantics;
- feature roles;
- leakage controls;
- split strategy;
- preprocessing requirements;
- fairness feasibility;
- counterfactual constraints;
- XAI compatibility;
- and later architecture decisions.

## 4. Add a measurable Phase 0 acceptance record

Update `docs/EXECUTION_PLAN.md` so Phase 0 explicitly records:

- objective;
- prerequisites;
- concepts involved;
- in-scope work;
- out-of-scope work;
- expected affected files;
- required checks and evidence;
- measurable Definition of Done;
- required documentation updates;
- current approval status.

Distinguish clearly between:

- completed by Codex;
- verified from repository evidence;
- pending external supervisor approval;
- supervisor-approved.

Do not rewrite history to imply that the original Phase 0 attempt passed.

## 5. Reconcile the meanings of MVP

Preserve `prompt.txt` as the original specification.

Update `PROJECT_REPORT.md` and `EXECUTION_PLAN.md` to distinguish:

### Research MVP

The minimum evidence-producing ML/XAI research prototype:

- one approved, documented dataset;
- leakage-safe reproducible preprocessing and splitting;
- an interpretable baseline and justified nonlinear comparators;
- cross-validated selection within training data;
- untouched held-out evaluation;
- global and local explanation evidence;
- a constrained counterfactual proof of concept;
- traceable experiment metadata;
- a concise research comparison or prediction-inspection presentation.

### Semester Application/Demo Scope

A later usable application built only after reliable research evidence exists. It may include, subject to later approval and justification:

- a minimal API;
- a reviewer-facing interface;
- experiment tracking or appropriate persistence;
- targeted tests;
- audit records;
- local reproducibility or containerization.

FastAPI, MLflow, PostgreSQL, React/Next, and Docker must remain unselected technologies until their respective decisions are approved.

### Enterprise Extensions

Keep production-oriented capabilities explicitly deferred, including unnecessary early microservices, Kubernetes, RBAC, production monitoring, CI/CD, cloud infrastructure, approval workflows, and real-lender integration.

State explicitly:

- finishing the Research MVP does not complete the original platform vision;
- finishing the Research MVP does not automatically complete the semester application;
- later application components must present verified research evidence rather than conceal weak ML methodology.

## 6. Resolve explanation-stability status

Make all planning documents agree that:

- explanation stability remains part of Aletheia’s complete research question;
- it is not required for completion of the initial Research MVP;
- it is required before claiming that the complete research question, including stability, has been answered;
- its perturbation rules, eligible features, sample selection, background/reference data, similarity metrics, and boundary-crossing treatment must be designed after dataset inspection;
- it must not be claimed as implemented, measured, or validated yet.

Keep fairness conditional on legitimate audit attributes, sufficient subgroup support, and appropriate methodology.

## 7. Correct approval language

Replace language that implies the external supervisor has already approved Phase 0.

Use precise categories where relevant:

- planned;
- proposed pending review;
- implemented but unverified;
- verified from repository evidence;
- experimentally demonstrated;
- supervisor-approved.

The current Phase 0 scope is proposed and documented, but not yet supervisor-approved.

## 8. Update the supervisor handoff

Rewrite `docs/SUPERVISOR_HANDOFF.md` as the concise handoff for this repair attempt.

It must include:

- current milestone;
- status;
- confirmed starting state;
- exact files modified;
- planning inconsistencies repaired;
- governance changes made;
- checks actually executed;
- exact check results;
- confirmation that no automated tests were applicable, if that remains true;
- confirmation that no dataset, architecture, dependencies, code, experiment, or later milestone work was introduced;
- unresolved issues;
- known limitations;
- architecture status;
- documentation updated;
- evidence the supervisor should inspect;
- suggested next action limited to external review.

The handoff must not claim that Phase 0 has passed.

# OUT OF SCOPE

Do not:

- select, recommend, compare, approve, download, or commit a dataset;
- perform EDA or data profiling;
- define actual dataset feature roles;
- choose the positive class, threshold, primary metric, or split strategy for an unseen dataset;
- design module boundaries or application architecture;
- modify `docs/ARCHITECTURE.md`;
- modify `prompt.txt`;
- select or install dependencies;
- create Python, notebook, frontend, backend, database, infrastructure, or test code;
- run ML experiments;
- fabricate tests, metrics, results, or approvals;
- create an executable Phase 1 task;
- overwrite `docs/CURRENT_TASK.md` with a future task;
- introduce ADRs without a genuine major decision requiring one;
- add governance layers beyond what this workflow needs;
- begin any subsequent phase;
- commit, push, merge, create or move branches, or rewrite Git history.

# ANTI-OVERENGINEERING RULES

- Prefer small, direct edits to existing documents.
- Do not create a policy framework for its own sake.
- Do not duplicate the complete contents of `prompt.txt`.
- Link responsibilities between documents instead of repeating long rules everywhere.
- Do not design future application architecture during a planning repair.
- Do not add technologies merely to make the project appear enterprise-grade.
- Do not turn a documentation repair into a repository restructuring exercise.

# DOCUMENTATION EXPECTATIONS

The expected modified files are limited to:

- `AGENTS.md`
- `docs/PROJECT_REPORT.md`
- `docs/EXECUTION_PLAN.md`
- `docs/SUPERVISOR_HANDOFF.md`

`docs/CURRENT_TASK.md` should remain the approved task being executed and must not be replaced with a future task.

The following must remain unchanged:

- `prompt.txt`
- `docs/ARCHITECTURE.md`

If another file genuinely requires modification, stop and explain why before expanding scope.

# TESTING AND VERIFICATION

Because this is documentation-only work, do not invent application tests.

At minimum:

1. inspect the complete final diff;
2. run `git diff --check`;
3. inspect `git status --short`;
4. inspect the final changed-file list;
5. verify that only authorized files changed, apart from the user-created `docs/CURRENT_TASK.md`;
6. verify that `prompt.txt` is unchanged;
7. verify that `docs/ARCHITECTURE.md` is unchanged;
8. search the final documents for contradictory execution-order statements;
9. search for inconsistent uses of “MVP” and confirm each use identifies the intended scope;
10. search for claims that explanation stability is already implemented or is both required and optional for the same milestone;
11. verify that no document claims supervisor approval;
12. verify that no dataset, code, dependency, architecture, experiment, or future task was introduced;
13. compare `PROJECT_REPORT.md`, `EXECUTION_PLAN.md`, `SUPERVISOR_HANDOFF.md`, `AGENTS.md`, `prompt.txt`, and `ARCHITECTURE.md` for consistency.

Report every command or check actually performed and its exact result. If a check was not run, say so.

# LEARNING AND DEFENCE NOTES

Update only the appropriate existing sections of `PROJECT_REPORT.md` with concise, project-specific explanations of:

- permanent vision versus current task authorization;
- Research MVP versus semester application scope;
- why dataset evidence precedes architecture;
- why Definitions of Done and external gates matter;
- why explanation stability remains part of the full research claim even if it follows the initial Research MVP.

Do not turn the report into a generic project-management textbook.

# ACCEPTANCE CRITERIA / DEFINITION OF DONE

This repair is complete only if all of the following are true:

- [ ] `AGENTS.md` formally governs `docs/CURRENT_TASK.md`.
- [ ] `AGENTS.md` records that Codex must not commit or push under the current policy.
- [ ] `prompt.txt` remains unchanged as the permanent original specification.
- [ ] `docs/ARCHITECTURE.md` remains unchanged and unapproved.
- [ ] `EXECUTION_PLAN.md` uses the research-first sequence with dataset audit before architecture.
- [ ] Phase 0 has a measurable acceptance record.
- [ ] Phase 0 is not represented as supervisor-approved.
- [ ] Research MVP, semester application scope, and enterprise extensions are unambiguous.
- [ ] Completing the Research MVP cannot be confused with completing the original platform vision.
- [ ] Explanation stability has one consistent status across the documents.
- [ ] Fairness remains conditional rather than promised.
- [ ] Phase 1 remains blocked and unexecuted.
- [ ] No executable Phase 1 task has been created.
- [ ] `SUPERVISOR_HANDOFF.md` accurately reports this repair attempt.
- [ ] No dataset, EDA, architecture, dependency, code, experiment, or later-phase work was introduced.
- [ ] Documentation-only verification checks complete without unresolved inconsistency.
- [ ] The final diff contains no unrelated changes.
- [ ] No Git commit, push, merge, branch mutation, or history rewrite was performed by Codex.

If any item is false, report the milestone as incomplete.

# FINAL CODEX RESPONSE

At completion, report:

1. current milestone status;
2. what changed;
3. why each change was needed;
4. files created;
5. files modified;
6. files intentionally left unchanged;
7. checks actually run;
8. exact check results;
9. decisions recorded;
10. unresolved issues;
11. known limitations;
12. what the user should understand;
13. confirmation that Phase 1 did not begin;
14. confirmation that no Git commit or push was performed;
15. recommended commit message.

Recommended commit-message format:

`docs: repair Phase 0 planning governance`

Do not claim external supervisor approval.

# STOP RULE

Stop immediately after completing and verifying this Phase 0 documentation and governance repair.

Do not:

- begin Phase 1;
- select or inspect datasets;
- design architecture;
- install dependencies;
- implement code;
- replace `docs/CURRENT_TASK.md` with another milestone;
- commit or push changes.

The user will inspect the working tree, perform the commit and push, and return the resulting repository state for independent external supervisor review.