import hashlib
import hmac
import json
import os
import secrets
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode


_TOKEN_LIFETIME_SECONDS = 12 * 60 * 60


def _encode(value: bytes) -> str:
    return urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    encoded = value.encode("ascii")
    return urlsafe_b64decode(encoded + b"=" * (-len(encoded) % 4))


def _secret_key() -> bytes:
    secret = os.getenv("JWT_SECRET_KEY", "")
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be configured with at least 32 bytes")
    return secret.encode("utf-8")


def validate_token_configuration() -> None:
    _secret_key()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        310_000,
    )
    return f"{salt.hex()}:{password_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, expected_hash = stored_hash.split(":", maxsplit=1)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            310_000,
        ).hex()
    except (AttributeError, TypeError, ValueError):
        return False
    return hmac.compare_digest(actual_hash, expected_hash)


def create_access_token(email: str) -> str:
    header = _encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _encode(
        json.dumps(
            {"sub": email, "exp": int(time.time()) + _TOKEN_LIFETIME_SECONDS},
            separators=(",", ":"),
        ).encode("utf-8")
    )
    signing_input = f"{header}.{payload}"
    signature = hmac.new(_secret_key(), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_encode(signature)}"


def read_access_token(token: str) -> str:
    try:
        header, payload, provided_signature = token.split(".")
        claims_header = json.loads(_decode(header))
        if claims_header != {"alg": "HS256", "typ": "JWT"}:
            raise ValueError("Invalid access token header")

        signing_input = f"{header}.{payload}"
        expected_signature = _encode(
            hmac.new(_secret_key(), signing_input.encode("ascii"), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(provided_signature, expected_signature):
            raise ValueError("Invalid access token signature")

        claims = json.loads(_decode(payload))
        email = claims["sub"]
        expiration = claims["exp"]
        if not isinstance(email, str) or isinstance(expiration, bool) or not isinstance(expiration, int):
            raise ValueError("Invalid access token claims")
        if expiration <= int(time.time()):
            raise ValueError("Expired access token")
        return email
    except (AttributeError, KeyError, TypeError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError("Invalid access token") from error
