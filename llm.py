import requests
from config import OLLAMA_URL, SELECTED_MODEL

class LLM:

    def __init__(self):
        self.url = OLLAMA_URL
        self.model = SELECTED_MODEL

    def ask(self, question: str) -> str:
        print(self.model)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ],
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]