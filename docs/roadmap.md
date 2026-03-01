# FinFlow AI Delivery Roadmap

## Phase 1 (Done)
- Monorepo bootstrap
- FastAPI app skeleton
- Central config and environment loading
- AI provider switching (`claude`, `gemini`, `grok`)
- Health endpoints and tests

## Phase 2 (Done)
- Conversational onboarding backend routes (`/onboarding/start`, `/onboarding/message`)
- Onboarding state machine and budget proposal generation
- SQLite persistence for onboarding/budget/goal entities
- Flutter onboarding chat screen wired to backend
- Automated tests for onboarding happy path and persistence

## Definition Of Done For Phase 2
- Backend starts locally and initializes DB
- Onboarding can be completed end-to-end through API
- Confirming onboarding stores budget + categories + goal entries
- Flutter app can complete onboarding conversation against local backend
- Backend tests and Flutter tests pass

## Next
Phase 3 builds natural language expense logging and dashboard cards with real-time budget updates.
