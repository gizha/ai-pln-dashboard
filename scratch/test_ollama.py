import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="separated_app/backend/.env", override=True)
ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

def test_ollama_connection():
    url = f"{ollama_host}/api/generate"
    payload = {
        "model": ollama_model,
        "prompt": "Tulis satu kata saja: Halo",
        "stream": False
    }
    print(f"Mencoba menghubungi Ollama di {url} menggunakan model {ollama_model}...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            print("Berhasil! Respon Ollama:", result)
        else:
            print("Gagal! Detail error:", response.text)
    except Exception as e:
        print("\n[PERINGATAN] Gagal terhubung ke Ollama lokal!")
        print("Pastikan aplikasi Ollama sudah berjalan dan model sudah diunduh.")
        print(f"Perintah untuk mengunduh model: 'ollama run {ollama_model}'")
        print("Detail Error:", e)

if __name__ == "__main__":
    test_ollama_connection()
