class EneState:
    def __init__(self):

        self.energy = 70
        self.mood = "neutral"
        self.last_interaction = None

        self.sprite = "assets/idle.png"

        self.is_thinking = False
        self.is_talking = False

    def update_sprite(self, mood):
        self.mood = mood

        if mood == "happy":
            self.sprite = "assets/happy.png"
        elif mood == "tired":
            self.sprite = "assets/tired.png"
        elif mood == "bored":
            self.sprite = "assets/bored.png"
        else:
            self.sprite = "assets/idle.png"