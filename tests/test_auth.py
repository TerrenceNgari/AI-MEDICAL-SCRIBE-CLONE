from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from medical_scribe.auth import authenticate_user, create_account, init_auth_db


def test_create_account_and_authenticate(tmp_path: Path):
    db_path = tmp_path / "users.db"
    init_auth_db(str(db_path))

    created, message = create_account("doctor@example.com", "securePass123", str(db_path))
    assert created is True
    assert "successfully" in message.lower()

    assert authenticate_user("doctor@example.com", "securePass123", str(db_path)) is True
    assert authenticate_user("doctor@example.com", "wrong-pass", str(db_path)) is False


def test_duplicate_email_rejected(tmp_path: Path):
    db_path = tmp_path / "users.db"
    init_auth_db(str(db_path))

    first_created, _ = create_account("doc@example.com", "securePass123", str(db_path))
    second_created, second_message = create_account("doc@example.com", "securePass123", str(db_path))

    assert first_created is True
    assert second_created is False
    assert "already exists" in second_message.lower()


def test_invalid_email_and_short_password_rejected(tmp_path: Path):
    db_path = tmp_path / "users.db"
    init_auth_db(str(db_path))

    bad_email_created, _ = create_account("not-an-email", "securePass123", str(db_path))
    short_password_created, _ = create_account("doc2@example.com", "short", str(db_path))

    assert bad_email_created is False
    assert short_password_created is False
