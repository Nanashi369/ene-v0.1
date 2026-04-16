from core.controller import EneController
from core.brain import Brain
from core.emotion import EmotionSystem
from core.personality import Personality
from core.ene_state import EneState
from core.llm import LLMClient
from core.config import AppConfig
from core.memory_manager import LayeredMemoryManager

from voices.voice_manager import VoiceManager
from voices.tts.edge_tts import edgetts
from voices.tts.xtts_engine import xttsengine

from ui.ene_app import EneApp

def bootstrap():
    config = AppConfig()

    # 🔊 VOZES (INSTÂNCIAS REAIS)
    edge = edgetts()
    xtts = xttsengine()

    voice = VoiceManager(edge, xtts)
    voice.set_mode(config.voice_mode)

    # 🧠 BASES DO SISTEMA
    state = EneState()
    brain = Brain()
    memory = LayeredMemoryManager()
    emotion = EmotionSystem()
    personality = Personality()
    llm = LLMClient(model=config.ollama_model, url=config.ollama_url)

    # 🧠 CONTROLLER (CÉREBRO CENTRAL)
    controller = EneController(
        state=state,
        llm=llm,
        voice=voice,
        brain=brain,
        memory=memory,
        emotion=emotion,
        personality=personality,
        config=config,
    )

    # 🖥 UI
    app = EneApp(controller)


if __name__ == "__main__":
    bootstrap() 