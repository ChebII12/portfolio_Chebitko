# First Aid AI - API Documentation

## Overview
This document describes the current Module 1 backend API behavior.

## Base URL
- Development: `http://localhost:8000`
- Production: `https://yourdomain.com`

## Implemented routes
- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/verify-email`
- `POST /api/auth/resend-verification`
- `POST /api/auth/login`
- `POST /api/auth/change-password`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`
- `GET /api/auth/users/{user_id}`
- `PUT /api/auth/users/{user_id}`
- `GET /api/profile/me`
- `PATCH /api/profile/me`
- `GET /api/profile/medical`
- `PUT /api/profile/medical`
- `PATCH /api/profile/medical`
- `DELETE /api/profile/medical`
- `POST /api/questionnaire/analyze`
- `POST /api/questionnaire/skip`

## Error format
```json
{
  "detail": "Human-readable message"
}
```

## Validation status codes
- `400`: explicit validation in route logic
- `404`: missing resource
- `409`: conflict (duplicate email)
- `422`: request-body schema validation (Pydantic)
- `500`: internal server error

## Frontend integration notes
- The frontend stores the JWT in `localStorage['access_token']` and the flow state in `localStorage['module1-flow-state']`.
- Authenticated requests should be sent with `Authorization: Bearer <token>`.
- Questionnaire submissions must include exactly 6 answers in the canonical backend order.
- UI answer labels should be normalized to the backend-accepted values before submit.
- The current Module 1 flow is registration → email verification → login/questionnaire → assessment → dashboard → profile.
- If Groq classification fails or is unavailable, the backend returns the deterministic local classification instead of failing the request.
- AI provider status: questionnaire AI classification currently uses Groq when `GROQ_API_KEY` is configured. Google Cloud is used for BigQuery persistence, not for AI classification.

---

## Health check
### `GET /api/health`

Success:
```json
{
  "status": "healthy",
  "message": "First Aid AI Backend is running"
}
```

---

## Register user
### `POST /api/auth/register`

Request:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

Success:
```json
{
  "user_id": "uuid-string",
  "message": "Verification required. Please check your email.",
  "email": "john@example.com",
  "requires_verification": true
}
```

Local demo note: when `EMAIL_DELIVERY_MODE=console` and `APP_ENVIRONMENT` is not `production`, the response also includes `dev_verification_code` so the verification screen can show the code without requiring email delivery. The backend also logs `DEV EMAIL VERIFICATION CODE for user@example.com: 123456`.

If `EMAIL_DELIVERY_MODE=smtp` and the SMTP send fails, the endpoint returns `503` with `Verification email could not be sent. Please try again or contact support.`

Common errors:
- `400` invalid email format
- `400` weak password
- `400` invalid name length
- `409` email already registered
- `422` malformed request body
- `500` internal error

---

## Verify email
### `POST /api/auth/verify-email`

Request:
```json
{
  "email": "john@example.com",
  "code": "123456"
}
```

Success:
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user_id": "uuid-string",
  "name": "John Doe",
  "email": "john@example.com",
  "level": null,
  "message": "Email verified successfully"
}
```

Common errors:
- `400` email and code are required
- `400` email is already verified
- `404` user not found
- `401` invalid or expired verification code
- `422` malformed request body
- `500` internal error

---

## Resend verification code
### `POST /api/auth/resend-verification`

Request:
```json
{
  "email": "john@example.com"
}
```

Success:
```json
{
  "message": "If the email is registered, a new code has been sent."
}
```

Notes:
- Missing or unknown emails do not reveal whether an account exists.
- Already verified accounts return `400`.

---

## Login user
### `POST /api/auth/login`

Request:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

Success:
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user_id": "uuid-string",
  "name": "John Doe",
  "email": "john@example.com",
  "level": "beginner"
}
```

Common errors:
- `400` email and password are required
- `401` invalid email or password
- `403` email address has not been verified yet
- `422` malformed request body

---

## Change password
### `POST /api/auth/change-password`

Authenticated endpoint for changing a password while signed in.

Request:
```json
{
  "current_password": "SecurePass123!",
  "new_password": "NewSecurePass123"
}
```

Success:
```json
{
  "message": "Password changed successfully"
}
```

Common errors:
- `400` missing fields or weak new password
- `401` current password is incorrect

---

## Forgot password
### `POST /api/auth/forgot-password`

Request:
```json
{
  "email": "john@example.com"
}
```

Success always uses a generic response so the API does not reveal whether an account exists:
```json
{
  "message": "If an account with this email exists, reset instructions have been sent."
}
```

Behavior:
- If the account exists, the backend creates a six-digit reset code.
- The reset code is stored hashed in `password_reset_tokens`.
- In `EMAIL_DELIVERY_MODE=console`, the backend logs `DEV PASSWORD RESET CODE for john@example.com: 123456`.
- In `EMAIL_DELIVERY_MODE=smtp`, the backend sends the code with the configured SMTP settings.
- The raw reset code is not returned by the API.

---

## Reset password
### `POST /api/auth/reset-password`

Request:
```json
{
  "email": "john@example.com",
  "reset_code": "123456",
  "new_password": "NewSecurePass123"
}
```

Success:
```json
{
  "message": "Password reset successfully"
}
```

Common errors:
- `400` missing fields, invalid email, or weak password
- `401` invalid, expired, or already-used reset code

---

## Get current account profile
### `GET /api/profile/me`

Returns a safe account profile for the authenticated user.

Success:
```json
{
  "user_id": "uuid-string",
  "name": "John Doe",
  "email": "john@example.com",
  "level": "beginner",
  "email_verified": true,
  "registration_ts": "2026-05-22T10:12:00+00:00",
  "updated_ts": "2026-05-22T10:15:00+00:00",
  "latest_assessment": {
    "level": "beginner",
    "confidence": 0.25,
    "classification_source": "local_rules",
    "created_ts": "2026-05-22T10:14:00+00:00"
  }
}
```

Never returned: `password_hash`, verification code, reset code, reset code hash, or service credentials.

---

## Update current account profile
### `PATCH /api/profile/me`

Allowed fields:
```json
{
  "name": "John Updated"
}
```

The route preserves email, password hash, verification fields, readiness level, and registration timestamp.

---

## Get medical profile
### `GET /api/profile/medical`

Authenticated endpoint. Returns only the current user's optional medical profile. If no medical profile exists, optional fields return `null`.

---

## Create or update medical profile
### `PUT /api/profile/medical`
### `PATCH /api/profile/medical`

All medical fields are optional:
```json
{
  "sex": "female",
  "age": 35,
  "special_conditions": "Pregnancy, mobility limitation, or other optional context",
  "chronic_illnesses": "Asthma",
  "everyday_medicines": "Inhaler",
  "allergies": "Penicillin",
  "emergency_contact_name": "Alex",
  "emergency_contact_phone": "+123456789",
  "blood_type": "O+",
  "medical_notes": "Optional notes"
}
```

Validation:
- `age`: `0` to `120`
- `sex`: `female`, `male`, `other`, `prefer_not_to_say`
- `blood_type`: `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, `unknown`
- text fields have maximum lengths

Medical data is stored separately from account login data in `user_medical_profiles` and is not automatically sent to AI in this version.

---

## Clear medical profile
### `DELETE /api/profile/medical`

Authenticated endpoint. Deletes only the current user's optional medical profile data and returns:
```json
{
  "message": "Medical profile cleared"
}
```

This route does not delete the base account, email verification state, password hash, readiness level, or questionnaire history.

---

## Get user
### `GET /api/auth/users/{user_id}`

Success:
```json
{
  "id": "uuid-string",
  "name": "John Doe",
  "email": "john@example.com",
  "level": "beginner",
  "registration_date": "2026-04-24T12:00:00+00:00",
  "questionnaire_data": {
    "answers": ["Rarely", "Always close", "No", "No", "Don't know what they are", "Travel solo"],
    "confidence": 0.25,
    "classification_source": "local_rules",
    "assessment_id": "assessment-uuid"
  }
}
```

Common errors:
- `400` invalid user ID format
- `404` user not found

---

## Update user
### `PUT /api/auth/users/{user_id}`

Request:
```json
{
  "name": "John Updated",
  "email": "john.updated@example.com",
  "level": "intermediate",
  "questionnaire_data": {}
}
```

Success: updated user object.

Note: self-service enforcement applies; authenticated users may only fetch/update their own profile.

Common errors:
- `400` invalid user ID format
- `400` invalid email/name/level
- `404` user not found
- `409` email conflict
- `422` malformed request body
- `500` internal error

---

## Analyze questionnaire
### `POST /api/questionnaire/analyze`

Request:
```json
{
  "user_id": "uuid-string",
  "answers": [
    "Rarely",
    "Always close",
    "No",
    "No",
    "Don't know what they are",
    "Travel solo"
  ]
}
```

Success:
```json
{
  "level": "beginner",
  "confidence": 0.25,
  "explanation": "Detailed step-by-step first aid guidance will be shown because your answers indicate limited recent training or emergency practice.",
  "classification_source": "local_rules",
  "message": "Level assessment completed"
}
```

Behavior notes:
- Request schema enforces `answers` min/max length of 6.
- Route logic also validates answer values per question.
- Local deterministic classification always runs.
- If `GROQ_API_KEY` exists, AI attempt may override local result.
- If AI fails/times out/parsing fails, local result is returned.
- If questionnaire persistence fails, the API returns `500`.
- If the user in the token does not match `request.user_id`, the API returns `403`.
- `classification_source` is one of `local_rules`, `groq_ai`, `deterministic_fallback`, or `questionnaire_skipped`.

Common errors:
- `400` `Authenticated user is required`
- `400` `Invalid user_id format`
- `400` `Exactly 6 answers are required`
- `400` `Invalid answer for question N`
- `403` token user mismatch with `user_id`
- `404` `User not found`
- `422` missing required request fields / schema errors

---

## Accepted answer values

### Q1 travel frequency
- `rarely`, `monthly`, `weekly`, `a few times a year`

### Q2 distance from medical facility
- `close`, `hours`, `day`, `always close`, `a few hours away`, `day or more`

### Q3 certification
- `none`, `old`, `current`, `advanced`, `no`, `yes, but a long time ago`, `yes, currently certified`, `yes, advanced instructor/responder`, `advanced training (emt, etc.)`

### Q4 real-life experience
- `none`, `minor`, `critical`, `no`, `yes, for minor injuries`, `yes, for critical emergencies`, `critical emergencies`

### Q5 trauma supplies comfort
- `unknown`, `theory`, `trained`, `i don't know how to use them`, `know in theory only`, `i am trained and confident`, `don't know what they are`, `trained and comfortable using`

### Q6 group responsibility
- `solo`, `group`, `medic`, `mostly solo`, `in groups, not designated medic`, `in a group, but not responsible`, `designated group medic/leader`, `in a group, as the designated medic/leader`, `travel solo`

Note: matching is case-insensitive after trimming whitespace.

---

## Skip questionnaire
### `POST /api/questionnaire/skip`

Authenticated users may skip the questionnaire. The backend persists a safe beginner default in `user_profiles.level` and writes a `questionnaire_assessments_wide` row with `classification_source: "questionnaire_skipped"`.

Success:
```json
{
  "level": "beginner",
  "confidence": 1.0,
  "explanation": "Beginner was assigned as the safest default because the questionnaire was skipped.",
  "classification_source": "questionnaire_skipped",
  "message": "Beginner level assigned because questionnaire was skipped"
}
```

Common errors:
- `400` invalid authenticated user id
- `404` user not found
- `500` persistence failure with retry guidance

---

## Persistence

When configured, BigQuery stores:
- `user_profiles`
- `questionnaire_assessments_wide`
- `user_medical_profiles`
- `password_reset_tokens`

When BigQuery is unavailable in local development or tests, the backend uses in-memory fallback stores.

### Table: `user_medical_profiles`
Purpose: stores optional sensitive personal/medical context for the authenticated user. It is separated from `user_profiles`.

Fields:
- `medical_profile_id` STRING
- `user_id` STRING
- `sex` STRING
- `age` INT64
- `special_conditions` STRING
- `chronic_illnesses` STRING
- `everyday_medicines` STRING
- `allergies` STRING
- `emergency_contact_name` STRING
- `emergency_contact_phone` STRING
- `blood_type` STRING
- `medical_notes` STRING
- `created_ts` TIMESTAMP
- `updated_ts` TIMESTAMP

### Table: `password_reset_tokens`
Purpose: stores one-time password reset codes as hashes.

Fields:
- `reset_id` STRING
- `user_id` STRING
- `email` STRING
- `reset_code_hash` STRING
- `expires_ts` TIMESTAMP
- `used` BOOL
- `created_ts` TIMESTAMP
- `used_ts` TIMESTAMP

## Versioning
Current routes are unversioned under `/api/*`.
Path versioning (`/api/v1/*`) is reserved for future releases.

## OpenAPI
Interactive docs are available at `/docs` when backend is running.
