import os
import time
import threading
import subprocess
import pygame


class EdgeTTS:
    def __init__(self):
        pygame.mixer.init()
        self.busy = False

    # =========================
    # Interface pública
    # =========================
    def falar(self, text):
        if self.busy:
            print("[Edge] ocupado")
            return

        self.busy = True

        threading.Thread(
            target=self._speak,
            args=(text,),
            daemon=True
        ).start()

    # =========================
    # execução real
    # =========================
    def _speak(self, text):
        try:
            os.makedirs("voices", exist_ok=True)

            filename = f"voices/ene_{int(time.time()*1000)}.mp3"

            # 🧹 limpa arquivos antigos (CORRETO)
            for f in os.listdir("voices"):
                if f.startswith("ene_") and f.endswith(".mp3"):
                    try:
                        os.remove(os.path.join("voices", f))
                    except:
                        pass

            subprocess.run([
                "edge-tts",
                "--voice", "pt-BR-FranciscaNeural",
                "--text", text,
                "--write-media", filename
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

            time.sleep(0.2)

            # tenta remover arquivo
            try:
                os.remove(filename)
            except:
                pass

        except Exception as e:
            print("[Edge] erro:", e)

        finally:
            self.busy = False