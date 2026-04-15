class LLMClient:
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = "llama3"

    def generate(self, prompt):
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json().get("response", "").strip()