class VoiceManager:
    def __init__(self, edge_tts, xtts_engine):
        self.edge_tts = edge_tts
        self.xtts = xtts_engine

        self.internet = True
        self.xtts_ready = False

    # =========================
    # Interface pública (única)
    # =========================
    def falar(self, texto, emocao=0.0, prioridade=0):
        print(f"[VoiceManager] Pedido de fala: {texto}")

        engine = self._decidir_engine(emocao, prioridade)

        if engine == "xtts":
            return self._usar_xtts(texto)

        elif engine == "edge":
            return self._usar_edge(texto)

        print("[VoiceManager] Nenhuma engine disponível")
        return None

    # =========================
    # Decisão central
    # =========================
    def _decidir_engine(self, emocao, prioridade):
        if not self.internet:
            return "xtts"

        if prioridade >= 2 and self.xtts_ready:
            return "xtts"

        if emocao >= 0.7 and self.xtts_ready:
            return "xtts"

        return "edge"

    # =========================
    # Execução
    # =========================
    def _usar_edge(self, texto):
        try:
            print("[VoiceManager] → Edge")
            return self.edge_tts.falar(texto)

        except Exception as e:
            print("[VoiceManager] Edge falhou:", e)

            if self.xtts_ready:
                return self._usar_xtts(texto)

            return None

    def _usar_xtts(self, texto):
        if not self.xtts_ready:
            print("[VoiceManager] XTTS não pronto")
            return None

        try:
            print("[VoiceManager] → XTTS")
            return self.xtts.falar(texto)

        except Exception as e:
            print("[VoiceManager] XTTS falhou:", e)
            return None