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
        "Ele está diferente hoje...",
        "Algo mudou no padrão dele...",
        "Estou processando memórias recentes..."
    ]

    thought = random.choice(base_thoughts)

    # 🔥 memória influencia pensamento
    if memory:
        last = memory[-1].get("text","")
        thought += f" (lembro de: {last[:30]})"

    if emotion.get("mood") == "happy":
        thought = "Estou mais viva hoje... gosto disso..."

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

class Brain:
    def think(self, perception, memory, context):

        emotion = context["emotion"]
        personality = context["personality"]

        base = f"Estou processando: {perception}"

        # 😴 cansado → pensamento lento
        if emotion == "tired":
            return "Estou meio lenta... " + base

        # 😡 irritado (se você adicionar depois)
        if emotion == "bored":
            return "Hmm... isso de novo? " + base

        # 😄 feliz
        if emotion == "happy":
            return "Isso é interessante! " + base

        # 👀 curioso
        if emotion == "curious":
            return "Isso chamou minha atenção... " + base

        return base