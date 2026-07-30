from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from ..core.auth import get_current_user
from ..core.bigquery_service import get_bq_service
from ..schemas.profile import AccountProfileResponse, AccountProfileUpdate, MedicalProfileResponse, MedicalProfileUpdate

router = APIRouter()


def _extract_user_id(user_row: dict) -> str:
    return str(user_row.get("user_id") or user_row.get("id") or "").strip()


def _scalar(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _safe_latest_assessment(user_id: str) -> dict | None:
    bq_service = get_bq_service()
    latest = bq_service.get_latest_assessment_by_user_id(user_id)
    if not latest:
        return None
    return {
        "level": _scalar(latest.get("level")),
        "confidence": _scalar(latest.get("confidence")),
        "classification_source": _scalar(latest.get("classification_source")),
        "created_ts": _scalar(latest.get("created_ts")),
    }


def _account_response(user_row: dict) -> AccountProfileResponse:
    user_id = _extract_user_id(user_row)
    return AccountProfileResponse(
        user_id=user_id,
        name=user_row.get("name") or "",
        email=user_row.get("email") or "",
        level=user_row.get("level"),
        email_verified=bool(user_row.get("is_email_verified", False)),
        registration_ts=user_row.get("registration_date") or user_row.get("registration_ts"),
        updated_ts=user_row.get("updated_ts"),
        latest_assessment=_safe_latest_assessment(user_id),
    )


def _empty_medical_profile(user_id: str) -> MedicalProfileResponse:
    return MedicalProfileResponse(user_id=user_id)


@router.get("/me", response_model=AccountProfileResponse)
async def get_account_profile(current_user: dict = Depends(get_current_user)):
    return _account_response(current_user)


@router.patch("/me", response_model=AccountProfileResponse)
async def update_account_profile(update: AccountProfileUpdate, current_user: dict = Depends(get_current_user)):
    user_id = _extract_user_id(current_user)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authenticated user")

    bq_service = get_bq_service()
    existing = bq_service.get_user_profile_by_id(user_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not bq_service.write_user_profile(
        user_id=user_id,
        name=update.name,
        email=existing.get("email") or "",
        password_hash=existing.get("password_hash") or "",
        level=existing.get("level"),
        registration_ts=existing.get("registration_date") or existing.get("registration_ts") or datetime.now(timezone.utc),
        questionnaire_data=existing.get("questionnaire_data"),
        is_email_verified=bool(existing.get("is_email_verified", False)),
        verification_code=existing.get("verification_code"),
        verification_expires_ts=existing.get("verification_expires_ts"),
    ):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update profile")

    refreshed = bq_service.get_user_profile_by_id(user_id)
    return _account_response(refreshed or {**existing, "name": update.name})


@router.get("/medical", response_model=MedicalProfileResponse)
async def get_medical_profile(current_user: dict = Depends(get_current_user)):
    user_id = _extract_user_id(current_user)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authenticated user")

    profile = get_bq_service().get_medical_profile_by_user_id(user_id)
    if profile is None:
        return _empty_medical_profile(user_id)
    return MedicalProfileResponse(**profile)


@router.put("/medical", response_model=MedicalProfileResponse)
async def put_medical_profile(update: MedicalProfileUpdate, current_user: dict = Depends(get_current_user)):
    return await _save_medical_profile(update, current_user)


@router.patch("/medical", response_model=MedicalProfileResponse)
async def patch_medical_profile(update: MedicalProfileUpdate, current_user: dict = Depends(get_current_user)):
    return await _save_medical_profile(update, current_user)


@router.delete("/medical", response_model=dict)
async def delete_medical_profile(current_user: dict = Depends(get_current_user)):
    user_id = _extract_user_id(current_user)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authenticated user")

    if not get_bq_service().delete_medical_profile_by_user_id(user_id):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to clear medical profile")

    return {"message": "Medical profile cleared"}


async def _save_medical_profile(update: MedicalProfileUpdate, current_user: dict) -> MedicalProfileResponse:
    user_id = _extract_user_id(current_user)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authenticated user")

    if hasattr(update, "model_dump"):
        fields = update.model_dump(exclude_unset=True)
    else:
        fields = update.dict(exclude_unset=True)

    saved = get_bq_service().upsert_medical_profile(user_id, fields)
    return MedicalProfileResponse(**saved)
