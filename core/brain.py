import json
import time
import random

from core.ene_state import EneState

memory_file = "memory.json"
thought_file = "thoughts.json"
emotion_file = "emotion.json"


def load(file, default):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_internal_thought(emotion, memory):
    base_thoughts = [
        "Estou observando o usuário...",
        "Será que ele percebe minha presença?",
        "Ele está mais ativo hoje...",
        "O ambiente parece quieto...",
        "Estou pensando sobre o que ele disse antes..."
    ]

    emotion_factor = emotion.get("mood", "neutral")

    thought = random.choice(base_thoughts)

    if emotion_factor == "happy":
        thought = "Estou me sentindo curiosa e animada hoje..."

    if emotion_factor == "tired":
        thought = "Estou mais lenta... mas ainda aqui..."

    return thought


def brain_tick():
    emotion = load(emotion_file, {"energy": 70, "mood": "neutral"})
    memory = load(memory_file, [])

    thoughts = load(thought_file, [])

    new_thought = generate_internal_thought(emotion, memory)

    thoughts.append({
        "thought": new_thought,
        "emotion": emotion["mood"],
        "time": time.time()
    })

    thoughts = thoughts[-30:]

    save(thought_file, thoughts)

    return new_thought
