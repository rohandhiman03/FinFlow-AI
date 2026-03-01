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

## Phase 3 (Done)
- Natural-language expense log endpoint (`/transactions/log`)
- Budget summary endpoint (`/transactions/budget-summary`)
- Transaction table + aggregation for month-to-date spent/remaining/utilization
- Flutter dashboard screen with category progress bars and persistent expense input
- App shell logic: onboarding if no budget, dashboard if budget exists
- Automated tests covering transactions and summary updates

## Phase 4 (Done)
- Statement upload endpoint for CSV/PDF ingestion (`/statements/upload`)
- Statement reconciliation endpoint with matched/gaps/orphans (`/statements/{id}/reconciliation`)
- Gap confirmation endpoint to create missing transactions (`/statements/{id}/gaps/{entry_id}/confirm`)
- Statement/entry persistence models and reconciliation status tracking
- Flutter statements screen for upload, reconciliation review, and confirmation
- Automated backend tests for upload/reconciliation/confirmation flow

## Next
Phase 5 builds financial health report generation + score computation and exposes report/history UI in app.
