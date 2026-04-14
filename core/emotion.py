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


def update_emotion(emotion, event=None):
    """
    Atualização simples baseada em eventos.
    Depois isso vira IA emocional real.
    """

    if event == "click":
        emotion["curiosity"] = min(100, emotion["curiosity"] + 5)
        emotion["energy"] = max(0, emotion["energy"] - 2)

    elif event == "idle":
        emotion["energy"] = max(0, emotion["energy"] - 1)

    elif event == "talk":
        emotion["focus"] = min(100, emotion["focus"] + 3)

    # clamp geral
    emotion["energy"] = max(0, min(100, emotion["energy"]))
    emotion["focus"] = max(0, min(100, emotion["focus"]))
    emotion["curiosity"] = max(0, min(100, emotion["curiosity"]))

    return emotion