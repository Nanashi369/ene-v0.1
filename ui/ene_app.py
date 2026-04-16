from importlib.resources import path
import tkinter as tk
import threading
import time
import random
from PIL import Image, ImageTk
from flask import app


class EneSpriteWindow:
    def __init__(self, master, controller):

        self.controller = controller

        self.root = tk.Toplevel(master)
        self.root.title("Ene Sprite")
        self.root.geometry("600x400")
        self.root.configure(bg="black")
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", False)

        self.label = tk.Label(self.root, bg="black")
        self.label.pack()

        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.do_drag)

    def update_sprite(self, path):
        from PIL import Image, ImageTk

        try:
            img = Image.open(path).resize((580, 580))
        except Exception:
            return

        self.tk_img = ImageTk.PhotoImage(img)
        self.label.config(image=self.tk_img)

    def start_drag(self, e):
        self.offset_x = e.x
        self.offset_y = e.y

    def do_drag(self, e):
        x = self.root.winfo_pointerx() - self.offset_x
        y = self.root.winfo_pointery() - self.offset_y
        self.root.geometry(f"+{x}+{y}")

class EneChatWindow:
    def __init__(self, master, controller):

        self.controller = controller
        self._ptt = {
            "ready": False,
            "recognizer": None,
            "mic": None,
            "stopper": None,
            "last_audio": None,
        }

        self.root = tk.Toplevel(master)
        self.root.title("Ene Chat")
        self.root.geometry("400x150")
        self.root.attributes("-topmost", False)

        self.text = tk.Label(self.root, text="...", wraplength=380)
        self.text.pack()

        status = self.controller.get_continuous_status()
        label = "Ações contínuas: ON" if status["enabled"] else "Ações contínuas: OFF"
        self.continuous_btn = tk.Button(self.root, text=label, command=self._toggle_continuous)
        self.continuous_btn.pack(fill="x")

        self.stop_btn = tk.Button(self.root, text="Parar fala/geração", command=self._stop_now)
        self.stop_btn.pack(fill="x")

        self.feature_btn = tk.Button(self.root, text="Visão contínua: OFF", command=self._toggle_vision_feature)
        self.feature_btn.pack(fill="x")

        self.ptt_btn = tk.Button(self.root, text="Segurar para falar")
        self.ptt_btn.pack(fill="x")
        self.ptt_btn.bind("<ButtonPress-1>", self._ptt_start)
        self.ptt_btn.bind("<ButtonRelease-1>", self._ptt_stop)

        self.entry = tk.Entry(self.root)
        self.entry.pack(fill="x")

        self.entry.bind("<Return>", self.on_enter)

    def on_enter(self, event):
        text = self.entry.get()
        self.entry.delete(0, tk.END)

        self.text.config(text="...")

        threading.Thread(
            target=self._process,
            args=(text,),
            daemon=True
        ).start()


    def _process(self, text):
        reply = self.controller.handle_input(text)

        self.root.after(0, lambda: self.text.config(text=reply))
        self.root.after(0, self._refresh_continuous_button)

    def _refresh_continuous_button(self):
        status = self.controller.get_continuous_status()
        label = "Ações contínuas: ON" if status["enabled"] else "Ações contínuas: OFF"
        self.continuous_btn.config(text=label)
        vision = bool(status["features"].get("continuous_vision", False))
        self.feature_btn.config(text=f"Visão contínua: {'ON' if vision else 'OFF'}")

    def _toggle_continuous(self):
        enabled = self.controller.toggle_continuous_mode()
        self._refresh_continuous_button()
        if enabled:
            self.text.config(text="Modo contínuo ligado. (Pode consumir mais CPU/RAM)")
        else:
            self.text.config(text="Modo contínuo desligado. (Economia de desempenho)")

    def _toggle_vision_feature(self):
        status = self.controller.get_continuous_status()
        current = bool(status["features"].get("continuous_vision", False))
        self.controller.set_continuous_feature("continuous_vision", not current)
        self._refresh_continuous_button()
        self.text.config(text=f"Visão contínua {'ligada' if not current else 'desligada'}.")

    def _stop_now(self):
        self.controller.interrupt_generation()
        self.text.config(text="Interrompido.")

    def _ptt_init(self):
        if self._ptt["ready"]:
            return True
        try:
            import speech_recognition as sr

            self._ptt["recognizer"] = sr.Recognizer()
            self._ptt["mic"] = sr.Microphone()
            self._ptt["ready"] = True
            return True
        except Exception:
            self._ptt["ready"] = False
            return False

    def _ptt_start(self, _event=None):
        if not self._ptt_init():
            self.text.config(text="STT não instalado. Instale: pip install SpeechRecognition pyaudio")
            return

        import speech_recognition as sr

        if self._ptt["stopper"] is not None:
            return

        self.text.config(text="ouvindo...")

        def callback(_rec: sr.Recognizer, audio: sr.AudioData):
            self._ptt["last_audio"] = audio

        with self._ptt["mic"] as source:
            # ruído ambiente (rápido)
            try:
                self._ptt["recognizer"].adjust_for_ambient_noise(source, duration=0.2)
            except Exception:
                pass

        stopper = self._ptt["recognizer"].listen_in_background(self._ptt["mic"], callback)
        self._ptt["stopper"] = stopper

    def _ptt_stop(self, _event=None):
        stopper = self._ptt.get("stopper")
        if stopper is None:
            return

        try:
            stopper(wait_for_stop=False)
        except Exception:
            pass

        self._ptt["stopper"] = None

        audio = self._ptt.get("last_audio")
        self._ptt["last_audio"] = None
        if audio is None:
            self.text.config(text="não ouvi nada.")
            return

        def worker():
            try:
                r = self._ptt["recognizer"]
                # Google é simples e funciona "agora"; depois dá pra trocar por Whisper local.
                said = r.recognize_google(audio, language="pt-BR")
            except Exception as e:
                self.root.after(0, lambda: self.text.config(text=f"falha no STT: {e}"))
                return

            self.root.after(0, lambda: self.entry.delete(0, tk.END))
            self.root.after(0, lambda: self.text.config(text=f"Você: {said}"))

            reply = self.controller.handle_input(said)
            self.root.after(0, lambda: self.text.config(text=reply))

        threading.Thread(target=worker, daemon=True).start()

class EneApp:
    def __init__(self, controller):

        self.controller = controller

        # 🔥 ÚNICO ROOT REAL
        self.root = tk.Tk()
        self.root.withdraw()  # esconde janela vazia

        self.sprite = EneSpriteWindow(self.root, controller)
        self.chat = EneChatWindow(self.root, controller)

        self.loop()

        self.root.mainloop()
    def loop(self):
        sprite_path = self.controller.get_sprite()
        self.sprite.update_sprite(sprite_path)
        self.controller.run_continuous_tasks()
        self.chat._refresh_continuous_button()

        self.sprite.root.after(50, self.loop)

