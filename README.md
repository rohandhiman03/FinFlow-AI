# FinFlow AI

AI-native personal finance platform.

## Monorepo Structure
- `frontend/finflow_app`: Flutter client (iOS/Android/Web).
- `backend`: FastAPI service (API, AI orchestration, data layer).
- `docs`: architecture and phase plans.

## Phase Plan
1. Phase 1: Foundation (repo, config, backend skeleton, AI provider switching, health checks)
2. Phase 2: Conversational onboarding
3. Phase 3: Expense logging + dashboard
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

## Backend Quickstart
```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Set AI provider in `.env`:

```env
AI_PROVIDER=claude  # claude | gemini | grok
```

### Onboarding API (Phase 2)
```http
POST /api/v1/onboarding/start
POST /api/v1/onboarding/message
```

Example start payload:
```json
{ "reset_existing": true }
```

Example message payload:
```json
{ "session_id": "<id>", "message": "Salary 5000 monthly" }
```

## Frontend Quickstart
```bash
cd frontend/finflow_app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://localhost:8000 --dart-define=AI_PROVIDER=claude
```
