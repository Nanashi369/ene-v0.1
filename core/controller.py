import requests
from core.prompt_builder import build_prompt
from core.interfaces import LLMProvider, MemoryProvider, VoiceProvider
from core.commands import handle_local_command
from core.skills_registry import SkillRegistry


class EneController:
    def __init__(
        self,
        voice: VoiceProvider,
        brain,
        memory: MemoryProvider,
        emotion,
        personality,
        state,
        llm: LLMProvider,
        config=None,
    ):
        self.state = state
        self.llm = llm
        self.voice = voice
        self.brain = brain
        self.memory = memory
        self.emotion = emotion
        self.personality = personality
        self.config = config
        self.skills = SkillRegistry()
        self._last_continuous_run = 0.0
        self._last_vision_run = 0.0
        self._last_vision_text = ""
        self._interrupt_generation = False

    def _handle_commands(self, text):
        return handle_local_command(self, text)
    
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
        self._interrupt_generation = False
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

                final = self._generate_reply(prompt)

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

            final = self._generate_reply(prompt)

            self.voice.falar(final, emocao="neutral")

            return final  # 🔥 garante saída aqui

        # =========================
        #  FLUXO NORMAL DA ENE
        # =========================

        # 💾 memória
        mem = self.memory.search(perception)

        # ❤️ emoção
        emotion = self.emotion.evaluate(perception, mem)

        self.state.set_mood(emotion)
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
            thought,
            memory_source=self.memory,
        )

        final = self._generate_reply(prompt)

        self.voice.falar(final, emocao=emotion)
        self.state.last_response = final
        self.state.last_user_input = text
        
        return final

    def _generate_reply(self, prompt: str) -> str:
        # Se o provider suportar streaming, consome incrementalmente.
        # Caso contrário, fallback simples.
        if hasattr(self.llm, "stream_generate"):
            chunks = []
            try:
                for chunk in self.llm.stream_generate(prompt):
                    if self._interrupt_generation:
                        break
                    chunks.append(chunk)
                final = "".join(chunks).strip()
                if final:
                    return final
            except Exception:
                pass
        return self.llm.generate(prompt)

    def brain_tick(self):
        if not self.is_continuous_enabled("proactive_speech"):
            return None

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

    def interrupt_generation(self):
        self._interrupt_generation = True
        if hasattr(self.voice, "stop_all"):
            self.voice.stop_all()

    # =========================
    # CONTROLES CONTÍNUOS
    # =========================
    def set_continuous_mode(self, enabled: bool):
        self.state.continuous_enabled = bool(enabled)

    def toggle_continuous_mode(self) -> bool:
        self.state.continuous_enabled = not self.state.continuous_enabled
        return self.state.continuous_enabled

    def is_continuous_enabled(self, feature: str | None = None) -> bool:
        if not self.state.continuous_enabled:
            return False
        if feature is None:
            return True
        return bool(self.state.continuous_features.get(feature, False))

    def set_continuous_feature(self, feature: str, enabled: bool):
        self.state.continuous_features[feature] = bool(enabled)

    def get_continuous_status(self):
        return {
            "enabled": bool(self.state.continuous_enabled),
            "features": dict(self.state.continuous_features),
        }

    def run_continuous_tasks(self):
        """
        Runner leve para tarefas contínuas.
        Mantém throttling para não sobrecarregar hardware.
        """
        import time

        if not self.state.continuous_enabled:
            return None

        now = time.time()
        interval = 1.0
        if self.config is not None:
            interval = float(getattr(self.config, "continuous_interval_seconds", 1.0))
        if now - self._last_continuous_run < interval:
            return None
        self._last_continuous_run = now

        # Fase 3: fala proativa
        fala = self.brain_tick()

        # Fase 4: visão contínua opcional e leve
        if self.is_continuous_enabled("continuous_vision"):
            vision_interval = 90.0
            if self.config is not None:
                vision_interval = float(getattr(self.config, "vision_interval_seconds", 90.0))
            if now - self._last_vision_run >= vision_interval:
                self._last_vision_run = now
                try:
                    from core.vision import analyze_screen

                    desc = analyze_screen()
                    # guarda apenas mudanças significativas para evitar spam de memória.
                    if desc and desc != self._last_vision_text and not desc.startswith("[VISION ERROR]"):
                        self._last_vision_text = desc
                        self.memory.remember(f"[vision] {desc}", "curious", intensity=0.7)
                except Exception:
                    pass

        return fala