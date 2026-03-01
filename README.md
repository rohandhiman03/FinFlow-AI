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

## Backend Quickstart
```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Set AI provider in `.env`:

```env
AI_PROVIDER=claude  # claude | gemini | grok
```

## Frontend Quickstart
```bash
cd frontend/finflow_app
flutter pub get
flutter run
```
