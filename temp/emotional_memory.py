import time


class EmotionalMemory:
    def __init__(self):
        self.memories = []

    # -------------------------
    # SALVAR MEMÓRIA VIVA
    # -------------------------
    def remember(self, text, emotion, intensity=1.0):

        self.memories.append({
            "text": text,
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": time.time()
        })

        # mantém só últimas 100
        self.memories = self.memories[-100:]

    # -------------------------
    # BUSCA CONTEXTUAL
    # -------------------------
    def search(self, query):

        results = []

        for m in self.memories:
            if query in m["text"]:
                results.append(m)

        return results[-5:]  # últimas relevantes

    # -------------------------
    # BIAS EMOCIONAL
    # -------------------------
    def emotional_bias(self):

        if not self.memories:
            return "neutral"

        recent = self.memories[-10:]

        score = {
            "happy": 0,
            "tired": 0,
            "bored": 0,
            "neutral": 0
        }

        for m in recent:
            e = m["emotion"]
            if e in score:
                score[e] += m["intensity"]

        return max(score, key=score.get)

    # -------------------------
    # MEMÓRIA AFETA EMOÇÃO
    # -------------------------
    def emotional_recall(self):

        if not self.memories:
            return 0

        last = self.memories[-1]

        if last["emotion"] == "happy":
            return +5
        if last["emotion"] == "tired":
            return -5

        return 0