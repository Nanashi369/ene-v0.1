import tkinter as tk
import threading
import time
import random
from PIL import Image, ImageTk


class EneApp:
    def __init__(self, controller):
        self.controller = controller

        self.root = tk.Tk()
        self.root.title("Ene")
        self.root.geometry("420x500")
        self.root.configure(bg="black")

        # 💬 fala da Ene
        self.label = tk.Label(
            self.root,
            text="...",
            fg="white",
            bg="black",
            wraplength=400,
            font=("Segoe UI", 14)
        )
        self.label.pack(pady=10)

        # 🖼 sprite
        self.image_label = tk.Label(self.root, bg="black")
        self.image_label.pack()

        # ⌨ input
        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.entry.bind("<Return>", self.on_enter)

        # estado
        self.running = True

        # loops
        threading.Thread(target=self.life_loop, daemon=True).start()
        self.ui_loop()

        self.root.mainloop()

    # -------------------------
    # INPUT DO USUÁRIO
    # -------------------------
    def on_enter(self, event):
        text = self.entry.get()
        self.entry.delete(0, tk.END)

        self.label.config(text="...")

        threading.Thread(
            target=self.send_to_controller,
            args=(text,),
            daemon=True
        ).start()

    def send_to_controller(self, text):
        reply = self.controller.handle_input(text)
        self.root.after(0, lambda: self.label.config(text=reply))

    # -------------------------
    # VIDA AUTÔNOMA
    # -------------------------
    def life_loop(self):
        while self.running:
            time.sleep(random.randint(5, 10))

            thought = self.controller.brain_tick()

            if random.random() < 0.4:
                self.root.after(0, lambda: self.label.config(text=thought))

    # -------------------------
    # RENDER VISUAL
    # -------------------------
    def ui_loop(self):
        sprite = self.state.sprite
        sprite = self.controller.state.sprite

        if sprite:
            try:
                img = Image.open(sprite)
                img = img.resize((280, 280))
                photo = ImageTk.PhotoImage(img)

                self.image_label.config(image=photo)
                self.image_label.image = photo
            except:
                pass

        self.root.after(50, self.ui_loop)

    # -------------------------
    # FECHAR
    # -------------------------
    def close(self):
        self.running = False
        self.root.destroy()