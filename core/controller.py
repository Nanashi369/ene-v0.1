from pydoc import text
from typing import final

from click import prompt
from matplotlib.style import context

from core import emotion, emotion, memory, perception, personality, personality
from core.prompt_builder import build_prompt


class EneController:
    def __init__(self, voice, brain, memory, emotion, personality, state, llm):
        self.state = state
        self.llm = llm
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

        # 🔥 sincroniza com state
        self.state.mood = emotion
        self.state.energy = self.emotion.energy

        # 🧬 personalidade
        personality = self.personality

        # 🧠 pensamento
        thought = self.brain.think(
            perception,
            mem,
            {
                "emotion": emotion,
                "personality": personality
            }
        )

        # 🧠 evolução
        self.personality.evolve(mem, emotion)

        # 💾 memória viva
        self.memory.remember(text, emotion)

        # 🧠 prompt
        from core.prompt_builder import build_prompt

        prompt = build_prompt(
            perception,
            mem,
            emotion,
            personality,
            thought
        )

        # 🔊 resposta
        final = self.llm.generate(prompt)

        # 🎭 voz
        self.voice.falar(final, emocao=emotion)

        return final

    def brain_tick(self):
        context = {
            "emotion": self.state.mood,
            "personality": self.personality.get()
        }

        return self.brain.think("", [], context)

    def get_sprite(self):
        return self.state.sprite

    def get_mood(self):
        return self.state.mood

    def set_state(self, key, value):
        setattr(self.state, key, value)