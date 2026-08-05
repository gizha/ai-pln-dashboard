import os
import re
import requests
import sqlite3
import threading
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv

# Load environment variables (added comment to trigger uvicorn reload)
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path, override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "railway")
DB_PORT = int(os.getenv("DB_PORT", 3306))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")


app = FastAPI(title="AI PLN Backend API")

# Enable CORS for frontend calling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "local_fallback.db")

def init_mysql_db():
    try:
        # Connect to MySQL (without specifying database first to create it if missing)
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            ssl_disabled=True,
            connection_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS karyawan_pln")
        cursor.execute("USE karyawan_pln")
        
        # Create karyawan_pln table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS karyawan_pln (
            id INT AUTO_INCREMENT PRIMARY KEY,
            NIP VARCHAR(50) UNIQUE NOT NULL,
            Nama VARCHAR(100) NOT NULL,
            Jenis_Kelamin CHAR(1),
            Tanggal_Lahir DATE,
            Divisi VARCHAR(50),
            Jabatan VARCHAR(50),
            Tanggal_Masuk DATE,
            Status_Pegawai VARCHAR(50),
            Email VARCHAR(100)
        )
        """)
        
        # Populate karyawan_pln if empty
        cursor.execute("SELECT COUNT(*) FROM karyawan_pln")
        if cursor.fetchone()[0] == 0:
            karyawan_data = [
                ('NP100000', 'Yoga Permata', 'P', '2001-05-16', 'Keuangan', 'Staff', '2023-11-09', 'Aktif', 'yoga.permata@pln.id'),
                ('NP100001', 'Dimas Wijaya', 'P', '1974-11-24', 'Pengadaan', 'Supervisor', '1997-09-10', 'Aktif', 'dimas.wijaya@pln.id'),
                ('NP100002', 'Lina Wijaya', 'L', '1980-01-16', 'K3L', 'Staff', '2008-03-12', 'Aktif', 'lina.wijaya@pln.id'),
                ('NP100003', 'Yoga Maulana', 'L', '1984-10-01', 'Operasi', 'Assistant Manager', '2012-02-06', 'Aktif', 'yoga.maulana@pln.id'),
                ('NP100004', 'Nanda Pratama', 'L', '1993-03-10', 'Pengadaan', 'Supervisor', '2016-10-31', 'Aktif', 'nanda.pratama@pln.id'),
                ('NP100005', 'Rina Maulana', 'P', '1987-11-30', 'SDM', 'Staff', '2010-07-20', 'Aktif', 'rina.maulana@pln.id'),
                ('NP100006', 'Ayu Permata', 'P', '1971-07-02', 'Keuangan', 'Assistant Manager', '2001-01-09', 'Aktif', 'ayu.permata@pln.id'),
                ('NP100007', 'Yusuf Firmansyah', 'P', '2001-05-19', 'Pembangkitan', 'Staff', '2023-01-18', 'Aktif', 'yusuf.firmansyah@pln.id'),
                ('NP100008', 'Rina Permata', 'L', '1987-02-06', 'Operasi', 'Manager', '2007-05-20', 'Aktif', 'rina.permata@pln.id'),
                ('NP100009', 'Nabila Wijaya', 'P', '1990-11-29', 'Operasi', 'Staff', '2010-10-03', 'Aktif', 'nabila.wijaya@pln.id')
            ]
            cursor.executemany("""
            INSERT INTO karyawan_pln (NIP, Nama, Jenis_Kelamin, Tanggal_Lahir, Divisi, Jabatan, Tanggal_Masuk, Status_Pegawai, Email)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, karyawan_data)

        # Drop absensi table if it exists to overwrite invalid NIP seeds
        cursor.execute("DROP TABLE IF EXISTS absensi")
        
        # Create absensi table
        cursor.execute("""
        CREATE TABLE absensi (
            id INT AUTO_INCREMENT PRIMARY KEY,
            NIP VARCHAR(50) NOT NULL,
            Tanggal DATE NOT NULL,
            Status VARCHAR(20) NOT NULL,
            FOREIGN KEY (NIP) REFERENCES karyawan_pln(NIP)
        )
        """)
        
        # Populate absensi
        attendance_data = [
            # 2026-08-02
            ('NP100000', '2026-08-02', 'Masuk'), ('NP100001', '2026-08-02', 'Masuk'), ('NP100002', '2026-08-02', 'Masuk'),
            ('NP100003', '2026-08-02', 'Masuk'), ('NP100004', '2026-08-02', 'Masuk'), ('NP100005', '2026-08-02', 'Tidak'),
            ('NP100006', '2026-08-02', 'Masuk'), ('NP100007', '2026-08-02', 'Masuk'), ('NP100008', '2026-08-02', 'Masuk'),
            ('NP100009', '2026-08-02', 'Tidak'),
            # 2026-08-03
            ('NP100000', '2026-08-03', 'Masuk'), ('NP100001', '2026-08-03', 'Masuk'), ('NP100002', '2026-08-03', 'Tidak'),
            ('NP100003', '2026-08-03', 'Masuk'), ('NP100004', '2026-08-03', 'Masuk'), ('NP100005', '2026-08-03', 'Masuk'),
            ('NP100006', '2026-08-03', 'Masuk'), ('NP100007', '2026-08-03', 'Tidak'), ('NP100008', '2026-08-03', 'Masuk'),
            ('NP100009', '2026-08-03', 'Masuk'),
            # 2026-08-04
            ('NP100000', '2026-08-04', 'Masuk'), ('NP100001', '2026-08-04', 'Masuk'), ('NP100002', '2026-08-04', 'Masuk'),
            ('NP100003', '2026-08-04', 'Tidak'), ('NP100004', '2026-08-04', 'Masuk'), ('NP100005', '2026-08-04', 'Masuk'),
            ('NP100006', '2026-08-04', 'Masuk'), ('NP100007', '2026-08-04', 'Tidak'), ('NP100008', '2026-08-04', 'Masuk'),
            ('NP100009', '2026-08-04', 'Masuk')
        ]
        cursor.executemany("""
        INSERT INTO absensi (NIP, Tanggal, Status)
        VALUES (%s, %s, %s)
        """, attendance_data)

        # Create classicmodels database & customers table
        cursor.execute("CREATE DATABASE IF NOT EXISTS classicmodels")
        cursor.execute("USE classicmodels")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customerNumber INT PRIMARY KEY,
            customerName VARCHAR(100) NOT NULL,
            city VARCHAR(50),
            country VARCHAR(50),
            creditLimit DECIMAL(10,2),
            salesRepEmployeeNumber INT
        )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        if cursor.fetchone()[0] == 0:
            customer_data = [
                (101, 'Atelier Graphique', 'Paris', 'France', 21000, 1370),
                (112, 'Signal Gift Stores', 'Las Vegas', 'USA', 71800, 1166),
                (114, 'Australian Collectors, Co.', 'Melbourne', 'Australia', 117300, 1166),
                (119, 'La Rochelle Gifts', 'La Rochelle', 'France', 118400, 1370),
                (121, 'Baane Inc.', 'Stavern', 'Norway', 81700, 1504),
                (124, 'Mini Creations Ltd.', 'New York', 'USA', 210500, 1286),
                (125, 'Havel & Zbyszek Co', 'Warsaw', 'Poland', 0, 1501),
                (128, 'Blauer See Auto', 'Berlin', 'Germany', 59300, 1504),
                (129, 'Mini Wheels Co.', 'San Francisco', 'USA', 64600, 1286),
                (131, 'Land of Toys Inc.', 'NYC', 'USA', 114900, 1323)
            ]
            cursor.executemany("""
            INSERT INTO customers (customerNumber, customerName, city, country, creditLimit, salesRepEmployeeNumber)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, customer_data)

        conn.commit()
        cursor.close()
        conn.close()
        print("MySQL Database auto-initialized successfully.")
    except Exception as err:
        print(f"Skipped MySQL initialization: {err}")

def init_sqlite_db():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables to refresh with correct NIPs
    cursor.execute("DROP TABLE IF EXISTS absensi")
    cursor.execute("DROP TABLE IF EXISTS karyawan_pln")
    cursor.execute("DROP TABLE IF EXISTS customers")
    
    # Create karyawan_pln table
    cursor.execute("""
    CREATE TABLE karyawan_pln (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        NIP TEXT UNIQUE NOT NULL,
        Nama TEXT NOT NULL,
        Jenis_Kelamin TEXT,
        Tanggal_Lahir TEXT,
        Divisi TEXT,
        Jabatan TEXT,
        Tanggal_Masuk TEXT,
        Status_Pegawai TEXT,
        Email TEXT
    )
    """)
    
    karyawan_data = [
        ('NP100000', 'Yoga Permata', 'P', '2001-05-16', 'Keuangan', 'Staff', '2023-11-09', 'Aktif', 'yoga.permata@pln.id'),
        ('NP100001', 'Dimas Wijaya', 'P', '1974-11-24', 'Pengadaan', 'Supervisor', '1997-09-10', 'Aktif', 'dimas.wijaya@pln.id'),
        ('NP100002', 'Lina Wijaya', 'L', '1980-01-16', 'K3L', 'Staff', '2008-03-12', 'Aktif', 'lina.wijaya@pln.id'),
        ('NP100003', 'Yoga Maulana', 'L', '1984-10-01', 'Operasi', 'Assistant Manager', '2012-02-06', 'Aktif', 'yoga.maulana@pln.id'),
        ('NP100004', 'Nanda Pratama', 'L', '1993-03-10', 'Pengadaan', 'Supervisor', '2016-10-31', 'Aktif', 'nanda.pratama@pln.id'),
        ('NP100005', 'Rina Maulana', 'P', '1987-11-30', 'SDM', 'Staff', '2010-07-20', 'Aktif', 'rina.maulana@pln.id'),
        ('NP100006', 'Ayu Permata', 'P', '1971-07-02', 'Keuangan', 'Assistant Manager', '2001-01-09', 'Aktif', 'ayu.permata@pln.id'),
        ('NP100007', 'Yusuf Firmansyah', 'P', '2001-05-19', 'Pembangkitan', 'Staff', '2023-01-18', 'Aktif', 'yusuf.firmansyah@pln.id'),
        ('NP100008', 'Rina Permata', 'L', '1987-02-06', 'Operasi', 'Manager', '2007-05-20', 'Aktif', 'rina.permata@pln.id'),
        ('NP100009', 'Nabila Wijaya', 'P', '1990-11-29', 'Operasi', 'Staff', '2010-10-03', 'Aktif', 'nabila.wijaya@pln.id')
    ]
    cursor.executemany("""
    INSERT INTO karyawan_pln (NIP, Nama, Jenis_Kelamin, Tanggal_Lahir, Divisi, Jabatan, Tanggal_Masuk, Status_Pegawai, Email)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, karyawan_data)

    # Create absensi table
    cursor.execute("""
    CREATE TABLE absensi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        NIP TEXT NOT NULL,
        Tanggal TEXT NOT NULL,
        Status TEXT NOT NULL,
        FOREIGN KEY (NIP) REFERENCES karyawan_pln(NIP)
    )
    """)
    
    attendance_data = [
        ('NP100000', '2026-08-02', 'Masuk'), ('NP100001', '2026-08-02', 'Masuk'), ('NP100002', '2026-08-02', 'Masuk'),
        ('NP100003', '2026-08-02', 'Masuk'), ('NP100004', '2026-08-02', 'Masuk'), ('NP100005', '2026-08-02', 'Tidak'),
        ('NP100006', '2026-08-02', 'Masuk'), ('NP100007', '2026-08-02', 'Masuk'), ('NP100008', '2026-08-02', 'Masuk'),
        ('NP100009', '2026-08-02', 'Tidak'),
        
        ('NP100000', '2026-08-03', 'Masuk'), ('NP100001', '2026-08-03', 'Masuk'), ('NP100002', '2026-08-03', 'Tidak'),
        ('NP100003', '2026-08-03', 'Masuk'), ('NP100004', '2026-08-03', 'Masuk'), ('NP100005', '2026-08-03', 'Masuk'),
        ('NP100006', '2026-08-03', 'Masuk'), ('NP100007', '2026-08-03', 'Tidak'), ('NP100008', '2026-08-03', 'Masuk'),
        ('NP100009', '2026-08-03', 'Masuk'),
        
        ('NP100000', '2026-08-04', 'Masuk'), ('NP100001', '2026-08-04', 'Masuk'), ('NP100002', '2026-08-04', 'Masuk'),
        ('NP100003', '2026-08-04', 'Tidak'), ('NP100004', '2026-08-04', 'Masuk'), ('NP100005', '2026-08-04', 'Masuk'),
        ('NP100006', '2026-08-04', 'Masuk'), ('NP100007', '2026-08-04', 'Tidak'), ('NP100008', '2026-08-04', 'Masuk'),
        ('NP100009', '2026-08-04', 'Masuk')
    ]
    cursor.executemany("""
    INSERT INTO absensi (NIP, Tanggal, Status)
    VALUES (?, ?, ?)
    """, attendance_data)

    # Create customers table
    cursor.execute("""
    CREATE TABLE customers (
        customerNumber INTEGER PRIMARY KEY,
        customerName TEXT NOT NULL,
        city TEXT,
        country TEXT,
        creditLimit REAL,
        salesRepEmployeeNumber INTEGER
    )
    """)
    
    customer_data = [
        (101, 'Atelier Graphique', 'Paris', 'France', 21000, 1370),
        (112, 'Signal Gift Stores', 'Las Vegas', 'USA', 71800, 1166),
        (114, 'Australian Collectors, Co.', 'Melbourne', 'Australia', 117300, 1166),
        (119, 'La Rochelle Gifts', 'La Rochelle', 'France', 118400, 1370),
        (121, 'Baane Inc.', 'Stavern', 'Norway', 81700, 1504),
        (124, 'Mini Creations Ltd.', 'New York', 'USA', 210500, 1286),
        (125, 'Havel & Zbyszek Co', 'Warsaw', 'Poland', 0, 1501),
        (128, 'Blauer See Auto', 'Berlin', 'Germany', 59300, 1504),
        (129, 'Mini Wheels Co.', 'San Francisco', 'USA', 64600, 1286),
        (131, 'Land of Toys Inc.', 'NYC', 'USA', 114900, 1323)
    ]
    cursor.executemany("""
    INSERT INTO customers (customerNumber, customerName, city, country, creditLimit, salesRepEmployeeNumber)
    VALUES (?, ?, ?, ?, ?, ?)
    """, customer_data)

    conn.commit()
    conn.close()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_sqlite_connection():
    init_sqlite_db()
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = dict_factory
    return conn

def get_db_connection(database=None):
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database if database is not None else DB_NAME,
        port=DB_PORT,
        ssl_disabled=True,
        connection_timeout=5
    )

@app.on_event("startup")
def startup_event():
    init_sqlite_db()
    init_mysql_db()

def call_gemini_api(prompt, temperature=0.0):
    import time
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set in backend.")
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
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Jika 429 (Too Many Requests)
            if response.status_code == 429:
                try:
                    res_json = response.json()
                    error_msg = res_json.get("error", {}).get("message", "")
                    # Jika ini batas kuota harian yang habis, langsung gagalkan tanpa retry
                    if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                        raise HTTPException(
                            status_code=429,
                            detail="Batas kuota harian API Gemini gratisan Anda telah habis (maksimal 20 requests per hari). Silakan ganti API Key di file .env dengan key baru, atau gunakan Ollama lokal jika tersedia."
                        )
                except Exception as json_err:
                    if isinstance(json_err, HTTPException):
                        raise json_err
                
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                    
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            # Cek apakah error tidak bisa di-retry (misal: 400 Bad Request, 403 Forbidden, 404 Not Found)
            is_retryable = True
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code not in [429, 502, 503, 504]:
                    is_retryable = False
            
            if not is_retryable or attempt == max_retries - 1:
                # Sembunyikan API key dari pesan error demi alasan keamanan
                if status_code == 429:
                    raise HTTPException(
                        status_code=429,
                        detail="Batas kuota/kecepatan (Rate Limit 429) API Gemini gratisan Anda sedang penuh. Silakan tunggu sekitar 30-60 detik lalu coba lagi."
                    )
                else:
                    msg = str(e)
                    if GEMINI_API_KEY:
                        msg = msg.replace(GEMINI_API_KEY, "HIDDEN_KEY")
                    msg = re.sub(r'key=[a-zA-Z0-9_\-]+', 'key=HIDDEN_KEY', msg)
                    raise HTTPException(
                        status_code=500,
                        detail=f"Terjadi kesalahan saat memanggil Gemini API: {msg}"
                    )
            
            time.sleep(2 ** attempt)

def call_ollama_api(prompt, model=None, temperature=0.0):
    if model is None:
        model = OLLAMA_MODEL
    url = f"{OLLAMA_HOST}/api/generate"
    headers = {
        "Content-Type": "application/json",
        "Connection": "close"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Gagal terhubung ke Ollama lokal di {OLLAMA_HOST}. Pastikan aplikasi Ollama sudah berjalan dan model '{model}' sudah diunduh menggunakan perintah 'ollama run {model}'."
        )

# Thread-local state to track LLM provider fallback
thread_local = threading.local()

def get_fallback_flag():
    return getattr(thread_local, "fallback_to_ollama", False)

def set_fallback_flag(val: bool):
    thread_local.fallback_to_ollama = val

def call_llm(prompt, provider="gemini", temperature=0.0):
    if provider.lower() == "ollama":
        return call_ollama_api(prompt, temperature=temperature)
    else:
        try:
            return call_gemini_api(prompt, temperature=temperature)
        except Exception as e:
            print(f"Gemini API call failed: {e}. Trying fallback to Ollama.")
            set_fallback_flag(True)
            try:
                return call_ollama_api(prompt, temperature=temperature)
            except Exception as ollama_err:
                print(f"Ollama fallback also failed: {ollama_err}")
                raise e

def build_schema_text():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA IN ('karyawan_pln', 'classicmodels')
            ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
        """)
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
    except Exception as e:
        # Fallback schema description for offline/SQLite mode
        return """Database `karyawan_pln`:
  - Tabel `karyawan_pln.karyawan_pln`: id (int), NIP (varchar), Nama (varchar), Jenis_Kelamin (char), Tanggal_Lahir (date), Divisi (varchar), Jabatan (varchar), Tanggal_Masuk (date), Status_Pegawai (varchar), Email (varchar)
  - Tabel `karyawan_pln.absensi`: id (int), NIP (varchar), Tanggal (date), Status (varchar)
Database `classicmodels`:
  - Tabel `classicmodels.customers`: customerNumber (int), customerName (varchar), city (varchar), country (varchar), creditLimit (decimal), salesRepEmployeeNumber (int)"""

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

def is_safe_select(query):
    q = query.lower()
    if not q.strip().startswith("select"):
        return False
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate", "create", "grant", "revoke", "--", "/*"]
    for kw in forbidden:
        if kw in q:
            return False
    return True

# Fungsi ini bertugas membuat instruksi (prompt) terstruktur agar Gemini hanya menerjemahkan pertanyaan menjadi query SQL berdasarkan informasi struktur tabel (schema) saja
def generate_sql(question, provider="gemini"):
    schema_text = build_schema_text()
    prompt = f"""Kamu adalah penerjemah pertanyaan Bahasa Indonesia menjadi query SQL MySQL.

Berikut skema semua database yang tersedia:
{schema_text}

Aturan:
- Hanya buat query SELECT. Jangan pernah membuat INSERT, UPDATE, DELETE, DROP, atau ALTER.
- WAJIB tulis nama tabel lengkap dengan format database.tabel, contoh: karyawan_pln.karyawan_pln atau classicmodels.customers.
- Pilih database yang paling sesuai dengan topik pertanyaan. Pertanyaan soal karyawan/pegawai PLN pakai database karyawan_pln. Pertanyaan soal customer/order/produk/pembayaran pakai database classicmodels.
- Kalau butuh JOIN antar tabel dalam 1 database, tetap qualify tiap tabel dengan nama database-nya.
- Hanya gunakan nama kolom yang benar-benar ada di skema di atas. Jangan mengarang nama kolom.
- Untuk pencarian teks gunakan LIKE '%kata%'.
- Jawab HANYA dengan query SQL, tanpa penjelasan, tanpa markdown, tanda kutip pembungkus.
- Query harus diakhiri dengan titik koma.

Contoh:
Pertanyaan: berapa jumlah karyawan?
SQL: SELECT COUNT(*) AS total FROM karyawan_pln.karyawan_pln;

Pertanyaan: siapa saja karyawan di divisi Keuangan?
SQL: SELECT nama, jabatan FROM karyawan_pln.karyawan_pln WHERE divisi = 'Keuangan';

Pertanyaan: berapa banyak karyawan perempuan?
SQL: SELECT COUNT(*) AS total FROM karyawan_pln.karyawan_pln WHERE jenis_kelamin = 'P';

Pertanyaan: siapa saja customer dari Prancis?
SQL: SELECT customerName, city FROM classicmodels.customers WHERE country = 'France';

Pertanyaan: berapa jumlah customer di kota Nantes?
SQL: SELECT COUNT(*) AS total FROM classicmodels.customers WHERE city = 'Nantes';

Pertanyaan: berapa jumlah karyawan yang masuk (hadir) pada tanggal 2026-08-04?
SQL: SELECT COUNT(*) AS total FROM karyawan_pln.absensi WHERE Tanggal = '2026-08-04' AND Status = 'Masuk';

Pertanyaan: siapa saja karyawan divisi IT yang tidak masuk pada tanggal 2026-08-04?
SQL: SELECT k.nama FROM karyawan_pln.karyawan_pln k JOIN karyawan_pln.absensi a ON k.nip = a.NIP WHERE k.divisi = 'IT' AND a.Tanggal = '2026-08-04' AND a.Status = 'Tidak';

Pertanyaan: pembayaran produk terlama tanggal berapa dan oleh siapa?
SQL: SELECT p.paymentDate, c.customerName FROM classicmodels.payments p JOIN classicmodels.customers c ON p.customerNumber = c.customerNumber ORDER BY p.paymentDate ASC LIMIT 1;

Pertanyaan: siapa saja customer yang membayar terbanyak dan berapa jumlahnya?
SQL: SELECT c.customerName, SUM(p.amount) AS total_payment FROM classicmodels.customers c JOIN classicmodels.payments p ON c.customerNumber = p.customerNumber GROUP BY c.customerName ORDER BY total_payment DESC LIMIT 5;

Pertanyaan: {question}
SQL:"""
    # Memanggil API LLM dengan parameter provider dan temperature=0.0
    raw = call_llm(prompt, provider=provider, temperature=0.0)
    return clean_sql(raw)

def summarize_result(question, rows):
    # 1. Jika data kosong, langsung kembalikan pesan gagal secara lokal
    if not rows:
        return "Data tidak ditemukan untuk pertanyaan tersebut di database lokal."
    
    # 2. Jika hasilnya cuma 1 baris & 1 kolom (seperti total COUNT/jumlah data)
    if len(rows) == 1 and len(rows[0]) == 1:
        key, val = list(rows[0].items())[0]
        # Format nilai angka agar rapi jika float/int (Merapikan format angka ribuan secara lokal menggunakan Python)
        if isinstance(val, float):
            val = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        elif isinstance(val, int):
            val = f"{val:,}".replace(",", ".")
        return f"Berdasarkan data di database lokal, hasil pencarian **{key}** adalah: =={val}=="
    
    # 3. Jika hasilnya banyak kolom/baris, format sebagai Markdown Table
    # Filter keys to exclude ID / Password demi privasi
    sample_row = rows[0]
    headers = [k for k in sample_row.keys() if k.lower() not in ["id", "password"]]
    
    if not headers:
        return "Data ditemukan tetapi disembunyikan demi alasan privasi."
        
    markdown_lines = []
    markdown_lines.append("Berikut adalah data hasil query yang ditemukan di database lokal:")
    markdown_lines.append("")
    
    # Header row
    markdown_lines.append("| " + " | ".join(headers) + " |")
    # Separator row
    markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    
    # Data rows (max 15 agar bubble chat tidak terlalu panjang)
    for row in rows[:15]:
        vals = []
        for h in headers:
            val = row.get(h, "-")
            if val is None:
                val = "-"
            # Format angka agar rapi
            if isinstance(val, float):
                val = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            elif isinstance(val, int):
                # Jangan format NIP atau ID kode pos dengan titik pemisah ribuan
                if h.lower() not in ["nip", "customernumber", "salesrepemployeenumber"]:
                    val = f"{val:,}".replace(",", ".")
            vals.append(str(val).replace("|", "\\|")) # escape tanda pipa
        markdown_lines.append("| " + " | ".join(vals) + " |")
        
    # 4. Jika datanya sangat banyak, beri catatan kaki
    if len(rows) > 15:
        markdown_lines.append("")
        markdown_lines.append(f"*... dan {len(rows) - 15} data lainnya (bisa dilihat lengkap di tabel dashboard).*")
        
    return "\n".join(markdown_lines)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: List[ChatMessage] = []
    provider: str = "gemini"

@app.get("/api/data")
def get_table_data(table: str = "karyawan_pln", db: str = "karyawan_pln"):
    # Bersihkan nama tabel dan db dari karakter aneh demi keamanan SQL Injection sederhana
    if not re.match(r"^[a-zA-Z0-9_]+$", table) or not re.match(r"^[a-zA-Z0-9_]+$", db):
        raise HTTPException(status_code=400, detail="Invalid table or database name.")
        
    try:
        conn = get_db_connection(database=db)
        cursor = conn.cursor(dictionary=True)
        # Ambil semua data lengkap agar frontend bisa melakukan paginasi dan grafik dengan akurat
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"table": table, "data": rows, "mode": "online"}
    except Exception as e:
        print(f"Error connecting to MySQL for table {table}: {e}. Falling back to SQLite.")
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            # Mapping tabel classicmodels dan absensi ke SQLite fallback
            if table == "customers":
                sqlite_table = "customers"
            elif table == "absensi":
                sqlite_table = "absensi"
            else:
                sqlite_table = "karyawan_pln"
            cursor.execute(f"SELECT * FROM {sqlite_table}")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return {"table": sqlite_table, "data": rows, "mode": "offline_fallback"}
        except Exception as sqlite_err:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)} | SQLite error: {str(sqlite_err)}")

def reformulate_question(question: str, history: List[ChatMessage], provider="gemini") -> str:
    if not history:
        return question

    # Deteksi pergantian database secara paksa lewat kata kunci (Heuristic Topic Switch)
    q_lower = question.lower()
    classicmodels_kws = ["customer", "pelanggan", "pembayaran", "payment", "produk", "product", "order", "kantor", "office", "credit", "limit"]
    karyawan_kws = ["karyawan", "pegawai", "staff", "divisi", "jabatan", "absensi", "hadir", "masuk", "sakit", "izin", "alfa", "nip"]
    
    # Cek histori apakah membahas database karyawan atau classicmodels
    is_last_karyawan = any(any(kw in msg.content.lower() for kw in karyawan_kws) for msg in history if msg.role == "user")
    is_last_classic = any(any(kw in msg.content.lower() for kw in classicmodels_kws) for msg in history if msg.role == "user")
    
    is_new_karyawan = any(kw in q_lower for kw in karyawan_kws)
    is_new_classic = any(kw in q_lower for kw in classicmodels_kws)
    
    # Jika riwayat tentang karyawan, tapi pertanyaan baru tentang classicmodels (atau sebaliknya),
    # langsung kembalikan pertanyaan baru secara utuh tanpa modifikasi (TOPIC SWITCH)
    if (is_last_karyawan and is_new_classic) or (is_last_classic and is_new_karyawan):
        print("Heuristic Topic Switch detected! Skipping reformulation.")
        return question
    
    # Hanya gunakan 2 pesan terakhir (1 pertukaran) untuk menghindari percampuran topik/database
    recent_history = history[-2:]
    history_text = ""
    for msg in recent_history:
        sender = "User" if msg.role == "user" else "Assistant"
        content_preview = msg.content
        if len(content_preview) > 500:
            content_preview = content_preview[:500] + "..."
        history_text += f"{sender}: {content_preview}\n"
    
    prompt = f"""Tugas Anda adalah memeriksa apakah "Pertanyaan Lanjutan Terbaru" memerlukan konteks dari "Riwayat Percakapan" untuk dipahami.

Riwayat Percakapan:
{history_text}
Pertanyaan Lanjutan Terbaru: {question}

Aturan Penting:
1. Permintaan format (seperti meminta grafik/chart, tabel, atau pengurutan dari data sebelumnya) adalah pertanyaan lanjutan yang berhubungan. Anda harus menggabungkannya dengan subjek riwayat (contoh: "bar chartnya gimana" menjadi "tampilkan bar chart untuk sebaran umur staf").
2. Jika "Pertanyaan Lanjutan Terbaru" membahas topik/subjek/database baru yang tidak berkaitan dengan riwayat (misalnya dari karyawan/absensi beralih ke pelanggan/penjualan/pembayaran di classicmodels, atau sebaliknya), Anda WAJIB mengembalikan "Pertanyaan Lanjutan Terbaru" secara persis apa adanya (yaitu: "{question}") tanpa diubah!
3. Hanya ubah pertanyaan jika menggunakan kata ganti referensi ("dia", "mereka", "gajinya") atau kata penunjuk format ("grafiknya", "tabelnya"). Untuk pertanyaan singkat lanjutan (seperti "siapa saja", "siapa saja mereka", "sebutkan namanya"), gabungkan dengan konteks riwayat. Namun, JANGAN PERNAH mengubah atau mengganti kata tanya (seperti "siapa", "tanggal berapa", "kapan") jika itu adalah bagian dari pertanyaan baru yang lengkap dan mandiri.
4. Jawab HANYA dengan teks pertanyaan mandiri hasil penggabungan/reformulasi saja, tanpa penjelasan atau komentar tambahan.
5. Contoh penggabungan: Jika riwayat membahas "berapa jumlah karyawan yang masuk pada tanggal 2026-08-04" dan pertanyaan lanjutannya adalah "siapa saja", Anda harus menggabungkannya menjadi "siapa saja nama karyawan yang masuk pada tanggal 2026-08-04?".

Pertanyaan Mandiri:"""
    
    try:
        # Memanggil API LLM dengan parameter provider dan temperature=0.0
        reformulated = call_llm(prompt, provider=provider, temperature=0.0)
        result = reformulated.strip()
        
        # Bersihkan label yang mungkin tidak sengaja ditambahkan oleh LLM lokal
        result = result.replace("Pertanyaan Lanjutan Terbaru:", "")
        result = result.replace("Pertanyaan Mandiri:", "")
        result = result.replace("Pertanyaan:", "")
        result = result.strip()
        
        return result if result else question
    except Exception as e:
        print(f"Error reformulating question: {e}")
        return question

@app.get("/api/tables")
def get_all_tables():
    tables = []
    try:
        # Coba hubungkan ke MySQL server untuk mengambil semua tabel dari database karyawan_pln dan classicmodels
        conn = get_db_connection(database="information_schema")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME 
            FROM TABLES 
            WHERE TABLE_SCHEMA IN ('karyawan_pln', 'classicmodels')
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for db_name, table_name in rows:
            tables.append({
                "db": db_name,
                "table": table_name,
                "display": f"{db_name}.{table_name}"
            })
    except Exception as e:
        print(f"Error getting MySQL tables: {e}. Using SQLite fallback tables.")
        # Fallback SQLite table mapping
        tables = [
            {"db": "karyawan_pln", "table": "karyawan_pln", "display": "karyawan_pln.karyawan_pln"},
            {"db": "karyawan_pln", "table": "absensi", "display": "karyawan_pln.absensi"},
            {"db": "classicmodels", "table": "customers", "display": "classicmodels.customers"}
        ]
    return {"tables": tables}

def extract_chart_info(question: str, sql_query: str, rows: list) -> Optional[dict]:
    # Hanya buat chart jika baris data ada antara 2 dan 100 baris, dan memiliki setidaknya 2 kolom
    if not rows or len(rows) < 2 or len(rows) > 100:
        return None
        
    sample = rows[0]
    keys = list(sample.keys())
    if len(keys) < 2:
        return None
        
    q = question.lower()
    sql = sql_query.lower()
    
    # Deteksi apakah user secara eksplisit meminta chart/grafik
    chart_keywords = ["grafik", "chart", "visualisasi", "diagram", "gambarkan", "pie", "doughnut", "donat", "bar", "line", "garis", "batang", "lingkaran"]
    is_chart_requested = any(w in q for w in chart_keywords)
    
    if not is_chart_requested:
        return None
        
    # 1. Tentukan tipe tiap kolom berdasarkan baris data yang ada (hindari None)
    col_types = {}
    for k in keys:
        col_types[k] = "string" # default
        for r in rows:
            val = r.get(k)
            if val is not None:
                if isinstance(val, (int, float)):
                    col_types[k] = "numeric"
                    break
                val_str = str(val).strip()
                if val_str.replace(".", "", 1).replace("-", "", 1).isdigit():
                    col_types[k] = "numeric"
                    break
                else:
                    col_types[k] = "string"
                    break

    # 2. Cari kolom kategori (labels) dan kolom nilai numerik (values)
    label_col = None
    value_col = None
    
    # Kata kunci untuk kolom metrik/nilai (Y-axis)
    metric_kws = ['jumlah', 'total', 'count', 'sum', 'avg', 'mean', 'limit', 'price', 'salary', 'gaji', 'bayar', 'amount', 'quantity', 'qty', 'revenue', 'profit', 'sales', 'credit']
    # Kata kunci untuk kolom label/kategori (X-axis)
    label_kws = ['umur', 'tahun', 'bulan', 'hari', 'tanggal', 'date', 'year', 'month', 'day', 'age', 'nip', 'number', 'code', 'id', 'jenis_kelamin', 'gender', 'nama', 'name']

    # Filter out internal/forbidden fields
    filtered_keys = [k for k in keys if k.lower() not in ["id", "password", "pass"]]
    
    if len(filtered_keys) >= 2:
        # Pisahkan berdasarkan tipe data
        numeric_keys = [k for k in filtered_keys if col_types[k] == "numeric" and k.lower() not in ["nip", "customernumber", "salesrepemployeenumber"]]
        string_keys = [k for k in filtered_keys if col_types[k] == "string"]
        
        # Kasus A: Ada kolom string dan ada kolom angka
        if string_keys and numeric_keys:
            label_col = string_keys[0]
            value_col = numeric_keys[0]
        # Kasus B: Semua kolom angka (misalnya: umur dan jumlah)
        elif len(numeric_keys) >= 2:
            col1, col2 = numeric_keys[0], numeric_keys[1]
            
            col1_is_metric = any(kw in col1.lower() for kw in metric_kws)
            col2_is_metric = any(kw in col2.lower() for kw in metric_kws)
            col1_is_label = any(kw in col1.lower() for kw in label_kws)
            col2_is_label = any(kw in col2.lower() for kw in label_kws)
            
            if col1_is_metric and not col2_is_metric:
                value_col = col1
                label_col = col2
            elif col2_is_metric and not col1_is_metric:
                value_col = col2
                label_col = col1
            elif col2_is_label and not col1_is_label:
                label_col = col2
                value_col = col1
            elif col1_is_label and not col2_is_label:
                label_col = col1
                value_col = col2
            else:
                label_col = col1
                value_col = col2
        # Kasus C: Semua kolom string
        else:
            label_col = filtered_keys[0]
            value_col = filtered_keys[1]
            
    if not label_col or not value_col:
        return None
        
    # Rekomendasi tipe chart berdasarkan pertanyaan pengguna secara cerdas
    chart_type = "bar" # Default
    if any(w in q for w in ["pie", "lingkaran"]):
        chart_type = "pie"
    elif any(w in q for w in ["doughnut", "donat"]):
        chart_type = "doughnut"
    elif any(w in q for w in ["line", "garis", "tren", "trend"]):
        chart_type = "line"
    elif any(w in q for w in ["bar", "batang"]):
        chart_type = "bar"
    else:
        # Jika tidak ditentukan, pilih tipe terbaik berdasarkan jumlah data
        if len(rows) <= 5:
            chart_type = "doughnut"
        else:
            chart_type = "bar"
    
    labels = []
    values = []
    for r in rows:
        labels.append(str(r.get(label_col, "-")))
        try:
            values.append(float(r.get(value_col, 0)))
        except:
            values.append(0.0)
            
    return {
        "type": chart_type,
        "labels": labels,
        "values": values,
        "label": value_col
    }

# Cache penyimpanan query SQL sementara
sql_cache = {}

# Alur Eksekusi di Endpoint
@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    set_fallback_flag(False)
    # Buat key pencocokan cache yang seragam (lowercase, hilangkan spasi dan tanda tanya)
    cache_key = ""
    try:
        # Reformulate question if history exists, passing provider
        final_question = reformulate_question(request.question, request.history, provider=request.provider)
        print(f"Original question: {request.question} | Reformulated: {final_question} | Provider: {request.provider}")
        
        # Sertakan nama provider ke dalam key cache agar tidak tabrakan
        cache_key = f"{request.provider}:{final_question.strip().lower().rstrip('?')}"
        
        # Cek apakah query untuk pertanyaan ini sudah pernah dihasilkan sebelumnya (CACHE HIT)
        if cache_key in sql_cache:
            sql_query = sql_cache[cache_key]
            print(f"Cache HIT! Menggunakan query SQL dari memori cache untuk: '{final_question}'")
        else:
            # 1. Panggil fungsi untuk mengubah pertanyaan menjadi SQL via Gemini/Ollama (CACHE MISS)
            sql_query = generate_sql(final_question, provider=request.provider)
            sql_cache[cache_key] = sql_query
            print(f"Cache MISS! Menghasilkan query SQL baru via {request.provider.upper()}.")
        
        # Target prefix replacements
        modified_sql = sql_query
        
        if not is_safe_select(modified_sql):
            return {
                "answer": "Maaf, saya hanya bisa menjawab pertanyaan yang bersifat membaca data.",
                "sql": sql_query,
                "rows": [],
                "chart_info": None
            }
            
        rows = []
        used_sql = modified_sql
        try:
            # 2. Hubungkan ke database MySQL LOKAL
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # 3. Jalankan query SQL tersebut secara LOKAL
            cursor.execute(modified_sql)
            rows = cursor.fetchall()  # Data ditarik di sini (hanya di memori lokal komputer)
            cursor.close()
            conn.close()
        except Exception as e:
            # Jika database utama gagal, hapus query bermasalah ini dari cache agar tidak disimpan permanen
            if cache_key in sql_cache:
                sql_cache.pop(cache_key, None)
                
            # Fallback to SQLite
            # Strip database prefixes for SQLite
            sqlite_sql = sql_query.replace("classicmodels.", "")
            sqlite_sql = sqlite_sql.replace("karyawan_pln.", "")
            sqlite_sql = sqlite_sql.replace(f"{DB_NAME}.", "")
            
            print(f"Online query failed: {e}. Running offline on SQLite: {sqlite_sql}")
            
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute(sqlite_sql)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            used_sql = sqlite_sql
            
        # 4. MEMBUAT RINGKASAN SECARA LOKAL (Tanpa mengirim 'rows' ke Gemini cloud)
        answer = summarize_result(final_question, rows)
        
        # 5. EKSTRAKSI INFORMASI GRAFIK SECARA DINAMIS
        chart_info = extract_chart_info(final_question, used_sql, rows)
        
        # Tambahkan notifikasi jika terjadi fallback ke Ollama
        if get_fallback_flag():
            answer = "*Koneksi Cloud Gemini terhambat. Sistem otomatis beralih menggunakan Ollama lokal sebagai cadangan.*\n\n" + answer
            
        return {
            "answer": answer,
            "sql": used_sql,
            "rows": rows,
            "chart_info": chart_info
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        # Sembunyikan API key dari pesan error
        msg = str(e)
        if GEMINI_API_KEY:
            msg = msg.replace(GEMINI_API_KEY, "HIDDEN_KEY")
        msg = re.sub(r'key=[a-zA-Z0-9_\-]+', 'key=HIDDEN_KEY', msg)
        raise HTTPException(status_code=500, detail=msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
