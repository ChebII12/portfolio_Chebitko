from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, validator


ALLOWED_SEX_VALUES = {"female", "male", "other", "prefer_not_to_say"}
ALLOWED_BLOOD_TYPES = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "unknown"}
TEXT_LIMITS = {
    "special_conditions": 1000,
    "chronic_illnesses": 1000,
    "everyday_medicines": 1000,
    "allergies": 1000,
    "medical_notes": 1500,
    "emergency_contact_name": 120,
    "emergency_contact_phone": 40,
}


class AccountProfileResponse(BaseModel):
    user_id: str
    name: str
    email: str
    level: Optional[str] = None
    email_verified: bool = False
    registration_ts: Optional[datetime] = None
    updated_ts: Optional[datetime] = None
    latest_assessment: Optional[Dict[str, Any]] = None


class AccountProfileUpdate(BaseModel):
    name: str

    @validator("name")
    def validate_name(cls, value: str) -> str:
        normalized = (value or "").strip()
        if len(normalized) < 2:
            raise ValueError("Name must be at least 2 characters long")
        if len(normalized) > 80:
            raise ValueError("Name must be 80 characters or fewer")
        return normalized


class MedicalProfileBase(BaseModel):
    sex: Optional[str] = None
    age: Optional[int] = None
    special_conditions: Optional[str] = None
    chronic_illnesses: Optional[str] = None
    everyday_medicines: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_type: Optional[str] = None
    medical_notes: Optional[str] = None

    @validator("sex")
    def validate_sex(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized == "":
            return None
        if normalized not in ALLOWED_SEX_VALUES:
            raise ValueError("Invalid sex value")
        return normalized

    @validator("blood_type")
    def validate_blood_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized == "":
            return None
        if normalized == "UNKNOWN":
            return "unknown"
        if normalized not in ALLOWED_BLOOD_TYPES:
            raise ValueError("Invalid blood type")
        return normalized

    @validator("age")
    def validate_age(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return None
        if value < 0 or value > 120:
            raise ValueError("Age must be between 0 and 120")
        return value

    @validator(
        "special_conditions",
        "chronic_illnesses",
        "everyday_medicines",
        "allergies",
        "emergency_contact_name",
        "emergency_contact_phone",
        "medical_notes",
    )
    def validate_text(cls, value: Optional[str], values, field) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        if normalized == "":
            return None
        max_length = TEXT_LIMITS[field.name]
        if len(normalized) > max_length:
            raise ValueError(f"{field.name} must be {max_length} characters or fewer")
        return normalized


class MedicalProfileUpdate(MedicalProfileBase):
    pass


class MedicalProfileResponse(MedicalProfileBase):
    medical_profile_id: Optional[str] = None
    user_id: str
    created_ts: Optional[datetime] = None
    updated_ts: Optional[datetime] = None

