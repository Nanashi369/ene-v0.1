import os
import requests


class OllamaLLM:
    def __init__(self, model: str | None = None, url: str | None = None):
        self.url = url or os.getenv("ENE_OLLAMA_URL", "http://localhost:11434/api/generate")
        self.model = model or os.getenv("ENE_OLLAMA_MODEL", "llama3")

    def generate(self, prompt):
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )

            return response.json().get("response", "").strip()

        except Exception as e:
            return f"[LLM ERROR] {str(e)}"

    def stream_generate(self, prompt):
        """
        Streaming incremental (Ollama NDJSON).
        Em caso de falha, retorna uma única chunk com generate().
        """
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                },
                stream=True,
                timeout=120,
            )
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    data = requests.models.complexjson.loads(line)
                except Exception:
                    continue
                chunk = data.get("response", "")
                if chunk:
                    yield chunk
                if data.get("done"):
                    break
        except Exception:
            text = self.generate(prompt)
            if text:
                yield text


# Compatibilidade com código atual
LLMClient = OllamaLLM