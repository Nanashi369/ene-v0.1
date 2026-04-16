import json
import time
from dataclasses import dataclass


@dataclass
class MemoryPaths:
    short_path: str = "memory_short.json"
    medium_path: str = "memory_medium.json"
    summary_path: str = "memory_summary.json"


class LayeredMemoryManager:
    """
    Memória em camadas:
    - short: últimas interações (rápida, alta fidelidade)
    - medium: histórico compactado
    - summary: resumo periódico para contexto barato
    """

    def __init__(self, paths: MemoryPaths | None = None):
        self.paths = paths or MemoryPaths()
        self.short = self._load(self.paths.short_path, [])
        self.medium = self._load(self.paths.medium_path, [])
        self.summary = self._load(self.paths.summary_path, [])

        self.short_limit = 40
        self.medium_limit = 250
        self.summary_every = 12

    def _load(self, path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _save(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _persist(self):
        self._save(self.paths.short_path, self.short[-self.short_limit :])
        self._save(self.paths.medium_path, self.medium[-self.medium_limit :])
        self._save(self.paths.summary_path, self.summary[-80:])

    def remember(self, text, emotion, intensity=1.0):
        item = {
            "text": text,
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": time.time(),
        }
        self.short.append(item)
        self.medium.append(item)

        self.short = self.short[-self.short_limit :]
        self.medium = self.medium[-self.medium_limit :]

        if len(self.short) % self.summary_every == 0:
            self._build_summary()

        self._persist()

    def search(self, query):
        query = (query or "").lower().strip()

        # busca curta por relevância textual
        short_hits = []
        medium_hits = []

        def score(text: str):
            if not query:
                return 1
            words = [w for w in query.split(" ") if w]
            text_l = text.lower()
            return sum(1 for w in words if w in text_l)

        for m in self.short:
            s = score(m.get("text", ""))
            if s > 0:
                short_hits.append((s, m))

        for m in self.medium:
            s = score(m.get("text", ""))
            if s > 0:
                medium_hits.append((s, m))

        short_hits.sort(key=lambda x: x[0], reverse=True)
        medium_hits.sort(key=lambda x: x[0], reverse=True)

        merged = [m for _, m in short_hits[:4]] + [m for _, m in medium_hits[:3]]
        if not merged:
            merged = self.short[-5:]

        # remove duplicatas por timestamp
        seen = set()
        out = []
        for m in merged:
            ts = m.get("timestamp")
            if ts in seen:
                continue
            seen.add(ts)
            out.append(m)
        return out[-7:]

    def get_summary_text(self):
        if not self.summary:
            return ""
        return "\n".join(s.get("summary", "") for s in self.summary[-3:])

    def _build_summary(self):
        recent = self.short[-self.summary_every :]
        if not recent:
            return

        texts = [m.get("text", "") for m in recent if m.get("text")]
        if not texts:
            return

        # Sumarização leve e local (sem chamada extra de LLM):
        # reduz custo e mantém contexto básico.
        compact = " | ".join(texts[:8])
        if len(compact) > 400:
            compact = compact[:400] + "..."

        moods = {}
        for m in recent:
            emo = str(m.get("emotion", "neutral"))
            moods[emo] = moods.get(emo, 0) + 1
        dominant = max(moods, key=moods.get) if moods else "neutral"

        self.summary.append(
            {
                "summary": f"Resumo recente ({dominant}): {compact}",
                "timestamp": time.time(),
            }
        )

