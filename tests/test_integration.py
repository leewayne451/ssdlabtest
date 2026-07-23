"""
Integration tests for the ssdlabtest auth demo.

These hit the running app directly over HTTP (no browser involved) to
verify the backend password-validation rules (OWASP ASVS V2.1 checks
implemented in server.js):
  - length must be 8-64 characters
  - password must not appear in the common-password dictionary
  - a valid, unique password is accepted and the account is created
"""
import pathlib
import uuid

import pytest
import requests

BASE_URL = "http://localhost:3000"
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _pick_common_password() -> str:
    """Read the app's own 100k.txt dictionary and return a real entry that
    also satisfies the 8-64 length rule, so the 'too common' test is always
    checking an entry that's actually loaded into common_passwords."""
    dict_path = REPO_ROOT / "100k.txt"
    with open(dict_path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            candidate = line.strip()
            if 8 <= len(candidate) <= 64:
                return candidate
    raise RuntimeError("Could not find a usable entry in 100k.txt")


COMMON_PASSWORD = _pick_common_password()


def register(username, password):
    return requests.post(
        f"{BASE_URL}/api/register",
        json={"username": username, "password": password},
        timeout=10,
    )


def unique_username(prefix="itest"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_home_page_loads():
    resp = requests.get(BASE_URL, timeout=10)
    assert resp.status_code == 200
    assert "Account Creation" in resp.text


def test_password_too_short_is_rejected():
    resp = register(unique_username(), "abc123")
    body = resp.json()
    assert resp.status_code == 400
    assert body["success"] is False
    assert "8" in body["message"]


def test_password_too_long_is_rejected():
    resp = register(unique_username(), "a" * 65)
    body = resp.json()
    assert resp.status_code == 400
    assert body["success"] is False
    assert "64" in body["message"]


def test_common_password_is_rejected():
    resp = register(unique_username(), COMMON_PASSWORD)
    body = resp.json()
    assert resp.status_code == 400
    assert body["success"] is False
    assert "common" in body["message"].lower()


def test_valid_unique_password_is_accepted():
    resp = register(unique_username(), "Xk9#mQ2vLp7$Rz01")
    body = resp.json()
    assert resp.status_code == 200
    assert body["success"] is True


def test_missing_username_is_rejected():
    resp = requests.post(
        f"{BASE_URL}/api/register",
        json={"password": "Xk9#mQ2vLp7$Rz01"},
        timeout=10,
    )
    assert resp.status_code == 400


def test_missing_password_is_rejected():
    resp = requests.post(
        f"{BASE_URL}/api/register",
        json={"username": unique_username()},
        timeout=10,
    )
    assert resp.status_code == 400
