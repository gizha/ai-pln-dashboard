import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="separated_app/backend/.env", override=True)

host = os.getenv("OLLAMA_CLOUD_HOST")
api_key = os.getenv("OLLAMA_CLOUD_API_KEY")

print(f"Connecting to Ollama Cloud at {host}...")
url = f"{host}/api/tags"
headers = {}
if api_key:
    headers["Authorization"] = f"Bearer {api_key}"

try:
    response = requests.get(url, headers=headers, timeout=10)
    print("Status:", response.status_code)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print("Available models on Ollama Cloud:")
        for m in models:
            print(f"- {m['name']}")
    else:
        print("Response:", response.text)
except Exception as e:
    print("Error:", e)
