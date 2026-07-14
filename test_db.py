import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="karyawan_pln"
)

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM karyawan_pln")

hasil = cursor.fetchone()

print("Jumlah data:", hasil[0])