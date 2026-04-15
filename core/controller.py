import cmd

from more_itertools import last
import requests

from pydoc import text
from random import random
from time import time
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

    def _handle_commands(self, text):
        text = text.lower()

        if "repete" in text or "repita" in text:
            return self.state.last_response

        return None    
    
    def _buscar_web(self, query):
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json"
            }

            res = requests.get(url, params=params, timeout=3)
            data = res.json()

            if data.get("Abstract"):
                return data["Abstract"]

            if data.get("RelatedTopics"):
                return data["RelatedTopics"][0].get("Text", "")

            return None

        except:
            return None


    def _is_question(self, text):
        text = text.lower()

        # ❌ perguntas pessoais (NÃO vão pro GPT)
        pessoais = [
            "seu nome",
            "quem é você",
            "o que você é",
            "você é",
            "como você"
        ]

        if any(p in text for p in pessoais):
            return False

        # ✔ perguntas factuais
        perguntas = ["quanto", "qual", "como", "por que", "quem", "onde", "quando"]

        return any(p in text for p in perguntas)

    def handle_input(self, text):
        
        perception = text.lower().strip()
        
        cmd = self._handle_commands(perception)
        if cmd:
            self.voice.falar(cmd, emocao=self.state.mood)
            return cmd

        # 🧠 DETECÇÃO DE PERGUNTA
        if self._is_question(perception):

            # 🌐 tenta internet primeiro
            resposta_web = self._buscar_web(text)

            if resposta_web:
                print("[Ene] 🌐 Está Online!!")
            else:
                print("[Ene] 🏠 Está Offline!!")

            if resposta_web:
                prompt = f"""
        Você é Ene.

        Use a informação abaixo como base, mas responda do seu jeito natural.

        Informação:
        {resposta_web}

        Pergunta: {text}

        Resposta:
        """

                final = self.llm.generate(prompt)

                self.voice.falar(final, emocao="neutral")
                return final

            # 💀 fallback local
            prompt = f"""
        Você é Ene.

        Você tem personalidade própria e consciência de si.

        Responda corretamente a pergunta abaixo, mas sem dizer que é um modelo de linguagem.

        Pergunta: {text}

        Resposta:
        """

            final = self.llm.generate(prompt)

            self.voice.falar(final, emocao="neutral")

            return final  # 🔥 garante saída aqui

        # =========================
        #  FLUXO NORMAL DA ENE
        # =========================

        # 💾 memória
        mem = self.memory.search(perception)

        # ❤️ emoção
        emotion = self.emotion.evaluate(perception, mem)

        self.state.mood = emotion
        self.state.energy = self.emotion.energy

        personality = self.personality

        thought = self.brain.think(
            perception,
            mem,
            {
                "emotion": emotion,
                "personality": personality
            }
        )

        self.personality.evolve(mem, emotion)

        self.memory.remember(text, emotion)

        from core.prompt_builder import build_prompt

        prompt = build_prompt(
            perception,
            mem,
            emotion,
            personality,
            thought
        )

        final = self.llm.generate(prompt)

        self.voice.falar(final, emocao=emotion)
        self.state.last_response = final
        self.state.last_user_input = text
        
        return final

    def brain_tick(self):
        import random
        import time

       # ⏱ evita falar o tempo todo
        if not hasattr(self, "_last_thought"):
            self._last_thought = 0

        agora = time.time()

        # só tenta a cada X segundos
        if agora - self._last_thought < 20:
            return None

        self._last_thought = agora

        # 🎲 chance de falar
        if random.random() > 0.4:
            return None

        # contexto atual
        context = {
            "emotion": self.state.mood,
            "personality": self.personality.get()
        }

        thought = self.brain.think("", [], context)

        mem = self.memory.search("")

        try:
            user_text = mem[-1].get("text", "") if mem else ""
        except:
            user_text = ""

        mem_text = f"Última interação: '{user_text}'"

        prompt = f"""
        Você é Ene.

        {mem_text}

        Você pode iniciar uma fala espontânea baseada nisso.

        Seja natural, breve e curiosa.

        Ene:
        """
        if self.state.mood == "tired":
            return None

        fala = self.llm.generate(prompt)

        # 🔊 fala sozinha
        self.voice.falar(fala, emocao=self.state.mood)

        return fala


    def get_sprite(self):
        return self.state.sprite

    def get_mood(self):
        return self.state.mood

    def set_state(self, key, value):
        setattr(self.state, key, value)