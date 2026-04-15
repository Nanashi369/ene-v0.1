from pydoc import text
from typing import final

from click import prompt

from core import emotion, emotion, memory, perception, personality, personality
from core.prompt_builder import build_prompt


class EneController:
    def __init__(self, voice, brain, memory, emotion, personality):
        self.voice = voice
        self.brain = brain
        self.memory = memory
        self.emotion = emotion
        self.personality = personality
 

    def handle_input(self, text):

        perception = text.lower().strip()

        # 💾 memória
        mem = self.memory.search(perception)

        # ❤️ emoção
        emotion = self.emotion.evaluate(perception, mem)

        # 🧬 personalidade
        personality = self.personality.get()

        # 🧠 pensamento do brain
        thought = self.brain.think(
            perception,
            mem,
            {
                "emotion": emotion,
                "personality": personality
            }
        )

        # 🧠 PERSONALIDADE EVOLUI
        self.personality.evolve(mem, emotion)

        # 💾 MEMÓRIA VIVA
        self.memory.remember(text, emotion)

        # 🔥 AQUI É O PONTO CERTO DO PROMPT BUILDER
        prompt = build_prompt(
            perception,
            mem,
            emotion,
            personality,
            thought
        )

        # 🔊 LLM FALA
        final = generate_response(prompt)

        # 🎭 voz
        self.voice.falar(final, emocao=emotion)

        return final