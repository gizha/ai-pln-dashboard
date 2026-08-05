# untuk memastikan server API merespons dengan benar tanpa perlu membuka browser atau frontend.

import requests

print("=== Mengetes API Backend Terpisah ===")

# 1. Test GET /api/data
try:
    print("\n1. Menguji GET /api/data?table=karyawan_pln...")
    response = requests.get("http://127.0.0.1:8000/api/data?table=karyawan_pln", timeout=15)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        data = response.json().get("data", [])
        print(f"Berhasil! Ditemukan {len(data)} karyawan di database.")
        print("Sampel Karyawan 1:", data[0] if data else "Tidak ada data")
    else:
        print("Gagal! Detail:", response.text)
except Exception as e:
    print("Error:", e)

# 2. Test POST /api/chat
try:
    print("\n2. Menguji POST /api/chat...")
    payload = {"question": "pembelian produk terbanyak siapa"}
    response = requests.post("http://127.0.0.1:8000/api/chat", json=payload, timeout=30)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        res_json = response.json()
        print("Berhasil!")
        print("Jawaban AI:", res_json.get("answer"))
        print("SQL Query:", res_json.get("sql"))
    else:
        print("Gagal! Detail:", response.text)
except Exception as e:
    print("Error:", e)
