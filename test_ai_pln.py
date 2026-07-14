import mysql.connector
import requests

# koneksi database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="karyawan_pln"
)

cursor = conn.cursor(dictionary=True)

# ambil data karyawan
cursor.execute("""
SELECT nama, divisi, jabatan
FROM karyawan_pln
LIMIT 5
""")

data = cursor.fetchall()


print("=== AI PLN Assistant ===")
print("Ketik 'exit' untuk keluar\n")

while True:
    pertanyaan = input("Anda : ")

    if pertanyaan.lower() == "exit":
        print("AI PLN : Sampai jumpa!")
        break

    prompt = f"""
Kamu adalah AI Assistant PLN.

Berikut data karyawan PLN:

{data}

Jawab pertanyaan user berdasarkan data tersebut.

Pertanyaan:
{pertanyaan}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    jawaban = response.json()["response"]

    print("\nAI PLN :", jawaban)
    print()