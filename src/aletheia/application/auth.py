"""Access-token verification with a trusted bounded JWKS cache."""

import threading
import time
from dataclasses import dataclass

import httpx
import jwt


class ServiceError(Exception):
    def __init__(self, status: int, code: str):
        self.status, self.code = status, code
        super().__init__(code)


@dataclass(frozen=True)
class Identity:
    issuer: str
    sub: str
    roles: frozenset[str]


class TokenVerifier:
    def __init__(self, settings, fetch=None, clock=time.time):
        self.settings, self.clock = settings, clock
        self.fetch = fetch or self._fetch
        self.lock = threading.Lock()
        self.keys, self.fetched, self.last_attempt = {}, 0.0, 0.0

    def _fetch(self):
        with httpx.Client(
            timeout=self.settings.jwks_timeout_seconds,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            response = client.get(self.settings.oidc_jwks_uri)
            response.raise_for_status()
            if len(response.content) > 65536:
                raise ValueError("JWKS too large")
            return response.json()

    def key(self, kid):
        with self.lock:
            now = self.clock()
            fresh = now - self.fetched < self.settings.jwks_cache_seconds
            if fresh and kid in self.keys:
                return self.keys[kid]
            if now - self.last_attempt < 1:
                raise ServiceError(
                    401 if fresh else 503,
                    "invalid_token" if fresh else "identity_unavailable",
                )
            self.last_attempt = now
            try:
                result = self.fetch()
                if not isinstance(result["keys"], list) or len(result["keys"]) > 32:
                    raise ValueError("invalid JWKS")
                keys = {}
                for item in result["keys"]:
                    if (
                        item.get("kty") != "RSA"
                        or item.get("use", "sig") != "sig"
                        or item.get("alg", "RS256") != "RS256"
                    ):
                        continue
                    key_id = item["kid"]
                    if key_id in keys:
                        raise ValueError("duplicate key")
                    parsed = jwt.PyJWK.from_dict(item, algorithm="RS256").key
                    if parsed.key_size < 2048:
                        raise ValueError("weak key")
                    keys[key_id] = parsed
                self.keys, self.fetched = keys, now
            except (ValueError, KeyError, TypeError, httpx.HTTPError) as exc:
                raise ServiceError(503, "identity_unavailable") from exc
            if kid not in self.keys:
                raise ServiceError(401, "invalid_token")
            return self.keys[kid]

    def ready(self):
        return (
            bool(self.keys)
            and self.clock() - self.fetched < self.settings.jwks_cache_seconds
        )

    def verify(self, token: str) -> Identity:
        try:
            if len(token) > 8192:
                raise ValueError("token too long")
            header = jwt.get_unverified_header(token)
            if (
                header.get("alg") != "RS256"
                or header.get("typ") not in {"at+jwt", "JWT"}
                or "jku" in header
                or "jwk" in header
            ):
                raise ValueError("invalid header")
            claims = jwt.decode(
                token,
                self.key(header["kid"]),
                algorithms=["RS256"],
                audience=self.settings.oidc_audience,
                issuer=self.settings.oidc_issuer,
                leeway=self.settings.clock_skew_seconds,
                options={
                    "require": ["iss", "sub", "aud", "exp", "iat", "roles", "token_use"]
                },
            )
            if claims["token_use"] != "access" or not isinstance(claims["roles"], list):
                raise ValueError("access-token profile required")
            if any(type(claims[k]) is not int for k in ("exp", "iat")):
                raise ValueError("integer timestamps required")
            if (
                not 0
                < claims["exp"] - claims["iat"]
                <= self.settings.oidc_max_token_lifetime_seconds
            ):
                raise ValueError("excess token lifetime")
            if (
                not claims["sub"]
                or len(claims["sub"]) > 255
                or not all(isinstance(r, str) for r in claims["roles"])
            ):
                raise ValueError("invalid subject/roles")
            return Identity(
                claims["iss"],
                claims["sub"],
                frozenset(claims["roles"]) & {"engineer", "reviewer", "administrator"},
            )
        except (jwt.PyJWTError, ValueError, KeyError, TypeError) as exc:
            raise ServiceError(401, "invalid_token") from exc
