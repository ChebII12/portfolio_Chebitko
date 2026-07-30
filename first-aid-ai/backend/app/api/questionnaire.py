from datetime import datetime, timezone
from typing import List, Optional, Tuple
import httpx
import json
import uuid

from fastapi import APIRouter, HTTPException, status, Depends

from ..core.bigquery_service import get_bq_service
from ..core.auth import get_current_user
from ..core.config import settings
from ..schemas.questionnaire import QuestionnaireAnalyzeRequest, QuestionnaireAnalyzeResponse

router = APIRouter()

ALLOWED_ANSWERS = [
    {"rarely", "monthly", "weekly", "a few times a year"},
    {"close", "hours", "day", "always close", "a few hours away", "day or more"},
    {"none", "old", "current", "advanced", "no", "yes, but a long time ago", "yes, currently certified", "yes, advanced instructor/responder", "advanced training (emt, etc.)"},
    {"none", "minor", "critical", "no", "yes, for minor injuries", "yes, for critical emergencies", "critical emergencies"},
    {"unknown", "theory", "trained", "i don't know how to use them", "know in theory only", "i am trained and confident", "don't know what they are", "trained and comfortable using"},
    {"solo", "group", "medic", "mostly solo", "in groups, not designated medic", "in a group, but not responsible", "designated group medic/leader", "in a group, as the designated medic/leader", "travel solo"},
]

ANSWER_SCORES = [
    {"rarely": 0, "a few times a year": 1, "monthly": 1, "weekly": 2},
    {"always close": 0, "close": 0, "a few hours away": 1, "hours": 1, "day or more": 2, "day": 2},
    {"no": 0, "none": 0, "yes, but a long time ago": 0, "old": 0, "yes, currently certified": 1, "current": 1, "yes, advanced instructor/responder": 2, "advanced training (emt, etc.)": 2, "advanced": 2},
    {"no": 0, "none": 0, "yes, for minor injuries": 1, "minor": 1, "yes, for critical emergencies": 2, "critical emergencies": 2, "critical": 2},
    {"i don't know how to use them": 0, "don't know what they are": 0, "unknown": 0, "i know the theory": 1, "know in theory only": 1, "theory": 1, "i am trained and confident": 2, "trained and comfortable using": 2, "trained": 2},
    {"mostly solo": 0, "travel solo": 0, "solo": 0, "in a group, but not responsible": 1, "in groups, not designated medic": 1, "group": 1, "in a group, as the designated medic/leader": 2, "designated group medic/leader": 2, "medic": 2},
]


def _normalize_answer(answer: str) -> str:
    return answer.strip().lower()


def _validate_answers(answers: List[str]) -> None:
    if len(answers) != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactly 6 answers are required"
        )

    for index, answer in enumerate(answers):
        if _normalize_answer(answer) not in ALLOWED_ANSWERS[index]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid answer for question {index + 1}"
            )


def _classify_answers_locally(answers: List[str]) -> Tuple[str, float]:
    max_score = 12
    score = 0
    for index, answer in enumerate(answers):
        normalized = _normalize_answer(answer)
        score += ANSWER_SCORES[index].get(normalized, 0)

    normalized_score = score / max_score
    if normalized_score >= 0.75:
        level = "expert"
    elif normalized_score >= 0.40:
        level = "intermediate"
    else:
        level = "beginner"

    return level, round(normalized_score, 2)


def _level_explanation(level: str, source: str) -> str:
    explanations = {
        "beginner": "Detailed step-by-step first aid guidance will be shown because your answers indicate limited recent training or emergency practice.",
        "intermediate": "Balanced guidance with practical context will be shown because your answers indicate some training, travel exposure, or emergency experience.",
        "expert": "Concise advanced guidance will be shown because your answers indicate strong training, frequent travel exposure, or leadership responsibility.",
    }
    explanation = explanations.get(level, explanations["beginner"])
    if source == "questionnaire_skipped":
        return "Beginner was assigned as the safest default because the questionnaire was skipped."
    if source == "deterministic_fallback":
        return f"{explanation} The deterministic fallback was used because AI classification was unavailable or failed."
    return explanation


def _parse_ai_response(content: str) -> Tuple[str, float]:
    cleaned = content.strip().strip("`")
    if cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()

    parsed = json.loads(cleaned)
    level = parsed.get("level", "beginner")
    confidence = float(parsed.get("confidence", 0.0))
    if level not in ["beginner", "intermediate", "expert"]:
        raise ValueError("Invalid level from AI")

    if confidence < 0.0 or confidence > 1.0:
        confidence = 0.0
    return level, round(confidence, 2)


def _is_ai_result_safe(ai_level: str, ai_confidence: float, local_level: str, local_confidence: float) -> bool:
    """Reject low-confidence or clearly contradictory AI classifications."""
    if ai_level not in ["beginner", "intermediate", "expert"]:
        return False
    if ai_confidence < 0.5:
        return False

    level_rank = {"beginner": 0, "intermediate": 1, "expert": 2}
    rank_distance = abs(level_rank[ai_level] - level_rank[local_level])
    if local_confidence >= 0.75 and rank_distance > 1:
        return False
    if local_confidence <= 0.25 and rank_distance > 1:
        return False
    return True


def _validate_request_user_id(legacy_user_id: Optional[str], authenticated_user_id: str) -> None:
    legacy_user_id = (legacy_user_id or "").strip()
    if not legacy_user_id:
        return

    try:
        parsed_legacy_user_id = str(uuid.UUID(legacy_user_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format",
        )

    if parsed_legacy_user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token user does not match questionnaire user_id",
        )


def _persist_assessment_result(
    *,
    bq_service,
    user_uuid: uuid.UUID,
    db_user: dict,
    answers: List[str],
    level: str,
    confidence: float,
    classification_source: str,
) -> str:
    assessment_id = str(uuid.uuid4())
    created_ts = datetime.now(timezone.utc)
    questionnaire_data = {
        "answers": answers,
        "confidence": confidence,
        "classification_source": classification_source,
        "assessment_id": assessment_id,
    }

    try:
        profile_written = bq_service.write_user_profile(
            user_id=str(user_uuid),
            name=db_user.get("name"),
            email=db_user.get("email"),
            password_hash=db_user.get("password_hash") or "",
            level=level,
            registration_ts=db_user.get("registration_date") or datetime.now(timezone.utc),
            questionnaire_data=questionnaire_data,
            is_email_verified=bool(db_user.get("is_email_verified", False)),
            verification_code=db_user.get("verification_code"),
            verification_expires_ts=db_user.get("verification_expires_ts"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user level. Please retry.",
        ) from exc

    if not profile_written:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user level. Please retry.",
        )

    try:
        assessment_written = bq_service.write_assessment(
            assessment_id=assessment_id,
            user_id=str(user_uuid),
            answers={
                "q1_travel_frequency": answers[0],
                "q2_distance_from_medical": answers[1],
                "q3_certification_status": answers[2],
                "q4_real_life_experience": answers[3],
                "q5_trauma_supplies_comfort": answers[4],
                "q6_group_role": answers[5],
            },
            level=level,
            confidence=confidence,
            classification_source=classification_source,
            created_ts=created_ts,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User level was saved, but the assessment row could not be saved. Please retry so BigQuery has both records.",
        ) from exc

    if not assessment_written:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User level was saved, but the assessment row could not be saved. Please retry so BigQuery has both records.",
        )

    return assessment_id


@router.post("/analyze", response_model=QuestionnaireAnalyzeResponse)
async def analyze_questionnaire(
    request: QuestionnaireAnalyzeRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = str(current_user.get("user_id") or current_user.get("id") or "").strip()
    answers = request.answers

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authenticated user is required"
        )

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user id in token"
        )

    _validate_request_user_id(request.user_id, str(user_uuid))

    bq_service = get_bq_service()
    db_user = bq_service.get_user_profile_by_id(str(user_uuid))
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    _validate_answers(answers)

    default_level, default_confidence = _classify_answers_locally(answers)

    # Construct AI prompt
    prompt = f"""
You are a medical training assessment AI. Based on the following questionnaire answers, classify the user's first aid preparation level as either "beginner", "intermediate", or "expert".

Questionnaire Answers:
1. Travel frequency: {answers[0] if len(answers) > 0 else 'N/A'}
2. Distance from medical facility: {answers[1] if len(answers) > 1 else 'N/A'}
3. First aid certification: {answers[2] if len(answers) > 2 else 'N/A'}
4. Real-life experience: {answers[3] if len(answers) > 3 else 'N/A'}
5. Trauma supplies comfort: {answers[4] if len(answers) > 4 else 'N/A'}
6. Group responsibility: {answers[5] if len(answers) > 5 else 'N/A'}

Classification Criteria:

Beginner:
- Limited travel experience (Rarely)
- Close to medical facilities (Always close)
- No formal training (No/Yes long ago)
- No real experience (No)
- Uncomfortable with supplies (Don't know)
- Travels solo or not responsible

Intermediate:
- Moderate travel experience (A few times a year/Monthly)
- Some distance from facilities (A few hours)
- Some training (Yes currently certified)
- Minor experience (Yes for minor injuries)
- Theoretical knowledge (Know theory)
- Some group responsibility

Expert:
- Frequent travel (Weekly)
- Far from facilities (Day or more)
- Advanced training (Advanced instructor)
- Critical experience (Critical emergencies)
- Confident with supplies (Trained)
- Designated medic/leader role

Return only a JSON object: {{"level": "beginner|intermediate|expert", "confidence": 0.0-1.0}}
"""

    level = default_level
    confidence = default_confidence
    classification_source = "local_rules"

    if settings.groq_api_key:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    settings.groq_api_url,
                    headers={
                        "Authorization": f"Bearer {settings.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.groq_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "max_tokens": 100
                    }
                )

                if response.status_code == 200:
                    ai_response = response.json()
                    content = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "")
                    ai_level, ai_confidence = _parse_ai_response(content)
                    if _is_ai_result_safe(ai_level, ai_confidence, default_level, default_confidence):
                        level, confidence = ai_level, ai_confidence
                        classification_source = "groq_ai"
                    else:
                        classification_source = "deterministic_fallback"
                else:
                    classification_source = "deterministic_fallback"
        except Exception:
            # Keep deterministic fallback result if external AI call fails.
            classification_source = "deterministic_fallback"

    _persist_assessment_result(
        bq_service=bq_service,
        user_uuid=user_uuid,
        db_user=db_user,
        answers=answers,
        level=level,
        confidence=confidence,
        classification_source=classification_source,
    )

    return {
        "level": level,
        "confidence": confidence,
        "explanation": _level_explanation(level, classification_source),
        "classification_source": classification_source,
        "message": "Level assessment completed"
    }


@router.post("/skip", response_model=QuestionnaireAnalyzeResponse)
async def skip_questionnaire(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("user_id") or current_user.get("id") or "").strip()
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user id in token",
        )

    bq_service = get_bq_service()
    db_user = bq_service.get_user_profile_by_id(str(user_uuid))
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    skipped_answers = ["skipped", "skipped", "skipped", "skipped", "skipped", "skipped"]
    _persist_assessment_result(
        bq_service=bq_service,
        user_uuid=user_uuid,
        db_user=db_user,
        answers=skipped_answers,
        level="beginner",
        confidence=1.0,
        classification_source="questionnaire_skipped",
    )

    return {
        "level": "beginner",
        "confidence": 1.0,
        "explanation": _level_explanation("beginner", "questionnaire_skipped"),
        "classification_source": "questionnaire_skipped",
        "message": "Beginner level assigned because questionnaire was skipped",
    }
