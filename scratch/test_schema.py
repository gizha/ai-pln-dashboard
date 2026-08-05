import os
import mysql.connector
from dotenv import load_dotenv

# Menguji fungsi pembacaan struktur (skema) kolom database. Hasil bacaan skema yg dikirim ke Gemini AI agar AI tahu tabel dan kolom apa saja yang tersedia untuk dicari.
load_dotenv(dotenv_path="separated_app/backend/.env", override=True)

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

try:
    print("Connecting to DB...")
    conn = get_db_connection()
    print("Connected successfully!")
    cursor = conn.cursor()
    print("Running query on INFORMATION_SCHEMA...")
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
    """, (DB_NAME,))
    rows = cursor.fetchall()
    print(f"Query finished! Returned {len(rows)} rows.")
    for r in rows[:10]:
        print(r)
    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
