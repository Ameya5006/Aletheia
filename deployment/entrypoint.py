"""Container-only secret loading and explicit command dispatch; never seed state."""

import os
import shutil
import sys
from pathlib import Path


def secret(name):
    path = Path("/run/secrets") / name
    value = path.read_text().strip()
    if not value or "\n" in value:
        raise ValueError("missing or invalid secret file")
    return value


def main():
    command, *arguments = sys.argv[1:]
    if command == "stage-release":
        from aletheia.application.release import VerifiedRelease

        digest = os.environ["APP_RELEASE_SHA256"]
        VerifiedRelease(Path("/source"), digest)
        destination = Path("/release/current")
        if not destination.exists():
            shutil.copytree("/source", destination)
        VerifiedRelease(destination, digest)
        print("verified byte-preserving release staged; no registration or activation")
        return
    if command == "mlflow":
        os.execvp(
            "python",
            [
                "python",
                "-m",
                "mlflow",
                "server",
                "--host",
                "0.0.0.0",
                "--port",
                "5000",
                "--workers",
                "1",
                "--backend-store-uri",
                secret("mlflow_db_url"),
                "--serve-artifacts",
                "--artifacts-destination",
                "/registry/artifacts",
                "--allowed-hosts",
                "mlflow:5000,localhost:5000,127.0.0.1:5000",
            ],
        )
    if command == "migrate":
        os.environ["ALETHEIA_MIGRATION_URL"] = secret("owner_db_url")
        os.execvp("python", ["python", "-m", "alembic", "upgrade", "head"])
    os.environ["DATABASE_URL"] = secret(
        "app_db_url" if command == "api" else "owner_db_url"
    )
    from aletheia.application.config import Settings

    Settings.from_env()  # fail before launch; secret values hidden in validation
    if command == "api":
        os.execvp(
            "python",
            [
                "python",
                "-m",
                "uvicorn",
                "aletheia.application.api:app_factory",
                "--factory",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--workers",
                "1",
                "--no-access-log",
                "--no-proxy-headers",
                "--timeout-graceful-shutdown",
                "15",
            ],
        )
    if command == "operator":
        os.execvp(
            "python", ["python", "-m", "aletheia.application.operator", *arguments]
        )
    raise ValueError("unknown container command")


if __name__ == "__main__":
    main()
