Persistent Project Knowledge and Reporting Rules
1. Purpose
This repository is both a software project and a learning project.
A successful implementation is not enough.
Every important part of the system must remain understandable and defensible after development is complete.
The repository must therefore maintain a persistent written record of:
•	what was implemented,
•	why it was implemented,
•	why the work happened in that order,
•	what alternatives were considered,
•	what trade-offs were accepted,
•	what machine-learning concepts were involved,
•	what failed during development,
•	what was learned,
•	and how the final system can be explained technically.
The canonical record is:
docs/PROJECT_REPORT.md
This file is part of the project deliverable, not optional documentation.
________________________________________
2. Instruction Precedence
When working in this repository, follow instructions in this order:
1.	Repository-level governing instructions
2.	Explicit architectural/safety constraints documented in the repository
3.	Current approved project design
4.	Current task/request
5.	Agent preferences or default behaviour
Lower-priority instructions must never silently override higher-priority constraints.
Do not modify the governing instruction file unless explicitly instructed to do so.
________________________________________
3. Read Before Acting
Before making a substantial change:
1.	Read the repository-level instructions.
2.	Read the relevant existing code.
3.	Read docs/PROJECT_REPORT.md.
4.	Read docs/ARCHITECTURE.md if the task affects architecture.
5.	Inspect relevant tests.
6.	Understand the current phase of the project.
Do not assume the repository still matches an earlier conversation.
The repository contents are the source of truth.
________________________________________
4. Mandatory Living Project Report
Maintain:
docs/PROJECT_REPORT.md
If the file does not exist, create it before or during the first meaningful implementation milestone.
Do NOT recreate or overwrite the report on every task.
Update it incrementally.
The report must describe the project in language that a CSE student can understand and later use for:
•	semester evaluation,
•	viva preparation,
•	internship interviews,
•	technical discussions,
•	resume preparation,
•	project presentations.
The report should remain technically accurate but should not read like raw developer logs.
________________________________________
5. Required PROJECT_REPORT.md Structure
Maintain the following sections.
5.1 Project Overview
Keep an up-to-date explanation of:
•	the problem being solved,
•	target users,
•	project objectives,
•	what makes the system technically interesting,
•	major system capabilities,
•	project boundaries.
This section should describe the current project, not merely the original idea.
________________________________________
5.2 Problem Statement
Document:
•	what problem exists,
•	why it matters,
•	why ordinary predictive ML is insufficient,
•	how explainability/auditability addresses the problem,
•	what the project intentionally does NOT attempt to solve.
________________________________________
5.3 System Architecture
Maintain a concise explanation of:
•	frontend,
•	backend,
•	ML pipeline,
•	database,
•	experiment tracking,
•	model storage,
•	explainability pipeline,
•	external integrations if any,
•	deployment architecture.
Include a simple architecture diagram when useful.
When architecture changes materially, update both:
docs/PROJECT_REPORT.md
and
docs/ARCHITECTURE.md
________________________________________
5.4 Data Flow
Explain major flows such as:
Training flow
Dataset
→ validation
→ preprocessing
→ feature engineering
→ train/validation/test separation
→ model training
→ evaluation
→ explainability analysis
→ experiment tracking
→ model registration.
Prediction flow
Request
→ validation
→ preprocessing
→ model inference
→ probability/prediction
→ explanation
→ audit record
→ response.
The report should explain WHY each stage exists.
________________________________________
5.5 Implementation Timeline
Maintain a chronological record of meaningful milestones.
For every milestone record:
Milestone
What was accomplished.
Why this came now
Why this step logically followed previous work.
What was implemented
Important components added or changed.
Why
Why the chosen implementation was appropriate.
Concepts involved
Relevant software-engineering or ML concepts.
Result
What became possible after completing it.
Avoid recording trivial edits such as formatting changes or renamed variables.
Record conceptual progress, not keystrokes.
________________________________________
6. Decision Records
Any significant technical decision must be documented.
Examples:
•	selecting FastAPI instead of another backend framework,
•	choosing PostgreSQL,
•	choosing a modular monolith,
•	selecting a particular dataset,
•	choosing Logistic Regression as a baseline,
•	choosing SHAP,
•	deciding how counterfactuals are generated,
•	defining train/test boundaries,
•	selecting evaluation metrics,
•	changing the model-selection strategy,
•	introducing MLflow,
•	adopting a particular preprocessing method.
For each important decision record:
Decision
What was chosen.
Context
What problem required a decision.
Alternatives considered
What realistic alternatives existed.
Choice
What was selected.
Reason
Why it was selected.
Trade-offs
What disadvantages were accepted.
When to reconsider
What future condition could justify changing the decision.
Small decisions can be recorded directly inside PROJECT_REPORT.md.
Major architectural decisions may additionally receive a dedicated record under:
docs/decisions/
Do not create an ADR for trivial implementation choices.
________________________________________
7. Machine Learning Experiment Records
Every meaningful ML experiment must be documented.
Record:
•	experiment objective,
•	dataset version,
•	features,
•	target variable,
•	preprocessing,
•	train/validation/test strategy,
•	model,
•	hyperparameters,
•	metrics,
•	result,
•	interpretation,
•	problems discovered,
•	conclusion.
Never report a metric without explaining what it means.
Do not record only:
"Random Forest accuracy = 91%."
Record what that result implies and whether it is actually better for the project.
________________________________________
8. Model Comparison Records
Whenever multiple models are compared, document:
•	why those models were selected,
•	expected strengths,
•	expected weaknesses,
•	evaluation methodology,
•	cross-validation strategy,
•	classification metrics,
•	inference considerations,
•	interpretability considerations,
•	final decision.
The report must distinguish:
best numerical performance
from
best model for the system requirements.
________________________________________
9. Explainability Records
For every explainability method used, document:
•	what the technique does,
•	why it is required,
•	whether it is global or local,
•	whether it is model-specific or model-agnostic,
•	limitations,
•	what its output means,
•	what its output does NOT prove.
Example topics may include:
•	model coefficients,
•	feature importance,
•	permutation importance,
•	SHAP,
•	LIME,
•	counterfactual explanations.
Do not describe post-hoc explanations as perfect descriptions of the internal reasoning of a model.
Document their limitations honestly.
________________________________________
10. Counterfactual Records
When counterfactual explanations are implemented, document:
•	what a counterfactual explanation means,
•	how candidate changes are generated,
•	mutable features,
•	immutable features,
•	constrained features,
•	feasibility conditions,
•	distance/cost function,
•	limitations.
Record at least one worked example that can later be explained during an interview.
________________________________________
11. Fairness Analysis Records
If fairness analysis is implemented, document:
•	which groups are compared,
•	why the comparison is meaningful,
•	metrics used,
•	observed disparities,
•	limitations,
•	dataset limitations.
Never conclude merely:
"The model is unbiased."
State what was measured instead.
________________________________________
12. Bugs and Engineering Lessons
Maintain a section:
Important Problems Encountered
Only record problems that taught something meaningful.
For each one:
Problem
What failed.
Symptoms
How the problem appeared.
Root cause
Why it happened.
Fix
What changed.
Lesson
What should be remembered.
Examples worth documenting:
•	data leakage,
•	incorrect preprocessing order,
•	train/test mismatch,
•	model serialization problems,
•	schema incompatibility,
•	SHAP compatibility issues,
•	API validation bugs,
•	database transaction problems,
•	deployment/environment differences.
This section is particularly valuable for interviews because engineering interviews often ask:
"Tell me about a difficult bug you encountered."
The report should preserve real answers to that question.
________________________________________
13. Concept Learning Notes
Whenever an important concept is introduced, add a concise explanation under:
Concepts Learned Through This Project
Use this structure:
Concept
Technical name.
Simple explanation
Explain it without unnecessary jargon.
Where we used it
Specific project component.
Why it mattered
What problem it solved.
What I should be able to explain
2–5 interview/viva points.
Relevant topics may include:
•	train/test split,
•	cross-validation,
•	overfitting,
•	precision,
•	recall,
•	F1,
•	ROC-AUC,
•	feature scaling,
•	feature encoding,
•	Logistic Regression,
•	Decision Trees,
•	Random Forest,
•	Gradient Boosting,
•	regularization,
•	feature importance,
•	SHAP,
•	counterfactual explanations,
•	calibration,
•	model versioning,
•	experiment tracking,
•	MLOps,
•	APIs,
•	dependency injection,
•	database schema design.
Do not turn this section into a textbook.
Document concepts in the context in which they were actually used.
________________________________________
14. "Why Did We Do This?" Rule
For every major feature, the report must answer:
1.	What does it do?
2.	Why do we need it?
3.	Why did we implement it at this stage?
4.	What would be missing without it?
5.	What alternative approach could have been used?
6.	Why was the selected approach preferable?
A description without rationale is incomplete.
________________________________________
15. Interview Defence Section
Maintain:
Project Defence and Interview Preparation
Continuously add questions that become relevant as the project develops.
For every question include a concise answer based on the actual implementation.
Examples:
Why did you choose this project?
What problem does it solve?
Why is explainability necessary?
Why not simply use the most accurate model?
What dataset did you use?
How did you prevent data leakage?
Why did you choose your evaluation metrics?
Why use cross-validation?
What was your baseline model?
Why did the final model outperform the baseline?
What is SHAP?
What are the limitations of SHAP?
What is a counterfactual explanation?
How do you ensure counterfactuals are realistic?
How did you evaluate fairness?
How is the model served?
How does a prediction move through the system?
How are model versions tracked?
What would need to change before deploying this in a real organisation?
What was the hardest engineering problem?
What would you improve if given another month?
Answers must reflect the real project.
Never fabricate accomplishments.
________________________________________
16. Semester Viva Preparation
Maintain a subsection containing likely academic questions related to concepts actually implemented.
Group them into:
•	Basic
•	Intermediate
•	Difficult
Include both:
•	conceptual questions,
•	implementation-specific questions.
Whenever a new ML concept becomes part of the project, add appropriate questions.
________________________________________
17. Resume Evidence
Maintain a section:
Resume Evidence
Do not write exaggerated resume claims during early development.
Instead maintain verified facts such as:
•	number of model families compared,
•	dataset size,
•	best measured metrics,
•	number of implemented explainability techniques,
•	measured inference latency,
•	test count,
•	deployment status,
•	experiment count.
At the end, these facts can be converted into strong resume bullets.
Never invent numbers.
________________________________________
18. Limitations
Maintain an honest limitations section.
Examples may include:
•	dataset representativeness,
•	explanation reliability,
•	fairness metric limitations,
•	counterfactual feasibility,
•	model generalisation,
•	limited production monitoring,
•	absence of real-world validation.
Do not hide limitations.
Understanding limitations strengthens the technical credibility of the project.
________________________________________
19. Future Work
Only list extensions that logically follow from the existing architecture.
Separate:
Useful next steps
from
Research extensions.
Avoid meaningless future-work lists containing every popular AI technology.
________________________________________
20. Report Update Rule
Before declaring a meaningful milestone complete:
1.	implementation must work;
2.	relevant tests must pass;
3.	documentation affected by the change must be updated;
4.	docs/PROJECT_REPORT.md must reflect the meaningful work completed.
If no meaningful knowledge or project decision changed, do not modify the report merely to create activity.
The goal is accurate project memory, not documentation noise.
________________________________________
21. Report Quality Rules
The report must:
•	use clear English,
•	favour understanding over jargon,
•	explain technical terms,
•	contain actual project facts,
•	clearly separate implementation facts from future plans,
•	avoid marketing language,
•	avoid fake metrics,
•	avoid unsupported claims,
•	avoid copying generated explanations blindly,
•	remain internally consistent.
The report should eventually allow someone who did not participate in development to understand:
•	what the system does,
•	how it works,
•	why it was designed that way,
•	how the ML works,
•	what experiments were performed,
•	what limitations exist.
________________________________________
22. Teaching During Development
Important implementation work should also function as teaching.
Before implementing a new core concept:
1.	explain the idea simply;
2.	explain why it is needed now;
3.	explain where it fits in the architecture;
4.	show a small example if necessary;
5.	implement it;
6.	explain important code paths;
7.	verify behaviour;
8.	update the project report.
For important logic, occasionally ask the learner to explain the component back in their own words or make a small modification.
Do not slow down obvious boilerplate unnecessarily.
________________________________________
23. Code Ownership Rule
Generated code should remain understandable.
For core logic such as:
•	preprocessing,
•	feature engineering,
•	training,
•	evaluation,
•	explainability,
•	counterfactual generation,
•	model selection,
•	inference,
•	API orchestration,
prefer small understandable changes over huge generated implementations.
If a large implementation is unavoidable, explain:
•	component responsibilities,
•	data flow,
•	important abstractions,
•	failure modes.
________________________________________
24. Enterprise Engineering Without Over-Engineering
Use professional engineering principles where they solve actual problems.
Prefer:
•	clear boundaries,
•	SOLID principles,
•	dependency inversion,
•	testable components,
•	configuration management,
•	typed interfaces,
•	proper validation,
•	structured logging,
•	reproducible ML pipelines.
Avoid:
•	unnecessary microservices,
•	premature distributed systems,
•	excessive interfaces,
•	unnecessary design patterns,
•	unnecessary infrastructure.
An architecture is not enterprise-grade because it is complicated.
It is enterprise-grade when it is:
•	maintainable,
•	testable,
•	auditable,
•	understandable,
•	extensible,
•	reliable.
________________________________________
25. External Dependency Rule
Before introducing a significant new external dependency, model, hosted service, dataset, database technology, or API:
Explain:
•	what is needed,
•	why it is needed,
•	where it will be used,
•	alternatives,
•	licence/cost where relevant,
•	hardware/runtime implications,
•	fallback if it is not adopted.
Do not silently introduce important dependencies.
________________________________________
26. Architecture Change Rule
Before making a change that materially affects:
•	module boundaries,
•	database schema,
•	ML pipeline structure,
•	public APIs,
•	model artifact format,
•	experiment tracking,
•	deployment strategy,
state:
•	current architecture,
•	proposed change,
•	reason,
•	affected components,
•	migration implications,
•	tests required.
Then update architectural documentation after implementation.
________________________________________
27. Data Leakage Rule
Machine-learning correctness takes precedence over convenience.
Never knowingly:
•	fit preprocessing using test data,
•	use target-derived information as an input feature,
•	allow future information into historical predictions,
•	tune repeatedly against the final test set,
•	evaluate on training data and present it as generalisation performance.
If potential leakage is discovered, stop and explain it before continuing.
Document the issue in the report if it materially affected the project.
________________________________________
28. Reproducibility Rule
Where practical, experiments must be reproducible.
Record:
•	random seed,
•	data version,
•	preprocessing,
•	features,
•	algorithm,
•	hyperparameters,
•	metrics.
Avoid unexplained manually generated model artifacts.
________________________________________
29. Definition of Done
A significant task is not complete merely because code was written.
Before marking meaningful work complete verify:
•	implementation works,
•	tests relevant to the change pass,
•	no obvious data leakage was introduced,
•	architecture remains consistent,
•	important decisions are documented,
•	project report is current,
•	the implemented concept can be explained in simple language.
If one of these is false, report the work as incomplete.
________________________________________
30. Final Project Documentation Goal
At project completion, docs/PROJECT_REPORT.md should function as:
•	engineering report,
•	ML experiment summary,
•	architecture explanation,
•	decision history,
•	learning record,
•	semester viva preparation document,
•	interview preparation reference.
A reader should be able to reconstruct not only:
what was built
but also:
why the project evolved the way it did.

# Supervisor Handoff

This project is externally supervised by a separate technical reviewer.

Maintain:

docs/SUPERVISOR_HANDOFF.md

This file represents the CURRENT repository state for review.

Unlike PROJECT_REPORT.md, which is a long-term project record,
SUPERVISOR_HANDOFF.md should remain concise and should be rewritten
after every meaningful milestone.

Before declaring a milestone complete, update SUPERVISOR_HANDOFF.md with:

1. Current milestone
2. Status
3. What was implemented
4. Files created/modified
5. Important decisions and why
6. Tests/checks actually executed
7. Exact test results
8. ML experiment results, if applicable
9. Problems encountered
10. Known limitations
11. Architecture changes
12. Documentation updated
13. Evidence the supervisor should inspect
14. Unresolved questions
15. Suggested next step

Never fabricate tests, metrics, results, implementation, or verification.

Clearly distinguish:
- implemented and verified;
- implemented but not verified;
- planned;
- suggested.

The suggested next step is advisory only.
The external supervisor determines whether the project advances.

Do not use SUPERVISOR_HANDOFF.md as a substitute for updating
PROJECT_REPORT.md or ARCHITECTURE.md.