import json
import requests


class OllamaService:

    def __init__(
        self,
        model_name="llama3.2:3b",
        base_url="http://127.0.0.1:11434"
    ):

        self.model_name = model_name
        self.url = f"{base_url}/api/generate"

    def generate(self, prompt):

        response = requests.post(
            self.url,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_ctx": 4096
                }
            },
            timeout=600
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            ""
        ).strip()

    def generate_json(self, prompt, schema, *, num_predict=None, timeout=600):

        response = requests.post(
            self.url,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": schema,
                "options": {
                    "temperature": 0,
                    "num_ctx": 4096,
                    **({"num_predict": num_predict} if num_predict is not None else {})
                }
            },
            timeout=timeout
        )

        response.raise_for_status()

        text = response.json().get(
            "response",
            ""
        ).strip()

        if not text:
            raise ValueError(
                "Ollama devolvió una respuesta vacía."
            )

        try:

            return json.loads(text)

        except json.JSONDecodeError as error:

            raise ValueError(
                "Ollama no devolvió JSON válido."
            ) from error
