# PLN DataHub AI

PLN DataHub AI adalah proyek dashboard dan chatbot berbasis AI untuk mengeksplorasi data karyawan dan customer secara interaktif. Proyek ini menggabungkan frontend web, backend FastAPI, integrasi LLM (Gemini/Ollama), dan fallback SQLite untuk mode offline.

## Fitur Utama

- Dashboard distribusi data dengan KPI dan grafik
- Tabel data dinamis dari database
- Chatbot Ask PLN untuk bertanya dalam bahasa natural
- Dukungan provider AI:
  - Gemini API (cloud)
  - Ollama lokal sebagai fallback
- Fallback data SQLite untuk mode offline
- Skema database yang bisa ditampilkan di UI

## Teknologi yang Digunakan

- Frontend: HTML, CSS, JavaScript, Tailwind CSS, Chart.js
- Backend: Python, FastAPI, Uvicorn
- Database:
  - MySQL / MariaDB
  - SQLite fallback lokal
- AI Integration:
  - Gemini API
  - Ollama
- Backend: Python, FastAPI, Uvicorn
- Database:
  - MySQL / MariaDB (utama)
  - SQLite (fallback) — file `separated_app/backend/local_fallback.db`
- AI Integration:
  - Gemini API (cloud)
  - Ollama (cloud & lokal)

## Project Structure

```text
AI-PLN/
├── separated_app/
│   ├── backend/
│   │   ├── main.py
│   │   └── requirements.txt
│   └── frontend/
│       ├── index.html
│       ├── app.js
│       └── style.css
├── scratch/
├── sync_to_railway.py
├── test_endpoints.py
└── README.md
```

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/gizha/ai-pln-dashboard.git
cd ai-pln-dashboard
```

### 2. Setup Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
cd separated_app/backend
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Buat file `.env` di folder `separated_app/backend` dengan variabel berikut (sesuaikan nilai):

```env
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_db_password
DB_NAME=railway
DB_PORT=3306
OLLAMA_CLOUD_API_KEY=your_ollama_cloud_api_key
OLLAMA_CLOUD_HOST=https://ollama.com
OLLAMA_CLOUD_MODEL=gpt-oss:20b
OLLAMA_LOCAL_HOST=http://127.0.0.1:11434
OLLAMA_LOCAL_MODEL=qwen2.5:7b-instruct
```

Catatan:
- Nama variabel harus sesuai dengan yang dipakai di backend (`GEMINI_API_KEY`, `DB_*`, `OLLAMA_CLOUD_*`, `OLLAMA_LOCAL_*`).
- Jangan commit file `.env` ke GitHub. Tambahkan `.env` ke `.gitignore`.

### 5. Jalankan Backend

```bash
cd separated_app/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Jalankan Frontend

Buka `separated_app/frontend/index.html` di browser, atau jalankan server statis singkat mis.:

```bash
# dari folder separated_app/frontend
python -m http.server 5500
# lalu buka http://127.0.0.1:5500
```

## Notes & Deployment

- Proyek menyertakan fallback SQLite (`local_fallback.db`) sehingga fitur dasar dapat berjalan tanpa MySQL.
- Untuk production, simpan credential di environment variables pada platform deployment (Railway, Render, Heroku, dsb.).
- Pastikan tidak meng-commit file database berisi data sensitif pada repositori publik.

## Security Reminder

- Jangan commit token API, password, dan `.env`
- Jangan upload database lokal atau data sensitif ke repository publik
- Simpan credential di environment variable deployment, bukan di source code

## License

Proyek ini dibuat untuk demo dan pengembangan internal. Sesuaikan lisensi bila ingin dipublikasikan.
