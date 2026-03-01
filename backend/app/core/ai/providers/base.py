from abc import ABC, abstractmethod


class AIProviderError(RuntimeError):
    pass


class AIProvider(ABC):
    name: str

    @abstractmethod
    def check_config(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def describe(self) -> str:
        raise NotImplementedError
