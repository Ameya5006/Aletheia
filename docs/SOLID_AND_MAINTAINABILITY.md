# SOLID and maintainability assessment

[README](../README.md) · [High-level design](HIGH_LEVEL_DESIGN.md) · [Low-level design](LOW_LEVEL_DESIGN.md)

**Overall rating: good for a bounded student showcase, with moderate
maintainability debt.** This is a qualitative assessment of current source,
not a measured score or production certification. The strongest properties are
explicit evidence boundaries, dependency injection seams, transactional audit
semantics and behavior-focused tests. The main costs are large orchestration
modules, direct SQL coupling in routes, implicit adapter interfaces and deployment
scripts tied to one approved environment.

No refactoring is performed for this assessment. Recommendations below are
future work requiring the appropriate approval. Severity means the practical
cost or risk of the identified gap in the current single-replica showcase.
“Moderate” merits attention before extending the system; “low” does not justify
an abstraction by itself. Test links identify evidence to inspect, not a claim
that those tests were rerun while writing this document.

## Single Responsibility Principle

**Meaning:** a component should have one coherent reason to change.

**Evidence and strengths:** [case_input.py](../src/aletheia/application/case_input.py)
owns canonical input validation; [auth.py](../src/aletheia/application/auth.py)
owns access-token verification; [release.py](../src/aletheia/application/release.py)
owns trusted release loading and serving. Research foundation, modeling,
evaluation and explanation live in separate
[healthcare modules](../src/aletheia/domains/healthcare).

**Partial compliance:** [api.py](../src/aletheia/application/api.py) combines
middleware, limits, readiness, response projection and routes.
[store.py](../src/aletheia/application/store.py) combines entitlements, release
publication, predictions, reviews and audit transactions. These are cohesive
around delivery/persistence but have multiple reasons to change.

**Severity:** moderate for extension; not evidence of incorrect results.
**Future improvement:** extract cohesive use cases and route groups when a new
workflow is authorized. Preserve the single transaction owning prediction,
idempotency and audit rather than splitting atomic behavior across services.

## Open/Closed Principle

**Meaning:** add supported behavior through stable extension points without
repeatedly editing established behavior.

**Evidence and strengths:** [create_app](../src/aletheia/application/api.py)
accepts release, store and verifier collaborators. The research/delivery
separation lets the HTTP layer evolve without fitting the model again.
[CalibratedModel](../src/aletheia/application/pyfunc_model.py) adapts the approved
callable to MLflow instead of changing its frozen serialization.

**Partial compliance:** input fields, supported roles, release identities and
workflow branches are deliberately explicit. A second serving domain would
require edits in release, schema, store and UI; there is no plugin framework.
The fixed model identity is an integrity control, not a defect to generalize away.

**Severity:** low for the approved single-domain product; moderate if another
domain becomes approved.
**Future improvement:** introduce a narrow domain-serving interface only when a
second real implementation exists, preserving domain-specific validation and
approval constraints.

## Liskov Substitution Principle

**Meaning:** an implementation used in place of another must preserve the
caller's behavioral contract, including failure and output semantics.

**Evidence and strengths:** [application fixtures](../tests/application/conftest.py)
and [release/auth tests](../tests/application/test_release_auth.py) exercise
replaceable collaborators. The [MLflow adapter](../src/aletheia/application/pyfunc_model.py)
returns the complete calibrated callable output rather than silently substituting
the uncalibrated estimator.

**Partial compliance:** most application collaborators use duck typing, not an
explicit protocol hierarchy. There is little inheritance to assess. A fake
store can satisfy method names while omitting transaction, authorization or
idempotency behavior; successful unit tests alone do not establish substitutability.

**Severity:** low in current production composition; moderate for future adapters.
**Future improvement:** define minimal behavioral contracts where alternatives
actually arise and apply shared contract tests. Keep
[PostgreSQL tests](../tests/application/test_postgres_api.py) because an in-memory
substitute cannot prove PostgreSQL locking or trigger behavior.

## Interface Segregation Principle

**Meaning:** callers should depend only on the capabilities they need.

**Evidence and strengths:** the browser separates
[generic transport](../frontend/src/api/client.ts) from
[analysis calls](../frontend/src/api/analyses.ts).
[TokenVerifier](../src/aletheia/application/auth.py) exposes a small verification
surface, and [case input](../src/aletheia/application/case_input.py) remains
independent of database operations.

**Partial compliance:** Store is a broad object used by HTTP and operator code;
some API routes also reach its SQLAlchemy engine and schema directly. Injecting
Store therefore exposes more capabilities than a read-only route needs.

**Severity:** moderate for route isolation and future changes.
**Future improvement:** introduce focused query/use-case functions for history,
audit and release operations before adding broad repository interfaces.

## Dependency Inversion Principle

**Meaning:** important policy should not require a particular delivery mechanism
where a stable abstraction can separate them.

**Evidence and strengths:** research code under
[domains/healthcare](../src/aletheia/domains/healthcare) does not call FastAPI.
The application factory accepts dependencies;
[TokenVerifier](../src/aletheia/application/auth.py) accepts a clock and JWKS fetcher;
[ApiClient](../frontend/src/api/client.ts) accepts transport and token suppliers.
These are useful seams for deterministic tests.

**Partial compliance:** API imports concrete Store and VerifiedRelease types
and constructs defaults. Routes issue SQLAlchemy queries directly.
[registry.py](../src/aletheia/application/registry.py) knows MLflow and filesystem
publication details. There is no claim of strict ports-and-adapters architecture.

**Severity:** moderate.
**Future improvement:** move route-specific persistence queries behind focused
store methods; type the existing seams before adding another database or registry
implementation. Do not introduce a dependency-injection framework solely for style.

## Cohesion

**Evidence and strengths:** application modules are grouped by delivery concern;
healthcare modules express domain concepts, and
[frontend pages](../frontend/src/pages) group user workflows. Frozen research and
application adapters have distinct ownership.

**Partial compliance:** the generic `Store.command` handles predictions and
reviews using branching; [CaseAnalysis](../frontend/src/pages/CaseAnalysis.tsx)
coordinates entry, result, save and rerun state.
These group related operations but increase the number of invariants a reader
must understand together.

**Severity:** moderate as workflows grow.
**Future improvement:** separate command preparation from shared commit logic
and extract stateful UI hooks when changes justify it. Keep common atomic
invariants explicit instead of duplicating transaction code.

## Coupling

**Evidence and strengths:** HTTP clients use versioned envelopes; research
artifacts are consumed through a verified adapter.
[ADR 0008](decisions/0008-application-mlops-contract.md) explains why byte
identity and delivery separation were selected. Its original fixed-input scope
is historical; current manual intake is documented in the HLD and report.

**Partial compliance:** API/schema/store are tightly coupled, response contracts
exist in Python and TypeScript, and deployment scripts encode the approved
topology. Frozen source/runtime bindings intentionally restrict upgrades.
Registry and application database publication also require reconciliation.

**Severity:** moderate; deliberate integrity coupling is justified.
**Future improvement:** retain [contract checks](../frontend/package.json),
centralize repeated deployment constants when a second environment is approved,
and document upgrade/rebinding gates. Do not weaken checks merely to reduce coupling.

## Testability

**Evidence and strengths:** injected clock/fetch/transport collaborators support
deterministic tests. Tests cover
[case workflow](../tests/application/test_case_workflow.py),
[canonicalization](../tests/application/test_case_input.py),
[registry recovery](../tests/application/test_registry.py),
[PostgreSQL repairs](../tests/application/test_repair_postgres.py) and
[deployment rollback](../tests/deployment/test_ci_rollback.py).
[Browser and recovery helpers](../deployment/tests) exercise the real stack.

**Partial compliance:** full application/release tests require approved frozen
artifacts and PostgreSQL. Public pull-request CI runs fewer backend tests than
authorized deployment CI because private frozen fixtures are unavailable.
Mocks and static script tests do not prove a live cloud deployment.

**Severity:** moderate for independent reproduction.
**Future improvement:** keep artifact-free checks easy to run, document fixture
prerequisites and preserve separate labels for local, hosted and historical
evidence. Test new behavior at its actual persistence or network boundary.

## Configuration separation

**Evidence and strengths:** [Settings](../src/aletheia/application/config.py)
validates environment values and uses `SecretStr`; invalid release identity
settings and wildcard CORS are rejected. [Compose](../deployment/compose.yaml)
uses explicit configuration and mounted secret files.
[Cloud entrypoint](../deployment/azure/cloud-entrypoint.sh) adapts secret injection
to the existing runtime.

**Partial compliance:** model pins and cloud resource names are intentionally
specific; some limits remain constants in API/store code. Build-time frontend
flags and runtime backend identity settings require coordinated configuration.

**Severity:** low for one frozen deployment; moderate for additional environments.
**Future improvement:** document coordinated configuration and validate it before
deployment. Parameterize only settings that need supported variation; never
turn integrity checks into optional toggles.

## Error handling

**Evidence and strengths:** [ServiceError](../src/aletheia/application/auth.py)
and [API handlers](../src/aletheia/application/api.py) produce stable, sanitized
error codes. [Client error copy](../frontend/src/api/client.ts) distinguishes
auth, scope, conflict, unavailability and uncertain timeout outcomes.
Transactional audit failures suppress success; retries preserve identity.

**Partial compliance:** errors mix domain/application conditions with HTTP status
codes. Synchronous inference cannot be killed by browser cancellation; deadlines
are checked around work and before commit. CI rollback calls are best effort.

**Severity:** moderate operationally.
**Future improvement:** preserve timeout ambiguity in UI copy, add narrower
internal error categories only when needed, and explicitly verify rollback
readback when deployment management calls fail.

## Observability

**Evidence and strengths:** [API](../src/aletheia/application/api.py) logs request
metadata without payloads, supplies correlation IDs, separates liveness/readiness
and exposes bounded internal counters. Persistent audit events provide decision
history. [Operator marker parser](../deployment/azure/ci-log-marker.py) and
[boundary tests](../tests/deployment/test_ci_private_boundary.py) address real
deployment-observation failures recorded in the report.

**Partial compliance:** counters are process-local and reset on restart;
audit evidence is not a full operational monitoring system. No production
tracing, retained central log destination, drift service or alert/SLO program
is established.

**Severity:** moderate for showcase diagnosis; high before production operation.
**Future improvement:** select privacy-safe aggregate telemetry and bounded
retention under a separate approved cost/privacy design. Do not log inputs or
credentials to compensate for missing observability.

## Security boundaries

**Evidence and strengths:** JWT signature/issuer/audience checks, local
entitlement intersection, resource scope, strict input schemas, pre-load hash
verification and append-only database controls address different trust
boundaries. [Migrations](../migrations/versions),
[release/auth tests](../tests/application/test_release_auth.py),
[private-ingress checks](../deployment/azure/ci-smoke.py) and
[credential scanner](../deployment/azure/ci-secret-scan.py) make those controls
inspectable. Cloud deployment uses OIDC federation; API and MLflow ingress are private.

**Partial compliance:** provisioned identity is not public onboarding.
PostgreSQL retains the approved Azure-services firewall exception. A privileged
database owner can rewrite storage; hashes need a trusted anchor. The backend
image has retained findings with documented dispositions, and immutable runtime
requirements complicate dependency remediation.

**Severity:** moderate within the bounded educational access model; high before
handling sensitive real-world cases or claiming production readiness.
**Future improvement:** separately approve external identity onboarding,
dependency remediation compatible with frozen evidence, monitoring and disaster
recovery requirements. Preserve the full vulnerability inventory and avoid
describing successful scan execution as a clean security result.

## Practical priorities

1. Keep contracts, frozen identities and transaction tests intact while making
   documentation and developer setup easier to follow.
2. Before adding workflows, reduce direct route-to-schema access and separate
   cohesive command preparation from shared atomic persistence.
3. Before adding a second deployment/domain, introduce only the interfaces and
   configuration variation demonstrated necessary by that second implementation.
4. Before production use, address identity operations, dependency findings,
   monitoring, recovery guarantees and real-world model validation under separate
   approval.

These recommendations are advisory, not authorization to advance a milestone.
The [project report](PROJECT_REPORT.md) records actual verification results
and remaining limitations.
