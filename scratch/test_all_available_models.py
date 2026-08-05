import os
import requests
from dotenv import load_dotenv

# Menguji beberapa variasi model Gemini (seperti gemini-3.5-flash, gemini-3.1-flash-lite, dll.) untuk membandingkan model mana yang paling cepat, akurat, dan stabil dalam memberikan respons.
load_dotenv(dotenv_path="separated_app/backend/.env", override=True)
api_key = os.getenv("GEMINI_API_KEY")

def try_model(model_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": "Hello, write a short word 'Hi'"}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Model: {model_name} -> Status: {response.status_code}")
        if response.status_code != 200:
            print("Response:", response.text[:300])
        else:
            print("Response:", response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip())
    except Exception as e:
        print(f"Model: {model_name} -> Error: {e}")

models_to_try = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest"
]

for model in models_to_try:
    print(f"\nTrying {model}...")
    try_model(model)
