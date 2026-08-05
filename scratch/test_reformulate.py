import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="separated_app/backend/.env", override=True)
ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

history_text = """User: berapa aja umur staf
Assistant: Berikut adalah data hasil query yang ditemukan di database lokal:
| usia |
|---|
| 25 |
| 51 |
| 46 |
"""

question = "bar chartnya gimana"

prompt = f"""Tugas Anda adalah memeriksa apakah "Pertanyaan Lanjutan Terbaru" memerlukan konteks dari "Riwayat Percakapan" untuk dipahami.

Riwayat Percakapan:
{history_text}
Pertanyaan Lanjutan Terbaru: {question}

Aturan Penting:
1. Permintaan format (seperti meminta grafik/chart, tabel, atau pengurutan dari data sebelumnya) adalah pertanyaan lanjutan yang berhubungan. Anda harus menggabungkannya dengan subjek riwayat (contoh: "bar chartnya gimana" menjadi "tampilkan bar chart untuk sebaran umur staf").
2. Jika "Pertanyaan Lanjutan Terbaru" benar-benar membahas topik/subjek baru yang tidak berkaitan dengan riwayat (misalnya beralih ke pelanggan/penjualan, sementara riwayat membahas karyawan), Anda WAJIB mengembalikan "Pertanyaan Lanjutan Terbaru" secara persis apa adanya tanpa diubah!
3. Hanya ubah pertanyaan jika menggunakan kata ganti ("dia", "gajinya") atau kata penunjuk format ("grafiknya", "tabelnya").
4. Jawab HANYA dengan teks pertanyaan mandiri hasil penggabungan/reformulasi saja, tanpa penjelasan atau komentar tambahan.

Pertanyaan Mandiri:"""

url = f"{ollama_host}/api/generate"
payload = {
    "model": ollama_model,
    "prompt": prompt,
    "stream": False,
    "options": {"temperature": 0.0}
}

try:
    response = requests.post(url, json=payload, timeout=90)
    print("Ollama Response:", response.json().get("response", "").strip())
except Exception as e:
    print("Error:", e)
