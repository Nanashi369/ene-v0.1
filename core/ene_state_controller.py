from pdb import run
import time
import random
import threading

from matplotlib import text

from core.Ene_core import talk
from core.memory import load_memory, save_memory
from core.ene_state import EneState
from core.ene_visuals import EneVisuals
from core.emotion import load_emotion, save_emotion, update_emotion
from voices.voice_manager import VoiceManager       

class EneController:
    def __init__(self, voice_manager):
        self.voice = voice_manager

        self.state = EneState()
        self.visuals = EneVisuals()

        self.emotion = load_emotion()
        self.memory = load_memory()

        self.is_thinking = False
        self.is_speaking = False
        self.last_reply = ""

    # 💬 INTERAÇÃO PRINCIPAL
    def handle_user_input(self, user_input, mode="user"):
        print("carregando resposta...")

        if self.is_thinking:
            return "..."

        self.is_thinking = True

        self.state.last_interaction_time = time.time()
        self.emotion = update_emotion(self.emotion, "talk")

        reply = talk(
            user_input,
            self.state,
            self.memory,
            self.emotion,
            mode
        )

        self.is_thinking = False

        if reply == self.last_reply:
            return "..."

        self.last_reply = reply

        print("🧠 RESPOSTA:", reply)

        save_emotion(self.emotion)
        save_memory(self.memory)

        # 🎙️ fala via VoiceManager (CORRETO)
        if self.can_speak():
            intent = {
                "texto": reply,
                "emocao": self.emotion,
                "prioridade": 1,
                "tipo": "normal"
            }

            self.voice.falar(**intent)

        return reply

    def can_speak(self):
        return time.time() - self.state.last_speak_time > 5
    def update(self):
        return self.visuals.get_sprite_path(self.state)