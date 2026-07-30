"""
BigQuery Integration Service for Module 1 Migration
Supports Phase 2-5: Dual-write, backfill, parity, and cutover
"""

import json
import logging
import re
from typing import Optional, Dict, Any
from datetime import datetime, timezone

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
except ModuleNotFoundError:  # pragma: no cover - used in local test environments without Google libs
    class _DummyQueryJobConfig:
        def __init__(self, *args, **kwargs):
            self.query_parameters = kwargs.get("query_parameters", [])

    class _DummyScalarQueryParameter:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class _DummyClient:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError("google.cloud.bigquery is not installed")

    class _DummyDataset:
        def __init__(self, *args, **kwargs):
            self.location = None

    class _DummyTable:
        def __init__(self, *args, **kwargs):
            self.schema = kwargs.get("schema")

    class _DummySchemaField:
        def __init__(self, *args, **kwargs):
            self.name = args[0] if args else None

    class _DummyBigQueryModule:
        Client = _DummyClient
        QueryJobConfig = _DummyQueryJobConfig
        ScalarQueryParameter = _DummyScalarQueryParameter
        Dataset = _DummyDataset
        Table = _DummyTable
        SchemaField = _DummySchemaField

    class _DummyServiceAccountModule:
        class Credentials:
            @staticmethod
            def from_service_account_file(*args, **kwargs):
                raise ModuleNotFoundError("google.oauth2.service_account is not installed")

    bigquery = _DummyBigQueryModule()
    service_account = _DummyServiceAccountModule()

from .config import settings

logger = logging.getLogger(__name__)

# Module-level in-memory stores (used for tests and local development when BigQuery is not configured)
_MEMORY_USERS: Dict[str, Dict[str, Any]] = {}
_MEMORY_ASSESSMENTS: Dict[str, Dict[str, Any]] = {}
_MEMORY_MEDICAL_PROFILES: Dict[str, Dict[str, Any]] = {}
_MEMORY_RESET_TOKENS: Dict[str, Dict[str, Any]] = {}


class BigQueryService:
    """Handle BigQuery writes and reads as the primary persistence layer."""
    
    def __init__(self):
        self.project_id = settings.bigquery_project_id
        self.dataset_id = settings.bigquery_dataset_id
        self.client: Optional[bigquery.Client] = None
        # Support environments where BigQuery is not configured (tests, local dev without credentials).
        # If BIGQUERY_PROJECT_ID is not provided or client initialization fails, fall back to an in-memory store.
        # Use module-level memory stores so tests can access/reset them easily
        self._in_memory = {
            "user_profiles": _MEMORY_USERS,  # user_id -> dict
            "assessments": _MEMORY_ASSESSMENTS,    # assessment_id -> dict
            "medical_profiles": _MEMORY_MEDICAL_PROFILES,  # user_id -> dict
            "password_reset_tokens": _MEMORY_RESET_TOKENS,  # reset_id -> dict
        }

        if not self.project_id:
            logger.warning("BIGQUERY_PROJECT_ID not set; using in-memory fallback for BigQueryService")
            return

        try:
            self._initialize_client()
        except Exception as e:
            # Fall back to in-memory mode when Google Cloud libraries are missing
            # (common in MSYS2/MinGW local dev environments)
            logger.warning(f"BigQuery client init failed, using in-memory fallback: {e}")
            self.client = None
    
    def _initialize_client(self, credentials_path: Optional[str] = None):
        """Initialize BigQuery client with credentials."""
        effective_credentials_path = credentials_path or settings.bigquery_credentials_path

        if effective_credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                effective_credentials_path
            )
            self.client = bigquery.Client(
                project=self.project_id,
                credentials=credentials
            )
        else:
            # Use Application Default Credentials
            self.client = bigquery.Client(project=self.project_id)
        
        logger.info(f"BigQuery client initialized for project {self.project_id}")
    
    def write_user_profile(self, user_id: str, name: str, email: str, 
                          password_hash: str, level: Optional[str], registration_ts: datetime,
                          questionnaire_data: Optional[Dict[str, Any]] = None,
                          is_email_verified: bool = False,
                          verification_code: Optional[str] = None,
                          verification_expires_ts: Optional[datetime] = None) -> bool:
        """
        Upsert user profile into BigQuery user_profiles table.
        Returns True on success, False if error occurs.
        """
        payload = {
            "user_id": str(user_id),
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "level": level,
            "registration_ts": registration_ts.isoformat() if hasattr(registration_ts, "isoformat") else registration_ts,
            "updated_ts": datetime.now(timezone.utc).isoformat(),
            "questionnaire_data": questionnaire_data,
            "is_email_verified": is_email_verified,
            "verification_code": verification_code,
            "verification_expires_ts": verification_expires_ts.isoformat() if hasattr(verification_expires_ts, "isoformat") and verification_expires_ts else verification_expires_ts,
        }
        serialized_questionnaire_data = self._serialize_questionnaire_data(questionnaire_data)

        try:
            table_id = f"{self.project_id}.{self.dataset_id}.user_profiles"
            # If client is not initialized, write to in-memory store
            if not self.client:
                self._in_memory["user_profiles"][payload["user_id"]] = {
                    "user_id": payload["user_id"],
                    "name": payload["name"],
                    "email": payload["email"],
                    "password_hash": payload["password_hash"],
                    "level": payload["level"],
                    "registration_ts": payload["registration_ts"],
                    "updated_ts": payload["updated_ts"],
                    "questionnaire_data": payload["questionnaire_data"],
                    "is_email_verified": payload["is_email_verified"],
                    "verification_code": payload["verification_code"],
                    "verification_expires_ts": payload["verification_expires_ts"],
                }
                logger.debug(f"(in-memory) wrote user profile for {user_id}")
                return True

            query = f"""#standardSQL
MERGE `{table_id}` T
USING (
    SELECT
        @user_id AS user_id,
        @name AS name,
        @email AS email,
        @password_hash AS password_hash,
        @level AS level,
        @registration_ts AS registration_ts,
        @updated_ts AS updated_ts,
        @questionnaire_data AS questionnaire_data,
        @is_email_verified AS is_email_verified,
        @verification_code AS verification_code,
        @verification_expires_ts AS verification_expires_ts
) S
ON T.user_id = S.user_id
WHEN MATCHED THEN
    UPDATE SET
        name = S.name,
        email = S.email,
        password_hash = S.password_hash,
        level = S.level,
        registration_ts = S.registration_ts,
        updated_ts = S.updated_ts,
        questionnaire_data = S.questionnaire_data,
        is_email_verified = S.is_email_verified,
        verification_code = S.verification_code,
        verification_expires_ts = S.verification_expires_ts
WHEN NOT MATCHED THEN
    INSERT (user_id, name, email, password_hash, level, registration_ts, updated_ts, questionnaire_data, is_email_verified, verification_code, verification_expires_ts)
    VALUES (S.user_id, S.name, S.email, S.password_hash, S.level, S.registration_ts, S.updated_ts, S.questionnaire_data, S.is_email_verified, S.verification_code, S.verification_expires_ts)
"""
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", payload["user_id"]),
                    bigquery.ScalarQueryParameter("name", "STRING", payload["name"]),
                    bigquery.ScalarQueryParameter("email", "STRING", payload["email"]),
                    bigquery.ScalarQueryParameter("password_hash", "STRING", payload["password_hash"]),
                    bigquery.ScalarQueryParameter("level", "STRING", payload["level"]),
                    bigquery.ScalarQueryParameter("registration_ts", "TIMESTAMP", payload["registration_ts"]),
                    bigquery.ScalarQueryParameter("updated_ts", "TIMESTAMP", payload["updated_ts"]),
                    bigquery.ScalarQueryParameter("questionnaire_data", "STRING", serialized_questionnaire_data),
                    bigquery.ScalarQueryParameter("is_email_verified", "BOOL", payload["is_email_verified"]),
                    bigquery.ScalarQueryParameter("verification_code", "STRING", payload["verification_code"]),
                    bigquery.ScalarQueryParameter("verification_expires_ts", "TIMESTAMP", payload["verification_expires_ts"]),
                ]
            )
            try:
                self.client.query(query, job_config=job_config).result(timeout=30)
            except Exception as e:
                if self._is_missing_column_error(e):
                    logger.warning("Detected missing user_profiles column; updating BigQuery schema and retrying")
                    self.create_dataset_and_tables()
                    self.client.query(query, job_config=job_config).result(timeout=30)
                else:
                    raise
            logger.debug(f"Successfully wrote user profile for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error writing user profile to BigQuery: {e}")
            raise
    
    def write_assessment(self, assessment_id: str, user_id: str, answers: Dict[str, str],
                        level: str, confidence: float, classification_source: str,
                        created_ts: datetime) -> bool:
        """
        Write questionnaire assessment to BigQuery questionnaire_assessments_wide table.
        Returns True on success, False if error occurs.
        """
        payload = {
            "assessment_id": str(assessment_id),
            "user_id": str(user_id),
            "q1_travel_frequency": answers.get("q1_travel_frequency", ""),
            "q2_distance_from_medical": answers.get("q2_distance_from_medical", ""),
            "q3_certification_status": answers.get("q3_certification_status", ""),
            "q4_real_life_experience": answers.get("q4_real_life_experience", ""),
            "q5_trauma_supplies_comfort": answers.get("q5_trauma_supplies_comfort", ""),
            "q6_group_role": answers.get("q6_group_role", ""),
            "level": level,
            "confidence": float(confidence),
            "classification_source": classification_source,
            "created_ts": created_ts.isoformat() if hasattr(created_ts, "isoformat") else created_ts,
        }
        
        try:
            if not self.client:
                # store assessments keyed by assessment_id
                self._in_memory["assessments"][payload["assessment_id"]] = payload
                logger.debug(f"(in-memory) wrote assessment {assessment_id}")
                return True

            table_id = f"{self.project_id}.{self.dataset_id}.questionnaire_assessments_wide"
            payload = self._coerce_payload_for_table_schema(table_id, payload)
            errors = self.client.insert_rows_json(table_id, [payload])
            if errors:
                logger.error(f"BigQuery write errors for assessment {assessment_id}: {errors}")
                raise Exception(f"BigQuery write errors: {errors}")
            logger.debug(f"Successfully wrote assessment {assessment_id}")
            return True
        except Exception as e:
            logger.error(f"Error writing assessment to BigQuery: {e}")
            raise

    def get_user_profile_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            # If client is not initialized, return from in-memory store
            if not self.client:
                row = self._in_memory["user_profiles"].get(str(user_id))
                if not row:
                    return None
                return self._attach_latest_questionnaire_data(dict(row))

            table_id = f"{self.project_id}.{self.dataset_id}.user_profiles"
            query = f"""#standardSQL
SELECT * FROM `{table_id}`
WHERE user_id = @user_id
LIMIT 1
"""
            job_config = bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", str(user_id))]
            )
            results = list(self.client.query(query, job_config=job_config).result(timeout=10))
            if not results:
                return None
            return self._attach_latest_questionnaire_data(dict(results[0]))
        except Exception as e:
            logger.error(f"Error reading user profile from BigQuery: {e}")
            raise

    def get_user_profile_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            # If client is not initialized, search in-memory store
            if not self.client:
                for row in self._in_memory["user_profiles"].values():
                    if row.get("email") == email:
                        return self._attach_latest_questionnaire_data(dict(row))
                return None

            table_id = f"{self.project_id}.{self.dataset_id}.user_profiles"
            query = f"""#standardSQL
SELECT * FROM `{table_id}`
WHERE email = @email
LIMIT 1
"""
            job_config = bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", email)]
            )
            results = list(self.client.query(query, job_config=job_config).result(timeout=10))
            if not results:
                return None
            return self._attach_latest_questionnaire_data(dict(results[0]))
        except Exception as e:
            logger.error(f"Error reading user profile by email from BigQuery: {e}")
            raise

    def get_latest_assessment_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            # If client is not initialized, return latest from in-memory assessments
            if not self.client:
                items = [v for v in self._in_memory["assessments"].values() if v.get("user_id") == str(user_id)]
                if not items:
                    return None
                # created_ts is stored as ISO string; sort descending
                items.sort(key=lambda x: x.get("created_ts"), reverse=True)
                return items[0]

            table_id = f"{self.project_id}.{self.dataset_id}.questionnaire_assessments_wide"
            created_ts_field = self._get_table_field(table_id, "created_ts")
            if created_ts_field and created_ts_field.mode == "REPEATED":
                order_by_created_ts = "IF(ARRAY_LENGTH(created_ts) > 0, created_ts[OFFSET(0)], NULL)"
            else:
                order_by_created_ts = "created_ts"
            query = f"""#standardSQL
SELECT * FROM `{table_id}`
WHERE user_id = @user_id
ORDER BY {order_by_created_ts} DESC
LIMIT 1
"""
            job_config = bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", str(user_id))]
            )
            results = list(self.client.query(query, job_config=job_config).result(timeout=10))
            if results:
                return dict(results[0])
            return None
        except Exception as e:
            logger.error(f"Error reading latest assessment from BigQuery: {e}")
            raise

    def get_medical_profile_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            if not self.client:
                row = self._in_memory["medical_profiles"].get(str(user_id))
                return dict(row) if row else None

            table_id = f"{self.project_id}.{self.dataset_id}.user_medical_profiles"
            query = f"""#standardSQL
SELECT * FROM `{table_id}`
WHERE user_id = @user_id
LIMIT 1
"""
            job_config = bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", str(user_id))]
            )
            results = list(self.client.query(query, job_config=job_config).result(timeout=10))
            if not results:
                return None
            return dict(results[0])
        except Exception as e:
            logger.error(f"Error reading medical profile from BigQuery: {e}")
            raise

    def upsert_medical_profile(self, user_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        existing = self.get_medical_profile_by_user_id(user_id)
        medical_profile_id = str(existing.get("medical_profile_id")) if existing else str(fields.get("medical_profile_id") or "")
        if not medical_profile_id:
            import uuid

            medical_profile_id = str(uuid.uuid4())

        allowed_fields = [
            "sex",
            "age",
            "special_conditions",
            "chronic_illnesses",
            "everyday_medicines",
            "allergies",
            "emergency_contact_name",
            "emergency_contact_phone",
            "blood_type",
            "medical_notes",
        ]
        payload = {
            "medical_profile_id": medical_profile_id,
            "user_id": str(user_id),
            "created_ts": existing.get("created_ts") if existing else now.isoformat(),
            "updated_ts": now.isoformat(),
        }
        for key in allowed_fields:
            payload[key] = fields.get(key, existing.get(key) if existing else None)

        try:
            if not self.client:
                self._in_memory["medical_profiles"][str(user_id)] = payload
                return dict(payload)

            table_id = f"{self.project_id}.{self.dataset_id}.user_medical_profiles"
            query = f"""#standardSQL
MERGE `{table_id}` T
USING (
    SELECT
        @medical_profile_id AS medical_profile_id,
        @user_id AS user_id,
        @sex AS sex,
        @age AS age,
        @special_conditions AS special_conditions,
        @chronic_illnesses AS chronic_illnesses,
        @everyday_medicines AS everyday_medicines,
        @allergies AS allergies,
        @emergency_contact_name AS emergency_contact_name,
        @emergency_contact_phone AS emergency_contact_phone,
        @blood_type AS blood_type,
        @medical_notes AS medical_notes,
        @created_ts AS created_ts,
        @updated_ts AS updated_ts
) S
ON T.user_id = S.user_id
WHEN MATCHED THEN
    UPDATE SET
        sex = S.sex,
        age = S.age,
        special_conditions = S.special_conditions,
        chronic_illnesses = S.chronic_illnesses,
        everyday_medicines = S.everyday_medicines,
        allergies = S.allergies,
        emergency_contact_name = S.emergency_contact_name,
        emergency_contact_phone = S.emergency_contact_phone,
        blood_type = S.blood_type,
        medical_notes = S.medical_notes,
        updated_ts = S.updated_ts
WHEN NOT MATCHED THEN
    INSERT (medical_profile_id, user_id, sex, age, special_conditions, chronic_illnesses, everyday_medicines, allergies, emergency_contact_name, emergency_contact_phone, blood_type, medical_notes, created_ts, updated_ts)
    VALUES (S.medical_profile_id, S.user_id, S.sex, S.age, S.special_conditions, S.chronic_illnesses, S.everyday_medicines, S.allergies, S.emergency_contact_name, S.emergency_contact_phone, S.blood_type, S.medical_notes, S.created_ts, S.updated_ts)
"""
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("medical_profile_id", "STRING", payload["medical_profile_id"]),
                    bigquery.ScalarQueryParameter("user_id", "STRING", payload["user_id"]),
                    bigquery.ScalarQueryParameter("sex", "STRING", payload["sex"]),
                    bigquery.ScalarQueryParameter("age", "INT64", payload["age"]),
                    bigquery.ScalarQueryParameter("special_conditions", "STRING", payload["special_conditions"]),
                    bigquery.ScalarQueryParameter("chronic_illnesses", "STRING", payload["chronic_illnesses"]),
                    bigquery.ScalarQueryParameter("everyday_medicines", "STRING", payload["everyday_medicines"]),
                    bigquery.ScalarQueryParameter("allergies", "STRING", payload["allergies"]),
                    bigquery.ScalarQueryParameter("emergency_contact_name", "STRING", payload["emergency_contact_name"]),
                    bigquery.ScalarQueryParameter("emergency_contact_phone", "STRING", payload["emergency_contact_phone"]),
                    bigquery.ScalarQueryParameter("blood_type", "STRING", payload["blood_type"]),
                    bigquery.ScalarQueryParameter("medical_notes", "STRING", payload["medical_notes"]),
                    bigquery.ScalarQueryParameter("created_ts", "TIMESTAMP", payload["created_ts"]),
                    bigquery.ScalarQueryParameter("updated_ts", "TIMESTAMP", payload["updated_ts"]),
                ]
            )
            self.client.query(query, job_config=job_config).result(timeout=30)
            return payload
        except Exception as e:
            logger.error(f"Error writing medical profile to BigQuery: {e}")
            raise

    def delete_medical_profile_by_user_id(self, user_id: str) -> bool:
        try:
            if not self.client:
                self._in_memory["medical_profiles"].pop(str(user_id), None)
                return True

            table_id = f"{self.project_id}.{self.dataset_id}.user_medical_profiles"
            query = f"""#standardSQL
DELETE FROM `{table_id}`
WHERE user_id = @user_id
"""
            job_config = bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", str(user_id))]
            )
            self.client.query(query, job_config=job_config).result(timeout=30)
            return True
        except Exception as e:
            logger.error(f"Error deleting medical profile from BigQuery: {e}")
            raise

    def create_password_reset_token(self, reset_id: str, user_id: str, email: str, reset_code_hash: str, expires_ts: datetime, created_ts: datetime) -> bool:
        payload = {
            "reset_id": str(reset_id),
            "user_id": str(user_id),
            "email": email,
            "reset_code_hash": reset_code_hash,
            "expires_ts": expires_ts.isoformat() if hasattr(expires_ts, "isoformat") else expires_ts,
            "used": False,
            "created_ts": created_ts.isoformat() if hasattr(created_ts, "isoformat") else created_ts,
            "used_ts": None,
        }
        try:
            if not self.client:
                self._in_memory["password_reset_tokens"][payload["reset_id"]] = payload
                return True

            table_id = f"{self.project_id}.{self.dataset_id}.password_reset_tokens"
            errors = self.client.insert_rows_json(table_id, [payload])
            if errors:
                logger.error("BigQuery write errors for password reset token: %s", errors)
                raise Exception(f"BigQuery write errors: {errors}")
            return True
        except Exception as e:
            logger.error(f"Error writing password reset token to BigQuery: {e}")
            raise

    def get_active_password_reset_tokens_by_email(self, email: str) -> list:
        now = datetime.now(timezone.utc)
        try:
            if not self.client:
                tokens = []
                for row in self._in_memory["password_reset_tokens"].values():
                    if row.get("email") != email or row.get("used"):
                        continue
                    expires_ts = row.get("expires_ts")
                    expires_dt = self._parse_datetime(expires_ts)
                    if expires_dt and expires_dt >= now:
                        tokens.append(dict(row))
                tokens.sort(key=lambda row: row.get("created_ts") or "", reverse=True)
                return tokens

            table_id = f"{self.project_id}.{self.dataset_id}.password_reset_tokens"
            query = f"""#standardSQL
SELECT t.* FROM `{table_id}` AS t
WHERE t.email = @email
  AND t.used = FALSE
  AND t.expires_ts >= CURRENT_TIMESTAMP()
  AND NOT EXISTS (
    SELECT 1
    FROM `{table_id}` AS used_marker
    WHERE used_marker.reset_id = t.reset_id
      AND used_marker.used = TRUE
  )
ORDER BY t.created_ts DESC
LIMIT 10
"""
            job_config = bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", email)]
            )
            return [dict(row) for row in self.client.query(query, job_config=job_config).result(timeout=10)]
        except Exception as e:
            logger.error(f"Error reading password reset tokens from BigQuery: {e}")
            raise

    def mark_password_reset_token_used(self, reset_id: str, used_ts: datetime) -> bool:
        try:
            if not self.client:
                token = self._in_memory["password_reset_tokens"].get(str(reset_id))
                if not token:
                    return False
                token["used"] = True
                token["used_ts"] = used_ts.isoformat()
                return True

            table_id = f"{self.project_id}.{self.dataset_id}.password_reset_tokens"
            # BigQuery rejects UPDATE/DELETE for rows that are still in the streaming buffer.
            # Password reset tokens are often consumed immediately after being streamed, so
            # mark usage with an append-only marker row and exclude marked reset_id values
            # from get_active_password_reset_tokens_by_email().
            payload = {
                "reset_id": str(reset_id),
                "user_id": "",
                "email": "",
                "reset_code_hash": "",
                "expires_ts": used_ts.isoformat() if hasattr(used_ts, "isoformat") else used_ts,
                "used": True,
                "created_ts": used_ts.isoformat() if hasattr(used_ts, "isoformat") else used_ts,
                "used_ts": used_ts.isoformat() if hasattr(used_ts, "isoformat") else used_ts,
            }
            errors = self.client.insert_rows_json(table_id, [payload])
            if errors:
                logger.error("BigQuery write errors for password reset used marker: %s", errors)
                raise Exception(f"BigQuery write errors: {errors}")
            return True
        except Exception as e:
            logger.error(f"Error marking password reset token used in BigQuery: {e}")
            raise

    def _attach_latest_questionnaire_data(self, user_row: Dict[str, Any]) -> Dict[str, Any]:
        """Attach questionnaire_data derived from the latest assessment for compatibility."""
        user_id = str(user_row.get("user_id") or user_row.get("id") or "")
        try:
            assessment = self.get_latest_assessment_by_user_id(user_id)
        except Exception as e:
            logger.warning(f"Could not attach latest assessment for user {user_id}: {e}")
            assessment = None
        questionnaire_data = self._parse_questionnaire_data(user_row.get("questionnaire_data"))
        if questionnaire_data is None and assessment:
            questionnaire_data = {
                "answers": [
                    self._scalar_from_bigquery_value(assessment.get("q1_travel_frequency")),
                    self._scalar_from_bigquery_value(assessment.get("q2_distance_from_medical")),
                    self._scalar_from_bigquery_value(assessment.get("q3_certification_status")),
                    self._scalar_from_bigquery_value(assessment.get("q4_real_life_experience")),
                    self._scalar_from_bigquery_value(assessment.get("q5_trauma_supplies_comfort")),
                    self._scalar_from_bigquery_value(assessment.get("q6_group_role")),
                ],
                "confidence": self._scalar_from_bigquery_value(assessment.get("confidence")),
                "classification_source": self._scalar_from_bigquery_value(assessment.get("classification_source")),
            }

        row_user_id = self._scalar_from_bigquery_value(user_row.get("user_id") or user_row.get("id"))
        return {
            "id": row_user_id,
            "user_id": row_user_id,
            "name": self._scalar_from_bigquery_value(user_row.get("name")),
            "email": self._scalar_from_bigquery_value(user_row.get("email")),
            "level": self._scalar_from_bigquery_value(user_row.get("level")),
            "registration_date": user_row.get("registration_ts") or user_row.get("registration_date"),
            "updated_ts": user_row.get("updated_ts"),
            "password_hash": user_row.get("password_hash"),
            "questionnaire_data": questionnaire_data,
            "is_email_verified": user_row.get("is_email_verified", False),
            "verification_code": user_row.get("verification_code"),
            "verification_expires_ts": user_row.get("verification_expires_ts"),
        }

    def _serialize_questionnaire_data(self, questionnaire_data: Optional[Dict[str, Any]]) -> Optional[str]:
        if questionnaire_data is None:
            return None
        try:
            return json.dumps(questionnaire_data, ensure_ascii=False)
        except TypeError:
            logger.warning("Failed to serialize questionnaire_data; storing no questionnaire payload")
            return None

    def _parse_questionnaire_data(self, questionnaire_data: Any) -> Optional[Dict[str, Any]]:
        if questionnaire_data is None or questionnaire_data == "":
            return None
        if isinstance(questionnaire_data, dict):
            return questionnaire_data
        if isinstance(questionnaire_data, str):
            try:
                parsed = json.loads(questionnaire_data)
                return parsed if isinstance(parsed, dict) else None
            except (TypeError, json.JSONDecodeError):
                logger.warning("Failed to parse questionnaire_data from stored payload")
                return None
        return None

    def _is_missing_column_error(self, error: Exception) -> bool:
        message = str(error).lower()
        return "unrecognized name" in message or "no such field" in message

    def _ensure_table_columns(self, table_id: str, required_schema: list) -> None:
        """Add nullable columns that are missing from an existing BigQuery table."""
        table = self.client.get_table(table_id)
        existing_names = {field.name for field in table.schema}
        missing_fields = [field for field in required_schema if field.name not in existing_names]
        if not missing_fields:
            return

        non_nullable_missing = [field.name for field in missing_fields if field.mode == "REQUIRED"]
        if non_nullable_missing:
            logger.warning(
                "BigQuery table %s is missing required columns that cannot be auto-added safely: %s",
                table_id,
                ", ".join(non_nullable_missing),
            )

        addable_fields = [field for field in missing_fields if field.mode != "REQUIRED"]
        if not addable_fields:
            return

        table.schema = list(table.schema) + addable_fields
        self.client.update_table(table, ["schema"])
        logger.info(
            "Added missing BigQuery columns to %s: %s",
            table_id,
            ", ".join(field.name for field in addable_fields),
        )

    def _get_table_field(self, table_id: str, field_name: str):
        try:
            table = self.client.get_table(table_id)
            for field in table.schema:
                if field.name == field_name:
                    return field
        except Exception as e:
            logger.warning(f"Could not inspect BigQuery table schema for {table_id}: {e}")
        return None

    def _coerce_payload_for_table_schema(self, table_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Match insert payload values to the current BigQuery table schema.

        Some existing demo tables were created with repeated fields. This keeps
        the app compatible with those tables without dropping or recreating data.
        """
        try:
            table = self.client.get_table(table_id)
        except Exception as e:
            logger.warning(f"Could not inspect BigQuery table schema for payload coercion: {e}")
            return payload

        coerced = dict(payload)
        fields_by_name = {field.name: field for field in table.schema}
        for key, value in list(coerced.items()):
            field = fields_by_name.get(key)
            if not field:
                continue
            if field.mode == "REPEATED" and not isinstance(value, list):
                coerced[key] = [value]
            elif field.mode != "REPEATED" and isinstance(value, list):
                coerced[key] = value[0] if value else None
        return coerced

    def _scalar_from_bigquery_value(self, value: Any) -> Any:
        if isinstance(value, list):
            return value[0] if value else None
        return value

    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                return None
        return None
    

    def create_dataset_and_tables(self) -> bool:
        """
        Create BigQuery dataset and tables if they don't exist.
        Returns True on success, raises Exception on failure.
        """
        try:
            # Create dataset
            dataset_id_full = f"{self.project_id}.{self.dataset_id}"
            dataset = bigquery.Dataset(dataset_id_full)
            dataset.location = "EU"
            
            dataset = self.client.create_dataset(dataset, exists_ok=True, timeout=30)
            logger.info(f"Dataset {dataset_id_full} created or already exists")
            
            # Create user_profiles table
            user_profiles_table_id = f"{self.project_id}.{self.dataset_id}.user_profiles"
            user_profiles_schema = [
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("password_hash", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("level", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("registration_ts", "TIMESTAMP", mode="NULLABLE"),
                bigquery.SchemaField("updated_ts", "TIMESTAMP", mode="NULLABLE"),
                bigquery.SchemaField("questionnaire_data", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("is_email_verified", "BOOL", mode="NULLABLE"),
                bigquery.SchemaField("verification_code", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("verification_expires_ts", "TIMESTAMP", mode="NULLABLE"),
            ]
            
            user_profiles_table = bigquery.Table(user_profiles_table_id, schema=user_profiles_schema)
            user_profiles_table = self.client.create_table(user_profiles_table, exists_ok=True, timeout=30)
            self._ensure_table_columns(user_profiles_table_id, user_profiles_schema)
            logger.info(f"Table {user_profiles_table_id} created or already exists")
            
            # Create questionnaire_assessments_wide table
            assessments_table_id = f"{self.project_id}.{self.dataset_id}.questionnaire_assessments_wide"
            assessments_schema = [
                bigquery.SchemaField("assessment_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("q1_travel_frequency", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("q2_distance_from_medical", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("q3_certification_status", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("q4_real_life_experience", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("q5_trauma_supplies_comfort", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("q6_group_role", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("level", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("confidence", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("classification_source", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("created_ts", "TIMESTAMP", mode="REQUIRED"),
            ]
            
            assessments_table = bigquery.Table(assessments_table_id, schema=assessments_schema)
            assessments_table = self.client.create_table(assessments_table, exists_ok=True, timeout=30)
            self._ensure_table_columns(assessments_table_id, assessments_schema)
            logger.info(f"Table {assessments_table_id} created or already exists")

            medical_profiles_table_id = f"{self.project_id}.{self.dataset_id}.user_medical_profiles"
            medical_profiles_schema = [
                bigquery.SchemaField("medical_profile_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("sex", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("age", "INT64", mode="NULLABLE"),
                bigquery.SchemaField("special_conditions", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("chronic_illnesses", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("everyday_medicines", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("allergies", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("emergency_contact_name", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("emergency_contact_phone", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("blood_type", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("medical_notes", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("created_ts", "TIMESTAMP", mode="NULLABLE"),
                bigquery.SchemaField("updated_ts", "TIMESTAMP", mode="NULLABLE"),
            ]
            medical_profiles_table = bigquery.Table(medical_profiles_table_id, schema=medical_profiles_schema)
            medical_profiles_table = self.client.create_table(medical_profiles_table, exists_ok=True, timeout=30)
            self._ensure_table_columns(medical_profiles_table_id, medical_profiles_schema)
            logger.info(f"Table {medical_profiles_table_id} created or already exists")

            reset_tokens_table_id = f"{self.project_id}.{self.dataset_id}.password_reset_tokens"
            reset_tokens_schema = [
                bigquery.SchemaField("reset_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("reset_code_hash", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("expires_ts", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("used", "BOOL", mode="REQUIRED"),
                bigquery.SchemaField("created_ts", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("used_ts", "TIMESTAMP", mode="NULLABLE"),
            ]
            reset_tokens_table = bigquery.Table(reset_tokens_table_id, schema=reset_tokens_schema)
            reset_tokens_table = self.client.create_table(reset_tokens_table, exists_ok=True, timeout=30)
            self._ensure_table_columns(reset_tokens_table_id, reset_tokens_schema)
            logger.info(f"Table {reset_tokens_table_id} created or already exists")
            
            return True
        except Exception as e:
            logger.error(f"Error creating BigQuery dataset/tables: {e}")
            raise


# Global service instance
bq_service: Optional[BigQueryService] = None


def get_bq_service() -> BigQueryService:
    """Get or initialize BigQuery service."""
    global bq_service
    if bq_service is None:
        bq_service = BigQueryService()
    return bq_service





