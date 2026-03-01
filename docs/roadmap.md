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

## Phase 5 (Done)
- Financial report generation endpoint (`/reports/generate`)
- Latest report + history endpoints (`/reports/latest`, `/reports/history`)
- Financial health score engine with 5 scored dimensions and grade output
- Category performance and insight extraction from real monthly data
- One prioritized recommendation per report
- Flutter reports screen with generate and latest report rendering
- Automated backend tests for report generation and retrieval

## Phase 6 (Done)
- Advisory Q&A endpoint with scenario evaluation (`/advisory/ask`)
- Suggestion apply endpoint that updates budget allocations (`/advisory/apply`)
- Advisory session/message/suggestion persistence for continuity
- Reasoning traces returned alongside answers
- Flutter advisory screen with ask flow and one-tap apply actions
- Automated backend tests for ask/apply behavior

## Phase 7 (Done)
- Goals CRUD-lite endpoints (`/goals`, `/goals/{id}/contribute`) with progress/on-track calculations
- Weekly digest endpoint and digest settings endpoints (`/digest/weekly`, `/digest/settings`)
- Digest preferences persistence (`frequency`, `day`, `time`)
- Flutter goals screen with create/list/contribute interactions
- Flutter digest screen with settings and weekly summary rendering
- Automated backend tests for goals and digest flows

## Next
Phase 8 focuses on deployment readiness and hardening (auth, migrations, observability, production config, and final UI polish pass).
