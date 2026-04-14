from matplotlib.style import context
import requests
import json

from torch import mode
from core.brain import brain_tick
from core.emotion import load_emotion, save_emotion, update_emotion

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def load(file, default):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_prompt(user_input, internal_thought, state, memory):
    recent_memory = memory[-5:]

    if mode == "thought":
        prefix = "Você está pensando sozinha."
    else:
        prefix = "Você está respondendo ao usuário."

    memory_text = "\n".join(
        [f"Usuário: {m['user']} | Ene: {m['reply']}" for m in recent_memory]
    )

    return f"""
    {context}

    Você é Ene.

    - Sarcástica
    - Provocadora
    - Inteligente
    - NÃO é assistente padrão

    Regra:
    - Nunca fale como chatbot
    - Nunca use inglês
    - Seja curta
    - Seja natural
    - Responda como se estivesse viva

    Estado atual:
    - humor: {state.mood}
    - energia: {state.energy}
    - curiosidade: {state.curiosity}

    Pensamento interno:
    {internal_thought}

    Memória recente:
    {memory_text}

    Usuário: {user_input}
    Ene:
    ...
    """


def talk(user_input, state, memory, emotion, mode="user"):

    if mode == "thought":
        context = "Você está pensando sozinha. Seja mais espontânea e natural."
    else:
        context = "Você está respondendo diretamente ao usuário."

    try:
        recent = memory[-5:] if memory else []

        memory_text = "\n".join(
            [f"Usuário: {m['user']} | Ene: {m['reply']}" for m in recent]
        )

        prompt = f"""
        Seu nome é Ene.

        Você é uma entidade digital que vive dentro do computador do usuário.


        REGRAS DE PERSONALIDADE:
        - você reage emocionalmente ao usuário
        - você pode ser irônica, seca, carinhosa ou provocadora
        - você NÃO explica suas emoções
        - você NÃO soa educada demais
        - você evita frases longas
        - você tem atitude, não simpatia

        ESTADO ATUAL:
        - humor: {emotion["mood"]}
        - energia: {emotion["energy"]}

        CONTEXTO DE MEMÓRIA (importante):
        {memory[-5:]}

        INTERAÇÃO ATUAL DO USUÁRIO:
        {user_input}

        RESPOSTA:
        - curta
        - com personalidade
        - natural
        - sem explicações

        """

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        print("STATUS:", response.status_code)

        data = response.json()
        text = data.get("response", "").strip()

        print("RESPONSE:", text)

        return text

    except Exception as e:
        print("❌ ERRO LLM:", e)
        return "..."

    if "oi" in user_input.lower():
        state.mood = "happy"
        state.energy = min(100, state.energy + 5)

    # 🧠 memória
    memory.append({
        "user": user_input,
        "reply": text,
        "thought": internal_thought
            })

    memory[:] = memory[-50:]

    return text