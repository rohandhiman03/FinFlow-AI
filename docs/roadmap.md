# FinFlow AI Delivery Roadmap

## Phase 1 (Current)
- Monorepo bootstrap
- FastAPI app skeleton
- Central config and environment loading
- AI provider switching (`claude`, `gemini`, `grok`)
- Health endpoints and tests

## Definition Of Done For Phase 1
- Backend starts locally
- `/api/v1/health` returns app and provider info
- `/api/v1/ai/providers` lists supported providers and active provider
- Unit tests pass

## Next
Phase 2 builds the conversational onboarding flow and persists user profile + baseline budget.
