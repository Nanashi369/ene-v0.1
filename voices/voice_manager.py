import time
import threading


class voicemanager:
    def __init__(self, edge_tts, xtts_engine):
        
        self.edge = edge_tts
        self.xtts = xtts_engine

        self.internet = True
        self.xtts_ready = False

        self.is_speaking = False
        self.queue = []

    # =========================
    # CONTROLES EXTERNOS
    # =========================
    def set_internet(self, status: bool):
        self.internet = status

    def set_xtts_ready(self, status: bool):
        self.xtts_ready = status

    # =========================
    # API PRINCIPAL
    # =========================
    def falar(self, texto, emocao="neutral", prioridade=1, tipo="normal"):

        # 🔊 emoção controla estilo
        if emocao == "happy":
            texto = texto + " 🙂"

        elif emocao == "tired":
            texto = texto.lower()

        elif emocao == "curious":
            texto = "hmm... " + texto

        # 🎤 escolha de engine
        if emocao == "tired":
            self.edge.falar(texto)
        else:
            self.xtts.falar(texto)
        self.queue.append((texto, emocao, prioridade, tipo))

        if not self.is_speaking:
            self._processar_fila()

    # =========================
    # FILA INTERNA
    # =========================
    def _processar_fila(self):
        def worker():
            while self.queue:
                self.is_speaking = True

                texto, emocao, prioridade, tipo = self.queue.pop(0)

                engine = self._escolher_engine(emocao, prioridade, tipo)

                try:
                    engine.speak(texto)
                except Exception as e:
                    print("[VoiceManager] erro:", e)

                    # fallback final
                    if engine != self.edge:
                        print("[VoiceManager] fallback → Edge")
                        self.edge.speak(texto)

                time.sleep(0.1)

            self.is_speaking = False

        threading.Thread(target=worker, daemon=True).start()

    # =========================
    # DECISÃO INTELIGENTE
    # =========================
    def _escolher_engine(self, emocao, prioridade, tipo):

        # 💀 offline obrigatório
        if not self.internet:
            return self.xtts

        # 🎭 emoção alta → XTTS
        if emocao >= 0.7:
            return self.xtts

        # ⚡ fala crítica → XTTS
        if prioridade >= 2:
            return self.xtts

        # 🎯 tipo emocional → XTTS
        if tipo == "emocional":
            return self.xtts

        # 🟢 padrão → Edge (rápido)
        return self.edge