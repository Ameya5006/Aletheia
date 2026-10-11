"""Explicit local operator CLI. No public administrative write endpoint."""

import argparse
from pathlib import Path

from .auth import TokenVerifier
from .config import Settings
from .release import VerifiedRelease, build_release
from .store import Store


def main():
    parser = argparse.ArgumentParser(description="Aletheia backend operator")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build-release")
    build.add_argument("--destination", type=Path, required=True)
    sub.add_parser("bootstrap-initial-administrator")
    registry = sub.add_parser("import-release")
    registry.add_argument("--tracking-uri", required=True)
    approve = sub.add_parser("approve-release")
    approve.add_argument("--tracking-uri", required=True)
    approve.add_argument("--token-file", type=Path, required=True)
    for name in ("activate-release", "rollback-release", "revoke-release"):
        lifecycle = sub.add_parser(name)
        lifecycle.add_argument("--tracking-uri", required=True)
        lifecycle.add_argument("--token-file", type=Path, required=True)
    grant = sub.add_parser("grant-role")
    grant.add_argument("--token-file", type=Path, required=True)
    grant.add_argument("--issuer", required=True)
    grant.add_argument("--subject", required=True)
    grant.add_argument(
        "--role", choices=["engineer", "reviewer", "administrator"], required=True
    )
    revoke = sub.add_parser("revoke-role")
    disable = sub.add_parser("disable-subject")
    for command in (revoke, disable):
        command.add_argument("--token-file", type=Path, required=True)
        command.add_argument("--issuer", required=True)
        command.add_argument("--subject", required=True)
    revoke.add_argument(
        "--role", choices=["engineer", "reviewer", "administrator"], required=True
    )
    args = parser.parse_args()
    if args.command == "build-release":
        print(build_release(Path.cwd(), args.destination))
        return
    settings = Settings.from_env()
    store = Store(
        settings.database_url.get_secret_value(), settings.deployment_pin_path
    )
    if args.command == "bootstrap-initial-administrator":
        if (
            settings.bootstrap_oidc_issuer != settings.oidc_issuer
            or settings.bootstrap_oidc_sub is None
        ):
            parser.error("configured bootstrap issuer/subject required")
        store.bootstrap(
            settings.bootstrap_oidc_issuer,
            settings.bootstrap_oidc_sub.get_secret_value(),
        )
        print("initial administrator bootstrapped and audited")
        return
    if args.command in {"grant-role", "revoke-role", "disable-subject"}:
        identity = TokenVerifier(settings).verify(args.token_file.read_text().strip())
        if args.issuer != settings.oidc_issuer:
            parser.error("issuer mismatch")
        if args.command == "disable-subject":
            store.disable_subject(identity, args.issuer, args.subject)
        elif args.command == "revoke-role":
            store.revoke_role(identity, args.issuer, args.subject, args.role)
        else:
            store.grant(identity, args.issuer, args.subject, args.role)
        print("entitlement change committed and audited")
        return
    release = VerifiedRelease(settings.release_root, settings.release_sha256)
    from .registry import Registry

    registry = Registry(args.tracking_uri, endpoint=settings.mlflow_endpoint)
    result = registry.import_release(release)
    if args.command == "approve-release":
        identity = TokenVerifier(settings).verify(args.token_file.read_text().strip())
        if result["version"] != settings.model_version:
            parser.error("explicit serving version mismatch")
        store.register(identity, release, result)
        registry.publish_approval(store, identity, release, result)
    elif args.command in {"activate-release", "rollback-release", "revoke-release"}:
        identity = TokenVerifier(settings).verify(args.token_file.read_text().strip())
        if result["version"] != settings.model_version:
            parser.error("explicit serving version mismatch")
        action = {
            "activate-release": "activated",
            "rollback-release": "rolled_back",
            "revoke-release": "revoked",
        }[args.command]
        registry.publish_lifecycle(store, identity, release, result, action)
    print(
        f"verified {result['name']} version {result['version']} "
        f"release {release.digest}"
    )


if __name__ == "__main__":
    main()
