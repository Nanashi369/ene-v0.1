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

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", False)
        self.root.wm_attributes("-transparentcolor", "black")

        self.label = tk.Label(self.root, bg="black")
        self.label.pack()

        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.do_drag)

    def update_sprite(self, path):
        from PIL import Image, ImageTk

        img = Image.open(path).resize((580, 580))

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

        self.root = tk.Toplevel(master)
        self.root.title("Ene Chat")
        self.root.geometry("300x80")
        self.root.attributes("-topmost", False)
        self.root.wm_attributes("-transparentcolor", "black")

        self.text = tk.Label(self.root, text="...", wraplength=380)
        self.text.pack()

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

        self.sprite.root.after(50, self.loop)

