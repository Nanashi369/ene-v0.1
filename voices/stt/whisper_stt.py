from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
import os

class WhisperSTT:
    def __init__(self):
        print("[STT] carregando whisper...")
        self.model = WhisperModel("small", compute_type="int8")

    def gravar_audio(self, duration=5, filename="temp.wav"):
        fs = 16000
        print("[STT] gravando...")

        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()

        wav.write(filename, fs, audio)
        return filename

    def transcrever(self, audio_path):
        print("[STT] transcrevendo...")

        segments, _ = self.model.transcribe(audio_path, language="pt")

        text = " ".join([seg.text for seg in segments])

        return text.strip()

    def ouvir(self):
        audio = self.gravar_audio()
        texto = self.transcrever(audio)

        os.remove(audio)

        return texto