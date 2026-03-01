from app.core.ai.factory import get_provider
from app.core.ai.providers.base import AIProviderError
from app.core.config import Settings


def test_provider_factory_chooses_claude() -> None:
    settings = Settings(ai_provider="claude")
    provider = get_provider(settings)
    assert provider.name == "claude"


def test_provider_factory_chooses_gemini() -> None:
    settings = Settings(ai_provider="gemini")
    provider = get_provider(settings)
    assert provider.name == "gemini"


def test_provider_factory_chooses_grok() -> None:
    settings = Settings(ai_provider="grok")
    provider = get_provider(settings)
    assert provider.name == "grok"


def test_provider_factory_rejects_unsupported() -> None:
    settings = Settings(ai_provider="unknown")
    try:
        get_provider(settings)
        assert False, "Expected AIProviderError"
    except AIProviderError as exc:
        assert "Supported values" in str(exc)
