import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.api.auth import create_access_token, get_password_hash
from app.core.bigquery_service import get_bq_service
from app.main import app


client = TestClient(app)


def _seed_user(email: str = "profile@example.com", password: str = "SecurePass1", name: str = "Profile User"):
    service = get_bq_service()
    user_id = str(uuid.uuid4())
    service.write_user_profile(
        user_id=user_id,
        name=name,
        email=email,
        password_hash=get_password_hash(password),
        level="intermediate",
        registration_ts=datetime(2026, 5, 2, 14, 30, 0, tzinfo=timezone.utc),
        is_email_verified=True,
    )
    return service, user_id


def _headers(user_id: str, email: str = "profile@example.com"):
    token = create_access_token({"sub": user_id, "email": email})
    return {"Authorization": f"Bearer {token}"}


def test_get_account_profile_returns_safe_fields():
    _, user_id = _seed_user()

    response = client.get("/api/profile/me", headers=_headers(user_id))

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == user_id
    assert payload["email"] == "profile@example.com"
    assert payload["email_verified"] is True
    assert "password_hash" not in payload
    assert "verification_code" not in payload


def test_update_account_profile_preserves_auth_fields():
    service, user_id = _seed_user()
    before = service.get_user_profile_by_id(user_id)

    response = client.patch("/api/profile/me", json={"name": "Updated Name"}, headers=_headers(user_id))

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    after = service.get_user_profile_by_id(user_id)
    assert after["password_hash"] == before["password_hash"]
    assert after["email"] == before["email"]
    assert after["is_email_verified"] is True


def test_get_empty_medical_profile_returns_optional_fields():
    _, user_id = _seed_user()

    response = client.get("/api/profile/medical", headers=_headers(user_id))

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == user_id
    assert payload["age"] is None
    assert payload["medical_profile_id"] is None


def test_create_and_update_medical_profile():
    _, user_id = _seed_user()

    create_response = client.put(
        "/api/profile/medical",
        json={"age": 35, "sex": "female", "blood_type": "O+", "allergies": "Penicillin"},
        headers=_headers(user_id),
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["age"] == 35
    assert created["sex"] == "female"
    assert created["blood_type"] == "O+"
    assert created["medical_profile_id"]

    update_response = client.patch(
        "/api/profile/medical",
        json={"age": 36, "allergies": "None"},
        headers=_headers(user_id),
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["medical_profile_id"] == created["medical_profile_id"]
    assert updated["age"] == 36
    assert updated["blood_type"] == "O+"
    assert updated["allergies"] == "None"


def test_invalid_medical_age_and_blood_type_are_rejected():
    _, user_id = _seed_user()

    bad_age = client.put("/api/profile/medical", json={"age": 121}, headers=_headers(user_id))
    bad_blood = client.put("/api/profile/medical", json={"blood_type": "blue"}, headers=_headers(user_id))

    assert bad_age.status_code == 422
    assert bad_blood.status_code == 422


def test_medical_profile_isolated_per_authenticated_user():
    _, owner_id = _seed_user(email="owner@example.com")
    _, other_id = _seed_user(email="other@example.com")

    owner_response = client.put(
        "/api/profile/medical",
        json={"age": 44, "medical_notes": "Owner private note"},
        headers=_headers(owner_id, "owner@example.com"),
    )
    assert owner_response.status_code == 200

    other_response = client.get("/api/profile/medical", headers=_headers(other_id, "other@example.com"))
    assert other_response.status_code == 200
    assert other_response.json()["age"] is None
    assert other_response.json()["medical_notes"] is None


def test_delete_medical_profile_clears_current_user_data():
    _, user_id = _seed_user()

    create_response = client.put(
        "/api/profile/medical",
        json={"age": 42, "allergies": "Latex"},
        headers=_headers(user_id),
    )
    assert create_response.status_code == 200

    delete_response = client.delete("/api/profile/medical", headers=_headers(user_id))
    get_response = client.get("/api/profile/medical", headers=_headers(user_id))

    assert delete_response.status_code == 200
    assert get_response.status_code == 200
    assert get_response.json()["age"] is None
    assert get_response.json()["allergies"] is None


def test_change_password_succeeds_and_old_password_fails():
    _, user_id = _seed_user(password="SecurePass1")

    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "SecurePass1", "new_password": "NewSecure2"},
        headers=_headers(user_id),
    )
    assert response.status_code == 200

    old_login = client.post("/api/auth/login", json={"email": "profile@example.com", "password": "SecurePass1"})
    new_login = client.post("/api/auth/login", json={"email": "profile@example.com", "password": "NewSecure2"})
    assert old_login.status_code == 401
    assert new_login.status_code == 200


def test_change_password_fails_with_wrong_current_password():
    _, user_id = _seed_user(password="SecurePass1")

    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "WrongPass1", "new_password": "NewSecure2"},
        headers=_headers(user_id),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Current password is incorrect"


def test_forgot_password_returns_generic_response_and_no_raw_code():
    _seed_user(email="reset@example.com")

    response = client.post("/api/auth/forgot-password", json={"email": "reset@example.com"})
    unknown = client.post("/api/auth/forgot-password", json={"email": "unknown@example.com"})

    assert response.status_code == 200
    assert unknown.status_code == 200
    assert response.json() == unknown.json()
    assert "code" not in response.text.lower()


def test_reset_password_succeeds_and_code_cannot_be_reused():
    service, user_id = _seed_user(email="reset-success@example.com", password="SecurePass1")
    code = "123456"
    service.create_password_reset_token(
        reset_id=str(uuid.uuid4()),
        user_id=user_id,
        email="reset-success@example.com",
        reset_code_hash=get_password_hash(code),
        expires_ts=datetime.now(timezone.utc) + timedelta(minutes=30),
        created_ts=datetime.now(timezone.utc),
    )

    reset_response = client.post(
        "/api/auth/reset-password",
        json={"email": "reset-success@example.com", "reset_code": code, "new_password": "ResetPass2"},
    )
    reuse_response = client.post(
        "/api/auth/reset-password",
        json={"email": "reset-success@example.com", "reset_code": code, "new_password": "AnotherPass3"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"email": "reset-success@example.com", "password": "ResetPass2"},
    )

    assert reset_response.status_code == 200
    assert reuse_response.status_code == 401
    assert login_response.status_code == 200


def test_reset_password_fails_with_expired_code():
    service, user_id = _seed_user(email="expired-reset@example.com", password="SecurePass1")
    service.create_password_reset_token(
        reset_id=str(uuid.uuid4()),
        user_id=user_id,
        email="expired-reset@example.com",
        reset_code_hash=get_password_hash("123456"),
        expires_ts=datetime.now(timezone.utc) - timedelta(minutes=1),
        created_ts=datetime.now(timezone.utc) - timedelta(minutes=31),
    )

    response = client.post(
        "/api/auth/reset-password",
        json={"email": "expired-reset@example.com", "reset_code": "123456", "new_password": "ResetPass2"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired reset code"
