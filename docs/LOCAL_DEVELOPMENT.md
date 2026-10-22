# Local development and verification

A fresh clone contains code, dependency locks, example configuration and tests.
It does **not** contain the ignored approved model/audit bundle, signing keys,
tokens, database passwords or local evidence. Source verification is available
without those files; complete serving requires an authorized frozen bundle.
Do not run training, recalibration or held-out evaluation to fill that gap.

## Verify a fresh clone without model artifacts

Prerequisites: Python 3.12, Node.js 24 or later, npm, Git and network access to
the locked package distributions. Commands below use PowerShell from the
repository root. They describe the source-supported setup; exact checks
from the presentation milestone are recorded in [the project report](PROJECT_REPORT.md).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m ruff check src tests
New-Item -ItemType Directory -Force -Path artifacts | Out-Null
.\.venv\Scripts\python.exe -m pytest tests/unit tests/data -m "not live_data" --basetemp=artifacts/fresh-pytest
Copy-Item frontend/.env.example frontend/.env.local
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run format:check -- --end-of-line auto
npm.cmd --prefix frontend run lint
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
```

Confirm `python --version` reports Python 3.12 before creating the virtual environment.
The locked requirements include the editable build backend, so
`--no-build-isolation` avoids a second unpinned build-tool download.
On Windows, `npm.cmd` bypasses a PowerShell script execution-policy block and
`--end-of-line auto` accommodates Git's CRLF working-tree checkout without
formatting unchanged source. The selected Python tests use generated fixtures. This is a focused verification
path, not the full backend regression. Application tests using the `release`
fixture call `build_release`; database integration also requires a disposable
PostgreSQL test database. Running the whole suite without those prerequisites
does not establish full application correctness. Browser tests additionally
need Playwright browsers and the configured application/session.

`npm.cmd --prefix frontend run dev` starts the UI development server. It does not
create a model, database or authenticated API. The example frontend environment
contains public settings only; public Signup is not implemented.

## Prepare a complete local stack only with approved artifacts

This path requires Docker Engine/Desktop with Linux containers and Compose v2,
plus sufficient memory/disk for Python/MLflow, PostgreSQL and image builds.
Builds fetch pinned bases, locked Python/npm packages and the checksum-verified
SQLite source. Existing Docker resources must be retained.

The operator must first arrange the trusted original artifacts under
`artifacts/healthcare-model-v1/` and `artifacts/healthcare-audit-v1/`.
The release builder checks exact inventories, hashes, source bindings, runtime
versions and dependency pins before accepting the release. See
[`build_release`](../src/aletheia/application/release.py),
[`prepare.py`](../deployment/tests/prepare.py) and the
[approved manifest](../deployment/azure/approved-release-manifest.json).
These are aggregate/model artifacts, not a request for source dataset rows.
No public artifact download is provided. Obtain the approved bundle through
the project operator; do not substitute an arbitrary pickle/joblib file.

The hosted CI workflow has a separate privileged path for recovering verified
fixtures from its existing immutable image. It requires registry access and
is not a public fresh-clone setup. Its line-ending repair helper is designed
for an ephemeral CI checkout; do not run it against the maintained checkout.
If approved byte bindings differ locally, stop for operator review rather than
normalize frozen files or regenerate evidence.

Review a copy of the configuration example in an ignored directory:

```powershell
New-Item -ItemType Directory -Force artifacts/local-setup | Out-Null
Copy-Item deployment/.env.example artifacts/local-setup/config.env.example
```

The example is a configuration template, not a working credential set. The
local test preparer below generates a distinct `artifacts/stage3-local/config.env`
and private files. **Do not create that directory first.** The preparer refuses
an existing directory and writes secrets before validating the frozen release.
If it fails partway, retain the directory and diagnose the missing prerequisite;
do not delete existing state or repeatedly rerun preparation.

For a new, approved local setup only:

```powershell
.\.venv\Scripts\python.exe deployment/tests/prepare.py
$env:VITE_LOCAL_IDENTITY = 'true'
$composeArgs = @(
  'compose', '--env-file', 'artifacts/stage3-local/config.env',
  '-f', 'deployment/compose.yaml', '-f', 'deployment/compose.test.yaml',
  '--profile', 'test', '--profile', 'operator'
)
docker @composeArgs config --quiet
docker @composeArgs build --builder default
docker @composeArgs up -d --wait postgres identity mlflow
docker @composeArgs run --rm migrate
docker @composeArgs run --rm release-stage
docker @composeArgs run --rm release-import operator bootstrap-initial-administrator
docker @composeArgs run --rm release-import operator import-release --tracking-uri http://mlflow:5000
.\.venv\Scripts\python.exe deployment/tests/prepare.py --tokens
docker @composeArgs run --rm release-import operator approve-release --tracking-uri http://mlflow:5000 --token-file /run/secrets/operator_token
docker @composeArgs run --rm release-import operator activate-release --tracking-uri http://mlflow:5000 --token-file /run/secrets/operator_token
docker @composeArgs run --rm release-import operator grant-role --token-file /run/secrets/operator_token --issuer https://identity.test:8443 --subject synthetic-engineer --role engineer
docker @composeArgs run --rm release-import operator grant-role --token-file /run/secrets/operator_token --issuer https://identity.test:8443 --subject synthetic-reviewer --role reviewer
docker @composeArgs up -d --wait api frontend
Invoke-WebRequest http://127.0.0.1:18080/api/v1/health/live
Invoke-WebRequest http://127.0.0.1:18080/api/v1/health/ready
```

Stop at any failed command. The first bootstrap is deliberately one-time.
Migration creates the schema; staging validates/copies the release; import,
approval and activation are explicit state transitions. Starting services
does not grant identities or activate models automatically. The test override
enables backend development identity; `VITE_LOCAL_IDENTITY=true` enables the
matching frontend session screen at build time.

Open `http://127.0.0.1:18080/local-session`. The local operator privately supplies
the engineer token from `artifacts/stage3-local/secrets/engineer_token`; do not
print, commit, screenshot or record it. Use the reviewer identity only for
authorized review/audit actions. Tokens last ten minutes; refresh with
`prepare.py --tokens` and sign in again when needed. The test certificate lasts
two days: an expired identity fixture requires operator-managed renewal, not
TLS bypass. The `synthetic-*` subject names are historical internal fixture
identifiers; manually entered UI cases should be non-sensitive examples.

Expected health status is HTTP 200 after release activation. Readiness failures
can indicate unavailable PostgreSQL or invalid release/pin state; liveness alone
does not establish serving readiness.

## Stop and resume safely

```powershell
docker @composeArgs stop
```

This preserves volumes, images, releases and database state. Resume the same
configured project with `up -d --wait postgres identity mlflow api frontend`;
refresh short-lived tokens as needed. Do not repeat bootstrap/import/activation
as routine startup, use `down -v`, prune Docker data or delete evidence.
Existing projects use their own config paths and project names; do not replace
them with the new-setup defaults above.

Full regression, recovery and security harnesses are operator verification
workflows with additional evidence/fixture prerequisites. The
[deployment architecture](DEPLOYMENT_ARCHITECTURE.md) and
[local Docker recovery guide](LOCAL_DOCKER_CLEANUP.md) describe their
preservation boundaries. They are not required to browse the source or run
the focused artifact-free checks.
