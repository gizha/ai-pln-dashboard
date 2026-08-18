import requests
import json

url = "http://127.0.0.1:8000/api/chat"

# Step 1: Ask "berapa persen karyawan ga masuk keseluruhan"
payload1 = {
    "question": "berapa persen karyawan ga masuk keseluruhan",
    "history": [],
    "provider": "ollama_cloud",
    "translate": True
}

print("Sending Q1 to local API (Ollama Cloud)...")
try:
    response1 = requests.post(url, json=payload1, timeout=60)
    print("Q1 Status:", response1.status_code)
    if response1.status_code == 200:
        res1 = response1.json()
        print("Answer 1:", res1.get("translated_answer") or res1.get("answer"))
        print("SQL 1:", res1.get("sql"))
        
        # Step 2: Ask "berapa orang 20% itu berarti?"
        history = [
            {"role": "user", "content": payload1["question"]},
            {"role": "assistant", "content": res1.get("translated_answer") or res1.get("answer")}
        ]
        
        payload2 = {
            "question": "berapa orang 20% itu berarti?",
            "history": history,
            "provider": "ollama_cloud",
            "translate": True
        }
        
        print("\nSending Q2 to local API (Ollama Cloud)...")
        response2 = requests.post(url, json=payload2, timeout=60)
        print("Q2 Status:", response2.status_code)
        if response2.status_code == 200:
            res2 = response2.json()
            print("Answer 2:", res2.get("translated_answer") or res2.get("answer"))
            print("SQL 2:", res2.get("sql"))
            print("Rows 2:", res2.get("rows"))
        else:
            print("Q2 Error:", response2.text)
    else:
        print("Q1 Error:", response1.text)
except Exception as e:
    print("Request failed:", e)
