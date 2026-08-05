# PLN DataHub AI

PLN DataHub AI adalah project dashboard dan chatbot berbasis AI untuk mengeksplorasi data database PLN secara interaktif. Project ini menggabungkan frontend web, backend FastAPI, serta integrasi LLM untuk mengubah pertanyaan natural language menjadi query SQL dan jawaban data yang lebih mudah dipahami.

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

Buat file `.env` di folder `separated_app/backend` dengan isi berikut:

```env
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_db_password
DB_NAME=railway
DB_PORT=3306
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b-instruct
```

> Jangan commit file `.env` ke GitHub. Gunakan `.gitignore` untuk menghindari penyimpanan secret key dan file sensitif.

### 5. Jalankan Backend

```bash
cd separated_app/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Jalankan Frontend

Buka folder frontend lalu jalankan file `index.html` melalui browser lokal, atau gunakan server statis sederhana jika diperlukan.

## Deployment Notes

Project ini bisa diadaptasi untuk deployment ke layanan cloud seperti Railway, Render, atau platform hosting lain yang mendukung FastAPI.

## Security Reminder

- Jangan commit token API, password, dan `.env`
- Jangan upload database lokal atau data sensitif ke repository publik
- Simpan credential di environment variable deployment, bukan di source code

## License

Project ini dibuat untuk kebutuhan demo dan pengembangan internal. Silakan sesuaikan lisensi jika ingin dipublikasikan secara luas.
