import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="separated_app/backend/.env", override=True)
api_key = os.getenv("GEMINI_API_KEY")

def try_model(model_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": "Hello, write a short word 'Hi'"}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Model: {model_name} -> Status: {response.status_code}")
        if response.status_code != 200:
            print("Response:", response.text)
        else:
            print("Response:", response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", ""))
    except Exception as e:
        print("Error:", e)

print("Trying gemini-2.5-flash...")
try_model("gemini-2.5-flash")

print("\nTrying gemini-1.5-flash...")
try_model("gemini-1.5-flash")

print("\nTrying gemini-2.0-flash...")
try_model("gemini-2.0-flash")
