import base64
import os
from dataclasses import dataclass
from io import BytesIO

import requests
from PIL import Image, ImageGrab


@dataclass
class VisionConfig:
    temp_image_path: str = os.path.join("assets", "temp_screen.png")
    max_size: int = 1280  # maior lado
    ollama_url: str = "http://localhost:11434/api/generate"
    vision_model: str = "llava"


def capture_screen(config: VisionConfig) -> str:
    os.makedirs(os.path.dirname(config.temp_image_path), exist_ok=True)

    img = ImageGrab.grab()
    img = img.convert("RGB")

    w, h = img.size
    max_side = max(w, h)
    if max_side > config.max_size:
        scale = config.max_size / max_side
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        img = img.resize(new_size, Image.LANCZOS)

    img.save(config.temp_image_path, format="PNG", optimize=True)
    return config.temp_image_path


def _image_to_base64_png(path: str) -> str:
    img = Image.open(path).convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def analyze_screen(
    user_instruction: str | None = None,
    config: VisionConfig | None = None,
) -> str:
    """
    Faz captura de tela + manda para o Ollama usando um modelo multimodal (ex: llava).
    Retorna uma descrição breve em PT-BR.
    """
    config = config or VisionConfig()
    path = capture_screen(config)
    b64 = _image_to_base64_png(path)

    system = (
        "Você é Ene. Observe a imagem da tela do usuário e descreva de forma breve, "
        "natural e direta o que ele está fazendo / o que há de mais relevante. "
        "Não mencione que você é um modelo de linguagem. Responda em português brasileiro."
    )
    if user_instruction:
        system += f"\nInstrução extra do usuário: {user_instruction}"

    try:
        res = requests.post(
            config.ollama_url,
            json={
                "model": config.vision_model,
                "prompt": system,
                "images": [b64],
                "stream": False,
            },
            timeout=60,
        )
        res.raise_for_status()
        return (res.json().get("response", "") or "").strip()
    except Exception as e:
        return f"[VISION ERROR] {e}"

