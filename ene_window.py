from pydoc import text
from urllib import response

from core.llm import generate_response
from core.perception import detect_user_activity
from core.ene_state_controller import EneState
from core.emotion import load_emotion, save_emotion, update_emotion
from core.memory import load_memory, save_memory
from voices.voice_manager import VoiceManager
from voices.voice_manager import VoiceManager
from voices.edge_tts import EdgeTTS
from voices.xtts_engine import XTTSEngine


import json
import tkinter as tk
import random
import time
import threading

from PIL import Image, ImageTk

class EneApp:
    def __init__(self):
        edge = EdgeTTS()
        xtts = XTTSEngine()
        xtts.carregar()

        self.setup_core()
        self.setup_ui()
        self.start_threads()    

    def setup_core(self):
        from voices.edge_tts import EdgeTTS
        from voices.xtts_engine import XTTSEngine
        from voices.voice_manager import VoiceManager
    
        self.voice_manager = VoiceManager(self.edge, self.xtts)

        from core.ene_state_controller import EneController
        self.controller = EneController(self.voice_manager)

        self.voice_manager = VoiceManager(self.edge, self.xtts)
        self.controller = EneController(self.voice_manager)
        
        threading.Thread(target=self.life_loop, daemon=True).start() 
        self.root = tk.Tk()
        self.root.title("Ene")
        self.chat_entry = tk.Entry(self.root)
        self.chat_entry.pack()

        self.chat_entry.bind("<Return>", self.on_user_send)

        # janela sem borda (fica mais "pet")
        self.root.overrideredirect(False)
        self.root.geometry("420x500+200+100")
        self.root.configure(bg="black")

        self.label = tk.Label(
            self.root,
            text="hello wolrd",
            fg="white",
            bg="black",
            font=("Segoe UI", 15),
            wraplength=420,
            justify="left"
        )
        self.label.pack(padx=20, pady=20)

        self.image_label = tk.Label(self.root, bg="black")
        self.image_label.pack()

        # posição do mouse
        self.offset_x = 0
        self.offset_y = 0

        # eventos
        self.label.bind("<Button-1>", self.on_click)
        self.label.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        threading.Thread(target=self.life_loop, daemon=True).start()

        self.ui_loop()
        self.root.mainloop()
 
    def on_user_send(self, event):
        user_text = self.chat_entry.get()
        self.chat_entry.delete(0, tk.END)

        # mostra pensamento rápido
        self.label.config(text="...")

        # manda pro controller
        threading.Thread(
            target=self.handle_user_chat,
            args=(user_text,),
            daemon=True
        ).start()

    def render_state(self):
        sprite_path = self.controller.update()

        if sprite_path is None:
             return

        img = Image.open(sprite_path)
        img = img.resize((500,500))

        photo = ImageTk.PhotoImage(img)

        self.image_label.config(image=photo)
        self.image_label.image = photo
    
    def ui_loop(self):
        self.render_state()
        self.root.after(20, self.ui_loop)    

    # 🖱️ CLIQUE
    def on_click(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

        self.label.config(text="hm… calma aí")

        # roda IA em paralelo
        threading.Thread(
            target=self.handle_click_response,
            daemon=True
        ).start()
        
    def handle_click_response(self):
        reply = self.controller.handle_user_input("o usuario clicou em você. reaja.")

        self.root.after(0, lambda: self.label.config(text=reply))
        

    def handle_idle_thought(self, thought):
        prompt = f"""
             Você é Ene.

            - Personalidade:
            - provocadora
            - sarcástica
            - inteligente
            - brincalhona

        Situação:
        {thought}

         Responda com UMA frase curta e natural.
         """

        if random.random() < 0.3:
            response = self.controller.handle_user_input(thought, mode="thought")
        else:
            return

        self.root.after(0, lambda: self.label.config(text=response))

    # 🖱️ ARRASTAR
    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def load_memory(self):
        try:
             with open("memory.json", "r", encoding="utf-8") as f:
                 return json.load(f)
        except:
             return []


    # 🧠 VIDA AUTÔNOMA
    def life_loop(self):
        while True:
            time.sleep(random.randint(4, 10))

            # 🧠 pensamento interno
            from core.brain import brain_tick
            thought = brain_tick()

            print("🧠 pensamento:", thought)
            
            if self.controller.is_thinking:
                continue

            # ❌ não mexe direto no tkinter fora do main thread
            self.root.after(0, self._update_thought, thought)

            # 🎲 chance de falar sozinha
            if random.random() < 0.5 and self.controller.can_speak():
                self.root.after(0, lambda: self.label.config(text=thought))

    def _update_thought(self, thought):
        self.label.config(text=thought)

    def handle_user_chat(self, text):
        print("📨 ENVIADO:", text)

        reply = self.controller.handle_user_input(text, mode="user")

        print("🧠Ene:", reply)

        if reply is None:
            print("💀 reply veio None")

        if reply == "":
            print("💀 reply veio vazio")

        self.root.after(0, lambda: self.label.config(text=str(reply)))


if __name__ == "__main__":
    EneApp()