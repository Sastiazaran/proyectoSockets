"""Local account store shared conceptually with the C auth server."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,16}$")
MIN_PASSWORD_LEN = 4

CLIENT_DIR = Path(__file__).resolve().parent
REPO_DIR = CLIENT_DIR.parent
USERS_FILE = Path(os.environ.get("TICTACTOE_USERS_FILE", REPO_DIR / "data" / "users.txt"))


def _hash_password(username: str, password: str) -> str:
    payload = f"{username.lower()}:{password}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_username(username: str) -> str | None:
    if not USERNAME_RE.fullmatch(username):
        return "Use 3-16 letters, numbers, or underscores."
    return None


def validate_password(password: str) -> str | None:
    if len(password) < MIN_PASSWORD_LEN:
        return f"Password must be at least {MIN_PASSWORD_LEN} characters."
    if password in {"Password", "password"}:
        return "Choose a real password."
    return None


def _ensure_parent():
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        _write_all({"demo": _hash_password("demo", "demo123")})


def _read_all() -> dict[str, str]:
    _ensure_parent()
    users = {}
    try:
        text = USERS_FILE.read_text(encoding="utf-8")
    except OSError:
        return users
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            users[parts[0].lower()] = parts[1]
    return users


def _write_all(users: dict[str, str]) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# username sha256(username:password)", ""]
    for name in sorted(users):
        lines.append(f"{name} {users[name]}")
    USERS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def register(username: str, password: str) -> str | None:
    """Create an account. Returns an error message, or None on success."""
    username = username.strip()
    err = validate_username(username) or validate_password(password)
    if err:
        return err
    users = _read_all()
    key = username.lower()
    if key in users:
        return "That username is already taken."
    users[key] = _hash_password(key, password)
    _write_all(users)
    return None


def authenticate(username: str, password: str) -> bool:
    username = username.strip().lower()
    users = _read_all()
    stored = users.get(username)
    if stored is None:
        return False
    return stored == _hash_password(username, password)


def ensure_demo_user() -> None:
    users = _read_all()
    if "demo" not in users:
        users["demo"] = _hash_password("demo", "demo123")
        _write_all(users)
