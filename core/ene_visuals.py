import os

class EneVisuals:
    def __init__(self, base_path="assets"):
        self.base_path = base_path

    def get_sprite_path(self, state):
        mood = state.mood

        # caso normal
        if mood != "walk":
            path = os.path.join(self.base_path, mood)
            return self._pick_first(path)

        # caso especial surprise
        path = os.path.join(self.base_path, "idle")

        variant = state.surprise_variant

        if variant == 1:
            return self._pick_specific(path, "idle_1")
        elif variant == 2:
            return self._pick_specific(path, "idle_3")
        elif variant == 3:
            return self._pick_specific(path, "idle_2")

        return self._pick_first(path)

    def _pick_first(self, path):
        if os.path.exists(path):
            files = os.listdir(path)
            if files:
                return os.path.join(path, files[0])
        return None

    def _pick_specific(self, path, name):
        if os.path.exists(path):
            for f in os.listdir(path):
                if name in f:
                    return os.path.join(path, f)
        return None  
