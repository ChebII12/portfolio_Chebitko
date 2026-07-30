import uuid
import hashlib
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.api.auth import create_access_token
from app.core.bigquery_service import BigQueryService
from app.core.config import settings
from app.core.auth import get_current_user
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def _clear_bigquery_memory_store():
    from app.core import bigquery_service as bqs

    bqs._MEMORY_USERS.clear()
    bqs._MEMORY_ASSESSMENTS.clear()
    bqs._MEMORY_MEDICAL_PROFILES.clear()
    bqs._MEMORY_RESET_TOKENS.clear()
    yield
    bqs._MEMORY_USERS.clear()
    bqs._MEMORY_ASSESSMENTS.clear()
    bqs._MEMORY_MEDICAL_PROFILES.clear()
    bqs._MEMORY_RESET_TOKENS.clear()


def _seed_user(user_id: uuid.UUID, name: str = "Beta Tester", email: str = "beta@test.ai", level: str = "expert") -> BigQueryService:
    service = BigQueryService()
    service.write_user_profile(
        user_id=str(user_id),
        name=name,
        email=email,
        password_hash="hash",
        level=level,
        registration_ts=datetime(2026, 5, 2, 14, 30, 0),
        is_email_verified=True,
    )
    return service


def _auth_headers(user_id: uuid.UUID, email: str = "beta@test.ai") -> dict:
    token = create_access_token({"sub": str(user_id), "email": email})
    return {"Authorization": f"Bearer {token}"}


def test_get_user_invalid_uuid_returns_400_detail():
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)

    with patch("app.api.auth.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.get("/api/auth/users/not-a-uuid", headers=_auth_headers(fake_user_id))

    assert response.status_code == 400
    assert isinstance(response.json().get("detail"), str)


def test_get_user_unknown_uuid_returns_404_detail():
    unknown_user_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: {"id": str(unknown_user_id), "user_id": str(unknown_user_id)}
    try:
        response = client.get(f"/api/auth/users/{unknown_user_id}", headers=_auth_headers(unknown_user_id))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"


def test_get_user_success_serializes_profile_fields():
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)
    service.write_assessment(
        assessment_id=str(uuid.uuid4()),
        user_id=str(fake_user_id),
        answers={
            "q1_travel_frequency": "weekly",
            "q2_distance_from_medical": "day or more",
            "q3_certification_status": "yes, currently certified",
            "q4_real_life_experience": "yes, for minor injuries",
            "q5_trauma_supplies_comfort": "trained and comfortable using",
            "q6_group_role": "designated group medic/leader",
        },
        level="expert",
        confidence=1.0,
        classification_source="local_rules",
        created_ts=datetime(2026, 5, 2, 14, 40, 0),
    )

    with patch("app.api.auth.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.get(f"/api/auth/users/{fake_user_id}", headers=_auth_headers(fake_user_id))

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Beta Tester"
    assert payload["email"] == "beta@test.ai"
    assert payload["level"] == "expert"
    assert payload["id"] == str(fake_user_id)
    assert payload["registration_date"] == "2026-05-02T14:30:00"
    assert payload["questionnaire_data"]["classification_source"] == "local_rules"


def test_update_user_invalid_level_returns_400_detail():
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)

    with patch("app.api.auth.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.put(
            f"/api/auth/users/{fake_user_id}",
            json={"level": "invalid"},
            headers=_auth_headers(fake_user_id),
        )

    assert response.status_code == 400
    assert "Invalid level" in response.json().get("detail", "")


def test_get_user_forbidden_for_different_authenticated_user():
    owner_user_id = uuid.uuid4()
    requester_user_id = uuid.uuid4()
    service = BigQueryService()
    service.write_user_profile(
        user_id=str(owner_user_id),
        name="Owner User",
        email="owner@test.ai",
        password_hash="hash",
        level="beginner",
        registration_ts=datetime(2026, 5, 2, 14, 30, 0),
        is_email_verified=True,
    )
    service.write_user_profile(
        user_id=str(requester_user_id),
        name="Requester User",
        email="requester@test.ai",
        password_hash="hash",
        level="intermediate",
        registration_ts=datetime(2026, 5, 2, 14, 31, 0),
        is_email_verified=True,
    )

    with patch("app.api.auth.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.get(f"/api/auth/users/{owner_user_id}", headers=_auth_headers(requester_user_id, email="requester@test.ai"))

    assert response.status_code == 403
    assert response.json().get("detail") == "You can only access your own profile"


def test_update_user_forbidden_for_different_authenticated_user():
    owner_user_id = uuid.uuid4()
    requester_user_id = uuid.uuid4()
    service = BigQueryService()
    service.write_user_profile(
        user_id=str(owner_user_id),
        name="Owner User",
        email="owner@test.ai",
        password_hash="hash",
        level="beginner",
        registration_ts=datetime(2026, 5, 2, 14, 30, 0),
        is_email_verified=True,
    )
    service.write_user_profile(
        user_id=str(requester_user_id),
        name="Requester User",
        email="requester@test.ai",
        password_hash="hash",
        level="intermediate",
        registration_ts=datetime(2026, 5, 2, 14, 31, 0),
        is_email_verified=True,
    )

    with patch("app.api.auth.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.put(
            f"/api/auth/users/{owner_user_id}",
            json={"name": "Hijack Attempt"},
            headers=_auth_headers(requester_user_id, email="requester@test.ai"),
        )

    assert response.status_code == 403
    assert response.json().get("detail") == "You can only update your own profile"


def test_update_user_email_conflict_returns_409():
    first_user_id = uuid.uuid4()
    second_user_id = uuid.uuid4()
    service = BigQueryService()
    service.write_user_profile(
        user_id=str(first_user_id),
        name="First User",
        email="first@test.ai",
        password_hash="hash",
        level="beginner",
        registration_ts=datetime(2026, 5, 2, 14, 30, 0),
        is_email_verified=True,
    )
    service.write_user_profile(
        user_id=str(second_user_id),
        name="Second User",
        email="second@test.ai",
        password_hash="hash",
        level="expert",
        registration_ts=datetime(2026, 5, 2, 14, 31, 0),
        is_email_verified=True,
    )

    with patch("app.api.auth.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.put(
            f"/api/auth/users/{first_user_id}",
            json={"email": "second@test.ai"},
            headers=_auth_headers(first_user_id, email="first@test.ai"),
        )

    assert response.status_code == 409
    assert response.json().get("detail") == "Email already registered"


def test_update_user_name_whitespace_only_returns_400():
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)

    with patch("app.api.auth.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.put(
            f"/api/auth/users/{fake_user_id}",
            json={"name": "   "},
            headers=_auth_headers(fake_user_id),
        )

    assert response.status_code == 400
    assert response.json().get("detail") == "Name must be at least 2 characters long"


def test_questionnaire_length_validation_returns_400():
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.post(
            "/api/questionnaire/analyze",
            json={
                "user_id": str(fake_user_id),
                "answers": ["Rarely", "Always close", "No", "No", "Don't know what they are"],
            },
            headers=_auth_headers(fake_user_id),
        )

    assert response.status_code == 400
    assert response.json().get("detail") == "Exactly 6 answers are required"


def test_questionnaire_invalid_answer_q3_returns_400():
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.post(
            "/api/questionnaire/analyze",
            json={
                "user_id": str(fake_user_id),
                "answers": [
                    "Monthly",
                    "A few hours away",
                    "NOT_VALID",
                    "Yes, for minor injuries",
                    "Know in theory only",
                    "In groups, not designated medic",
                ],
            },
            headers=_auth_headers(fake_user_id),
        )

    assert response.status_code == 400
    assert response.json().get("detail") == "Invalid answer for question 3"


def test_questionnaire_ai_timeout_keeps_deterministic_fallback(monkeypatch):
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)

    class FailingAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            raise RuntimeError("simulated timeout")

    monkeypatch.setattr(settings, "groq_api_key", "set-for-test")

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ), patch(
        "app.api.questionnaire.httpx.AsyncClient", return_value=FailingAsyncClient()
    ):
        response = client.post(
            "/api/questionnaire/analyze",
            json={
                "user_id": str(fake_user_id),
                "answers": [
                    "Rarely",
                    "Always close",
                    "No",
                    "No",
                    "Don't know what they are",
                    "Travel solo",
                ],
            },
            headers=_auth_headers(fake_user_id),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["level"] in {"beginner", "intermediate", "expert"}
    latest = service.get_latest_assessment_by_user_id(str(fake_user_id))
    assert latest["classification_source"] == "deterministic_fallback"
    assert payload["classification_source"] == "deterministic_fallback"
    assert "explanation" in payload


def test_questionnaire_rejects_token_user_mismatch():
    token_user_id = uuid.uuid4()
    payload_user_id = uuid.uuid4()
    service = _seed_user(token_user_id)

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.post(
            "/api/questionnaire/analyze",
            json={
                "user_id": str(payload_user_id),
                "answers": [
                    "Rarely",
                    "Always close",
                    "No",
                    "No",
                    "Don't know what they are",
                    "Travel solo",
                ],
            },
            headers=_auth_headers(token_user_id),
        )

    assert response.status_code == 403
    assert response.json().get("detail") == "Token user does not match questionnaire user_id"


def test_questionnaire_accepts_whitespace_and_case_variants(monkeypatch):
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)
    monkeypatch.setattr(settings, "groq_api_key", "")

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.post(
            "/api/questionnaire/analyze",
            json={
                "user_id": str(fake_user_id),
                "answers": [
                    "  mOnThLy  ",
                    "  A FEW HOURS AWAY",
                    " yes, CURRENTLY certified ",
                    " yes, FOR minor injuries",
                    " know IN theory only ",
                    "  in groups, not designated medic  ",
                ],
            },
            headers=_auth_headers(fake_user_id),
        )

    assert response.status_code == 200
    assert response.json().get("level") in {"beginner", "intermediate", "expert"}


def test_questionnaire_ai_invalid_json_keeps_fallback(monkeypatch):
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)

    class InvalidJsonResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"choices": [{"message": {"content": "not-json"}}]}

    class InvalidJsonAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            return InvalidJsonResponse()

    monkeypatch.setattr(settings, "groq_api_key", "set-for-test")

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ), patch(
        "app.api.questionnaire.httpx.AsyncClient", return_value=InvalidJsonAsyncClient()
    ):
        response = client.post(
            "/api/questionnaire/analyze",
            json={
                "user_id": str(fake_user_id),
                "answers": [
                    "Rarely",
                    "Always close",
                    "No",
                    "No",
                    "Don't know what they are",
                    "Travel solo",
                ],
            },
            headers=_auth_headers(fake_user_id),
        )

    assert response.status_code == 200
    latest = service.get_latest_assessment_by_user_id(str(fake_user_id))
    assert latest["classification_source"] == "deterministic_fallback"


def test_questionnaire_ai_out_of_range_confidence_is_clamped(monkeypatch):
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id)

    class OutOfRangeConfidenceResponse:
        status_code = 200

        @staticmethod
        def json():
            return {
                "choices": [
                    {"message": {"content": '{"level": "expert", "confidence": 1.9}'}}
                ]
            }

    class OutOfRangeConfidenceAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            return OutOfRangeConfidenceResponse()

    monkeypatch.setattr(settings, "groq_api_key", "set-for-test")

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ), patch(
        "app.api.questionnaire.httpx.AsyncClient", return_value=OutOfRangeConfidenceAsyncClient()
    ):
        response = client.post(
            "/api/questionnaire/analyze",
            json={
                "user_id": str(fake_user_id),
                "answers": [
                    "Weekly",
                    "Day or more",
                    "Advanced training (EMT, etc.)",
                    "Critical emergencies",
                    "Trained and comfortable using",
                    "Designated group medic/leader",
                ],
            },
            headers=_auth_headers(fake_user_id),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["level"] == "expert"
    assert payload["confidence"] == 1.0
    assert payload["classification_source"] == "deterministic_fallback"
    latest = service.get_latest_assessment_by_user_id(str(fake_user_id))
    assert latest["classification_source"] == "deterministic_fallback"


def test_questionnaire_invalid_payload_user_id_format_returns_400():
    token_user_id = uuid.uuid4()
    service = _seed_user(token_user_id)

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.post(
            "/api/questionnaire/analyze",
            json={
                "user_id": "not-a-uuid",
                "answers": [
                    "Rarely",
                    "Always close",
                    "No",
                    "No",
                    "Don't know what they are",
                    "Travel solo",
                ],
            },
            headers=_auth_headers(token_user_id),
        )

    assert response.status_code == 400
    assert response.json().get("detail") == "Invalid user_id format"


def test_questionnaire_skip_assigns_beginner_and_persists_assessment():
    fake_user_id = uuid.uuid4()
    service = _seed_user(fake_user_id, level=None)

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.post(
            "/api/questionnaire/skip",
            headers=_auth_headers(fake_user_id),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["level"] == "beginner"
    assert payload["confidence"] == 1.0
    assert payload["classification_source"] == "questionnaire_skipped"
    assert "safest default" in payload["explanation"]

    user_row = service.get_user_profile_by_id(str(fake_user_id))
    latest = service.get_latest_assessment_by_user_id(str(fake_user_id))
    assert user_row["level"] == "beginner"
    assert latest["classification_source"] == "questionnaire_skipped"


def test_register_and_login_issue_bearer_tokens_with_secure_hashing():
    email = "token-user@example.com"
    password = "SecurePass1"

    register_response = client.post(
        "/api/auth/register",
        json={"name": "Token User", "email": email, "password": password},
    )

    assert register_response.status_code == 200
    register_payload = register_response.json()
    assert register_payload["requires_verification"] is True
    assert register_payload["user_id"]
    
    # Grab the user profile from BQ service mock
    from app.api.auth import get_bq_service
    service = get_bq_service()
    user_row = service.get_user_profile_by_email(email)
    
    # Override the verification code with a known hash of "123456" for testing
    from app.api.auth import get_password_hash
    known_code = "123456"
    known_hash = get_password_hash(known_code)
    
    service.write_user_profile(
        user_id=user_row["user_id"],
        name=user_row["name"],
        email=user_row["email"],
        password_hash=user_row["password_hash"],
        level=user_row.get("level"),
        registration_ts=user_row.get("registration_ts") or datetime.now(),
        is_email_verified=False,
        verification_code=known_hash,
        verification_expires_ts=user_row["verification_expires_ts"],
    )
    
    # Verify email
    verify_response = client.post(
        "/api/auth/verify-email",
        json={"email": email, "code": known_code}
    )
    assert verify_response.status_code == 200
    verify_payload = verify_response.json()
    assert verify_payload["access_token"]

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )

    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert login_payload["access_token"]
    assert login_payload["token_type"] == "bearer"
    assert login_payload["user_id"] == register_payload["user_id"]

    user_row = service.get_user_profile_by_email(email)
    assert user_row is not None
    assert str(user_row["password_hash"]).startswith("pbkdf2_sha256$")
    assert user_row["is_email_verified"] is True


def test_register_console_email_mode_returns_dev_code_and_logs(caplog, monkeypatch):
    monkeypatch.setattr(settings, "email_delivery_mode", "console")
    monkeypatch.setattr(settings, "app_environment", "development")

    response = client.post(
        "/api/auth/register",
        json={"name": "Console User", "email": "console@example.com", "password": "SecurePass1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["requires_verification"] is True
    assert len(payload["dev_verification_code"]) == 6
    assert "DEV EMAIL VERIFICATION CODE for console@example.com" in caplog.text


def test_register_production_console_mode_does_not_return_dev_code(monkeypatch):
    monkeypatch.setattr(settings, "email_delivery_mode", "console")
    monkeypatch.setattr(settings, "app_environment", "production")

    response = client.post(
        "/api/auth/register",
        json={"name": "Prod User", "email": "prod-console@example.com", "password": "SecurePass1"},
    )

    assert response.status_code == 200
    assert "dev_verification_code" not in response.json()


def test_register_smtp_mode_calls_email_sender(monkeypatch):
    monkeypatch.setattr(settings, "email_delivery_mode", "smtp")
    monkeypatch.setattr(settings, "email_log_codes", False)
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_server", "")
    monkeypatch.setattr(settings, "smtp_port", 587)
    monkeypatch.setattr(settings, "smtp_username", "mailer@example.com")
    monkeypatch.setattr(settings, "smtp_user", "")
    monkeypatch.setattr(settings, "smtp_password", "secret")
    monkeypatch.setattr(settings, "smtp_use_tls", True)

    sent_messages = []

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            self.host = host
            self.port = port
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            self.tls_started = True

        def login(self, username, password):
            self.username = username
            self.password = password

        def send_message(self, message):
            sent_messages.append(message)

    with patch("app.api.auth.smtplib.SMTP", FakeSMTP):
        response = client.post(
            "/api/auth/register",
            json={"name": "SMTP User", "email": "smtp@example.com", "password": "SecurePass1"},
        )

    assert response.status_code == 200
    assert "dev_verification_code" not in response.json()
    assert len(sent_messages) == 1
    assert sent_messages[0]["To"] == "smtp@example.com"


def test_register_smtp_mode_can_log_code_for_development(caplog, monkeypatch):
    monkeypatch.setattr(settings, "email_delivery_mode", "smtp")
    monkeypatch.setattr(settings, "email_log_codes", True)
    monkeypatch.setattr(settings, "app_environment", "development")
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_server", "")
    monkeypatch.setattr(settings, "smtp_port", 587)
    monkeypatch.setattr(settings, "smtp_username", "mailer@example.com")
    monkeypatch.setattr(settings, "smtp_user", "")
    monkeypatch.setattr(settings, "smtp_password", "secret")
    monkeypatch.setattr(settings, "smtp_use_tls", True)

    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            pass

        def login(self, username, password):
            pass

        def send_message(self, message):
            pass

    with patch("app.api.auth.smtplib.SMTP", FakeSMTP):
        response = client.post(
            "/api/auth/register",
            json={"name": "SMTP Log User", "email": "smtp-log@example.com", "password": "SecurePass1"},
        )

    assert response.status_code == 200
    assert len(response.json()["dev_verification_code"]) == 6
    assert "DEV EMAIL VERIFICATION CODE for smtp-log@example.com" in caplog.text


def test_register_smtp_failure_returns_clear_error(monkeypatch):
    monkeypatch.setattr(settings, "email_delivery_mode", "smtp")
    monkeypatch.setattr(settings, "email_log_codes", False)
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_server", "")

    class FailingSMTP:
        def __init__(self, *args, **kwargs):
            raise OSError("SMTP unavailable")

    with patch("app.api.auth.smtplib.SMTP", FailingSMTP):
        response = client.post(
            "/api/auth/register",
            json={"name": "Fail User", "email": "smtp-fail@example.com", "password": "SecurePass1"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "Verification email could not be sent. Please try again or contact support."


def test_register_smtp_failure_continues_when_codes_are_logged(caplog, monkeypatch):
    monkeypatch.setattr(settings, "email_delivery_mode", "smtp")
    monkeypatch.setattr(settings, "email_log_codes", True)
    monkeypatch.setattr(settings, "app_environment", "development")
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_server", "")

    class FailingSMTP:
        def __init__(self, *args, **kwargs):
            raise OSError("SMTP unavailable")

    with patch("app.api.auth.smtplib.SMTP", FailingSMTP):
        response = client.post(
            "/api/auth/register",
            json={"name": "Fallback User", "email": "smtp-log-fail@example.com", "password": "SecurePass1"},
        )

    assert response.status_code == 200
    assert response.json()["requires_verification"] is True
    assert len(response.json()["dev_verification_code"]) == 6
    assert "DEV EMAIL VERIFICATION CODE for smtp-log-fail@example.com" in caplog.text
    assert "Continuing registration for smtp-log-fail@example.com" in caplog.text


def test_verify_email_with_wrong_code_fails():
    response = client.post(
        "/api/auth/register",
        json={"name": "Wrong Code", "email": "wrong-code@example.com", "password": "SecurePass1"},
    )
    assert response.status_code == 200

    verify_response = client.post(
        "/api/auth/verify-email",
        json={"email": "wrong-code@example.com", "code": "000000"},
    )

    assert verify_response.status_code == 401
    assert verify_response.json()["detail"] == "Invalid verification code"


def test_resend_verification_console_mode_returns_new_dev_code(monkeypatch):
    monkeypatch.setattr(settings, "email_delivery_mode", "console")
    monkeypatch.setattr(settings, "app_environment", "development")

    register_response = client.post(
        "/api/auth/register",
        json={"name": "Resend User", "email": "resend@example.com", "password": "SecurePass1"},
    )
    assert register_response.status_code == 200
    first_code = register_response.json()["dev_verification_code"]

    resend_response = client.post(
        "/api/auth/resend-verification",
        json={"email": "resend@example.com"},
    )

    assert resend_response.status_code == 200
    second_code = resend_response.json()["dev_verification_code"]
    assert len(second_code) == 6
    assert second_code != first_code


def test_register_blocks_case_insensitive_duplicate_email():
    first = client.post(
        "/api/auth/register",
        json={"name": "Dup User", "email": "Dupe@Example.com", "password": "SecurePass1"},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/auth/register",
        json={"name": "Dup User 2", "email": "dupe@example.com", "password": "SecurePass2"},
    )
    assert second.status_code == 409
    assert second.json().get("detail") == "Email already registered"


def test_login_accepts_trimmed_and_case_normalized_email():
    email = "normalize-login@example.com"
    password = "SecurePass1"

    register_response = client.post(
        "/api/auth/register",
        json={"name": "Normalize Login", "email": email, "password": password},
    )
    assert register_response.status_code == 200

    from app.api.auth import get_bq_service
    service = get_bq_service()
    user_row = service.get_user_profile_by_email(email)
    
    # Manually verify
    service.write_user_profile(
        user_id=user_row["user_id"],
        name=user_row["name"],
        email=user_row["email"],
        password_hash=user_row["password_hash"],
        level=user_row.get("level"),
        registration_ts=user_row.get("registration_ts") or datetime.now(),
        is_email_verified=True,
    )

    login_response = client.post(
        "/api/auth/login",
        json={"email": "  NORMALIZE-LOGIN@EXAMPLE.COM  ", "password": password},
    )
    assert login_response.status_code == 200
    assert login_response.json().get("email") == email


def test_login_with_malformed_password_hash_returns_401():
    fake_user_id = uuid.uuid4()
    service = BigQueryService()
    service.write_user_profile(
        user_id=str(fake_user_id),
        name="Malformed Hash",
        email="malformed-hash@test.ai",
        password_hash="pbkdf2_sha256$invalid-format",
        level="beginner",
        registration_ts=datetime(2026, 5, 3, 10, 0, 0),
        is_email_verified=True,
    )

    with patch("app.api.auth.get_bq_service", return_value=service):
        response = client.post(
            "/api/auth/login",
            json={"email": "malformed-hash@test.ai", "password": "SecurePass1"},
        )

    assert response.status_code == 401
    assert response.json().get("detail") == "Invalid email or password"


def test_login_with_legacy_hash_upgrades_to_pbkdf2():
    fake_user_id = uuid.uuid4()
    email = "legacy-upgrade@test.ai"
    password = "SecurePass1"
    salt = "legacysalt"
    legacy_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    service = BigQueryService()
    service.write_user_profile(
        user_id=str(fake_user_id),
        name="Legacy User",
        email=email,
        password_hash=f"{salt}:{legacy_hash}",
        level="intermediate",
        registration_ts=datetime(2026, 5, 3, 10, 0, 0),
        is_email_verified=True,
    )

    with patch("app.api.auth.get_bq_service", return_value=service):
        response = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )

    assert response.status_code == 200
    upgraded_user = service.get_user_profile_by_email(email)
    assert upgraded_user is not None
    assert str(upgraded_user["password_hash"]).startswith("pbkdf2_sha256$")
