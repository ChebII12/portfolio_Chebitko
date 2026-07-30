from datetime import datetime, timedelta, timezone
from typing import Optional, cast
import base64
import hashlib
import jwt
import re
import secrets
import uuid
import smtplib
import asyncio
from email.message import EmailMessage
from email.utils import formataddr

from fastapi import APIRouter, Depends, HTTPException, status

from ..core.auth import get_current_user
from ..core.bigquery_service import get_bq_service
from ..core.config import settings
from ..schemas.user import User as UserSchema, UserCreate, UserUpdate

logger = __import__("logging").getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    """Raised when a required verification email cannot be delivered."""


def _smtp_host() -> str:
    return (settings.smtp_host or settings.smtp_server or "").strip()


def _smtp_username() -> str:
    return (settings.smtp_username or settings.smtp_user or "").strip()


def _is_console_email_mode() -> bool:
    return settings.email_delivery_mode == "console"


def _can_expose_dev_verification_code() -> bool:
    return settings.app_environment.lower() != "production" and (
        _is_console_email_mode() or settings.email_log_codes
    )


def _should_log_email_codes() -> bool:
    return settings.app_environment.lower() != "production" and (
        _is_console_email_mode() or settings.email_log_codes
    )


def _can_continue_after_email_delivery_failure() -> bool:
    return settings.app_environment.lower() != "production" and settings.email_log_codes


def _build_code_email(
    *,
    email_addr: str,
    code: str,
    subject: str,
    heading: str,
    intro: str,
    expiry_text: str,
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((settings.smtp_from_name, settings.smtp_from_email))
    msg["To"] = email_addr

    plain_text = (
        f"{heading}\n\n"
        f"{intro}\n\n"
        f"Your code is: {code}\n\n"
        f"{expiry_text}\n\n"
        "If you did not request this email, you can ignore it."
    )
    msg.set_content(plain_text)

    html = f"""\
<!doctype html>
<html>
  <body style="margin:0;background:#f5f7fa;font-family:Arial,Helvetica,sans-serif;color:#102a56;">
    <div style="max-width:520px;margin:0 auto;padding:28px 16px;">
      <div style="background:#ffffff;border:1px solid #e1e6ef;border-radius:24px;padding:28px;box-shadow:0 14px 34px rgba(16,42,86,0.08);">
        <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:20px;">
          <div style="width:40px;height:40px;border-radius:12px;background:#0057d9;color:#ffffff;text-align:center;line-height:40px;font-weight:800;font-size:22px;">+</div>
          <div style="font-size:18px;font-weight:800;color:#102a56;">First Aid AI</div>
        </div>
        <h1 style="margin:0 0 12px;font-size:24px;line-height:1.25;color:#102a56;">{heading}</h1>
        <p style="margin:0 0 22px;font-size:15px;line-height:1.6;color:#5f6878;">{intro}</p>
        <div style="margin:22px 0;padding:18px;border-radius:18px;background:#eaf2ff;text-align:center;">
          <div style="font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#004aad;">Verification code</div>
          <div style="margin-top:8px;font-size:34px;letter-spacing:6px;font-weight:800;color:#004aad;">{code}</div>
        </div>
        <p style="margin:0 0 16px;font-size:14px;line-height:1.6;color:#5f6878;">{expiry_text}</p>
        <p style="margin:0;font-size:13px;line-height:1.6;color:#7a8494;">If you did not request this email, you can ignore it.</p>
      </div>
    </div>
  </body>
</html>
"""
    msg.add_alternative(html, subtype="html")
    return msg


async def send_verification_email_async(email_addr: str, code: str):
    if _should_log_email_codes():
        logger.warning("DEV EMAIL VERIFICATION CODE for %s: %s", email_addr, code)

    if _is_console_email_mode():
        return

    host = _smtp_host()
    if not host:
        logger.error("EMAIL_DELIVERY_MODE=smtp but SMTP host/server is not configured")
        raise EmailDeliveryError("SMTP host is not configured")

    def _send_email():
        msg = _build_code_email(
            email_addr=email_addr,
            code=code,
            subject="Verify your First Aid AI email",
            heading="Verify your email",
            intro="Use this code to finish creating your First Aid AI account.",
            expiry_text="This code expires in 15 minutes.",
        )

        try:
            with smtplib.SMTP(host, settings.smtp_port, timeout=15) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                username = _smtp_username()
                if username and settings.smtp_password:
                    server.login(username, settings.smtp_password)
                server.send_message(msg)
            logger.info("Verification email sent to %s via SMTP host %s", email_addr, host)
        except Exception as e:
            logger.exception("Failed to send verification email to %s via SMTP host %s: %s", email_addr, host, e)
            raise EmailDeliveryError("Verification email could not be sent") from e

    await asyncio.to_thread(_send_email)


async def send_password_reset_email_async(email_addr: str, code: str):
    if _should_log_email_codes():
        logger.warning("DEV PASSWORD RESET CODE for %s: %s", email_addr, code)

    if _is_console_email_mode():
        return

    host = _smtp_host()
    if not host:
        logger.error("EMAIL_DELIVERY_MODE=smtp but SMTP host/server is not configured for password reset")
        raise EmailDeliveryError("SMTP host is not configured")

    def _send_email():
        msg = _build_code_email(
            email_addr=email_addr,
            code=code,
            subject="Reset your First Aid AI password",
            heading="Reset your password",
            intro="Use this code to set a new password for your First Aid AI account.",
            expiry_text="This code expires in 30 minutes.",
        )

        try:
            with smtplib.SMTP(host, settings.smtp_port, timeout=15) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                username = _smtp_username()
                if username and settings.smtp_password:
                    server.login(username, settings.smtp_password)
                server.send_message(msg)
            logger.info("Password reset email sent to %s via SMTP host %s", email_addr, host)
        except Exception as e:
            logger.exception("Failed to send password reset email to %s via SMTP host %s: %s", email_addr, host, e)
            raise EmailDeliveryError("Password reset email could not be sent") from e

    await asyncio.to_thread(_send_email)

router = APIRouter()

PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 210_000
PASSWORD_SALT_BYTES = 16


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def get_password_hash(password: str) -> str:
    salt = secrets.token_bytes(PASSWORD_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${_b64encode(salt)}${_b64encode(derived)}"


def validate_password_strength(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    return re.search(r"\d", password) is not None


def validate_email(email: str) -> bool:
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email) is not None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def _parse_user_uuid(user_id: str) -> str:
    candidate = (user_id or "").strip()
    try:
        return str(uuid.UUID(candidate))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")


def _extract_user_id(user_row: dict) -> str:
    return str(user_row.get("user_id") or user_row.get("id") or "").strip()


def _normalize_level(level: Optional[str]) -> Optional[str]:
    if level is None:
        return None
    normalized = str(level).strip()
    return normalized or None


def _serialize_user(user_row: dict) -> dict:
    return {
        "id": user_row.get("id") or user_row.get("user_id"),
        "name": user_row.get("name"),
        "email": user_row.get("email"),
        "level": user_row.get("level"),
        "registration_date": user_row.get("registration_date") or user_row.get("registration_ts"),
        "questionnaire_data": user_row.get("questionnaire_data"),
    }


def verify_password(candidate_password: str, stored_hash: str) -> bool:
    """Verify a password against either the new PBKDF2 format or the legacy salt:sha256 format."""
    if not stored_hash:
        return False

    if stored_hash.startswith(f"{PASSWORD_SCHEME}$"):
        try:
            _, iterations_text, salt_text, expected_text = stored_hash.split("$", 3)
            iterations = int(iterations_text)
            salt = _b64decode(salt_text)
            expected = _b64decode(expected_text)
        except (ValueError, TypeError):
            return False

        derived = hashlib.pbkdf2_hmac(
            "sha256",
            candidate_password.encode("utf-8"),
            salt,
            iterations,
        )
        return secrets.compare_digest(derived, expected)

    try:
        salt, expected = stored_hash.split(":", 1)
    except ValueError:
        return False

    legacy = hashlib.sha256((salt + candidate_password).encode("utf-8")).hexdigest()
    return secrets.compare_digest(legacy, expected)


def _needs_password_upgrade(stored_hash: str) -> bool:
    return not stored_hash.startswith(f"{PASSWORD_SCHEME}$")


def _generic_reset_response() -> dict:
    return {"message": "If an account with this email exists, reset instructions have been sent."}


def _generate_six_digit_code() -> str:
    return "".join([str(secrets.choice(range(10))) for _ in range(6)])


@router.post("/register", response_model=dict)
async def register_user(user: UserCreate):
    normalized_name = user.name.strip()
    normalized_email = user.email.strip().lower()

    if not validate_email(normalized_email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

    if not validate_password_strength(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and contain uppercase, lowercase, and number",
        )

    if len(normalized_name) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name must be at least 2 characters long")

    bq_service = get_bq_service()
    if bq_service.get_user_profile_by_email(normalized_email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    now = datetime.now(timezone.utc)

    # Generate a 6-digit verification code
    verification_code = _generate_six_digit_code()
    verification_expires_ts = now + timedelta(minutes=15)
    
    hashed_verification_code = get_password_hash(verification_code)

    if not bq_service.write_user_profile(
        user_id=user_id,
        name=normalized_name,
        email=normalized_email,
        password_hash=str(hashed_password),
        level=cast(Optional[str], None),
        registration_ts=now,
        is_email_verified=False,
        verification_code=hashed_verification_code,
        verification_expires_ts=verification_expires_ts
    ):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to persist user")

    try:
        await send_verification_email_async(normalized_email, verification_code)
    except EmailDeliveryError as exc:
        if _can_continue_after_email_delivery_failure():
            logger.warning(
                "Continuing registration for %s because EMAIL_LOG_CODES=true and the verification code was logged",
                normalized_email,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Verification email could not be sent. Please try again or contact support.",
            ) from exc

    response = {
        "user_id": user_id,
        "message": "Verification required. Please check your email or the backend terminal in local demo mode.",
        "email": normalized_email,
        "requires_verification": True
    }
    if _can_expose_dev_verification_code():
        response["dev_verification_code"] = verification_code
    return response


@router.post("/verify-email", response_model=dict)
async def verify_email(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    code = (payload.get("code") or "").strip()

    if not email or not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and code are required")

    bq_service = get_bq_service()
    user_row = bq_service.get_user_profile_by_email(email)
    
    if not user_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_row.get("is_email_verified"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already verified")
        
    stored_code_hash = user_row.get("verification_code")
    expires_ts = user_row.get("verification_expires_ts")
    
    if not stored_code_hash or not verify_password(code, stored_code_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid verification code")
        
    # Check expiration (accounting for string or datetime types depending on memory vs BQ returns)
    now = datetime.now(timezone.utc)
    if isinstance(expires_ts, str):
        try:
            expires_dt = datetime.fromisoformat(expires_ts.replace('Z', '+00:00'))
            if expires_dt.tzinfo is None:
                expires_dt = expires_dt.replace(tzinfo=timezone.utc)
        except ValueError:
            expires_dt = now - timedelta(days=1)
    else:
        expires_dt = expires_ts

    if not expires_dt or expires_dt < now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification code has expired")
        
    # Mark as verified
    user_id = _extract_user_id(user_row)
    if not bq_service.write_user_profile(
        user_id=user_id,
        name=user_row.get("name"),
        email=email,
        password_hash=user_row.get("password_hash"),
        level=_normalize_level(user_row.get("level")),
        registration_ts=user_row.get("registration_date") or user_row.get("registration_ts") or now,
        questionnaire_data=user_row.get("questionnaire_data"),
        is_email_verified=True,
        verification_code=None,
        verification_expires_ts=None
    ):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to verify user")
        
    token = create_access_token({"sub": user_id, "email": email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id,
        "name": user_row.get("name"),
        "email": email,
        "level": user_row.get("level"),
        "message": "Email verified successfully"
    }


@router.post("/resend-verification", response_model=dict)
async def resend_verification(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")
        
    bq_service = get_bq_service()
    user_row = bq_service.get_user_profile_by_email(email)
    
    if not user_row:
        # Don't reveal if user exists
        return {"message": "If the email is registered, a new code has been sent."}
        
    if user_row.get("is_email_verified"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already verified")
        
    now = datetime.now(timezone.utc)
    verification_code = _generate_six_digit_code()
    verification_expires_ts = now + timedelta(minutes=15)
    
    hashed_verification_code = get_password_hash(verification_code)

    if not bq_service.write_user_profile(
        user_id=_extract_user_id(user_row),
        name=user_row.get("name"),
        email=email,
        password_hash=user_row.get("password_hash"),
        level=_normalize_level(user_row.get("level")),
        registration_ts=user_row.get("registration_date") or user_row.get("registration_ts") or now,
        questionnaire_data=user_row.get("questionnaire_data"),
        is_email_verified=False,
        verification_code=hashed_verification_code,
        verification_expires_ts=verification_expires_ts
    ):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate new code")

    try:
        await send_verification_email_async(email, verification_code)
    except EmailDeliveryError as exc:
        if _can_continue_after_email_delivery_failure():
            logger.warning(
                "Continuing resend verification for %s because EMAIL_LOG_CODES=true and the verification code was logged",
                email,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Verification email could not be sent. Please try again or contact support.",
            ) from exc
        
    response = {"message": "If the email is registered, a new code has been sent or logged for local demo mode."}
    if _can_expose_dev_verification_code():
        response["dev_verification_code"] = verification_code
    return response


@router.post("/login", response_model=dict)
async def login(credentials: dict):
    """Authenticate user and return a JWT access token.

    Expected payload: {"email": "...", "password": "..."}
    """
    email = (credentials.get("email") or "").strip().lower()
    password = credentials.get("password") or ""

    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")

    bq_service = get_bq_service()
    user_row = bq_service.get_user_profile_by_email(email)
    if not user_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    stored = user_row.get("password_hash") or ""
    if not verify_password(password, stored):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
    if not user_row.get("is_email_verified"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email address before logging in")

    if _needs_password_upgrade(stored):
        upgraded_hash = get_password_hash(password)
        if not bq_service.write_user_profile(
            user_id=_extract_user_id(user_row),
            name=user_row.get("name"),
            email=email,
            password_hash=upgraded_hash,
            level=_normalize_level(user_row.get("level")),
            registration_ts=user_row.get("registration_date") or user_row.get("registration_ts") or datetime.now(timezone.utc),
            questionnaire_data=user_row.get("questionnaire_data"),
            is_email_verified=bool(user_row.get("is_email_verified", False)),
            verification_code=user_row.get("verification_code"),
            verification_expires_ts=user_row.get("verification_expires_ts"),
        ):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upgrade user credentials")

    user_id = _extract_user_id(user_row)
    token = create_access_token({"sub": user_id, "email": email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id,
        "name": user_row.get("name"),
        "email": email,
        "level": user_row.get("level"),
    }


@router.post("/change-password", response_model=dict)
async def change_password(payload: dict, current_user: dict = Depends(get_current_user)):
    current_password = payload.get("current_password") or ""
    new_password = payload.get("new_password") or ""

    if not current_password or not new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password and new password are required")

    if not validate_password_strength(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and contain uppercase, lowercase, and number",
        )

    stored = current_user.get("password_hash") or ""
    if not verify_password(current_password, stored):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    user_id = _extract_user_id(current_user)
    bq_service = get_bq_service()
    if not bq_service.write_user_profile(
        user_id=user_id,
        name=current_user.get("name") or "",
        email=current_user.get("email") or "",
        password_hash=get_password_hash(new_password),
        level=_normalize_level(current_user.get("level")),
        registration_ts=current_user.get("registration_date") or current_user.get("registration_ts") or datetime.now(timezone.utc),
        questionnaire_data=current_user.get("questionnaire_data"),
        is_email_verified=bool(current_user.get("is_email_verified", False)),
        verification_code=current_user.get("verification_code"),
        verification_expires_ts=current_user.get("verification_expires_ts"),
    ):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to change password")

    return {"message": "Password changed successfully"}


@router.post("/forgot-password", response_model=dict)
async def forgot_password(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    if not email or not validate_email(email):
        return _generic_reset_response()

    bq_service = get_bq_service()
    user_row = bq_service.get_user_profile_by_email(email)
    if not user_row:
        return _generic_reset_response()

    now = datetime.now(timezone.utc)
    reset_code = _generate_six_digit_code()
    reset_id = str(uuid.uuid4())
    bq_service.create_password_reset_token(
        reset_id=reset_id,
        user_id=_extract_user_id(user_row),
        email=email,
        reset_code_hash=get_password_hash(reset_code),
        expires_ts=now + timedelta(minutes=30),
        created_ts=now,
    )

    try:
        await send_password_reset_email_async(email, reset_code)
    except EmailDeliveryError:
        logger.exception("Password reset delivery failed for %s", email)

    return _generic_reset_response()


@router.post("/reset-password", response_model=dict)
async def reset_password(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    reset_code = (payload.get("reset_code") or "").strip()
    new_password = payload.get("new_password") or ""

    if not email or not reset_code or not new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email, reset code, and new password are required")

    if not validate_email(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

    if not validate_password_strength(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and contain uppercase, lowercase, and number",
        )

    bq_service = get_bq_service()
    user_row = bq_service.get_user_profile_by_email(email)
    if not user_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired reset code")

    matching_token = None
    for token_row in bq_service.get_active_password_reset_tokens_by_email(email):
        if verify_password(reset_code, token_row.get("reset_code_hash") or ""):
            matching_token = token_row
            break

    if not matching_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired reset code")

    now = datetime.now(timezone.utc)
    if not bq_service.write_user_profile(
        user_id=_extract_user_id(user_row),
        name=user_row.get("name") or "",
        email=email,
        password_hash=get_password_hash(new_password),
        level=_normalize_level(user_row.get("level")),
        registration_ts=user_row.get("registration_date") or user_row.get("registration_ts") or now,
        questionnaire_data=user_row.get("questionnaire_data"),
        is_email_verified=bool(user_row.get("is_email_verified", False)),
        verification_code=user_row.get("verification_code"),
        verification_expires_ts=user_row.get("verification_expires_ts"),
    ):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")

    if not bq_service.mark_password_reset_token_used(str(matching_token.get("reset_id")), now):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to mark reset code as used")

    return {"message": "Password reset successfully"}


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    user_uuid = _parse_user_uuid(user_id)
    current_user_id = _extract_user_id(current_user)
    if current_user_id != str(user_uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access your own profile")

    bq_service = get_bq_service()
    user_row = bq_service.get_user_profile_by_id(user_uuid)
    if user_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _serialize_user(user_row)


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(user_id: str, user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    user_uuid = _parse_user_uuid(user_id)
    current_user_id = _extract_user_id(current_user)
    if current_user_id != str(user_uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own profile")

    bq_service = get_bq_service()
    existing = bq_service.get_user_profile_by_id(user_uuid)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_name = existing["name"]
    updated_email = existing["email"]
    updated_level = existing.get("level")

    if hasattr(user_update, "model_dump"):
        update_data = user_update.model_dump(exclude_unset=True)
    else:
        update_data = user_update.dict(exclude_unset=True)
    if "name" in update_data and update_data["name"] is not None:
        updated_name = update_data["name"].strip()
        if len(updated_name) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name must be at least 2 characters long")

    if "email" in update_data and update_data["email"] is not None:
        updated_email = update_data["email"].strip().lower()
        if not validate_email(updated_email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
        existing_with_email = bq_service.get_user_profile_by_email(updated_email)
        if existing_with_email and str(existing_with_email.get("id")) != str(user_uuid):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    if "level" in update_data and update_data["level"] is not None:
        if update_data["level"] not in ["beginner", "intermediate", "expert"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid level. Must be beginner, intermediate, or expert")
        updated_level = update_data["level"]

    questionnaire_data = update_data.get("questionnaire_data", existing.get("questionnaire_data"))
    if questionnaire_data is not None:
        existing["questionnaire_data"] = questionnaire_data

    if not bq_service.write_user_profile(
        user_id=str(user_uuid),
        name=updated_name,
        email=updated_email,
        password_hash=existing.get("password_hash") or "",
        level=updated_level,
        registration_ts=existing.get("registration_date") or datetime.now(timezone.utc),
        questionnaire_data=questionnaire_data,
        is_email_verified=bool(existing.get("is_email_verified", False)),
        verification_code=existing.get("verification_code"),
        verification_expires_ts=existing.get("verification_expires_ts"),
    ):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")

    refreshed = bq_service.get_user_profile_by_id(user_uuid) or {
        **existing,
        "name": updated_name,
        "email": updated_email,
        "level": updated_level,
    }
    return _serialize_user(refreshed)
