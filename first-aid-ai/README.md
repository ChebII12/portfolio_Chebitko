# First Aid AI — Module 1

**AI-driven university project · Full-stack web application**

First Aid AI is an AI-driven university software project that prepares a traveler for personalized first-aid guidance. Module 1 implements the account and readiness layer: verified registration, onboarding, AI-supported skill assessment, profile management, optional medical context, and secure password flows.

This portfolio version combines the stable FastAPI backend with the project’s completed responsive frontend redesign. It runs locally without cloud credentials by using deterministic assessment rules and in-memory persistence, while keeping optional BigQuery and Groq integrations available through environment configuration.

## Academic context

The project demonstrates requirements-driven full-stack development, AI-assisted classification, API design, authentication, cloud-database integration, defensive fallback behavior, automated testing, and technical presentation. Module 1 is the implemented university submission; the remaining medical-assistance modules form the planned product roadmap.

## Implemented scope

- Registration with password validation and six-digit email verification
- JWT-protected routes and session restoration
- Questionnaire completion, safe skip behavior, and retakes
- Beginner, intermediate, or expert readiness classification
- Deterministic fallback when the optional AI provider is unavailable
- Responsive dashboard and assessment result screens
- Editable account name and separately stored optional medical profile
- Password change, forgot-password, and reset-password flows
- BigQuery persistence when Google Cloud credentials are configured
- Console email mode for a complete local demonstration

Modules for symptom analysis, camera analysis, nearby clinics, travel risk, and offline emergency guidance are presented as future roadmap items, not completed features.

## Stack

| Layer | Technology |
| --- | --- |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI, Python, Pydantic |
| Authentication | JWT, PBKDF2 password hashing |
| Persistence | Google BigQuery or local in-memory fallback |
| Optional AI | Groq API with deterministic fallback |
| Testing | pytest, Vitest, React Testing Library |
| Deployment | Docker Compose, Nginx, ngrok-compatible local demo |

## Run locally

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The default environment works without BigQuery or Groq. Verification and password-reset codes are shown in the backend console and returned to the local development UI.

### Frontend

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000). The Vite development server proxies `/api` requests to the backend on port `8000`.

## Verify

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q

cd ..\frontend
npm test -- --run
npm run build
```

## Optional cloud configuration

For BigQuery support, install `backend/requirements-prod.txt` and set the `BIGQUERY_*` values described in [`backend/.env.example`](./backend/.env.example). Add a Groq key only if AI-based classification is required; local classification remains available without it.

Never commit `.env` files or service-account credentials. The repository ignores local environment files, credential JSON, virtual environments, generated builds, and dependency folders.
Environment-specific cloud-console screenshots and presentation metadata are intentionally excluded from this public portfolio copy.

## Project material

- [API documentation](./docs/API_DOCUMENTATION.md)
- [Environment configuration](./docs/ENV_CONFIGURATION.md)

## Repository structure

```text
first-aid-ai/
├── backend/      FastAPI application, schemas, services, and tests
├── frontend/     Responsive React application and component tests
├── docs/         API and environment reference
├── monitoring/   Prometheus and Grafana configuration
├── nginx/        Reverse-proxy configuration
└── scripts/      Deployment and rollback helpers
```
