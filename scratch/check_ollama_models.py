import requests
import json

try:
    print("Checking Ollama connection and available models...")
    response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
    print("Status:", response.status_code)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print("Installed models:")
        for m in models:
            print(f"- {m['name']} (size: {m.get('size', 0) / (1024*1024):.2f} MB)")
    else:
        print("Response:", response.text)
except Exception as e:
    print("Failed to connect to Ollama local:", e)
