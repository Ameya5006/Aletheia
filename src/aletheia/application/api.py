"""Versioned synthetic-only FastAPI adapter. No HTTP operator bootstrap."""

import asyncio
import logging
import threading
import time
import uuid
from collections import defaultdict, deque
from typing import Literal

import sqlalchemy as sa
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, JsonValue
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException

from . import schema as s
from .auth import ServiceError, TokenVerifier
from .config import Settings
from .release import CASE, VerifiedRelease, safe_file, sha
from .store import Store, row

logger = logging.getLogger("aletheia.http")


class Envelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["application-v1"]
    request_id: uuid.UUID
    data: JsonValue
    evidence: dict[str, JsonValue] | None = None


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["application-v1"]
    request_id: uuid.UUID
    error: ErrorDetail


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal["application-v1"]
    case_id: Literal["synthetic-discharge-v1"]
    model_version: str = Field(pattern=r"^[1-9][0-9]*$")


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal["application-v1"]
    decision: Literal["acknowledged", "needs_investigation", "dismissed_demo"]
    reason_code: Literal["evidence_reviewed", "limitations_noted", "identity_issue"]
    expected_revision: int = Field(ge=0)


def valid_uuid(value):
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ServiceError(400, "invalid_id") from exc


def create_app(settings: Settings, release=None, store=None, verifier=None):
    # Invalid pinned bytes cause explicit startup failure, never fallback.
    release = release or VerifiedRelease(settings.release_root, settings.release_sha256)
    store = store or Store(
        settings.database_url.get_secret_value(), settings.deployment_pin_path
    )
    verifier = verifier or TokenVerifier(settings)
    app = FastAPI(
        responses={
            code: {"model": ErrorEnvelope}
            for code in (400, 401, 403, 404, 409, 413, 415, 422, 429, 503, 504, 500)
        }
        | {200: {"model": Envelope}, 201: {"model": Envelope}},
        docs_url="/docs" if settings.app_env != "release" else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.app_env != "release" else None,
    )
    app.state.store, app.state.release, app.state.verifier = store, release, verifier
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=[
            "Authorization",
            "Idempotency-Key",
            "Content-Type",
            "X-Request-ID",
        ],
    )
    limit_lock = threading.Lock()
    rates = defaultdict(deque)
    concurrency = threading.BoundedSemaphore(2)
    metrics = {"requests": 0, "errors": 0, "audit_successes": 0, "audit_failures": 0}

    def error(request, status, code):
        headers = {"WWW-Authenticate": "Bearer"} if status == 401 else {}
        if status == 429:
            headers["Retry-After"] = "60"
        return JSONResponse(
            {
                "schema_version": "application-v1",
                "request_id": str(request.state.request_id),
                "error": {"code": code, "message": code.replace("_", " ")},
            },
            status_code=status,
            headers=headers,
        )

    def response(
        request, data, status=200, source="precomputed_research", health=False
    ):
        result = {
            "schema_version": "application-v1",
            "request_id": str(request.state.request_id),
            "data": data,
        }
        if not health:
            result["evidence"] = {
                "domain": "healthcare",
                "model_version": settings.model_version,
                "model_sha256": release.protocol["identity"]["model_sha256"],
                "audit_protocol_sha256": release.protocol["protocol_sha256"],
                "audit_results_sha256": release.manifest["files"][
                    "artifacts/healthcare-audit-v1/results.json"
                ],
                "research_revision": release.manifest["research_revision"],
                "educational_only": True,
                "not_medical_advice": True,
                "source": source,
                "limitations": release.audit["limitations"],
            }
        # Validate the common response contract, while preserving saved JSON nulls.
        result = Envelope.model_validate(jsonable_encoder(result)).model_dump(
            mode="json", exclude_none=True
        )
        return JSONResponse(result, status_code=status)

    def rate(key, maximum):
        with limit_lock:
            now = time.monotonic()
            entries = rates[key]
            while entries and entries[0] < now - 60:
                entries.popleft()
            if len(entries) >= maximum:
                raise ServiceError(429, "rate_limited")
            entries.append(now)
            # Bound retained IP/subject counters as well as individual deques.
            if len(rates) > 4096:
                for old in list(rates):
                    if not rates[old] or rates[old][-1] < now - 60:
                        rates.pop(old, None)
                if len(rates) > 4096:
                    rates.pop(key, None)
                    raise ServiceError(429, "rate_limited")

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        begin = time.monotonic()
        try:
            request.state.request_id = valid_uuid(request.headers.get("X-Request-ID"))
        except ServiceError:
            request.state.request_id = uuid.uuid4()
        request.state.deadline = begin + settings.operation_timeout_seconds

        async def bounded_dispatch():
            if request.method == "POST":
                if (
                    request.headers.get("content-type", "").split(";")[0]
                    != "application/json"
                ):
                    raise ServiceError(415, "unsupported_media_type")
                chunks, size = [], 0
                async with asyncio.timeout(settings.operation_timeout_seconds):
                    async for chunk in request.stream():
                        size += len(chunk)
                        if size > 4096:
                            raise ServiceError(413, "body_too_large")
                        chunks.append(chunk)
                request._body = b"".join(chunks)
            if request.method == "GET":
                rate(
                    ("public", request.client.host if request.client else "unknown"), 60
                )
            return await call_next(request)

        try:
            # Await worker completion: cancellation cannot terminate synchronous
            # inference or a PostgreSQL commit. Worker deadlines roll back writes.
            result = await bounded_dispatch()
        except TimeoutError:
            result = error(request, 504, "deadline_exceeded")
        except ServiceError as exc:
            result = error(request, exc.status, exc.code)
        except Exception:
            result = error(request, 500, "internal_error")
        result.headers["X-Request-ID"] = str(request.state.request_id)
        result.headers["X-Content-Type-Options"] = "nosniff"
        result.headers["Referrer-Policy"] = "no-referrer"
        result.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'"
        )
        metrics["requests"] += 1
        metrics["errors"] += int(result.status_code >= 400)
        route = request.scope.get("route")
        logger.info(
            "request",
            extra={
                "request_id": str(request.state.request_id),
                "route_template": route.path if route else "unmatched",
                "method": request.method,
                "status": result.status_code,
                "duration_seconds": time.monotonic() - begin,
                "model_version": settings.model_version,
            },
        )
        return result

    @app.exception_handler(ServiceError)
    async def service_error(request, exc):
        return error(request, exc.status, exc.code)

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, exc):
        return error(request, 503, "persistence_unavailable")

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return error(request, 422, "schema_rejected")

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return error(
            request,
            exc.status_code,
            "not_found" if exc.status_code == 404 else "http_error",
        )

    def private(request, required=()):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise ServiceError(401, "invalid_token")
        identity = verifier.verify(header[7:])
        with store.engine.begin() as conn:
            actor, roles = store.authorize(conn, identity, required)
        return identity, actor, roles

    def ready():
        try:
            if (
                sha(safe_file(release.root, "release.json").read_bytes())
                != release.digest
            ):
                return False
            for name, digest in release.manifest["files"].items():
                if sha(safe_file(release.root, name).read_bytes()) != digest:
                    return False
            if not verifier.ready():
                try:
                    verifier.key("readiness-refresh")
                except ServiceError:
                    pass
            with store.engine.begin() as conn:
                store.approved(conn, settings.model_version, release.digest)
                return store.migrated(conn) and verifier.ready()
        except (SQLAlchemyError, ValueError, ServiceError):
            return False

    @app.get("/api/v1/health/live")
    def live(request: Request):
        return response(request, {"status": "alive"}, health=True)

    @app.get("/api/v1/health/ready")
    def readiness(request: Request):
        available = ready()
        return response(
            request,
            {"status": "ready" if available else "unready"},
            200 if available else 503,
            health=True,
        )

    @app.get("/api/v1/models/current")
    def current(request: Request):
        available = ready()
        return response(
            request,
            {
                "domain": "healthcare",
                "target": "readmitted_30d",
                "family": "histogram",
                "calibration": "sigmoid",
                "feature_policy_version": "healthcare-feature-v1",
                "threshold": 0.5,
                "approval_status": "approved" if available else "unavailable",
                "serving_available": available,
            },
        )

    @app.get("/api/v1/models/current/card")
    def card(request: Request):
        raw = safe_file(
            release.root, "docs/model_cards/healthcare_readmission_v1.md"
        ).read_bytes()
        return response(
            request,
            {
                "content_markdown": raw.decode("utf-8"),
                "card_sha256": sha(raw),
                "intended_use": "educational research",
                "limitations": release.audit["limitations"],
            },
        )

    @app.get("/api/v1/demo/cases")
    def cases(request: Request):
        return response(
            request, [{"id": CASE, "source": "synthetic", "features": release.case}]
        )

    def project(section):
        def endpoint(request: Request):
            return response(request, release.audit[section])

        return endpoint

    for path, section in (
        ("/explanations/global", "global"),
        (f"/explanations/local/{CASE}", "synthetic_local"),
        ("/audits/stability", "stability"),
        ("/audits/subgroups", "fairness"),
        ("/counterfactuals/feasibility", "counterfactual"),
    ):
        app.add_api_route(
            "/api/v1" + path, project(section), methods=["GET"], name=section
        )

    def present(value, review=False):
        out = {
            k: v
            for k, v in value.items()
            if k not in {"actor_id", "reviewer_id", "model_version_id"}
        }
        out["review_id" if review else "prediction_id"] = out.pop("id")
        out["event_id"] = out.pop("audit_event_id")
        if not review:
            out["positive_class"] = 1
            out["explanation_ref"] = out.pop("explanation_ref_id")
        return out

    @app.post("/api/v1/predictions", status_code=201)
    def predict(body: PredictionRequest, request: Request):
        identity, actor, _ = private(request, {"engineer", "reviewer", "administrator"})
        key = valid_uuid(request.headers.get("Idempotency-Key"))
        if body.model_version != settings.model_version:
            raise ServiceError(409, "version_conflict")
        rate(("prediction", actor), 10)
        if not ready():
            raise ServiceError(503, "service_unready")
        if not concurrency.acquire(blocking=False):
            raise ServiceError(429, "concurrency_limited")
        try:
            result = store.command(
                identity,
                body.model_dump(),
                key,
                request.state.request_id,
                settings.model_version,
                release,
                deadline=request.state.deadline,
            )
            metrics["audit_successes"] += 1
        except Exception:
            metrics["audit_failures"] += 1
            raise
        finally:
            concurrency.release()
        return response(request, present(result), 201, "synthetic_inference")

    @app.get("/api/v1/predictions/{prediction_id}")
    def prediction(prediction_id: str, request: Request):
        identity, _, _ = private(request)
        with store.engine.begin() as conn:
            value = store.accessible(conn, identity, valid_uuid(prediction_id))
        return response(request, present(value), source="synthetic_inference")

    @app.post("/api/v1/predictions/{prediction_id}/reviews", status_code=201)
    def review(prediction_id: str, body: ReviewRequest, request: Request):
        identity, actor, _ = private(request, {"reviewer"})
        rate(("review", actor), 20)
        result = store.command(
            identity,
            body.model_dump(),
            valid_uuid(request.headers.get("Idempotency-Key")),
            request.state.request_id,
            settings.model_version,
            release,
            valid_uuid(prediction_id),
            request.state.deadline,
        )
        return response(request, present(result, True), 201, "synthetic_inference")

    @app.get("/api/v1/predictions/{prediction_id}/reviews")
    def history(prediction_id: str, request: Request):
        identity, _, _ = private(request)
        pid = valid_uuid(prediction_id)
        with store.engine.begin() as conn:
            store.accessible(conn, identity, pid)
            values = conn.execute(
                sa.select(s.reviews)
                .where(s.reviews.c.prediction_id == pid)
                .order_by(s.reviews.c.revision.desc())
            ).mappings()
            return response(
                request,
                {
                    "items": [present(dict(v), True) for v in values],
                    "next_cursor": None,
                },
            )

    @app.get("/api/v1/audit-events")
    def audit_list(request: Request, cursor: str | None = None, limit: int = 20):
        identity, _, _ = private(request)
        if not 1 <= limit <= 100 or (
            cursor is not None and (not cursor.isdecimal() or len(cursor) > 18)
        ):
            raise ServiceError(400, "invalid_cursor")
        with store.engine.begin() as conn:
            query = store.audit_query(conn, identity)
            if cursor:
                query = query.where(s.events.c.sequence < int(cursor))
            values = list(
                conn.execute(
                    query.order_by(s.events.c.sequence.desc()).limit(limit + 1)
                ).mappings()
            )
            return response(
                request,
                {
                    "items": [
                        {k: v for k, v in e.items() if k != "actor_id"}
                        for e in values[:limit]
                    ],
                    "next_cursor": str(values[limit - 1]["sequence"])
                    if len(values) > limit
                    else None,
                },
            )

    @app.get("/api/v1/audit-events/{event_id}")
    def audit_detail(event_id: str, request: Request):
        identity, _, _ = private(request)
        with store.engine.begin() as conn:
            value = row(
                conn,
                store.audit_query(conn, identity).where(
                    s.events.c.id == valid_uuid(event_id)
                ),
            )
            if not value:
                raise ServiceError(404, "not_found")
            value.pop("actor_id")
            return response(request, value)

    @app.get("/api/v1/admin/model-versions")
    def model_list(request: Request, cursor: str | None = None, limit: int = 20):
        private(request, {"administrator"})
        if not 1 <= limit <= 100 or (cursor is not None and not cursor.isdecimal()):
            raise ServiceError(400, "invalid_cursor")
        with store.engine.begin() as conn:
            query = sa.select(s.models).order_by(
                sa.cast(s.models.c.version, sa.BigInteger).desc()
            )
            if cursor:
                query = query.where(
                    sa.cast(s.models.c.version, sa.BigInteger) < int(cursor)
                )
            values = list(conn.execute(query.limit(limit + 1)).mappings())
            return response(
                request,
                {
                    "items": [dict(v) for v in values[:limit]],
                    "next_cursor": values[limit - 1]["version"]
                    if len(values) > limit
                    else None,
                },
            )

    @app.get("/api/v1/admin/model-versions/{version}")
    def model_detail(version: str, request: Request):
        private(request, {"administrator"})
        with store.engine.begin() as conn:
            value = row(conn, sa.select(s.models).where(s.models.c.version == version))
            if not value:
                raise ServiceError(404, "not_found")
            value["release_events"] = [
                dict(x)
                for x in conn.execute(
                    sa.select(s.releases).where(
                        s.releases.c.model_version_id == value["id"]
                    )
                ).mappings()
            ]
            for e in value["release_events"]:
                e.pop("actor_id")
            return response(request, value)

    @app.get("/internal/metrics", include_in_schema=False)
    def internal_metrics(request: Request):
        private(request, {"administrator"})
        if not request.client or request.client.host not in {
            "127.0.0.1",
            "::1",
            "testclient",
        }:
            raise ServiceError(404, "not_found")
        return response(request, metrics, health=True)

    if settings.app_env == "release":

        @app.get("/openapi.json", include_in_schema=False)
        def protected_schema(request: Request):
            private(request, {"engineer", "administrator"})
            return JSONResponse(app.openapi())

    return app


def app_factory():
    return create_app(Settings.from_env())
