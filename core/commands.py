import re


def _normalize(text: str) -> str:
    t = (text or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def _natural_to_slash_command(low: str) -> str | None:
    # Liga/desliga contínuo
    if any(k in low for k in ("ligar modo continuo", "ativar modo continuo", "modo continuo ligado")):
        return "/continuo on"
    if any(k in low for k in ("desligar modo continuo", "desativar modo continuo", "modo continuo desligado")):
        return "/continuo off"

    # Status
    if low in ("status", "estado", "como voce esta", "como você está", "qual o status"):
        return "/status"

    # Parar
    if any(k in low for k in ("parar agora", "pare agora", "interromper", "cancelar resposta", "parar")):
        return "/parar"

    # Skills
    if any(k in low for k in ("listar skills", "listar habilidades", "quais skills", "quais habilidades")):
        return "/skills"

    if "abrir bloco de notas" in low or "abre bloco de notas" in low:
        return "/skill open_notepad"
    if "abrir calculadora" in low or "abre calculadora" in low:
        return "/skill open_calculator"

    # Ver tela (com ou sem instrução)
    if low.startswith("ver tela") or low.startswith("olhar tela") or low.startswith("analisar tela") or low.startswith("analisar tela"):
        # remove gatilho inicial e usa resto como instrução
        cleaned = low
        for prefix in ("ver tela", "olhar tela", "analisar tela", "analisar tela"):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip(" :,-")
                break
        if cleaned:
            return f"/ver {cleaned}"
        return "/ver"

    # Features contínuas por voz natural
    if "ligar visao continua" in low or "ligar visão contínua" in low or "ativar visao continua" in low:
        return "/feature continuous_vision on"
    if "desligar visao continua" in low or "desligar visão contínua" in low or "desativar visao continua" in low:
        return "/feature continuous_vision off"

    return None


def handle_local_command(controller, raw_text: str):
    text = (raw_text or "").strip()
    low = _normalize(text)

    natural_cmd = _natural_to_slash_command(low)
    if natural_cmd:
        text = natural_cmd
        low = natural_cmd

    if "repete" in low or "repita" in low:
        return controller.state.last_response

    if low.startswith("/ver"):
        try:
            from core.vision import analyze_screen

            extra = text[len("/ver") :].strip() or None
            return analyze_screen(user_instruction=extra)
        except Exception as e:
            return f"[VISION ERROR] {e}"

    if low in ("/continuo on", "/continuo ligar"):
        controller.set_continuous_mode(True)
        return "Ações contínuas: LIGADAS."

    if low in ("/continuo off", "/continuo desligar"):
        controller.set_continuous_mode(False)
        return "Ações contínuas: DESLIGADAS."

    if low.startswith("/feature "):
        # /feature proactive_speech on
        parts = low.split()
        if len(parts) != 3:
            return "Uso: /feature <nome> <on|off>"
        name, mode = parts[1], parts[2]
        controller.set_continuous_feature(name, mode == "on")
        return f"Feature '{name}': {'ON' if mode == 'on' else 'OFF'}."

    if low == "/status":
        st = controller.get_continuous_status()
        feat = ", ".join(f"{k}={'ON' if v else 'OFF'}" for k, v in st["features"].items())
        return f"Contínuo: {'ON' if st['enabled'] else 'OFF'} | {feat}"

    if low == "/parar":
        controller.interrupt_generation()
        return "Interrompido."

    if low == "/skills":
        return "Skills: " + ", ".join(controller.skills.list_skills())

    if low.startswith("/skill "):
        name = text[len("/skill ") :].strip()
        return controller.skills.run(name)

    return None

