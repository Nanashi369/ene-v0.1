import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    ollama_url: str = os.getenv("ENE_OLLAMA_URL", "http://localhost:11434/api/generate")
    ollama_model: str = os.getenv("ENE_OLLAMA_MODEL", "llama3")
    vision_model: str = os.getenv("ENE_VISION_MODEL", "llava")
    voice_mode: str = os.getenv("ENE_VOICE_MODE", "online")
    continuous_interval_seconds: float = float(os.getenv("ENE_CONTINUOUS_INTERVAL", "1.0"))
    vision_interval_seconds: float = float(os.getenv("ENE_VISION_INTERVAL", "90.0"))

