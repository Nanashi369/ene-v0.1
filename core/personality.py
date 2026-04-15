import json
import time


class Personality:
    def __init__(self, path="personality.json"):
        self.path = path
        self.data = self._load()

        # 🧬 traços base (nascem assim)
        if not self.data:
            self.data = {
                "curiosity": 0.6,
                "sarcasm": 0.4,
                "warmth": 0.5,
                "energy": 0.6,
                "stability": 0.5
            }

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # 🔥 atualização contínua
    def evolve(self, memory, emotion):

        # curiosidade cresce com novidade
       for m in memory:
        if m["emotion"] == "happy":
            self.data["warmth"] += 0.01

        if m["emotion"] == "tired":
            self.data["energy"] -= 0.01

        # sarcasmo sobe se emoção está estável
        if 0.4 < emotion < 0.7:
            self.data["sarcasm"] += 0.005

        # energia muda com emoção geral
        self.data["energy"] = (self.data["energy"] + emotion) / 2

        # estabilidade depende de memória recente
        if len(memory) > 5:
            self.data["stability"] += 0.002

        # limites
        for k in self.data:
            self.data[k] = max(0.0, min(1.0, self.data[k]))

        self._save()

    def influence_prompt(self, thought, emotion):
        if self.data["stability"] < 0.3:
            return "hesitante: " + thought

        if self.data["curiosity"] > 0.7:
            return "explorativo: " + thought

        return thought

    # 🧠 influenciar fala
    def modulate(self, text):
        if self.data["sarcasm"] > 0.7:
            text += " ...hm."

        if self.data["curiosity"] > 0.7:
            text = "Hmm... " + text

        return text

    def get(self):
        return self.data