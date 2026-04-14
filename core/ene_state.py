import random

class EneState:
    def __init__(self):
        self.mood = "idle"
        self.surprise_variant = None
        self.sprite = "assets/idle/idle_1.png"

        self.energy = 90
        self.focus = 30
        self.curiosity = 50
        self.last_interaction_time = 0
        self.last_speak_time = 0

    def set_mood(self, mood):
        self.mood = mood