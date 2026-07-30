import pytest

from app.core import bigquery_service as bqs
from app.core.config import settings


@pytest.fixture(autouse=True)
def _isolate_tests_from_real_bigquery(monkeypatch):
    # Keep unit tests deterministic and independent of local BigQuery setup.
    monkeypatch.setattr(settings, "bigquery_project_id", "")
    monkeypatch.setattr(settings, "bigquery_credentials_path", "")
    monkeypatch.setattr(settings, "email_delivery_mode", "console")
    monkeypatch.setattr(settings, "email_log_codes", False)
    monkeypatch.setattr(settings, "app_environment", "development")
    bqs._MEMORY_USERS.clear()
    bqs._MEMORY_ASSESSMENTS.clear()
    bqs._MEMORY_MEDICAL_PROFILES.clear()
    bqs._MEMORY_RESET_TOKENS.clear()
    bqs.bq_service = None
    yield
    bqs._MEMORY_USERS.clear()
    bqs._MEMORY_ASSESSMENTS.clear()
    bqs._MEMORY_MEDICAL_PROFILES.clear()
    bqs._MEMORY_RESET_TOKENS.clear()
    bqs.bq_service = None

