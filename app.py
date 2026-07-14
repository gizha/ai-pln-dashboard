import streamlit as st
import mysql.connector
import pandas as pd
import requests
import re

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="AI PLN Dashboard",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk mobile responsiveness
st.markdown("""
<style>
    /* Atur padding dan lebar maksimal untuk mobile */
    .main {
        max-width: 100%;
        padding: 1rem;
    }
    
    /* Buat kolom lebih responsive di mobile */
    @media (max-width: 640px) {
        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        [data-testid="stMetricContainer"] {
            min-width: calc(100% - 1rem);
        }
    }
    
    /* Tabel lebih readable di mobile */
    [data-testid="dataFrameContainer"] {
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

DB_CONFIG = dict(
    host="tokaido.proxy.rlwy.net",
    user="root",
    password="rLsbQEzojiyAdwhDWjOKMkMuwjmgzLxo",
    database="railway",
    port=45830,
    ssl_disabled=False
)

TABLE_NAME = "karyawan_pln"

# Daftar semua database yang boleh diakses chatbot.
# Tinggal tambah nama database di sini kalau mau nambah database lain lagi.
DATABASES = ["railway"]

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"


# =========================
# MOCK DATA (FALLBACK JIKA DB TIDAK TERSEDIA)
# =========================
def get_mock_karyawan_data():
    """Dummy data untuk testing saat database tidak available."""
    return [
        {"NIP": "1001", "Nama": "Budi Santoso", "Jenis_Kelamin": "L", "Tanggal_Lahir": "1985-03-15", "Divisi": "IT", "Jabatan": "Manager", "Tanggal_Masuk": "2015-06-01", "Status_Pegawai": "Tetap", "Email": "budi@pln.id"},
        {"NIP": "1002", "Nama": "Siti Nurhaliza", "Jenis_Kelamin": "P", "Tanggal_Lahir": "1990-07-22", "Divisi": "Finance", "Jabatan": "Supervisor", "Tanggal_Masuk": "2018-01-15", "Status_Pegawai": "Tetap", "Email": "siti@pln.id"},
        {"NIP": "1003", "Nama": "Ahmad Rizki", "Jenis_Kelamin": "L", "Tanggal_Lahir": "1988-11-10", "Divisi": "HR", "Jabatan": "Staff", "Tanggal_Masuk": "2016-03-20", "Status_Pegawai": "Tetap", "Email": "ahmad@pln.id"},
        {"NIP": "1004", "Nama": "Rina Wijaya", "Jenis_Kelamin": "P", "Tanggal_Lahir": "1992-05-08", "Divisi": "IT", "Jabatan": "Developer", "Tanggal_Masuk": "2020-02-10", "Status_Pegawai": "Tetap", "Email": "rina@pln.id"},
        {"NIP": "1005", "Nama": "Hendra Gunawan", "Jenis_Kelamin": "L", "Tanggal_Lahir": "1987-09-14", "Divisi": "Finance", "Jabatan": "Manager", "Tanggal_Masuk": "2017-04-05", "Status_Pegawai": "Tetap", "Email": "hendra@pln.id"},
    ]

def get_mock_classicmodels_data():
    """Dummy data customer untuk testing saat database tidak available."""
    return [
        {"customerNumber": 101, "customerName": "Atelier Graphique", "city": "Paris", "country": "France", "creditLimit": 21000, "salesRepEmployeeNumber": 1370},
        {"customerNumber": 112, "customerName": "Signal Gift Stores", "city": "Las Vegas", "country": "USA", "creditLimit": 71800, "salesRepEmployeeNumber": 1166},
        {"customerNumber": 114, "customerName": "Australian Collectors, Co.", "city": "Melbourne", "country": "Australia", "creditLimit": 117300, "salesRepEmployeeNumber": 1166},
        {"customerNumber": 119, "customerName": "La Rochelle Gifts", "city": "La Rochelle", "country": "France", "creditLimit": 118400, "salesRepEmployeeNumber": 1370},
        {"customerNumber": 121, "customerName": "Baane Inc.", "city": "Stavern", "country": "Norway", "creditLimit": 81700, "salesRepEmployeeNumber": 1504},
    ]


@st.cache_resource
def warm_up_model():
    """Panggil model sekali saat app start biar Ollama load ke memori lebih awal,
    jadi pertanyaan pertama dari user nggak kena cold-start delay."""
    try:
        requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": "hi", "stream": False},
            timeout=300
        )
    except Exception:
        pass
    return True


# =========================
# SKEMA MULTI-DATABASE (dibangun otomatis dari INFORMATION_SCHEMA)
# =========================
@st.cache_data(ttl=3600)
def build_schema_text():
    conn = mysql.connector.connect(
        host="localhost", user="root", password=""
    )
    cursor = conn.cursor()

    placeholders = ",".join(["%s"] * len(DATABASES))
    cursor.execute(f"""
        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA IN ({placeholders})
        ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
    """, DATABASES)
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


# =========================
# KONEKSI & QUERY DATABASE
# =========================
def get_connection(database=None):
    cfg = dict(DB_CONFIG)
    if database:
        cfg["database"] = database
    return mysql.connector.connect(**cfg)


CANONICAL_COLUMNS = [
    "NIP", "Nama", "Jenis_Kelamin", "Tanggal_Lahir",
    "Divisi", "Jabatan", "Tanggal_Masuk", "Status_Pegawai", "Email"
]


def normalize_row_keys(row):
    """Petakan nama kolom apapun casing-nya (divisi/Divisi/DIVISI) ke nama baku."""
    lookup = {c.lower(): c for c in CANONICAL_COLUMNS}
    return {
        lookup.get(k.lower(), k): v
        for k, v in row.items()
    }


def get_all_data():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        data = [normalize_row_keys(r) for r in data]

        # Buang baris "hantu" kalau header CSV ikut ke-import sebagai data
        data = [r for r in data if r.get("NIP") != "NIP"]

        return data, False  # (data, is_mock)
    except Exception as e:
        st.warning(f"⚠️ Database tidak tersedia. Menampilkan data sample untuk demo.")
        return get_mock_karyawan_data(), True  # (mock_data, is_mock)


def run_sql(query):
    """Eksekusi SQL SELECT dan kembalikan list of dict."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_classicmodels_data():
    """Ambil data customer dari classicmodels buat dashboard."""
    try:
        conn = get_connection("classicmodels")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT customerNumber, customerName, city, country,
                   creditLimit, salesRepEmployeeNumber
            FROM customers
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data, False  # (data, is_mock)
    except Exception as e:
        st.warning(f"⚠️ Database tidak tersedia. Menampilkan data sample untuk demo.")
        return get_mock_classicmodels_data(), True  # (mock_data, is_mock)


# =========================
# GUARDRAIL SQL
# =========================
FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop", "alter",
    "truncate", "create", "grant", "revoke", "--", "/*"
]


def clean_sql(raw_text):
    """Ambil query SQL murni dari output LLM (buang ```sql, penjelasan, dll)."""
    text = raw_text.strip()

    # Ambil isi dalam code block ```sql ... ``` kalau ada
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip()

    # Kalau LLM nulis beberapa baris/penjelasan, ambil baris yang mulai dengan SELECT
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    sql_lines = []
    capturing = False
    for line in lines:
        if line.lower().startswith("select"):
            capturing = True
        if capturing:
            sql_lines.append(line)

    query = " ".join(sql_lines) if sql_lines else text

    # Cuma ambil statement pertama (hindari multi-statement injection)
    query = query.split(";")[0].strip() + ";"
    return query


def is_safe_select(query):
    q = query.lower()
    if not q.strip().startswith("select"):
        return False
    for kw in FORBIDDEN_KEYWORDS:
        if kw in q:
            return False
    return True


# =========================
# LLM: GENERATE SQL DARI PERTANYAAN
# =========================
def generate_sql(question):
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
- Jawab HANYA dengan query SQL, tanpa penjelasan, tanpa markdown, tanpa tanda kutip pembungkus.
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

Pertanyaan: berapa jumlah karyawan classicmodels di kantor Paris?
SQL: SELECT COUNT(*) AS total FROM classicmodels.employees e JOIN classicmodels.offices o ON e.officeCode = o.officeCode WHERE o.city = 'Paris';

Pertanyaan: {question}
SQL:"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_ctx": 4096
            }
        },
        timeout=300
    )
    raw = response.json()["response"]
    return clean_sql(raw)


# =========================
# LLM: SUSUN JAWABAN NATURAL DARI HASIL QUERY
# =========================
def summarize_result(question, query, rows):
    if len(rows) == 0:
        return "Data tidak ditemukan untuk pertanyaan tersebut."

    prompt = f"""Kamu adalah AI Assistant PLN yang ramah.

Pertanyaan user: {question}

Hasil query database (JSON):
{rows}

Tugasmu:
- Jawab pertanyaan user berdasarkan HASIL QUERY di atas saja.
- Jangan mengarang data yang tidak ada di hasil query.
- Jika hasil query berupa daftar, sebutkan secara ringkas (boleh pakai poin-poin jika banyak).
- Jawab singkat, jelas, dalam Bahasa Indonesia.

Jawaban:"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096
            }
        },
        timeout=300
    )
    return response.json()["response"]


# =========================
# FUNGSI UTAMA CHAT AI
# =========================
def ask_ai(question):
    sql_query = generate_sql(question)

    if not is_safe_select(sql_query):
        return (
            "Maaf, saya hanya bisa menjawab pertanyaan yang bersifat "
            "membaca data (bukan mengubah data)."
        ), sql_query, None

    try:
        rows = run_sql(sql_query)
    except Exception as e:
        return f"Query yang dibuat AI gagal dieksekusi: {e}", sql_query, None

    answer = summarize_result(question, sql_query, rows)
    return answer, sql_query, rows


# =========================
# WARM-UP MODEL
# =========================
with st.spinner("Menyiapkan model AI..."):
    warm_up_model()

# =========================
# SIDEBAR: PILIH DATABASE DULU
# =========================
with st.sidebar:
    st.header("Kontrol")
    db_choice = st.selectbox("Pilih Database", DATABASES, index=0)
    show_sql = st.checkbox("Tampilkan SQL", value=False)
    if st.button("Reset chat"):
        st.session_state.messages = []
        # `st.experimental_rerun()` tidak tersedia di semua versi Streamlit;
        # cukup kosongkan session state. Streamlit akan merender ulang otomatis
        # setelah interaksi widget.

# =========================
# LOAD DATA SESUAI DATABASE YANG DIPILIH
# =========================
# LOAD DATA SESUAI DATABASE YANG DIPILIH
# =========================
if db_choice == "karyawan_pln":
    data, is_mock = get_all_data()
else:
    data, is_mock = get_classicmodels_data()

df = pd.DataFrame(data)

# =========================
# SIDEBAR: FILTER YANG NYESUAIN DATABASE
# =========================
with st.sidebar:
    if db_choice == "karyawan_pln":
        divisi_options = sorted(df["Divisi"].dropna().unique()) if not df.empty and "Divisi" in df.columns else []
        divisi_filter = st.multiselect("Filter Divisi", options=divisi_options, default=[])
        search_text = st.text_input("Cari Nama atau NIP")
        country_filter = []
    else:
        country_options = sorted(df["country"].dropna().unique()) if not df.empty and "country" in df.columns else []
        country_filter = st.multiselect("Filter Negara", options=country_options, default=[])
        search_text = st.text_input("Cari Nama Customer")
        divisi_filter = []

# =========================
# HEADER
# =========================
if db_choice == "karyawan_pln":
    st.title("AI PLN Dashboard")
    st.caption("Chatbot AI + MySQL + Ollama (Text-to-SQL)")
else:
    st.title("Classicmodels Dashboard")
    st.caption("Chatbot AI + MySQL + Ollama (Text-to-SQL)")

# Terapkan filter hanya untuk tampilan (tidak mengubah data sumber)
df_filtered = df.copy()
if not df_filtered.empty:
    if db_choice == "karyawan_pln":
        if divisi_filter:
            df_filtered = df_filtered[df_filtered["Divisi"].isin(divisi_filter)]
        if search_text:
            mask = df_filtered.apply(
                lambda r: search_text.lower() in str(r.get("Nama", "")).lower()
                          or search_text.lower() in str(r.get("NIP", "")).lower(),
                axis=1
            )
            df_filtered = df_filtered[mask]
    else:
        if country_filter:
            df_filtered = df_filtered[df_filtered["country"].isin(country_filter)]
        if search_text:
            mask = df_filtered["customerName"].str.lower().str.contains(
                search_text.lower(), na=False
            )
            df_filtered = df_filtered[mask]

label = "karyawan" if db_choice == "karyawan_pln" else "customer"
st.success(f"Data berhasil dimuat: {len(df)} {label} (menampilkan {len(df_filtered)} baris)")

# =========================
# KPI
# =========================
col1, col2, col3 = st.columns(3)

if db_choice == "karyawan_pln":
    with col1:
        st.metric("Total Karyawan", len(df_filtered))
    with col2:
        st.metric("Jumlah Divisi", df_filtered["Divisi"].nunique() if not df_filtered.empty and "Divisi" in df_filtered.columns else 0)
    with col3:
        st.metric("Jumlah Jabatan", df_filtered["Jabatan"].nunique() if not df_filtered.empty and "Jabatan" in df_filtered.columns else 0)
else:
    with col1:
        st.metric("Total Customer", len(df_filtered))
    with col2:
        st.metric("Jumlah Negara", df_filtered["country"].nunique() if not df_filtered.empty and "country" in df_filtered.columns else 0)
    with col3:
        avg_credit = df_filtered["creditLimit"].mean() if not df_filtered.empty and "creditLimit" in df_filtered.columns else 0
        st.metric("Rata-rata Credit Limit", f"${avg_credit:,.0f}")

st.divider()

# =========================
# TABEL DATA
# =========================
st.subheader("Data Karyawan" if db_choice == "karyawan_pln" else "Data Customer")
st.dataframe(df_filtered, use_container_width=True)

st.divider()

# =========================
# GRAFIK
# =========================
if db_choice == "karyawan_pln":
    st.subheader("Jumlah Karyawan per Divisi")
    if not df_filtered.empty and "Divisi" in df_filtered.columns:
        st.bar_chart(df_filtered["Divisi"].value_counts())
    else:
        st.info("Tidak ada data divisi untuk ditampilkan.")
else:
    st.subheader("Jumlah Customer per Negara (Top 10)")
    if not df_filtered.empty and "country" in df_filtered.columns:
        st.bar_chart(df_filtered["country"].value_counts().head(10))
    else:
        st.info("Tidak ada data negara untuk ditampilkan.")

st.divider()

# =========================
# CHATBOT
# =========================
st.subheader("AI PLN Assistant")

# Check jika Ollama tersedia
ollama_available = True
try:
    requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": "test", "stream": False},
        timeout=5
    )
except:
    ollama_available = False
    st.warning("⚠️ Model AI (Ollama) tidak tersedia di Streamlit Cloud. Chatbot sedang disabled.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # Tampilkan SQL hanya jika user mengaktifkan opsi di sidebar
        if msg.get("sql") and ('show_sql' in globals() and show_sql):
            with st.expander("Lihat SQL yang dijalankan"):
                st.code(msg["sql"], language="sql")

chat_placeholder = (
    "Tanyakan sesuatu tentang data karyawan..."
    if db_choice == "karyawan_pln"
    else "Tanyakan sesuatu tentang data customer/order..."
)
question = st.chat_input(chat_placeholder, disabled=not ollama_available)

if question and ollama_available:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.spinner("AI sedang menyusun query & berpikir..."):
        try:
            answer, sql_query, rows = ask_ai(question)
        except Exception as e:
            answer, sql_query = f"Error: {e}", None

    with st.chat_message("assistant"):
        st.write(answer)
        if sql_query and ('show_sql' in globals() and show_sql):
            with st.expander("Lihat SQL yang dijalankan"):
                st.code(sql_query, language="sql")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sql": sql_query
    })