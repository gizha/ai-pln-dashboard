import mysql.connector
import os
from dotenv import load_dotenv

# Memastikan koneksi Python ke database MySQL lokal (XAMPP) berhasil terhubung menggunakan konfigurasi host, port, username, dan password yang ditentukan.
print("Loading .env...")
load_dotenv(dotenv_path="separated_app/backend/.env", override=True)

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")
port = int(os.getenv("DB_PORT", 3306))

print(f"Connecting to {host}:{port} as {user} to database {database}...")
try:
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        connection_timeout=5,
        ssl_disabled=True
    )
    print("Connection successful!")
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print("Tables:", tables)
    conn.close()
except Exception as e:
    print("Error connecting to database:", e)
