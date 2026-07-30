# Environment Configuration Guide
**First Aid AI Module 1 - BigQuery Setup**
---
## Quick Start
### Development (Local)
```bash
cd backend
cp .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
### BigQuery Variables
```env
BIGQUERY_PROJECT_ID=your-google-cloud-project-id
BIGQUERY_DATASET_ID=first_aid_ai_module1
BIGQUERY_CREDENTIALS_PATH=C:/path/to/service-account.json
BIGQUERY_WRITE_ENABLED=true
BIGQUERY_READ_SOURCE=bigquery
```
---
## Environment Variables Reference
### BIGQUERY_PROJECT_ID
**Purpose:** Google Cloud project that owns the BigQuery dataset  
**Required:** Yes  
**Example:** `your-google-cloud-project-id`
### BIGQUERY_DATASET_ID
**Purpose:** Dataset used by Module 1  
**Required:** Yes  
**Default:** `first_aid_ai_module1`
### BIGQUERY_CREDENTIALS_PATH
**Purpose:** Service-account JSON path  
**Required:** Yes for real BigQuery usage  
**Example:** `C:/path/to/service-account.json`
### BIGQUERY_WRITE_ENABLED
**Purpose:** Enable BigQuery writes  
**Required:** No  
**Default:** `false`
### BIGQUERY_READ_SOURCE
**Purpose:** Read mode control  
**Required:** No  
**Allowed:** `legacy`, `shadow`, `bigquery`  
**Recommended for live use:** `bigquery`
### SECRET_KEY
**Purpose:** JWT signing key  
**Required:** Yes
### GROQ_API_KEY
**Purpose:** Optional AI classification key  
**Required:** No  
**Fallback:** Deterministic scoring always works
### Email verification delivery
**Purpose:** Controls how registration and resend deliver verification codes  
**Required for local demo:** Yes  
**Recommended local/demo values:**
```env
EMAIL_DELIVERY_MODE=console
APP_ENVIRONMENT=development
```
Console mode does not send real email. The backend terminal logs:
```text
DEV EMAIL VERIFICATION CODE for user@example.com: 123456
DEV PASSWORD RESET CODE for user@example.com: 123456
```
Outside production, the API also returns `dev_verification_code` so the frontend can show the local demo code.
Password reset codes are not returned by the API; use the backend terminal in console mode.

**SMTP values for real email with Brevo:**
```env
EMAIL_DELIVERY_MODE=smtp
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=your-brevo-smtp-login
SMTP_PASSWORD=your-brevo-smtp-key
SMTP_FROM_EMAIL=your-verified-brevo-sender@example.com
SMTP_FROM_NAME=First Aid AI
SMTP_USE_TLS=true
```
Brevo note: use the SMTP key generated in Brevo, not your normal Brevo account password. `SMTP_FROM_EMAIL` must be a sender email verified in Brevo. Backward-compatible names `SMTP_SERVER` and `SMTP_USER` are still supported. Prefer the newer `SMTP_HOST` and `SMTP_USERNAME` names for new setup.

For development demos with fake/test recipient emails, you can send through SMTP and still print the code in the backend terminal:
```env
EMAIL_DELIVERY_MODE=smtp
APP_ENVIRONMENT=development
EMAIL_LOG_CODES=true
```
Registration/resend also return `dev_verification_code` outside production so the local frontend can show the code after registration or resend. Keep `EMAIL_LOG_CODES=false` in production.

If SMTP mode cannot send the email, registration/resend returns:
```text
Verification email could not be sent. Please try again or contact support.
```
Password reset uses the same SMTP settings. The forgot-password endpoint still returns a generic response so it does not reveal whether an account exists.
### CORS_ORIGINS
**Purpose:** Allowed frontend origins  
**Example:** `http://localhost:3000,http://localhost:5173`
### Frontend persistence keys
**Purpose:** Browser storage used by the module 1 frontend flow  
**Keys:** `access_token`, `module1-flow-state`  
**Notes:** The frontend stores the JWT bearer token in `access_token` and the restored user/level flow state in `module1-flow-state`.
### Frontend route flow
**Purpose:** User navigation contract enforced by the React app  
**Routes:** `/` (registration), `/verify-email`, `/login`, `/forgot-password`, `/reset-password`, `/questionnaire`, `/assessment`, `/dashboard`, `/profile`
**Notes:** Registration now routes through email verification before a JWT is issued; protected routes require a valid JWT session and unauthenticated users are redirected to `/login`.

### Profile and password recovery tables
**Purpose:** Additional Module 1 account settings and optional health context
**Tables:** `user_medical_profiles`, `password_reset_tokens`
**Notes:** Medical profile fields are optional and stored separately from login/auth fields in `user_profiles`. Password reset codes are stored hashed and marked used after a successful reset.
---
## Development Setup
1. Copy `backend/.env.example` to `backend/.env`.
2. Set the BigQuery variables above.
3. Set `CORS_ORIGINS` to include the frontend origin(s) you will use locally and in production.
4. Set `EMAIL_DELIVERY_MODE=console` for local demos, or configure SMTP for real email.
5. Ensure the service-account JSON is readable by the backend container or local process.
6. Start the backend and frontend.
---
## Production Setup
### Recommended Environment Values
```env
BIGQUERY_PROJECT_ID=your-google-cloud-project-id
BIGQUERY_DATASET_ID=first_aid_ai_module1
BIGQUERY_CREDENTIALS_PATH=/run/secrets/credentials.json
BIGQUERY_WRITE_ENABLED=true
BIGQUERY_READ_SOURCE=bigquery
```
### Notes
- Use a service account with BigQuery Data Editor and Job User permissions.
- Keep the credentials file out of version control.
- Set `BIGQUERY_READ_SOURCE=bigquery` for the live runtime.
---
## Docker Compose Notes
- The backend container mounts the BigQuery credentials JSON as `/app/credentials.json`.
- No PostgreSQL service is required.
- Redis remains optional for caching.
---
## Troubleshooting
### BigQuery credentials error
**Cause:** Credentials file missing or unreadable  
**Check:**
```bash
python -c "from pathlib import Path; print(Path(r'C:/path/to/service-account.json').exists())"
```
### BigQuery dataset missing
**Cause:** Dataset not created yet  
**Fix:**
```bash
python -c "from app.core.bigquery_service import get_bq_service; s = get_bq_service(); s.enabled = True; s.project_id='your-google-cloud-project-id'; s._initialize_client(); print(s.create_dataset_and_tables())"
```
### AI key missing
**Cause:** `GROQ_API_KEY` is empty  
**Result:** Questionnaire still works using deterministic fallback.
### Verification email not arriving
**Cause:** SMTP is not configured, blocked, or using the wrong password type
**Fast demo fix:** Set `EMAIL_DELIVERY_MODE=console`, restart backend, register again or use resend. Copy the code from the backend terminal or from the local demo code shown on the verification screen.
### Password reset code not arriving
**Cause:** SMTP is not configured, blocked, or using the wrong password type
**Fast demo fix:** Set `EMAIL_DELIVERY_MODE=console`, restart backend, request reset again, and copy `DEV PASSWORD RESET CODE` from the backend terminal.
--- 
**Last Updated:** May 20, 2026  
**Status:** BigQuery-only runtime
