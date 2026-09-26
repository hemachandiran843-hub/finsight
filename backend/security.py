"""Auth helpers: PBKDF2 password hashing + HMAC-signed tokens + RBAC."""
import base64
import hashlib
import hmac
import json
import time

from config import token_secret, TOKEN_TTL_SECONDS


def hash_password(password: str, salt: str | None = None) -> str:
    if salt is None:
        salt = base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest()).decode()[:16]
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode(), 120_000)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode(), 120_000)
    return hmac.compare_digest(dk.hex(), stored.split("$", 1)[1])


def _sign(payload: bytes) -> str:
    return hmac.new(token_secret(), payload, hashlib.sha256).hexdigest()


def issue_token(email: str, name: str, role: str) -> str:
    payload = json.dumps({
        "email": email, "name": name, "role": role, "exp": time.time() + TOKEN_TTL_SECONDS,
    }, separators=(",", ":")).encode()
    b64 = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return f"{b64}.{_sign(payload)}"


def verify_token(token: str) -> dict | None:
    try:
        b64, sig = token.rsplit(".", 1)
        payload = base64.urlsafe_b64decode(b64 + "=" * (-len(b64) % 4))
        if not hmac.compare_digest(_sign(payload), sig):
            return None
        data = json.loads(payload)
        if data.get("exp", 0) < time.time():
            return None
        return data
    except Exception:
        return None


# ---------------------------------------------------------------- RBAC
PERMISSIONS = {
    "ceo":            {"dashboard", "ask", "evidence", "trends"},
    "credit_analyst": {"dashboard", "ask", "evidence", "trends", "upload", "mismatch"},
    "risk_manager":   {"dashboard", "ask", "evidence", "trends", "upload", "mismatch", "audit"},
}

ROLE_LABELS = {
    "ceo": "CEO",
    "credit_analyst": "Credit Analyst",
    "risk_manager": "Risk Manager",
}


def can(role: str, permission: str) -> bool:
    return permission in PERMISSIONS.get(role, set())
