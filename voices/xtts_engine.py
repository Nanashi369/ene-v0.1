from TTS.api import TTS
import threading
import os
import time

class XTTSEngine:
    def __init__(self):
        self.tts = None
        self.ready = False

    # =========================
    # Carregar modelo (thread)
    # =========================
    def carregar(self):
        def _load():
            print("[XTTS] Carregando modelo... segura aí 😅")

            self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

            self.ready = True
            print("[XTTS] Pronto para uso!")

        thread = threading.Thread(target=_load)
        thread.start()

    # =========================
    # Falar
    # =========================
    def falar(self, texto):
        if not self.ready:
            print("[XTTS] Ainda carregando...")
            return None

        try:
            os.makedirs("data/audio", exist_ok=True)

            output_path = f"data/audio/xtts_{int(time.time()*1000)}.wav"
            
            texto = "... " + texto  # pré-aquecimento (resolve voz rouca)

            self.tts.tts_to_file(
                text=texto,
                language="pt",
                speaker="female-en-5",
                file_path=output_path
            )

            print("[XTTS] Áudio gerado")

            return output_path

        except Exception as e:
            print("[XTTS] Erro:", e)
            return None