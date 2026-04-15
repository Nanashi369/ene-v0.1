from core.controller import EneController
from core.brain import Brain
from core.memory import EmotionalMemory
from core.emotion import EmotionSystem
from core.personality import Personality

from voices.voice_manager import voicemanager
from voices.tts.edge_tts import edgetts
from voices.tts.xtts_engine import xttsengine
from ui.ene_app import EneApp


def bootstrap():

    # 🔊 VOZES
    edge = edgetts()
    xtts = xttsengine()

    xtts.carregar()
    voice = voicemanager(edgetts, xttsengine)
    


    # 🧠 CÉREBRO
    brain = Brain()

    # 💾 MEMÓRIA
    memory = EmotionalMemory()

    # ❤️ EMOÇÃO
    emotion = EmotionSystem()

    # 🧬 PERSONALIDADE
    personality = Personality()

    # 🧠 CONTROLADOR CENTRAL
    controller = EneController(
        voice=voice,
        brain=brain,
        memory=memory,
        emotion=emotion,
        personality=personality
    )

    # 🖥 UI (corpo vivo)
    app = EneApp(controller)


if __name__ == "__main__":
    bootstrap()