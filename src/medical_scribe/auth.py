from __future__ import annotations

import hashlib
import hmac
import os
import re
import sqlite3
from datetime import datetime, timezone


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def init_auth_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_password(password: str, *, salt: bytes | None = None) -> str:
    salt_bytes = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 200_000)
    return f"{salt_bytes.hex()}${digest.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, digest_hex = stored_hash.split("$", maxsplit=1)
    except ValueError:
        return False

    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(expected, computed)


def create_account(email: str, password: str, db_path: str) -> tuple[bool, str]:
    normalized_email = _normalize_email(email)
    if not EMAIL_PATTERN.match(normalized_email):
        return False, "Please provide a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    password_hash = _hash_password(password)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (normalized_email, password_hash, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()


def authenticate_user(email: str, password: str, db_path: str) -> bool:
    normalized_email = _normalize_email(email)
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return False
    return _verify_password(password, row[0])
