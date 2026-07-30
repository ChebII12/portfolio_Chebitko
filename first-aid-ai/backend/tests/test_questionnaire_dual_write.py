import uuid
from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.auth import create_access_token
from app.core.bigquery_service import BigQueryService
from app.core.config import settings
from app.main import app


client = TestClient(app)


def _auth_headers(user_id: uuid.UUID, email: str = "test@example.com") -> dict:
    token = create_access_token({"sub": str(user_id), "email": email})
    return {"Authorization": f"Bearer {token}"}


def test_analyze_questionnaire_dual_write_persists_wide_row():
    fake_user_id = uuid.uuid4()
    service = BigQueryService()
    service.write_user_profile(
        user_id=str(fake_user_id),
        name="Test User",
        email="test@example.com",
        password_hash="hash",
        level=None,
        registration_ts=datetime(2026, 5, 15, 10, 0, 0),
    )

    payload = {
        "user_id": str(fake_user_id),
        "answers": [
            "Monthly",
            "A few hours away",
            "Yes, currently certified",
            "Yes, for minor injuries",
            "Know in theory only",
            "In groups, not designated medic",
        ],
    }

    original_groq_api_key = settings.groq_api_key
    settings.groq_api_key = ""

    with patch("app.api.questionnaire.get_bq_service", return_value=service), patch(
        "app.core.auth.get_bq_service", return_value=service
    ):
        response = client.post("/api/questionnaire/analyze", json=payload, headers=_auth_headers(fake_user_id))

    settings.groq_api_key = original_groq_api_key

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"level", "confidence", "explanation", "classification_source", "message"}
    assert body["level"] in {"beginner", "intermediate", "expert"}
    assert body["classification_source"] == "local_rules"

    latest = service.get_latest_assessment_by_user_id(str(fake_user_id))
    assert latest is not None
    assert latest["q1_travel_frequency"] == "Monthly"
    assert latest["q6_group_role"] == "In groups, not designated medic"
    assert latest["level"] == body["level"]
    assert latest["confidence"] == body["confidence"]

    user_row = service.get_user_profile_by_id(str(fake_user_id))
    assert user_row["level"] == body["level"]
    assert user_row["questionnaire_data"]["answers"] == payload["answers"]
    assert user_row["questionnaire_data"]["assessment_id"] == latest["assessment_id"]
    assert service._in_memory["user_profiles"][str(fake_user_id)]["questionnaire_data"]["answers"] == payload["answers"]
