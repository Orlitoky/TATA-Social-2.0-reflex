"""Password hashing, session tokens and validation helpers.

Only derived password hashes and hashed session tokens are ever persisted.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets

PBKDF2_ALGO = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260_000
SALT_BYTES = 16

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+\.[^@\s]{2,}$")
USERNAME_RE = re.compile(r"^[a-z0-9_.]{3,24}$")


def hash_password(password: str) -> str:
    """Derive a salted PBKDF2-SHA256 hash for storage."""
    salt = secrets.token_bytes(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return (
        f"{PBKDF2_ALGO}${PBKDF2_ITERATIONS}$"
        f"{base64.b64encode(salt).decode()}${base64.b64encode(derived).decode()}"
    )


def verify_password(password: str, stored: str) -> bool:
    """Constant-time verification of a password against a stored hash."""
    parts = stored.split("$")
    if len(parts) != 4 or parts[0] != PBKDF2_ALGO:
        return False
    try:
        iterations = int(parts[1])
        salt = base64.b64decode(parts[2])
        expected = base64.b64decode(parts[3])
    except (ValueError, TypeError):
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(derived, expected)


def new_session_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def normalize_email(email: str) -> str:
    return email.strip().lower()


def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_signup(
    email: str, username: str, password: str, confirm: str, display_name: str
) -> str:
    """Return an error message, or an empty string when the input is valid."""
    if not EMAIL_RE.match(normalize_email(email)):
        return "Enter a valid email address."
    if not USERNAME_RE.match(normalize_username(username)):
        return "Username must be 3-24 characters: letters, numbers, _ or ."
    if not display_name.strip():
        return "Display name is required."
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if password.lower() == password or password.upper() == password:
        return "Use both upper and lower case characters in your password."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number."
    if password != confirm:
        return "Passwords do not match."
    return ""
