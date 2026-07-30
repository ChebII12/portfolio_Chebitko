import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.bigquery_service import BigQueryService
from app.main import app


def run_demo_cases() -> None:
    client = TestClient(app)

    user_id = str(uuid.uuid4())
    service = BigQueryService()
    service.write_user_profile(
        user_id=user_id,
        name="Demo User",
        email="demo@example.com",
        password_hash="hash",
        level="",
        registration_ts=datetime.now(timezone.utc),
    )

    test_cases = [
        {
            "user_id": user_id,
            "answers": ["Rarely", "Always close", "No", "No", "Don't know what they are", "Travel solo"],
        },
        {
            "user_id": user_id,
            "answers": ["Monthly", "A few hours away", "Yes, currently certified", "Yes, for minor injuries", "Know in theory only", "In groups, not designated medic"],
        },
        {
            "user_id": user_id,
            "answers": ["Weekly", "Day or more", "Advanced training (EMT, etc.)", "Critical emergencies", "Trained and comfortable using", "Designated group medic/leader"],
        },
    ]

    with patch("app.api.questionnaire.get_bq_service", return_value=service):
        for i, test_data in enumerate(test_cases, 1):
            print(f"Test Case {i}: {test_data['answers'][0]} travel pattern")
            response = client.post("/api/questionnaire/analyze", json=test_data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Level: {data['level']}, Confidence: {data['confidence']}")
            else:
                print(f"Error: {response.text}")
            print()


if __name__ == "__main__":
    run_demo_cases()

