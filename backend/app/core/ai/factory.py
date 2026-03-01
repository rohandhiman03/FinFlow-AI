from app.core.ai.providers.base import AIProvider, AIProviderError
from app.core.ai.providers.claude import ClaudeProvider
from app.core.ai.providers.gemini import GeminiProvider
from app.core.ai.providers.grok import GrokProvider
from app.core.config import Settings


def get_provider(settings: Settings) -> AIProvider:
    provider = settings.ai_provider.lower().strip()

    if provider == "claude":
        return ClaudeProvider(api_key=settings.claude_api_key)
    if provider == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key)
    if provider == "grok":
        return GrokProvider(api_key=settings.grok_api_key)

    raise AIProviderError(
        f"Unsupported AI_PROVIDER '{settings.ai_provider}'. "
        f"Supported values: {', '.join(settings.supported_ai_providers)}"
    )
