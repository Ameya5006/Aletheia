# Local Docker cleanup dry run — 2026-10-16

**Inventory only. No deletion is authorized or executed.** The exact read-only container, image and volume names/statuses are retained in ignored `artifacts/azure-preflight/docker-inventory.json`.

| Item | Observed | Approximate storage context |
|---|---:|---|
| Aletheia containers | 31 total, 27 exited, 4 running | Container writable layers total 532.5 kB across **all** Docker containers; 397.3 kB globally reclaimable |
| Aletheia image tags | 7 | Docker reports 608.4 MB globally reclaimable images; shared layers mean tagged image sizes cannot be added |
| Aletheia-named volumes | 30 | Docker reports 2.906 GB globally reclaimable volumes, not an Aletheia-only estimate |
| Build cache | 119 records | 4.801 GB globally reclaimable; attribution to this project is unknown |

The stopped Aletheia containers include the interactive frontend, MLflow, PostgreSQL, identity and regression PostgreSQL containers; Stage 3 test/restore frontend, MLflow, PostgreSQL, identity and regression containers. Four API containers are running and healthy. The seven Aletheia image tags are the interactive frontend (two), interactive backend, Stage 3 regression, Stage 3 backend, Stage 3 PostgreSQL and Stage 3 frontend. The 30 named volumes include `pgdata`, `registry`, `release`, `state` and regression data for interactive, test, repair and restore stacks. The ignored JSON inventory has each exact name. Global reclaimable figures overlap and are **not** a safe deletion or savings estimate for Aletheia alone.

Preserve all local containers, images, volumes, repository, `.venv`, Stage 3 and interactive evidence, protected frozen model/audit artifacts and the Git stash. Before any later exact deletion list, make and test a reversible backup of every selected PostgreSQL data volume, MLflow registry volume, release/state volume and ignored verification artifact; record image digests/tags and restore instructions. Cleanup remains contingent on supervisor acceptance, cloud persistence/recovery proof, user commit/push, off-laptop evidence backup and the user's explicit approval of an exact list.
