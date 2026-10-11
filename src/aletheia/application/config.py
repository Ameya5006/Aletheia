"""Explicit environment configuration; secrets never enter repr or responses."""

import re
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator


class TrustedMLflowEndpoint(BaseModel):
    """Operator configuration, never supplied by an HTTP caller."""

    model_config = ConfigDict(extra="forbid")
    scheme: Literal["http", "https"] = "http"
    hostname: str = "127.0.0.1"
    port: int = Field(default=5000, ge=1, le=65535)

    @model_validator(mode="after")
    def private_host(self):
        if self.hostname not in {"localhost", "127.0.0.1", "::1"} and (
            not re.fullmatch(r"[a-z][a-z0-9-]{0,62}", self.hostname)
            or self.hostname in {"localhost", "com", "org", "net"}
        ):
            raise ValueError("exact loopback or configured private hostname required")
        return self

    @property
    def uri(self):
        host = f"[{self.hostname}]" if ":" in self.hostname else self.hostname
        return f"{self.scheme}://{host}:{self.port}"

    def validate_uri(self, value):
        parsed = urlsplit(value)
        if (
            parsed.scheme != self.scheme
            or parsed.hostname != self.hostname
            or parsed.port != self.port
            or parsed.username
            or parsed.password
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("unconfigured MLflow endpoint")
        return self.uri


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    app_env: Literal["development", "test", "release"]
    database_url: SecretStr
    release_root: Path
    release_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_version: str = Field(pattern=r"^[1-9][0-9]*$")
    oidc_issuer: str
    oidc_audience: str = Field(min_length=1)
    oidc_jwks_uri: str
    oidc_max_token_lifetime_seconds: int = Field(gt=0, le=86400)
    provider_token_lifetime_seconds: int = Field(gt=0, le=86400)
    development_identity: bool = False
    clock_skew_seconds: int = Field(default=60, ge=0, le=60)
    jwks_cache_seconds: int = Field(default=900, gt=0, le=900)
    jwks_timeout_seconds: float = Field(default=2, gt=0, le=2)
    cors_origins: list[str] = Field(default_factory=list)
    bootstrap_oidc_issuer: str | None = None
    bootstrap_oidc_sub: SecretStr | None = None
    mlflow_endpoint: TrustedMLflowEndpoint = Field(
        default_factory=TrustedMLflowEndpoint
    )
    deployment_pin_path: Path = Path("artifacts/backend-deployment-pin.json")
    operation_timeout_seconds: float = Field(default=10, gt=0, le=10)

    @model_validator(mode="after")
    def boundaries(self):
        if not self.database_url.get_secret_value().startswith("postgresql+psycopg://"):
            raise ValueError("PostgreSQL psycopg URL required")
        for value in (self.oidc_issuer, self.oidc_jwks_uri):
            url = urlsplit(value)
            if (
                url.scheme != "https"
                or not url.hostname
                or url.username
                or url.fragment
            ):
                raise ValueError("trusted HTTPS identity configuration required")
        if self.app_env == "release" and (
            self.development_identity
            or urlsplit(self.oidc_issuer).hostname in {"localhost", "127.0.0.1"}
            or urlsplit(self.oidc_issuer).hostname.endswith((".test", ".invalid"))
        ):
            raise ValueError("development identity forbidden in release")
        if self.provider_token_lifetime_seconds > self.oidc_max_token_lifetime_seconds:
            raise ValueError("provider token lifetime exceeds configured maximum")
        if "*" in self.cors_origins:
            raise ValueError("explicit CORS origins required")
        return self

    @classmethod
    def from_env(cls):
        import json
        import os

        mapping = {
            "release_root": "APP_RELEASE_ROOT",
            "release_sha256": "APP_RELEASE_SHA256",
            "model_version": "APP_MODEL_VERSION",
        }
        values = {}
        for name in cls.model_fields:
            key = mapping.get(name, name.upper())
            if key in os.environ:
                values[name] = os.environ[key]
        if "cors_origins" in values:
            values["cors_origins"] = json.loads(values["cors_origins"])
        if "mlflow_endpoint" in values:
            values["mlflow_endpoint"] = json.loads(values["mlflow_endpoint"])
        return cls.model_validate(values)
