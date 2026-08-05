import mysql.connector
import os
import sys

# Add backend dir to path to import config if needed
backend_dir = r"c:\AI-PLN\separated_app\backend"
sys.path.append(backend_dir)

from dotenv import load_dotenv
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path, override=True)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "karyawan_pln")
DB_PORT = int(os.getenv("DB_PORT", 3306))

print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT} as {DB_USER}...")
try:
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
    
    # Drop and recreate absensi
    cursor.execute("DROP TABLE IF EXISTS absensi")
    cursor.execute("""
    CREATE TABLE absensi (
        id INT AUTO_INCREMENT PRIMARY KEY,
        NIP VARCHAR(50) NOT NULL,
        Tanggal DATE NOT NULL,
        Status VARCHAR(20) NOT NULL,
        FOREIGN KEY (NIP) REFERENCES karyawan_pln(NIP)
    )
    """)
    
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
    
    conn.commit()
    print("SUCCESS: Absensi table created and seeded in MySQL database.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
