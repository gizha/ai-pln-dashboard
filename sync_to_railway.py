import mysql.connector

# Konfigurasi Database Lokal
LOCAL_CONFIG = dict(
    host="localhost",
    user="root",
    password=""
)

# Konfigurasi Database Railway
RAILWAY_CONFIG = dict(
    host="tokaido.proxy.rlwy.net",
    user="root",
    password="rLsbQEzojiyAdwhDWjOKMkMuwjmgzLxo",
    database="railway",
    port=45830
)

def sync_karyawan():
    print("Menghubungkan ke database lokal karyawan_pln...")
    try:
        local_conn = mysql.connector.connect(**LOCAL_CONFIG, database="karyawan_pln")
        local_cursor = local_conn.cursor(dictionary=True)
        local_cursor.execute("SELECT NIP, Nama, Jenis_Kelamin, Tanggal_Lahir, Divisi, Jabatan, Tanggal_Masuk, Status_Pegawai, Email FROM karyawan_pln")
        rows = local_cursor.fetchall()
        local_cursor.close()
        local_conn.close()
        print(f"Berhasil mengambil {len(rows)} data karyawan dari local.")
    except Exception as e:
        print("Gagal mengambil data karyawan lokal:", e)
        return

    print("Menghubungkan ke database Railway...")
    try:
        rw_conn = mysql.connector.connect(**RAILWAY_CONFIG)
        rw_cursor = rw_conn.cursor()
        
        # Kosongkan tabel karyawan_pln di Railway dulu
        rw_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        rw_cursor.execute("TRUNCATE TABLE karyawan_pln;")
        
        # Insert semua data
        insert_query = """
        INSERT INTO karyawan_pln (NIP, Nama, Jenis_Kelamin, Tanggal_Lahir, Divisi, Jabatan, Tanggal_Masuk, Status_Pegawai, Email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data_to_insert = [
            (
                r["NIP"], r["Nama"], r["Jenis_Kelamin"], r["Tanggal_Lahir"],
                r["Divisi"], r["Jabatan"], r["Tanggal_Masuk"], r["Status_Pegawai"], r["Email"]
            )
            for r in rows
        ]
        
        rw_cursor.executemany(insert_query, data_to_insert)
        rw_conn.commit()
        
        rw_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        rw_cursor.close()
        rw_conn.close()
        print("Berhasil menyinkronkan data karyawan ke Railway!")
    except Exception as e:
        print("Gagal menyimpan data karyawan ke Railway:", e)

def sync_customers():
    print("\nMenghubungkan ke database lokal classicmodels...")
    try:
        local_conn = mysql.connector.connect(**LOCAL_CONFIG, database="classicmodels")
        local_cursor = local_conn.cursor(dictionary=True)
        local_cursor.execute("SELECT customerNumber, customerName, city, country, creditLimit, salesRepEmployeeNumber FROM customers")
        rows = local_cursor.fetchall()
        local_cursor.close()
        local_conn.close()
        print(f"Berhasil mengambil {len(rows)} data customer dari local.")
    except Exception as e:
        print("Gagal mengambil data customer lokal:", e)
        return

    print("Menghubungkan ke database Railway...")
    try:
        rw_conn = mysql.connector.connect(**RAILWAY_CONFIG)
        rw_cursor = rw_conn.cursor()
        
        # Kosongkan tabel customers di Railway dulu
        rw_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        rw_cursor.execute("TRUNCATE TABLE customers;")
        
        # Insert semua data
        insert_query = """
        INSERT INTO customers (customerNumber, customerName, city, country, creditLimit, salesRepEmployeeNumber)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        data_to_insert = [
            (
                r["customerNumber"], r["customerName"], r["city"], r["country"],
                r["creditLimit"], r["salesRepEmployeeNumber"]
            )
            for r in rows
        ]
        
        rw_cursor.executemany(insert_query, data_to_insert)
        rw_conn.commit()
        
        rw_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        rw_cursor.close()
        rw_conn.close()
        print("Berhasil menyinkronkan data customers ke Railway!")
    except Exception as e:
        print("Gagal menyimpan data customers ke Railway:", e)

if __name__ == "__main__":
    sync_karyawan()
    sync_customers()
