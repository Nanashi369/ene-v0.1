class EneState:
    def __init__(self):

        self.energy = 70
        self.mood = "neutral"
        self.last_interaction = None

        self.sprite = "assets/idle.png"

        self.is_thinking = False
        self.is_talking = False

    def set_mood(self, mood):
        self.mood = mood