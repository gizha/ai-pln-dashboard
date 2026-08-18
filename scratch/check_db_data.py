import mysql.connector
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="separated_app/backend/.env", override=True)

print("--- MYSQL DATA ---")
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        ssl_disabled=True
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM karyawan_pln.karyawan_pln")
    print("karyawan_pln count in MySQL:", cursor.fetchone()[0])
    
    cursor.execute("SELECT COUNT(*) FROM karyawan_pln.absensi")
    print("absensi count in MySQL:", cursor.fetchone()[0])
    
    cursor.execute("SELECT COUNT(*) FROM classicmodels.customers")
    print("classicmodels.customers count in MySQL:", cursor.fetchone()[0])
    
    cursor.close()
    conn.close()
except Exception as e:
    print("MySQL Error:", e)

print("\n--- SQLITE DATA ---")
try:
    conn = sqlite3.connect("separated_app/backend/local_fallback.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in SQLite:", tables)
    
    for t in tables:
        table_name = t[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        print(f"{table_name} count in SQLite:", cursor.fetchone()[0])
        
    cursor.close()
    conn.close()
except Exception as e:
    print("SQLite Error:", e)
