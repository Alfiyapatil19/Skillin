import requests

# Ollama local API endpoint (correct)
OLLAMA_URL = "http://localhost:11434/v1/generate"
MODEL_NAME = "mistral"

def call_ai(prompt: str):
    """
    Sends a prompt to the Ollama local model and returns the response text.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "max_tokens": 1000  # adjust if needed
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        # The response JSON contains 'response' field
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        print("Ollama Error:", e)
        return None
