from typing import Protocol, Any


class LLMProvider(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class VoiceProvider(Protocol):
    def falar(self, texto: str, emocao: str = "neutral", prioridade: int = 1, tipo: str = "normal") -> Any:
        ...


class MemoryProvider(Protocol):
    def search(self, query: str):
        ...

    def remember(self, text: str, emotion: str, intensity: float = 1.0):
        ...

