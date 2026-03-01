from app.core.ai.providers.base import AIProvider


class GrokProvider(AIProvider):
    name = "grok"

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def check_config(self) -> None:
        return None

    def describe(self) -> str:
        return "xAI Grok provider"
