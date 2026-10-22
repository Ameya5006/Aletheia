# Local Docker cleanup and recovery

Use this guide before reclaiming local Docker storage. Review these command
examples against the explicitly selected local project before running them.
Never use global reclaimable figures as a
project-specific deletion or savings estimate: images share layers and Docker
reports storage across projects.

## Back up before removing resources

Keep backups in an ignored directory such as `artifacts/local-backups/`, with
a separate protected copy outside the laptop. Existing recovery evidence is
under `artifacts/azure-preflight/` and `artifacts/stage3-verification/`; preserve
it, the original frozen model/audit bundles, configuration, private signing
material, repository, Python environment and Git stash. Do not publish dumps,
tokens, private keys or raw evidence.

Record the exact Compose project, container and volume names, image tags and
digests, migration head and active release identity. Review the selected
project's existing environment file and Compose overrides; do not replace them
with new-setup defaults. See [local setup](LOCAL_DEVELOPMENT.md).

```powershell
docker compose ls
docker ps -a
docker image ls --digests
docker volume ls
docker system df
```

Stop frontend, API and MLflow writers before taking a consistent backup.
Keep PostgreSQL running while dumping both `aletheia_app` and
`aletheia_mlflow`. Preserve the `registry`, `release` and `state` volumes
together with the two database dumps. The registry contains MLflow artifacts;
database metadata alone cannot restore the model. A raw PostgreSQL volume copy
requires a stopped database and compatible server version.

For a reviewed Compose argument array `$composeArgs` and an existing private
`$backupDir`, dump inside the container, then copy the binary file. Repeat for
the MLflow database with its own filename. Do not pipe binary dumps through
PowerShell text redirection.

```powershell
docker @composeArgs stop frontend api mlflow
docker @composeArgs exec -T postgres pg_dump -U postgres -Fc -f /tmp/aletheia_app.dump aletheia_app
docker @composeArgs cp postgres:/tmp/aletheia_app.dump "$backupDir/aletheia_app.dump"
docker @composeArgs exec -T postgres pg_dump -U postgres -Fc -f /tmp/aletheia_mlflow.dump aletheia_mlflow
docker @composeArgs cp postgres:/tmp/aletheia_mlflow.dump "$backupDir/aletheia_mlflow.dump"
Get-FileHash -Algorithm SHA256 "$backupDir/aletheia_app.dump", "$backupDir/aletheia_mlflow.dump"
```

Archive the three associated volumes before restarting writers. Preserve file
bytes and ordinary permission bits; reject links, devices and unsafe archive
paths during extraction. The existing [restore harness](../deployment/tests/restore.py)
implements quiesced dumps, volume archives, SHA-256 checks and isolated restore.
It is specific to its configured test project and needs its fixture/evidence
prerequisites; inspect it before use rather than applying it to an arbitrary
existing stack. Hash the archives and test restoration before any deletion.

## Select cleanup precisely

`docker @composeArgs stop` preserves containers, images and volumes. If removal
is separately intended, inspect exact resource names and remove only the
selected backed-up resources. Avoid `docker system prune`, volume pruning and
`down -v`: stopped containers and apparently unused volumes can contain the
only recoverable state. Preserve source images until both rebuilding and
restoration have succeeded. No Docker deletion is performed by this guide.

## Rebuild and restore

With trusted model/audit artifacts and private configuration available, rebuild
the selected project's images using its original Compose files and build-time
settings:

```powershell
docker @composeArgs build --builder default
```

Rebuilding images does not restore PostgreSQL or MLflow data. Restore into a
new, uniquely named project with empty volumes and a separate loopback port;
refuse pre-existing destination resources. Start PostgreSQL and the required
identity service first. Create the expected databases and roles through the
matching initialization configuration. For a reviewed destination argument
array `$restoreArgs`, repeat these commands for both database dumps:

```powershell
docker @restoreArgs cp "$backupDir/aletheia_app.dump" postgres:/tmp/aletheia_app.dump
docker @restoreArgs exec -T postgres pg_restore -U postgres --exit-on-error -d aletheia_app /tmp/aletheia_app.dump
```

Restore the matching `registry`, `release` and `state` archives before starting
MLflow/API/frontend. Preserve the deployment pin and original release hashes;
do not regenerate a model, bootstrap an existing administrator or repeat release
activation to disguise missing state. Verify archive file hashes and permission
bits, not whole tar bytes: extraction can change archive metadata.

## Verify before discarding the originals

Confirm the expected Alembic migration head, active approved release, MLflow
model metadata and retrievable artifacts. Check liveness and readiness, then
authenticate with a fresh short-lived local identity and reopen a known saved
prediction and its audit link. Compare the stored result and model/evidence
identities to the backup. A restored stack starting successfully is insufficient.
Keep the source stack and off-laptop backups until these checks pass. Historical
verified restore outcomes and limitations are in the [project report](PROJECT_REPORT.md);
cloud recovery boundaries are in [deployment architecture](DEPLOYMENT_ARCHITECTURE.md).
