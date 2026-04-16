from core.prompt_parts import IDENTITY_BLOCK, MOOD_MAP, RULES_BLOCK


def build_prompt(user_input, memory, emotion, personality, thought, memory_source=None):

    recent_memory = memory[-5:] if memory else []

    def _format_memory_item(m: dict) -> str:
        # Suporta múltiplos formatos de memória:
        # - Memory (json): {"text": "...", "emotion": 0.5, ...}
        # - EmotionalMemory (runtime): {"text": "...", "emotion": "happy", ...}
        # - Conversa pareada (legado): {"user": "...", "reply": "...", ...}
        user = m.get("user")
        reply = m.get("reply")
        if user is not None or reply is not None:
            return f"Usuário: {user or ''} | Ene: {reply or ''}".strip()

        text = m.get("text", "")
        emo = m.get("emotion", None)
        if emo is None or emo == "":
            return f"- {text}".strip()
        return f"- ({emo}) {text}".strip()

    memory_text = "\n".join(_format_memory_item(m) for m in recent_memory if isinstance(m, dict))
    memory_summary = ""
    source = memory_source if memory_source is not None else memory
    if hasattr(source, "get_summary_text"):
        try:
            memory_summary = source.get_summary_text()
        except Exception:
            memory_summary = ""

    emotion_data = emotion if isinstance(emotion, dict) else {
    "mood": emotion,
    "energy": 50
}

    mood = emotion_data.get("mood", "neutral")

    emotion_block = f"""
    Estado interno atual:
    - humor: {mood} ({MOOD_MAP.get(mood)})
    - energia: {emotion_data.get("energy", 50)}
"""

    # 🧬 personalidade traduzida em comportamento
    if isinstance(personality, dict):
        traits = personality
    else:
        traits = personality.get()

    personality_block = f"""
Traços de personalidade:
- curiosidade: {traits["curiosity"]}
- sarcasmo: {traits["sarcasm"]}
- calor humano: {traits["warmth"]}
- estabilidade: {traits["stability"]}
"""

    # 🧠 pensamento interno (o cérebro cru)
    thought_block = f"""
Pensamento interno recente:
{thought}
"""

    # 🔥 memória recente dá continuidade psicológica
    memory_block = f"""
Memória recente:
{memory_text}
"""

    summary_block = ""
    if memory_summary:
        summary_block = f"""
Resumo de memória:
{memory_summary}
"""

    # 🧠 INPUT FINAL
    return f"""
{IDENTITY_BLOCK}

{emotion_block}

{personality_block}

{thought_block}

{memory_block}

{summary_block}

{RULES_BLOCK}

Usuário: {user_input}

Ene:
"""