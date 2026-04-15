import time
import threading


class VoiceManager:
    def __init__(self, edge_tts, xtts_engine):

        self.edge = edge_tts
        self.xtts = xtts_engine

        # 🎯 modo de operação
        self.mode = "online"  
        # "online"  → usa Edge
        # "offline" → usa XTTS
        # "auto"    → tenta Edge, fallback XTTS

        self.is_speaking = False
        self.queue = []

    # =========================
    # CONTROLE EXTERNO
    # =========================
    def set_mode(self, mode: str):
        self.mode = mode  # "online", "offline", "auto"

    # =========================
    # API PRINCIPAL
    # =========================
    def falar(self, texto, emocao="neutral", prioridade=1, tipo="normal"):

        # 🎭 emoção só muda estilo (NÃO engine)
        if emocao == "happy":
            texto += " 🙂"

        elif emocao == "tired":
            texto = texto.lower()

        elif emocao == "curious":
            texto = "hmm... " + texto

        # adiciona na fila
        self.queue.append((texto, emocao, prioridade, tipo))

        if not self.is_speaking:
            self._processar_fila()

    # =========================
    # FILA
    # =========================
    def _processar_fila(self):
        def worker():
            while self.queue:
                self.is_speaking = True

                texto, emocao, prioridade, tipo = self.queue.pop(0)

                engine = self._escolher_engine()

                try:
                    audio_path = engine.falar(texto)

                    # 🔊 tocar áudio se existir
                    if audio_path:
                        import simpleaudio as sa
                        wave_obj = sa.WaveObject.from_wave_file(audio_path)
                        play_obj = wave_obj.play()

                except Exception as e:
                    print("[VoiceManager] erro:", e)

                    # 🔥 fallback automático
                    if engine != self.edge:
                        try:
                            print("[VoiceManager] fallback → Edge")
                            audio_path = self.edge.falar(texto)

                            if audio_path:
                                import simpleaudio as sa
                                wave_obj = sa.WaveObject.from_wave_file(audio_path)
                                play_obj = wave_obj.play()

                        except Exception as e2:
                            print("[VoiceManager] fallback falhou:", e2)

                time.sleep(0.1)

            self.is_speaking = False

        threading.Thread(target=worker, daemon=True).start()

    # =========================
    # DECISÃO DE ENGINE (SIMPLES E PREVISÍVEL)
    # =========================
    def _escolher_engine(self):

        # 🔴 modo forçado offline
        if self.mode == "offline":
            return self.xtts

        # 🟢 modo forçado online
        if self.mode == "online":
            return self.edge

        # 🧠 modo automático
        if self.mode == "auto":
            try:
                import requests
                requests.get("https://www.google.com", timeout=1)
                return self.edge
            except:
                if not self.xtts_ready():
                    print("[VoiceManager] carregando XTTS...")
                    self.xtts.carregar()
                return self.xtts

        # fallback padrão
        return self.edge