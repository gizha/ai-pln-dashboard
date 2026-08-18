import requests

url = "http://127.0.0.1:8000/api/chat"
payload = {
    "question": "ada bidang apa aja di pln",
    "history": [],
    "provider": "gemini",
    "translate": True
}

try:
    response = requests.post(url, json=payload, timeout=30)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        res = response.json()
        print("Answer:", res.get("answer"))
        print("Translated Answer:", res.get("translated_answer"))
        print("SQL:", res.get("sql"))
        print("Rows:", res.get("rows"))
    else:
        print("Error:", response.text)
except Exception as e:
    print("Error connecting:", e)
