import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="separated_app/backend/.env", override=True)
api_key = os.getenv("GEMINI_API_KEY")
print("API Key exists:", bool(api_key))

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
    response = requests.get(url)
    print("Status code:", response.status_code)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print("Available models:")
        for m in models:
            print(" -", m.get("name"))
    else:
        print("Error details:", response.text)
except Exception as e:
    print("Request exception:", e)
