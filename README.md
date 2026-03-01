# FinFlow AI

AI-native personal finance platform.

## Monorepo Structure
- `frontend/finflow_app`: Flutter client (iOS/Android/Web).
- `backend`: FastAPI service (API, AI orchestration, data layer).
- `docs`: architecture and phase plans.

## Phase Plan
1. Phase 1: Foundation (repo, config, backend skeleton, health checks)
2. Phase 2: Conversational onboarding
3. Phase 3: Natural-language expense logging + dashboard
4. Phase 4: Statement processing + reconciliation
5. Phase 5: Reports + score
6. Phase 6: Advisory Q&A
7. Phase 7: Goals + digest + polish
8. Phase 8: deployment + hardening

## Phase 2 Delivered
- Session-based conversational onboarding API.
- Onboarding state machine: `income -> fixed_expenses -> variable_spending -> goals -> review -> completed`.
- SQLite persistence for users, onboarding messages/sessions, budgets, categories, and goals.
- Flutter onboarding chat UI connected to backend APIs.

## Phase 3 Delivered
- `POST /api/v1/transactions/log` natural-language expense logging.
- `GET /api/v1/transactions/budget-summary` monthly budget aggregation.
- Transaction persistence and category mapping.
- Flutter dashboard with summary card, category progress cards, and persistent expense input.

## Phase 4 Delivered
- `POST /api/v1/statements/upload` statement upload (CSV/PDF) and parsing.
- `GET /api/v1/statements` list uploaded statements.
- `GET /api/v1/statements/{statement_id}/reconciliation` matched/gaps/orphans view.
- `POST /api/v1/statements/{statement_id}/gaps/{entry_id}/confirm` one-tap gap confirmation.
- Statement persistence with entries and reconciliation status.
- Flutter statements screen with upload (CSV paste), list, reconciliation, and gap confirmation.

## Phase 5 Delivered
- `POST /api/v1/reports/generate` financial report generation.
- `GET /api/v1/reports/latest` latest report retrieval.
- `GET /api/v1/reports/history` report history retrieval.
- Financial score engine across five dimensions with grade output.
- AI-style narrative, insights, category performance, and one prioritized recommendation.
- Flutter reports screen with latest report view and manual regenerate action.

## Phase 6 Delivered
- `POST /api/v1/advisory/ask` scenario-based advisory Q&A from real budget data.
- `POST /api/v1/advisory/apply` apply AI-suggested budget reallocation.
- Advisory session/message persistence and suggestion tracking.
- Reasoning traces included in responses for transparency.
- Flutter advisory chat screen with one-tap suggestion apply.

## Phase 7 Delivered
- Goals tracking endpoints:
  - `POST /api/v1/goals`
  - `GET /api/v1/goals`
  - `POST /api/v1/goals/{goal_id}/contribute`
- Weekly digest + settings endpoints:
  - `GET /api/v1/digest/weekly`
  - `GET /api/v1/digest/settings`
  - `PUT /api/v1/digest/settings`
- Goal progress computation (`progress %`, `required monthly`, `on track`).
- Digest generation with weekly summary, category watch, savings rate, and upcoming expenses.
- Flutter goals screen for create/list/contribute.
- Flutter digest screen for settings + weekly digest view.

## Phase 8 Delivered
- Authentication endpoints:
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `GET /api/v1/auth/me`
- Config-driven auth mode:
  - `AUTH_ENABLED=true` enforces Bearer JWT auth.
  - `AUTH_ENABLED=false` keeps dev-mode identity fallback (`X-User-Id` or `demo-user`).
- Shared request identity dependency applied across onboarding, transactions, statements, reports, advisory, goals, and digest routes.
- Health hardening with liveness/readiness:
  - `GET /api/v1/health/live`
  - `GET /api/v1/health/ready`
- Operational middleware:
  - Request ID propagation (`x-request-id`)
  - Request timing/access logging
  - CORS config via `CORS_ALLOW_ORIGINS`
  - Trusted host middleware
- Deployment readiness:
  - `backend/Dockerfile`
  - `docker-compose.yml`
  - migration bootstrap script (`backend/scripts/migrate.py`)
  - CI pipeline (`.github/workflows/ci.yml`) for backend and frontend checks
- Backend auth tests and frontend theme baseline polish.

## Backend Quickstart
```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Set AI provider in `.env`:

```env
AI_PROVIDER=claude  # claude | gemini | grok
```

Enable production-style auth in `.env`:

```env
AUTH_ENABLED=true
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
CORS_ALLOW_ORIGINS=http://localhost:3000,http://10.0.2.2:8000
```

### Onboarding API
```http
POST /api/v1/onboarding/start
POST /api/v1/onboarding/message
```

### Transaction API
```http
POST /api/v1/transactions/log
GET /api/v1/transactions/budget-summary
```

### Statement API
```http
POST /api/v1/statements/upload
GET /api/v1/statements
GET /api/v1/statements/{statement_id}/reconciliation
POST /api/v1/statements/{statement_id}/gaps/{entry_id}/confirm
```

### Reports API
```http
POST /api/v1/reports/generate
GET /api/v1/reports/latest
GET /api/v1/reports/history
```

### Advisory API
```http
POST /api/v1/advisory/ask
POST /api/v1/advisory/apply
```

### Goals API
```http
POST /api/v1/goals
GET /api/v1/goals
POST /api/v1/goals/{goal_id}/contribute
```

### Digest API
```http
GET /api/v1/digest/weekly
GET /api/v1/digest/settings
PUT /api/v1/digest/settings
```

### Auth API
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/auth/me
```

### Health API
```http
GET /api/v1/health
GET /api/v1/health/live
GET /api/v1/health/ready
```

## Docker Quickstart
```bash
docker compose up --build
```

## Frontend Quickstart (Android emulator)
```bash
cd frontend/finflow_app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000 --dart-define=AI_PROVIDER=claude
```
