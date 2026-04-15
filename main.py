from core.controller import EneController
from core.brain import Brain
from core.memory import EmotionalMemory
from core.emotion import EmotionSystem
from core.personality import Personality
from core.ene_state import EneState
from core.llm import LLMClient

from voices.voice_manager import VoiceManager
from voices.tts.edge_tts import edgetts
from voices.tts.xtts_engine import xttsengine

from ui.ene_app import EneApp

def bootstrap():

    # 🔊 VOZES (INSTÂNCIAS REAIS)
    edge = edgetts()
    xtts = xttsengine() 

    voice = VoiceManager(edge, xtts)
    voice.set_mode("online")

    # 🧠 BASES DO SISTEMA
    state = EneState()
    brain = Brain()
    memory = EmotionalMemory()
    emotion = EmotionSystem()
    personality = Personality()
    llm = LLMClient()

    # 🧠 CONTROLLER (CÉREBRO CENTRAL)
    controller = EneController(
        state=state,
        llm=llm,
        voice=voice,
        brain=brain,
        memory=memory,
        emotion=emotion,
        personality=personality
    )

    # 🖥 UI
    app = EneApp(controller)


if __name__ == "__main__":
    bootstrap() 