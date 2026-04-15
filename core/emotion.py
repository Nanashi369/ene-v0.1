import json

EMOTION_FILE = "emotion.json"


def load_emotion():
    try:
        with open(EMOTION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "mood": "happy",
            "energy": 70,
            "focus": 50,
            "curiosity": 50
        }


def save_emotion(emotion):
    with open(EMOTION_FILE, "w", encoding="utf-8") as f:
        json.dump(emotion, f, indent=2, ensure_ascii=False)


import time
import random


class EmotionSystem:
    def __init__(self):
        self.energy = 70
        self.happiness = 50
        self.curiosity = 60
        self.boredom = 20

        self.last_update = time.time()

    # -------------------------
    # ATUALIZAÇÃO PRINCIPAL
    # -------------------------
    def evaluate(self, perception, memory):

        now = time.time()
        delta = now - self.last_update
        self.last_update = now

        # 🔋 energia cai com o tempo
        self.energy -= delta * 0.5

        # 😐 tédio sobe se não há input forte
        if not perception:
            self.boredom += 2
        else:
            self.boredom -= 5

        # 💡 curiosidade reage ao input
        self.curiosity += len(perception) * 0.1

        # ❤️ felicidade baseada em interação
        if "oi" in perception:
            self.happiness += 5

        # 🧠 memória influencia emoção
        if memory:
            self.happiness += 1
            self.curiosity += 1

        # clamp (limites)
        self._clamp()

        return self.get_emotion()

    # -------------------------
    # EMOÇÃO FINAL
    # -------------------------
    def get_emotion(self):

        if self.energy < 20:
            return "tired"

        if self.happiness > 70:
            return "happy"

        if self.boredom > 60:
            return "bored"

        if self.curiosity > 70:
            return "curious"

        return "neutral"

    # -------------------------
    # VARIAÇÃO DE INTENSIDADE
    # -------------------------
    def intensity(self):
        return (self.energy + self.happiness) / 200

    # -------------------------
    # AJUSTE MANUAL (eventos)
    # -------------------------
    def react(self, event):
        if event == "user_talk":
            self.happiness += 3
            self.energy += 1

        if event == "ignored":
            self.boredom += 5

        self._clamp()

    # -------------------------
    # LIMITE DE VALORES
    # -------------------------
    def _clamp(self):
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))
        self.curiosity = max(0, min(100, self.curiosity))
        self.boredom = max(0, min(100, self.boredom))