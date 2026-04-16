import os
import random
import json


class EneState:
    def __init__(self):

        self.energy = 70
        self.mood = "neutral"
        self.last_interaction = None

        self.sprite = "assets/idle/idle.png"
        self._sprite_index = self._build_sprite_index()
        self._sprite_map = self._load_sprite_map()

        self.is_thinking = False
        self.is_talking = False

        # Controles de ações contínuas (fases 3 e 4)
        # Master switch: se False, nada contínuo roda.
        self.continuous_enabled = False
        self.continuous_features = {
            "proactive_speech": True,   # brain_tick
            "continuous_vision": False, # reservado para fase 4
            "automation": False,        # reservado para fase 4
        }

    def set_mood(self, mood):
        self.mood = mood
        self.sprite = self._pick_sprite_for_mood(mood)

    def _build_sprite_index(self):
        index = {}
        assets_root = "assets"
        valid_ext = (".png", ".jpg", ".jpeg", ".webp", ".gif")
        if not os.path.isdir(assets_root):
            return index

        for root, _dirs, files in os.walk(assets_root):
            for fn in files:
                if not fn.lower().endswith(valid_ext):
                    continue
                full = os.path.join(root, fn).replace("\\", "/")
                rel = os.path.relpath(root, assets_root).replace("\\", "/").lower()
                bucket = rel.split("/")[0] if rel and rel != "." else "misc"
                index.setdefault(bucket, []).append(full)

                name = os.path.splitext(fn)[0].lower()
                index.setdefault(name, []).append(full)
        return index

    def _load_sprite_map(self):
        """
        Carrega configuração opcional de sprites:
        - assets/sprite_map.json
        Suporta:
        {
          "happy": ["assets/surprise/foo.png", "surprise", "idle"],
          "neutral": ["idle"]
        }
        Cada item pode ser caminho de arquivo ou bucket (pasta/nome base).
        """
        path = "assets/sprite_map.json"
        if not os.path.isfile(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                normalized = {}
                for k, v in data.items():
                    if isinstance(v, list):
                        normalized[str(k).lower()] = [str(x) for x in v]
                return normalized
        except Exception:
            return {}
        return {}

    def _pick_from_bucket(self, bucket_name):
        items = self._sprite_index.get(bucket_name.lower(), [])
        if not items:
            return None
        return random.choice(items)

    def _pick_sprite_for_mood(self, mood):
        mood = (mood or "neutral").lower().strip()

        # 1) Mapa customizado por arquivo JSON (prioridade máxima)
        custom = self._sprite_map.get(mood, [])
        for item in custom:
            item_norm = item.replace("\\", "/").strip()
            # caminho explícito
            if "/" in item_norm and os.path.isfile(item_norm):
                return item_norm
            # bucket lógico
            candidate = self._pick_from_bucket(item_norm)
            if candidate:
                return candidate

        # 2) Correlação automática por nome de pasta/arquivo
        auto_mapping_priority = {
            "happy": ["happy", "surprise", "walk", "idle"],
            "tired": ["tired", "idle", "bored"],
            "bored": ["bored", "idle"],
            "curious": ["curious", "click", "surprise", "idle"],
            "angry": ["angry", "bored", "idle"],
            "neutral": ["neutral", "idle"],
        }

        for bucket in auto_mapping_priority.get(mood, [mood, "idle"]):
            candidate = self._pick_from_bucket(bucket)
            if candidate:
                return candidate

        # fallback global
        all_items = []
        for items in self._sprite_index.values():
            all_items.extend(items)
        if all_items:
            return random.choice(all_items)
        return self.sprite