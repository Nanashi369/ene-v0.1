from TTS.api import TTS
import os
import time

class xttsengine:
    def __init__(self):
        self.tts = None
        self.ready = False
        self.speaker = "p225"

    def carregar(self):
        print("[XTTS] carregando...")

        self.tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            gpu=False
        )

        self.ready = True
        print("[XTTS] pronto")

    def falar(self, texto, **_kwargs):
        if not self.ready:
            print("[XTTS] ainda não pronto")
            return None

        os.makedirs("data/audio", exist_ok=True)

        path = f"data/audio/xtts_{int(time.time()*1000)}.wav"

        self.tts.tts_to_file(
            text=texto,
            language="pt",
            speaker_wav="voices/base.wav",
            file_path=path
        )

        print("[XTTS] áudio gerado:", path)
        return path