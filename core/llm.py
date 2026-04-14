import requests
from core.brain import brain_tick

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def generate_response(prompt):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 40
            }
        })

        return response.json()["response"].strip()

    except:
        return "hm… deu algum problema, mas finge que foi charme."