import os
import mysql.connector
import requests
import re
from dotenv import load_dotenv

# Menguji keakuratan logika Text-to-SQL. File ini memuat skema database lalu mengirim pertanyaan uji coba (misal: "pembelian produk terbanyak siapa") ke AI untuk mengecek apakah query SQL yang dihasilkan sudah benar, aman, dan valid sblm di chatbot utama.
load_dotenv(dotenv_path="separated_app/backend/.env", override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "railway")
DB_PORT = int(os.getenv("DB_PORT", 3306))

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

def call_gemini_api(prompt, temperature=0.0):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json",
        "Connection": "close"
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature
        }
    }
    print("Calling Gemini API...")
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print("Gemini response status:", response.status_code)
    response.raise_for_status()
    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]

def build_schema_text():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
    """, (DB_NAME,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    structure = {}
    for db, table, col, dtype in rows:
        structure.setdefault(db, {}).setdefault(table, []).append(f"{col} ({dtype})")

    lines = []
    for db, tables in structure.items():
        lines.append(f"Database `{db}`:")
        for table, cols in tables.items():
            lines.append(f"  - Tabel `{db}.{table}`: {', '.join(cols)}")
    return "\n".join(lines)

def clean_sql(raw_text):
    text = raw_text.strip()
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    sql_lines = []
    capturing = False
    for line in lines:
        if line.lower().startswith("select"):
            capturing = True
        if capturing:
            sql_lines.append(line)
    query = " ".join(sql_lines) if sql_lines else text
    query = query.split(";")[0].strip() + ";"
    return query

def generate_sql(question):
    schema_text = build_schema_text()
    prompt = f"""Kamu adalah penerjemah pertanyaan Bahasa Indonesia menjadi query SQL MySQL.

Berikut skema semua database yang tersedia:
{schema_text}

Aturan:
- Hanya buat query SELECT. Jangan pernah membuat INSERT, UPDATE, DELETE, DROP, atau ALTER.
- WAJIB tulis nama tabel lengkap dengan format database.tabel, contoh: {DB_NAME}.karyawan_pln atau {DB_NAME}.customers.
- Pilih database yang paling sesuai dengan topik pertanyaan. Pertanyaan soal karyawan/pegawai PLN pakai database karyawan_pln. Pertanyaan soal customer/order/produk/pembayaran pakai database classicmodels.
- Kalau butuh JOIN antar tabel dalam 1 database, tetap qualify tiap tabel dengan nama database-nya.
- Hanya gunakan nama kolom yang benar-benar ada di skema di atas. Jangan mengarang nama kolom.
- Untuk pencarian teks gunakan LIKE '%kata%'.
- Jawab HANYA dengan query SQL, tanpa penjelasan, tanpa markdown, tanpa tanda kutip pembungkus.
- Query harus diakhiri dengan titik koma.

Contoh:
Pertanyaan: berapa jumlah karyawan?
SQL: SELECT COUNT(*) AS total FROM {DB_NAME}.karyawan_pln;

Pertanyaan: siapa saja karyawan di divisi Keuangan?
SQL: SELECT nama, jabatan FROM {DB_NAME}.karyawan_pln WHERE divisi = 'Keuangan';

Pertanyaan: {question}
SQL:"""
    raw = call_gemini_api(prompt, temperature=0.0)
    return clean_sql(raw)

try:
    print("Testing generate_sql...")
    sql = generate_sql("pembelian produk terbanyak siapa")
    print("Generated SQL:", sql)
except Exception as e:
    print("Error:", e)
