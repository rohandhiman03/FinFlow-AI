from app.core.ai.providers.base import AIProvider


class ClaudeProvider(AIProvider):
    name = "claude"

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def check_config(self) -> None:
        # Key can be absent in early local dev; real calls will validate strictly.
        return None

    def describe(self) -> str:
        return "Anthropic Claude provider"
