const BACKEND_URL = "http://127.0.0.1:8000";

// DOM Elements
const dbSelect = document.getElementById("db-select");
const aiProviderSelect = document.getElementById("ai-provider-select");
const showSqlCheckbox = document.getElementById("show-sql-checkbox");
const translateCheckbox = document.getElementById("translate-checkbox");
const resetChatBtn = document.getElementById("reset-chat-btn");
const dataStatusAlert = document.getElementById("data-status-alert");
const dataStatusText = document.getElementById("data-status-text");
const kpiGrid = document.getElementById("kpi-grid");
const tableTitle = document.getElementById("table-title");
const tableHeaders = document.getElementById("table-headers");
const tableBody = document.getElementById("table-body");
const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const subtitleDesc = document.getElementById("subtitle-desc");
const downloadCsvBtn = document.getElementById("download-csv-btn");

// State
let currentLang = localStorage.getItem("pln_lang") || "id";
let currentTableData = [];
let availableTables = []; // Memuat semua list tabel secara dinamis
let currentPage = 1;
const rowsPerPage = 10;
let chatHistory = [];
let chartInstance1 = null;
let chartInstance2 = null;

// --- Language Localization Dictionary ---
const translations = {
    en: {
        nav_about: "About",
        nav_dashboard: "Dashboard",
        nav_ask: "Ask PLN",
        btn_theme_light: "Light Mode",
        btn_theme_dark: "Dark Mode",
        dashboard_title: "Data Distribution Dashboard",
        dashboard_subtitle: "Table Dashboard & Statistical Analysis",
        alert_db_connecting: "Connecting to database...",
        alert_db_connected_mysql: "Successfully connected to MySQL local database.",
        alert_db_connected_sqlite: "Main database unreachable. Successfully loaded from offline SQLite data fallback.",
        alert_db_error: "Failed to connect to database.",
        label_db_select: "Select Database Table",
        option_loading: "Loading tables list...",
        kpi_title_karyawan_1: "Total Employees",
        kpi_title_karyawan_2: "Total Divisions",
        kpi_title_karyawan_3: "Total Job Positions",
        kpi_title_customer_1: "Total Customers",
        kpi_title_customer_2: "Total Countries",
        kpi_title_customer_3: "Average Credit Limit",
        chart_title_karyawan_1: "Employees Per Division",
        chart_title_karyawan_2: "Employee Gender Distribution",
        chart_title_customer_1: "Top 7 Customer Countries",
        chart_title_customer_2: "Customer Credit Limit Distribution",
        credit_limit_none: "No Limit",
        table_title: "Employee Data",
        btn_download_csv: "Download CSV",
        btn_save_chart: "Save Chart",
        btn_prev: "Previous",
        btn_next: "Next",
        sidebar_history_title: "Query History",
        btn_clear_history: "Clear",
        history_empty: "No history yet.",
        chat_header: "Ask PLN",
        btn_schema_modal: "Database Schema",
        btn_reset_chat: "Reset Chat",
        label_provider: "AI Provider (LLM):",
        label_show_sql: "Show Executed SQL",
        label_translate: "Translate Descriptions",
        chat_input_placeholder: "Ask something about PLN database...",
        btn_send: "Send",
        chat_welcome: "Hello! I am Ask PLN, your intelligent assistant. How can I help you with database queries today?",
        schema_modal_title: "Database Structure Schema",
        btn_salin_tabel: "Copy Table",
        btn_salin_sql: "Copy SQL",
        sql_summary_title: "▼ View executed SQL",
        stats_prefix: "Response processed in",
        stats_suffix: "seconds.",
        fallback_msg: "Gemini Cloud connection interrupted. System automatically fell back to local Ollama as backup.",
        table_prefix: "Table:",
        no_data: "No data available.",
        schema_table_karyawan: "Table: karyawan_pln",
        schema_desc_karyawan: "Stores internal database of PLN employees.",
        schema_table_customers: "Table: customers",
        schema_desc_customers: "Stores customer profiles and credit limits.",
        schema_table_absensi: "Table: absensi",
        schema_desc_absensi: "Stores daily attendance logs of PLN employees.",
        footer_copyright: "© 2026 PLN DataHub AI. All Rights Reserved."
    },
    id: {
        nav_about: "Beranda",
        nav_dashboard: "Dashboard",
        nav_ask: "Ask PLN",
        btn_theme_light: "Mode Terang",
        btn_theme_dark: "Mode Gelap",
        dashboard_title: "Dashboard Distribusi Data",
        dashboard_subtitle: "Dashboard Tabel & Analisis Statistik",
        alert_db_connecting: "Menghubungkan ke database...",
        alert_db_connected_mysql: "Data berhasil dimuat dari database lokal MySQL.",
        alert_db_connected_sqlite: "Database utama tidak terjangkau. Berhasil memuat data dari SQLite lokal (Mode Offline).",
        alert_db_error: "Gagal menghubungkan ke database.",
        label_db_select: "Lihat Database",
        option_loading: "Memuat daftar tabel...",
        kpi_title_karyawan_1: "Total Karyawan",
        kpi_title_karyawan_2: "Jumlah Divisi",
        kpi_title_karyawan_3: "Jumlah Jabatan",
        kpi_title_customer_1: "Total Customer",
        kpi_title_customer_2: "Jumlah Negara",
        kpi_title_customer_3: "Rata-rata Credit Limit",
        chart_title_karyawan_1: "Jumlah Karyawan Per Divisi",
        chart_title_karyawan_2: "Distribusi Jenis Kelamin Karyawan",
        chart_title_customer_1: "Top 7 Negara Customer",
        chart_title_customer_2: "Limit Kredit Customer",
        credit_limit_none: "Tanpa Limit",
        table_title: "Data Karyawan",
        btn_download_csv: "Unduh CSV",
        btn_save_chart: "Simpan Grafik",
        btn_prev: "Sebelumnya",
        btn_next: "Selanjutnya",
        sidebar_history_title: "Riwayat Tanya",
        btn_clear_history: "Hapus",
        history_empty: "Belum ada riwayat.",
        chat_header: "Ask PLN",
        btn_schema_modal: "Skema Database",
        btn_reset_chat: "Reset Chat",
        label_provider: "Penyedia AI (LLM):",
        label_show_sql: "Tampilkan SQL yang Dijalankan",
        label_translate: "Terjemahkan Deskripsi",
        chat_input_placeholder: "Tanyakan sesuatu tentang database PLN...",
        btn_send: "Kirim",
        chat_welcome: "Halo! Saya adalah Ask PLN, asisten cerdas Anda. Ada yang bisa saya bantu tentang data database hari ini?",
        schema_modal_title: "Skema Struktur Database",
        btn_salin_tabel: "Salin Tabel",
        btn_salin_sql: "Salin SQL",
        sql_summary_title: "▼ Lihat SQL yang dijalankan",
        stats_prefix: "Respons selesai diproses dalam",
        stats_suffix: "detik.",
        fallback_msg: "Koneksi Cloud Gemini terhambat. Sistem otomatis beralih menggunakan Ollama lokal sebagai cadangan.",
        table_prefix: "Tabel:",
        no_data: "Tidak ada data.",
        schema_table_karyawan: "Tabel: karyawan_pln",
        schema_desc_karyawan: "Menyimpan data internal karyawan PLN.",
        schema_table_customers: "Tabel: customers",
        schema_desc_customers: "Menyimpan data pelanggan dan kredit limit.",
        schema_table_absensi: "Tabel: absensi",
        schema_desc_absensi: "Menyimpan data kehadiran harian karyawan PLN.",
        footer_copyright: "© 2026 PLN DataHub AI. Semua Hak Cipta Dilindungi."
    }
};

function getTranslation(key) {
    const langData = translations[currentLang];
    return langData && langData[key] ? langData[key] : key;
}

const suggestionQueries = {
    en: [
        { query: "How many employees are there currently?", label: "How many employees?" },
        { query: "Show 5 best selling products", label: "5 best selling products?" },
        { query: "Show employee distribution per division", label: "Division distribution?" },
        { query: "What is the average age of employees?", label: "Average age of employees?" }
    ],
    id: [
        { query: "Berapa jumlah karyawan saat ini?", label: "Berapa jumlah karyawan?" },
        { query: "Tampilkan 5 produk yang paling laris", label: "5 produk terlaris?" },
        { query: "Tampilkan sebaran karyawan tiap divisi", label: "Distribusi divisi?" },
        { query: "Berapa rata-rata umur karyawan?", label: "Rata-rata umur karyawan?" }
    ]
};

function renderSuggestionChips() {
    const container = document.getElementById("chat-suggestions-container");
    if (!container) return;
    
    container.innerHTML = "";
    const list = suggestionQueries[currentLang];
    list.forEach(item => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "suggestion-chip px-3 py-2 text-xs rounded-xl border text-slate-300 hover:text-white transition-all bg-slate-800/40 hover:bg-[#00A0E9]/10";
        btn.style.borderColor = "var(--card-border)";
        btn.setAttribute("data-query", item.query);
        btn.textContent = item.label;
        
        btn.addEventListener("click", () => {
            if (chatInput) {
                chatInput.value = item.query;
                chatForm.dispatchEvent(new Event("submit"));
            }
        });
        container.appendChild(btn);
    });
}

// Format helpers
function formatNumber(num) {
    return new Intl.NumberFormat('id-ID').format(Math.round(num));
}

// 0. Dynamic Table List Fetcher
async function loadTablesList() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/tables`);
        if (!response.ok) throw new Error("Gagal mengambil daftar tabel dari API.");
        const resJson = await response.json();
        availableTables = resJson.tables;
        
        if (dbSelect) {
            dbSelect.innerHTML = availableTables.map(t => 
                `<option value="${t.table}">${t.display}</option>`
            ).join("");
            
            // Muat tabel pertama kali
            if (availableTables.length > 0) {
                loadTableData(availableTables[0].table);
            }
        }
    } catch (error) {
        console.error("Gagal memuat daftar tabel, menggunakan fallback:", error);
        availableTables = [
            { db: "karyawan_pln", table: "karyawan_pln", display: "karyawan_pln.karyawan_pln" },
            { db: "classicmodels", table: "customers", display: "classicmodels.customers" }
        ];
        if (dbSelect) {
            dbSelect.innerHTML = availableTables.map(t => 
                `<option value="${t.table}">${t.display}</option>`
            ).join("");
            loadTableData("karyawan_pln");
        }
    }
}

// 1. Fetch & Load Table Data
async function loadTableData(tableName) {
    if (!tableName) return;
    
    // Cari asal database dari list tabel
    const tableConfig = availableTables.find(t => t.table === tableName) || { db: "karyawan_pln" };
    const dbName = tableConfig.db;
    
    dataStatusText.textContent = currentLang === "en"
        ? `Connecting to local database for table ${dbName}.${tableName}...`
        : `Menghubungkan ke database lokal untuk tabel ${dbName}.${tableName}...`;
    dataStatusAlert.className = "alert-status px-4 py-3 rounded-lg text-sm mb-6 flex items-center space-x-2";
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/data?table=${tableName}&db=${dbName}`);
        if (!response.ok) throw new Error("Gagal mengambil data dari API backend.");
        
        const resJson = await response.json();
        currentTableData = resJson.data;
        
        // Reset ke halaman pertama saat ganti tabel
        currentPage = 1;
        
        // Update UI
        updateAlertSuccess(tableName, currentTableData.length, resJson.mode);
        renderTable(tableName, currentTableData);
        calculateKPIs(tableName, currentTableData);
        renderCharts(tableName, currentTableData);
    } catch (error) {
        console.error(error);
        updateAlertError(tableName, error.message);
    }
}

function updateAlertSuccess(tableName, count, mode) {
    if (mode === "offline_fallback") {
        dataStatusText.textContent = currentLang === "en"
            ? `Main database unreachable. Successfully loaded ${count} rows from offline SQLite data.`
            : `⚠️ Database utama tidak terjangkau. Berhasil memuat ${count} data dari data lokal (Mode Offline).`;
        dataStatusAlert.className = "alert-status-warning px-4 py-3 rounded-lg text-sm mb-6 flex items-center space-x-2";
    } else {
        dataStatusText.textContent = currentLang === "en"
            ? `Data loaded successfully: ${count} rows from MySQL database.`
            : `Data berhasil dimuat: ${count} data dari database lokal.`;
        dataStatusAlert.className = "alert-status px-4 py-3 rounded-lg text-sm mb-6 flex items-center space-x-2";
    }
}

function updateAlertError(tableName, message) {
    dataStatusText.textContent = currentLang === "en"
        ? `Failed to connect to database for ${tableName}. Error: ${message}`
        : `⚠️ Gagal menghubungkan ke database untuk ${tableName}. Error: ${message}`;
    dataStatusAlert.className = "alert-status-error px-4 py-3 rounded-lg text-sm mb-6 flex items-center space-x-2";
}

// 2. Render Table
function renderTable(tableName, data) {
    // Judul tabel dinamis berdasarkan konfigurasi display atau nama tabel
    const tableConfig = availableTables.find(t => t.table === tableName);
    const prefix = getTranslation("table_prefix");
    tableTitle.textContent = tableConfig ? `${prefix} ${tableConfig.display}` : `${prefix} ${tableName}`;
    
    if (data.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="5" class="p-8 text-center text-slate-500">${getTranslation("no_data")}</td></tr>`;
        updatePaginationControls(0);
        return;
    }
    
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    const paginatedData = data.slice(startIndex, endIndex);
    
    // Ambil kolom/headers secara dinamis dari kunci baris pertama
    const allKeys = Object.keys(data[0]);
    const headers = allKeys.filter(key => {
        const k = key.toLowerCase();
        // Sembunyikan ID internal bawaan sistem database tapi pertahankan NIP/customerNumber
        if (k === "id" || k === "password" || k === "pass") return false;
        return true;
    });
    
    // Render dynamic headers
    tableHeaders.innerHTML = headers.map(h => {
        let displayHeader = h.replace(/_/g, ' ');
        displayHeader = displayHeader.replace(/\b\w/g, c => c.toUpperCase());
        return `<th class="p-4">${displayHeader}</th>`;
    }).join("");
    
    // Render dynamic rows
    tableBody.innerHTML = paginatedData.map(row => {
        return `<tr class="hover:bg-slate-800/20 transition-all">
            ${headers.map((h, index) => {
                let val = row[h];
                if (val === null || val === undefined) {
                    val = "-";
                }
                
                const keyLower = h.toLowerCase();
                
                // 1. Kolom Kode / Nomor (NIP, Code, Number) -> Font Mono & Sky Blue
                if (keyLower.includes("number") || keyLower === "nip" || keyLower.includes("code")) {
                    return `<td class="p-4 font-mono text-xs text-sky-400">${val}</td>`;
                }
                
                // 2. Kolom Utama / Nama -> Font Tebal
                if (index === 1 || keyLower.includes("name") || keyLower === "nama") {
                    return `<td class="p-4 font-semibold">${val}</td>`;
                }
                
                // 3. Kolom Uang / Limit / Nominal -> Font Emerald Hijau & format Moneter
                if (keyLower.includes("limit") || keyLower.includes("amount") || keyLower.includes("price") || keyLower.includes("credit")) {
                    const numVal = parseFloat(val) || 0;
                    return `<td class="p-4 font-semibold text-emerald-400">$${formatNumber(numVal)}</td>`;
                }
                
                // 4. Kolom Email -> Font Abu-abu & Kecil
                if (keyLower.includes("email")) {
                    return `<td class="p-4 text-slate-400 text-xs">${val}</td>`;
                }
                
                return `<td class="p-4">${val}</td>`;
            }).join("")}
        </tr>`;
    }).join("");
    
    updatePaginationControls(data.length);
}

function updatePaginationControls(totalCount) {
    const prevBtn = document.getElementById("prev-page-btn");
    const nextBtn = document.getElementById("next-page-btn");
    const pagInfo = document.getElementById("pagination-info");
    
    if (!pagInfo) return;
    
    if (totalCount === 0) {
        pagInfo.innerHTML = currentLang === "en" ? "Showing 0 rows" : "Menampilkan 0 baris";
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        return;
    }
    
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = Math.min(startIndex + rowsPerPage, totalCount);
    
    if (currentLang === "en") {
        pagInfo.innerHTML = `Showing <span class="font-semibold">${formatNumber(startIndex + 1)}</span> - <span class="font-semibold">${formatNumber(endIndex)}</span> of <span class="font-semibold">${formatNumber(totalCount)}</span> rows`;
    } else {
        pagInfo.innerHTML = `Menampilkan <span class="font-semibold">${formatNumber(startIndex + 1)}</span> - <span class="font-semibold">${formatNumber(endIndex)}</span> dari <span class="font-semibold">${formatNumber(totalCount)}</span> baris`;
    }
    
    prevBtn.disabled = (currentPage === 1);
    nextBtn.disabled = (endIndex >= totalCount);
}

// 3. Calculate KPIs
function calculateKPIs(tableName, data) {
    const kpiTitle1 = document.getElementById("kpi-title-1");
    const kpiValue1 = document.getElementById("kpi-value-1");
    const kpiTitle2 = document.getElementById("kpi-title-2");
    const kpiValue2 = document.getElementById("kpi-value-2");
    const kpiTitle3 = document.getElementById("kpi-title-3");
    const kpiValue3 = document.getElementById("kpi-value-3");
    
    if (tableName === "karyawan_pln") {
        const uniqueDivisi = new Set(data.map(r => r.Divisi || r.divisi).filter(Boolean)).size;
        const uniqueJabatan = new Set(data.map(r => r.Jabatan || r.jabatan).filter(Boolean)).size;
        
        kpiTitle1.textContent = currentLang === "en" ? "Total Employees" : "Total Karyawan";
        kpiValue1.textContent = data.length;
        
        kpiTitle2.textContent = currentLang === "en" ? "Total Divisions" : "Jumlah Divisi";
        kpiValue2.textContent = uniqueDivisi;
        
        kpiTitle3.textContent = currentLang === "en" ? "Total Job Positions" : "Jumlah Jabatan";
        kpiValue3.textContent = uniqueJabatan;
    } else if (tableName === "absensi") {
        let presentCount = 0;
        let absentCount = 0;
        data.forEach(r => {
            const status = r.Status || r.status || "Tidak";
            if (status === "Masuk") presentCount++;
            else absentCount++;
        });
        
        kpiTitle1.textContent = currentLang === "en" ? "Total Attendance Records" : "Total Log Kehadiran";
        kpiValue1.textContent = data.length;
        
        kpiTitle2.textContent = currentLang === "en" ? "Total Present" : "Karyawan Masuk";
        kpiValue2.textContent = presentCount;
        
        kpiTitle3.textContent = currentLang === "en" ? "Total Absent" : "Karyawan Absen";
        kpiValue3.textContent = absentCount;
    } else {
        const uniqueCountries = new Set(data.map(r => r.country).filter(Boolean)).size;
        const totalCredits = data.reduce((acc, curr) => acc + (parseFloat(curr.creditLimit) || 0), 0);
        const avgCredit = data.length > 0 ? totalCredits / data.length : 0;
        
        kpiTitle1.textContent = currentLang === "en" ? "Total Customers" : "Total Customer";
        kpiValue1.textContent = data.length;
        
        kpiTitle2.textContent = currentLang === "en" ? "Total Countries" : "Jumlah Negara";
        kpiValue2.textContent = uniqueCountries;
        
        kpiTitle3.textContent = currentLang === "en" ? "Average Credit Limit" : "Rata-rata Credit Limit";
        kpiValue3.textContent = `$${formatNumber(avgCredit)}`;
    }
}

// 4. Chatbot Interaction
// 4. Chatbot Interaction
async function handleChatSubmit(e) {
    e.preventDefault();
    const question = chatInput.value.trim();
    if (!question) return;
    
    // Remove suggestions container once user sends a message
    const suggestionsContainer = document.getElementById("chat-suggestions-container");
    if (suggestionsContainer) {
        suggestionsContainer.remove();
    }
    
    // Render user message
    appendMessage("user", question);
    chatInput.value = "";
    
    // Save to past queries history log
    addPastQuery(question);
    
    // Render loading indicator
    const loadingBubble = appendMessage("ai", "AI sedang menyusun query & berpikir...", true);
    
    const selectedProvider = aiProviderSelect ? aiProviderSelect.value : "gemini";
    
    const startTime = performance.now();
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ 
                question,
                history: chatHistory,
                provider: selectedProvider,
                translate: translateCheckbox ? translateCheckbox.checked : true
            })
        });
        
        if (!response.ok) {
            const errorJson = await response.json();
            throw new Error(errorJson.detail || "Gagal memproses pesan chat.");
        }
        
        const data = await response.json();
        
        const endTime = performance.now();
        const responseTimeSeconds = (endTime - startTime) / 1000;
        
        // Remove loading bubble
        loadingBubble.remove();
        
        // Render AI response with speed stats
        appendMessage("ai", data.answer, false, responseTimeSeconds, data.translated_answer);
        
        // Render Chart if returned by backend
        if (data.chart_info) {
            appendChatChart(data.chart_info);
        }
        
        // Save to chat history
        chatHistory.push({ role: "user", content: question });
        chatHistory.push({ role: "assistant", content: data.answer });
        
        // Render SQL if present (controlled dynamically via body class)
        if (data.sql) {
            appendSqlExpander(data.sql);
        }
    } catch (error) {
        console.error(error);
        loadingBubble.remove();
        appendMessage("ai", `⚠️ Error: ${error.message}`);
    }
}

function parseMarkdown(text) {
    // Bersihkan HTML untuk mencegah XSS
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
        
    const lines = html.split("\n");
    let inTable = false;
    let tableHtml = "";
    let parsedLines = [];
    
    for (let line of lines) {
        const trimmed = line.trim();
        const isRow = trimmed.startsWith("|") && trimmed.endsWith("|");
        
        if (isRow) {
            if (trimmed.includes("---")) {
                continue; // Lewati pembatas header
            }
            const cells = line.split("|").slice(1, -1).map(c => c.trim());
            
            if (!inTable) {
                inTable = true;
                tableHtml = "<table><thead><tr>";
                tableHtml += cells.map(c => `<th>${c}</th>`).join("");
                tableHtml += "</tr></thead><tbody>";
            } else {
                tableHtml += "<tr>";
                tableHtml += cells.map(c => `<td>${c}</td>`).join("");
                tableHtml += "</tr>";
            }
        } else {
            if (inTable) {
                inTable = false;
                tableHtml += "</tbody></table>";
                // Wrap table in relative container with floating Copy Button positioned cleanly above the table
                let tableWrapper = `<div class="relative group mt-3 mb-3">`;
                tableWrapper += `<div class="flex justify-end mb-1">`;
                tableWrapper += `<button type="button" class="copy-btn" onclick="copyTableText(this)" data-i18n="btn_salin_tabel">${getTranslation("btn_salin_tabel")}</button>`;
                tableWrapper += `</div>`;
                tableWrapper += `<div class="rounded-lg overflow-hidden">`;
                tableWrapper += tableHtml;
                tableWrapper += `</div>`;
                tableWrapper += `</div>`;
                parsedLines.push(tableWrapper);
                tableHtml = "";
            }
            // Format bold **text**, italic *text*, dan highlight ==text==
            let formattedLine = line
                .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                .replace(/\*(.*?)\*/g, "<em>$1</em>")
                .replace(/==(.*?)==/g, "<span class='chat-highlight'>$1</span>");
            parsedLines.push(formattedLine);
        }
    }
    
    if (inTable) {
        tableHtml += "</tbody></table>";
        let tableWrapper = `<div class="relative group mt-3 mb-3">`;
        tableWrapper += `<div class="flex justify-end mb-1">`;
        tableWrapper += `<button type="button" class="copy-btn" onclick="copyTableText(this)" data-i18n="btn_salin_tabel">${getTranslation("btn_salin_tabel")}</button>`;
        tableWrapper += `</div>`;
        tableWrapper += `<div class="rounded-lg overflow-hidden">`;
        tableWrapper += tableHtml;
        tableWrapper += `</div>`;
        tableWrapper += `</div>`;
        parsedLines.push(tableWrapper);
    }
    
    return parsedLines.join("<br>");
}

function appendMessage(sender, text, isLoading = false, responseTime = null, translatedText = null) {
    const bubbleWrapper = document.createElement("div");
    bubbleWrapper.className = `flex ${sender === "user" ? "justify-end" : "justify-start"} items-start space-x-3`;
    
    const bubble = document.createElement("div");
    if (sender === "user") {
        bubble.className = "chat-bubble-user p-3 rounded-2xl rounded-tr-none max-w-[80%] text-sm whitespace-pre-wrap transition-colors duration-500";
        bubble.setAttribute("data-query-text", text.trim().toLowerCase());
    } else {
        bubble.className = "chat-bubble-ai p-3 rounded-2xl rounded-tl-none max-w-[80%] text-sm";
    }
    
    if (isLoading) {
        bubble.innerHTML = `<span class="flex items-center space-x-2"><span class="animate-pulse">${text}</span></span>`;
    } else {
        if (sender === "ai") {
            if (translatedText && translatedText.trim() !== text.trim()) {
                // Render both versions wrapped in class containers for dynamic CSS switching
                const originalHtml = parseMarkdown(text);
                const translatedHtml = parseMarkdown(translatedText);
                bubble.innerHTML = `
                    <div class="untranslated-content">${originalHtml}</div>
                    <div class="translated-content">${translatedHtml}</div>
                `;
            } else {
                bubble.innerHTML = parseMarkdown(text);
            }
            
            // Append response time stats if provided
            if (responseTime !== null) {
                const statsDiv = document.createElement("div");
                statsDiv.className = "chat-stats-text";
                statsDiv.innerHTML = `Respons selesai diproses dalam ${responseTime.toFixed(2)} detik.`;
                bubble.appendChild(statsDiv);
            }
        } else {
            bubble.textContent = text;
        }
    }
    
    bubbleWrapper.appendChild(bubble);
    chatBox.appendChild(bubbleWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return bubbleWrapper;
}

function appendChatChart(chartInfo) {
    if (!chartInfo || !chartInfo.labels || !chartInfo.values) return;
    
    const canvasId = "chat-chart-" + Date.now();
    
    const wrapper = document.createElement("div");
    wrapper.className = "flex flex-col items-start pl-6 mt-2 mb-2 w-full max-w-[90%] space-y-1";
    
    // Header row with download button
    const btnRow = document.createElement("div");
    btnRow.className = "flex justify-end w-full pr-2";
    
    const downloadBtn = document.createElement("button");
    downloadBtn.type = "button";
    downloadBtn.className = "copy-btn";
    downloadBtn.innerHTML = getTranslation("btn_save_chart");
    downloadBtn.setAttribute("data-i18n", "btn_save_chart");
    downloadBtn.addEventListener("click", () => {
        downloadChart(canvasId, "grafik_chat_pln.png");
    });
    btnRow.appendChild(downloadBtn);
    wrapper.appendChild(btnRow);
    
    const container = document.createElement("div");
    container.className = "chat-chart-container w-full";
    
    const canvas = document.createElement("canvas");
    canvas.id = canvasId;
    container.appendChild(canvas);
    wrapper.appendChild(container);
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    const isLight = document.body.classList.contains("light");
    const textColor = isLight ? "#006064" : "#cbd5e1";
    const gridColor = isLight ? "rgba(0, 96, 100, 0.1)" : "#1e293b";
    
    // Pilihan warna
    const isPieOrDoughnut = chartInfo.type === "doughnut" || chartInfo.type === "pie";
    const bgColors = isPieOrDoughnut 
        ? ['#00A0E9', '#ED1C24', '#FFE600', '#94a3b8', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
        : '#00A0E9';
        
    // Konfigurasi dataset berdasarkan jenis chart
    const datasetConfig = {
        label: chartInfo.label || 'Jumlah',
        data: chartInfo.values,
        backgroundColor: bgColors,
        borderWidth: isLight ? 1 : 0
    };
    
    if (chartInfo.type === "line") {
        datasetConfig.borderColor = '#00A0E9';
        datasetConfig.backgroundColor = 'rgba(0, 160, 233, 0.1)';
        datasetConfig.fill = true;
        datasetConfig.borderWidth = 2;
        datasetConfig.tension = 0.3; // Garis melengkung halus
    } else if (chartInfo.type === "bar") {
        datasetConfig.borderRadius = 6;
    }
        
    new Chart(canvas, {
        type: chartInfo.type,
        data: {
            labels: chartInfo.labels,
            datasets: [datasetConfig]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: isPieOrDoughnut,
                    position: 'bottom',
                    labels: { color: textColor, font: { size: 9 } }
                }
            },
            scales: (chartInfo.type === "bar" || chartInfo.type === "line") ? {
                x: {
                    ticks: { color: textColor, font: { size: 9 } },
                    grid: { color: gridColor }
                },
                y: {
                    ticks: { color: textColor, font: { size: 9 } },
                    grid: { color: gridColor }
                }
            } : {}
        }
    });
}

function appendSqlExpander(sqlQuery) {
    const sqlWrapper = document.createElement("div");
    sqlWrapper.className = "sql-expander-wrapper flex justify-start pl-6 mt-1";
    
    const details = document.createElement("details");
    details.className = "relative text-xs bg-[#161b22] border border-slate-800 rounded-lg p-3 w-[90%] text-slate-400 font-mono cursor-pointer select-none";
    
    const summary = document.createElement("summary");
    summary.className = "font-bold text-[#00A0E9] mb-2 flex items-center justify-between pr-1";
    
    const titleSpan = document.createElement("span");
    titleSpan.textContent = "▼ Lihat SQL yang dijalankan";
    
    const copyBtn = document.createElement("button");
    copyBtn.className = "copy-btn ml-4";
    copyBtn.setAttribute("data-i18n", "btn_salin_sql");
    copyBtn.textContent = getTranslation("btn_salin_sql");
    copyBtn.type = "button";
    copyBtn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation(); // Prevent closing details on click
        copyToClipboard(sqlQuery, copyBtn);
    });
    
    summary.appendChild(titleSpan);
    summary.appendChild(copyBtn);
    
    const code = document.createElement("code");
    code.className = "block whitespace-pre-wrap mt-1 text-sky-300";
    code.textContent = sqlQuery;
    
    details.appendChild(summary);
    details.appendChild(code);
    sqlWrapper.appendChild(details);
    chatBox.appendChild(sqlWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 5. Initial Event Listeners
dbSelect.addEventListener("change", (e) => {
    const selectedTable = e.target.value;
    
    // Update secara dinamis teks subtitle halaman
    if (subtitleDesc) {
        subtitleDesc.textContent = `Dashboard Tabel ${selectedTable} & Integrasi AI`;
    }
    
    loadTableData(selectedTable);
});

resetChatBtn.addEventListener("click", () => {
    chatHistory = [];
    chatBox.innerHTML = `
        <div class="flex items-start space-x-3">
            <div class="chat-bubble-ai p-3 rounded-2xl rounded-tl-none max-w-[80%] text-sm">
                Halo! Saya adalah Ask PLN, asisten cerdas Anda. Ada yang bisa saya bantu tentang data database hari ini?
            </div>
        </div>
        
        <!-- Suggestions Chips (Prompt Starters) -->
        <div id="chat-suggestions-container" class="flex flex-wrap gap-2.5 pt-2 pl-9">
            <button type="button" class="suggestion-chip px-3 py-2 text-xs rounded-xl border text-slate-300 hover:text-white transition-all bg-slate-800/40 hover:bg-[#00A0E9]/10" style="border-color: var(--card-border);" data-query="Berapa jumlah karyawan saat ini?">
                Berapa jumlah karyawan?
            </button>
            <button type="button" class="suggestion-chip px-3 py-2 text-xs rounded-xl border text-slate-300 hover:text-white transition-all bg-slate-800/40 hover:bg-[#00A0E9]/10" style="border-color: var(--card-border);" data-query="Tampilkan 5 produk yang paling laris">
                5 produk terlaris?
            </button>
            <button type="button" class="suggestion-chip px-3 py-2 text-xs rounded-xl border text-slate-300 hover:text-white transition-all bg-slate-800/40 hover:bg-[#00A0E9]/10" style="border-color: var(--card-border);" data-query="Tampilkan sebaran karyawan tiap divisi">
                Distribusi divisi?
            </button>
            <button type="button" class="suggestion-chip px-3 py-2 text-xs rounded-xl border text-slate-300 hover:text-white transition-all bg-slate-800/40 hover:bg-[#00A0E9]/10" style="border-color: var(--card-border);" data-query="Berapa rata-rata umur karyawan?">
                Rata-rata umur karyawan?
            </button>
        </div>
    `;
    initSuggestionChips();
});

chatForm.addEventListener("submit", handleChatSubmit);

// --- Carousel Slider Logic ---
let currentSlide = 0;
let slides = Array.from(document.querySelectorAll(".carousel-slide"));
let dots = Array.from(document.querySelectorAll(".carousel-dot"));
const slidesContainer = document.querySelector(".carousel-slides");

// Fungsi untuk membersihkan slide yang gambarnya rusak (Error 404) secara sinkron/asinkron
function cleanupBrokenSlides() {
    let hasChanges = false;
    const allSlides = Array.from(document.querySelectorAll(".carousel-slide"));
    const allDots = Array.from(document.querySelectorAll(".carousel-dot"));
    
    allSlides.forEach((slide, index) => {
        const img = slide.querySelector("img");
        // Deteksi jika gambar gagal dimuat (baik sebelum JS aktif atau saat proses memuat berlangsung)
        if (img && (img.complete && img.naturalWidth === 0)) {
            slide.remove();
            const dot = allDots[index];
            if (dot) dot.remove();
            hasChanges = true;
        }
    });
    
    if (hasChanges) {
        // Perbarui array referensi slide & dot aktif secara global
        slides = Array.from(document.querySelectorAll(".carousel-slide"));
        dots = Array.from(document.querySelectorAll(".carousel-dot"));
        
        // Re-index ulang data-slide pada indikator titik yang tersisa
        dots.forEach((d, idx) => {
            d.setAttribute("data-slide", idx);
        });
        
        // Reset tampilan ke slide aktif yang valid
        showSlide(currentSlide);
    }
}

// Jalankan pembersihan awal untuk gambar yang sudah terdeteksi rusak saat halaman dimuat
cleanupBrokenSlides();

// Dengarkan juga event error jika proses memuat gambar gagal di kemudian waktu
document.querySelectorAll(".carousel-slide img").forEach(img => {
    img.addEventListener("error", cleanupBrokenSlides);
});

function showSlide(index) {
    if (!slidesContainer || slides.length === 0) return;
    if (index >= slides.length) currentSlide = 0;
    else if (index < 0) currentSlide = slides.length - 1;
    else currentSlide = index;
    
    // Toggle active class for premium fade transition
    slides.forEach((slide, idx) => {
        if (idx === currentSlide) {
            slide.classList.add("active");
        } else {
            slide.classList.remove("active");
        }
    });
    
    dots.forEach((dot, idx) => {
        if (idx === currentSlide) {
            dot.classList.add("carousel-dot-active");
        } else {
            dot.classList.remove("carousel-dot-active");
        }
    });
}

function nextSlide() {
    showSlide(currentSlide + 1);
}
function prevSlide() {
    showSlide(currentSlide - 1);
}

let slideInterval = setInterval(nextSlide, 5000);

function resetSlideInterval() {
    clearInterval(slideInterval);
    slideInterval = setInterval(nextSlide, 5000);
}

const prevBtn = document.getElementById("carousel-prev-btn");
const nextBtn = document.getElementById("carousel-next-btn");

if (prevBtn) {
    prevBtn.addEventListener("click", () => {
        prevSlide();
        resetSlideInterval();
    });
}
if (nextBtn) {
    nextBtn.addEventListener("click", () => {
        nextSlide();
        resetSlideInterval();
    });
}

dots.forEach(dot => {
    dot.addEventListener("click", (e) => {
        const slideIndex = parseInt(e.target.getAttribute("data-slide"));
        showSlide(slideIndex);
        resetSlideInterval();
    });
});

// --- Mobile Menu Toggle ---
const mobileMenuBtn = document.getElementById("mobile-menu-btn");
const mobileMenu = document.getElementById("mobile-menu");

if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener("click", () => {
        mobileMenu.classList.toggle("hidden");
    });
}

const mobileLinks = document.querySelectorAll(".nav-link-mobile");
mobileLinks.forEach(link => {
    link.addEventListener("click", () => {
        if (mobileMenu) mobileMenu.classList.add("hidden");
    });
});

// --- Section Switching / Tab Logic ---
const sections = ["about", "dashboard", "ask-pln"];
const navLinks = document.querySelectorAll(".nav-link");
const navLinksMobile = document.querySelectorAll(".nav-link-mobile");

function switchSection(sectionId) {
    sections.forEach(s => {
        const el = document.getElementById(`section-${s}`);
        if (el) {
            if (s === sectionId) {
                el.classList.remove("hidden");
            } else {
                el.classList.add("hidden");
            }
        }
    });
    
    // Update active nav links (desktop)
    navLinks.forEach(link => {
        link.classList.remove("nav-link-active");
        if (link.getAttribute("href") === `#section-${sectionId}`) {
            link.classList.add("nav-link-active");
        }
    });
    
    // Update active nav links (mobile)
    navLinksMobile.forEach(link => {
        link.classList.remove("nav-link-mobile-active");
        if (link.getAttribute("href") === `#section-${sectionId}`) {
            link.classList.add("nav-link-mobile-active");
        }
    });
}

// Add click listeners to navigation links to handle section switching
const allNavLinks = document.querySelectorAll(".nav-link, .nav-link-mobile");
allNavLinks.forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault();
        const targetId = link.getAttribute("href").replace("#section-", "");
        switchSection(targetId);
    });
});

// 6. Pagination Event Listeners
const prevPageBtn = document.getElementById("prev-page-btn");
const nextPageBtn = document.getElementById("next-page-btn");

if (prevPageBtn) {
    prevPageBtn.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable(dbSelect.value, currentTableData);
        }
    });
}

if (nextPageBtn) {
    nextPageBtn.addEventListener("click", () => {
        const maxPage = Math.ceil(currentTableData.length / rowsPerPage);
        if (currentPage < maxPage) {
            currentPage++;
            renderTable(dbSelect.value, currentTableData);
        }
    });
}

// Tab switching event listeners removed (now using single-page scrolling layout)

// 7. Theme Toggle Logic
function applyTheme(theme) {
    const isLight = (theme === "light");
    if (isLight) {
        document.body.classList.add("light");
    } else {
        document.body.classList.remove("light");
    }
    
    const textEn = isLight ? "Dark Mode" : "Light Mode";
    const textId = isLight ? "Mode Gelap" : "Mode Terang";
    const buttonText = currentLang === "en" ? textEn : textId;
    
    const themeText = document.getElementById("theme-toggle-text");
    if (themeText) themeText.textContent = buttonText;
    
    const themeTextMobile = document.getElementById("theme-toggle-text-mobile");
    if (themeTextMobile) themeTextMobile.textContent = buttonText;
}

// Initialize theme from localStorage or system preference
const savedTheme = localStorage.getItem("theme");
const systemPrefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
const initialTheme = savedTheme || (systemPrefersLight ? "light" : "dark");
applyTheme(initialTheme);

const themeToggleBtns = document.querySelectorAll("#theme-toggle-btn, #theme-toggle-btn-mobile");
themeToggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        const isCurrentlyLight = document.body.classList.contains("light");
        const newTheme = isCurrentlyLight ? "dark" : "light";
        localStorage.setItem("theme", newTheme);
        applyTheme(newTheme);
        
        // Redraw charts with the new theme colors if data exists
        if (currentTableData.length > 0) {
            renderCharts(dbSelect.value, currentTableData);
        }
    });
});

// 8. Render Charts (Chart.js)
function renderCharts(tableName, data) {
    const canvas1 = document.getElementById("chart-canvas-1");
    const canvas2 = document.getElementById("chart-canvas-2");
    const title1 = document.getElementById("chart-title-1");
    const title2 = document.getElementById("chart-title-2");
    
    if (!canvas1 || !canvas2) return;
    
    // Destroy previous chart instances to avoid hover/render bugs
    if (chartInstance1) chartInstance1.destroy();
    if (chartInstance2) chartInstance2.destroy();
    
    // Determine colors based on Dark/Light Mode
    const isLight = document.body.classList.contains("light");
    const textColor = isLight ? "#006064" : "#cbd5e1";
    const gridColor = isLight ? "rgba(0, 96, 100, 0.1)" : "#1e293b";
    const tooltipBg = isLight ? "#006064" : "#0d1117";
    
    if (tableName === "karyawan_pln") {
        title1.textContent = getTranslation("chart_title_karyawan_1");
        title2.textContent = getTranslation("chart_title_karyawan_2");
        
        // Calculate counts for Division
        const divCounts = {};
        data.forEach(row => {
            const div = row.Divisi || row.divisi || "Lainnya";
            divCounts[div] = (divCounts[div] || 0) + 1;
        });
        
        const divLabels = Object.keys(divCounts);
        const divValues = Object.values(divCounts);
        
        // Calculate counts for Gender
        const genderCounts = { "Laki-laki": 0, "Perempuan": 0 };
        data.forEach(row => {
            const jk = String(row.Jenis_Kelamin || row.jenis_kelamin || "").toUpperCase();
            if (jk === "L" || jk === "LAKI-LAKI") genderCounts["Laki-laki"]++;
            else if (jk === "P" || jk === "PEREMPUAN") genderCounts["Perempuan"]++;
        });
        
        // Render Bar Chart (Division)
        chartInstance1 = new Chart(canvas1, {
            type: 'bar',
            data: {
                labels: divLabels,
                datasets: [{
                    label: 'Jumlah Karyawan',
                    data: divValues,
                    backgroundColor: '#00A0E9', // PLN Blue
                    borderRadius: 6,
                    maxBarThickness: 35
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { backgroundColor: tooltipBg }
                },
                scales: {
                    x: {
                        ticks: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 'bold' } },
                        grid: { color: gridColor }
                    },
                    y: {
                        ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' }, stepSize: 1 },
                        grid: { color: gridColor }
                    }
                }
            }
        });
        
        const genderLabels = currentLang === "en" ? ["Male", "Female"] : ["Laki-laki", "Perempuan"];
        // Render Doughnut Chart (Gender)
        chartInstance2 = new Chart(canvas2, {
            type: 'doughnut',
            data: {
                labels: genderLabels,
                datasets: [{
                    data: Object.values(genderCounts),
                    backgroundColor: ['#00A0E9', '#ED1C24'], // PLN Blue & PLN Red
                    borderWidth: isLight ? 2 : 0,
                    borderColor: isLight ? '#ffffff' : 'transparent'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 'bold' } }
                    },
                    tooltip: { backgroundColor: tooltipBg }
                }
            }
        });
        
    } else if (tableName === "absensi") {
        title1.textContent = currentLang === "en" ? "Daily Attendance Trend" : "Tren Kehadiran Harian";
        title2.textContent = currentLang === "en" ? "Overall Attendance Distribution" : "Distribusi Kehadiran Keseluruhan";
        
        // Calculate daily presence/absence
        const dailyStats = {};
        data.forEach(row => {
            const date = row.Tanggal || row.tanggal || "Lainnya";
            const status = row.Status || row.status || "Tidak";
            if (!dailyStats[date]) {
                dailyStats[date] = { "Masuk": 0, "Tidak": 0 };
            }
            if (status === "Masuk") {
                dailyStats[date]["Masuk"]++;
            } else {
                dailyStats[date]["Tidak"]++;
            }
        });
        
        const sortedDates = Object.keys(dailyStats).sort();
        const presentValues = sortedDates.map(d => dailyStats[d]["Masuk"]);
        const absentValues = sortedDates.map(d => dailyStats[d]["Tidak"]);
        
        // Render Grouped Bar Chart (Daily trend)
        chartInstance1 = new Chart(canvas1, {
            type: 'bar',
            data: {
                labels: sortedDates,
                datasets: [
                    {
                        label: currentLang === "en" ? "Present" : "Masuk",
                        data: presentValues,
                        backgroundColor: '#00A0E9', // PLN Blue
                        borderRadius: 4
                    },
                    {
                        label: currentLang === "en" ? "Absent" : "Tidak Masuk",
                        data: absentValues,
                        backgroundColor: '#ED1C24', // PLN Red
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 'bold' } }
                    },
                    tooltip: { backgroundColor: tooltipBg }
                },
                scales: {
                    x: {
                        ticks: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 'bold' } },
                        grid: { color: gridColor }
                    },
                    y: {
                        ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' }, stepSize: 1 },
                        grid: { color: gridColor }
                    }
                }
            }
        });
        
        // Calculate overall stats
        let totalPresent = 0;
        let totalAbsent = 0;
        data.forEach(row => {
            const status = row.Status || row.status || "Tidak";
            if (status === "Masuk") totalPresent++;
            else totalAbsent++;
        });
        
        const attendanceLabels = currentLang === "en" ? ["Present", "Absent"] : ["Masuk", "Tidak Masuk"];
        // Render Doughnut Chart
        chartInstance2 = new Chart(canvas2, {
            type: 'doughnut',
            data: {
                labels: attendanceLabels,
                datasets: [{
                    data: [totalPresent, totalAbsent],
                    backgroundColor: ['#00A0E9', '#ED1C24'], // PLN Blue & PLN Red
                    borderWidth: isLight ? 2 : 0,
                    borderColor: isLight ? '#ffffff' : 'transparent'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 'bold' } }
                    },
                    tooltip: { backgroundColor: tooltipBg }
                }
            }
        });
    } else {
        // customers table
        title1.textContent = getTranslation("chart_title_customer_1");
        title2.textContent = getTranslation("chart_title_customer_2");
        
        // Calculate counts for Country
        const countryCounts = {};
        data.forEach(row => {
            const country = row.country || "Lainnya";
            countryCounts[country] = (countryCounts[country] || 0) + 1;
        });
        
        // Sort and slice top 7
        const sortedCountries = Object.entries(countryCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 7);
            
        const countryLabels = sortedCountries.map(x => x[0]);
        const countryValues = sortedCountries.map(x => x[1]);
        
        // Calculate ranges for Credit Limit
        const limitRanges = {
            "Tanpa Limit": 0,
            "< 50k": 0,
            "50k - 100k": 0,
            "> 100k": 0
        };
        data.forEach(row => {
            const limit = parseFloat(row.creditLimit || 0);
            if (limit === 0) limitRanges["Tanpa Limit"]++;
            else if (limit < 50000) limitRanges["< 50k"]++;
            else if (limit <= 100000) limitRanges["50k - 100k"]++;
            else limitRanges["> 100k"]++;
        });
        
        // Render Horizontal Bar Chart (Country)
        chartInstance1 = new Chart(canvas1, {
            type: 'bar',
            data: {
                labels: countryLabels,
                datasets: [{
                    label: 'Jumlah Customer',
                    data: countryValues,
                    backgroundColor: '#00A0E9', // PLN Blue
                    borderRadius: 6,
                    maxBarThickness: 35
                }]
            },
            options: {
                indexAxis: 'y', // Horizontal
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { backgroundColor: tooltipBg }
                },
                scales: {
                    x: {
                        ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' }, stepSize: 1 },
                        grid: { color: gridColor }
                    },
                    y: {
                        ticks: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 'bold' } },
                        grid: { color: gridColor }
                    }
                }
            }
        });
        
        const creditLabels = Object.keys(limitRanges).map(key => {
            if (key === "Tanpa Limit") return getTranslation("credit_limit_none");
            return key;
        });
        // Render Doughnut Chart (Credit Range)
        chartInstance2 = new Chart(canvas2, {
            type: 'doughnut',
            data: {
                labels: creditLabels,
                datasets: [{
                    data: Object.values(limitRanges),
                    backgroundColor: ['#94a3b8', '#FFE600', '#00A0E9', '#ED1C24'], // Grey, Yellow, Blue, Red
                    borderWidth: isLight ? 2 : 0,
                    borderColor: isLight ? '#ffffff' : 'transparent'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 'bold' } }
                    },
                    tooltip: { backgroundColor: tooltipBg }
                }
            }
        });
    }
}

// Load data awal saat startup
document.addEventListener("DOMContentLoaded", () => {
    loadTablesList();
    // Initialize carousel slide and active section state
    showSlide(0);
    switchSection("about");
    
    // Bind modal and suggestions listeners
    initSchemaModal();
    initSuggestionChips();
    
    // Initialize past queries history
    loadPastQueries();
    
    // Set initial language translations
    updateLanguage();

    // Initialize show SQL preference checkbox listener
    if (showSqlCheckbox) {
        showSqlCheckbox.addEventListener("change", () => {
            if (showSqlCheckbox.checked) {
                document.body.classList.add("show-sql-enabled");
                localStorage.setItem("pln_show_sql", "true");
            } else {
                document.body.classList.remove("show-sql-enabled");
                localStorage.setItem("pln_show_sql", "false");
            }
        });
        
        const savedShowSql = localStorage.getItem("pln_show_sql");
        if (savedShowSql === "true") {
            showSqlCheckbox.checked = true;
            document.body.classList.add("show-sql-enabled");
        } else {
            showSqlCheckbox.checked = false;
            document.body.classList.remove("show-sql-enabled");
        }
    }
    
    // Initialize translate preference checkbox listener
    if (translateCheckbox) {
        const applyTranslate = (enabled) => {
            if (enabled) {
                document.body.classList.add("translate-enabled");
                translateCheckbox.checked = true;
                localStorage.setItem("pln_translate", "true");
            } else {
                document.body.classList.remove("translate-enabled");
                translateCheckbox.checked = false;
                localStorage.setItem("pln_translate", "false");
            }
        };
        
        translateCheckbox.addEventListener("change", () => {
            applyTranslate(translateCheckbox.checked);
        });
        
        const savedTranslate = localStorage.getItem("pln_translate");
        applyTranslate(savedTranslate !== "false"); // Default to true
    }
});

// Function to download current table data as CSV
function downloadCSV() {
    if (!currentTableData || currentTableData.length === 0) {
        alert(currentLang === "en" ? "No data to download." : "Tidak ada data untuk diunduh.");
        return;
    }
    
    const tableName = dbSelect.value;
    const headers = Object.keys(currentTableData[0]);
    
    const csvRows = [];
    // Add header row
    csvRows.push(headers.join(","));
    
    // Add data rows
    for (const row of currentTableData) {
        const values = headers.map(header => {
            const val = row[header] === null || row[header] === undefined ? "" : String(row[header]);
            // Escape double quotes and wrap in quotes
            const escaped = val.replace(/"/g, '""');
            return `"${escaped}"`;
        });
        csvRows.push(values.join(","));
    }
    
    const csvString = csvRows.join("\r\n");
    const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${tableName}_export.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

if (downloadCsvBtn) {
    downloadCsvBtn.addEventListener("click", downloadCSV);
}

// --- Past Queries / Chat History List Logic ---
const clearHistoryBtn = document.getElementById("clear-history-btn");
const historyQueriesList = document.getElementById("history-queries-list");
let pastQueries = [];

function loadPastQueries() {
    try {
        const stored = localStorage.getItem("pln_past_queries");
        if (stored) {
            pastQueries = JSON.parse(stored);
        }
    } catch (e) {
        console.error("Error loading past queries", e);
        pastQueries = [];
    }
    renderPastQueries();
}

function savePastQueries() {
    try {
        localStorage.setItem("pln_past_queries", JSON.stringify(pastQueries));
    } catch (e) {
        console.error("Error saving past queries", e);
    }
}

function addPastQuery(query) {
    if (!query) return;
    // Remove if already exists (to bump to top)
    pastQueries = pastQueries.filter(q => q.toLowerCase() !== query.toLowerCase());
    // Add to top
    pastQueries.unshift(query);
    // Limit to 30 items
    if (pastQueries.length > 30) {
        pastQueries = pastQueries.slice(0, 30);
    }
    savePastQueries();
    renderPastQueries();
}

function renderPastQueries() {
    if (!historyQueriesList) return;
    
    if (pastQueries.length === 0) {
        historyQueriesList.innerHTML = `<div class="text-slate-500 text-center py-8 text-xs">Belum ada riwayat.</div>`;
        return;
    }
    
    historyQueriesList.innerHTML = "";
    pastQueries.forEach(query => {
        const item = document.createElement("button");
        item.type = "button";
        item.className = "history-query-item";
        
        const textSpan = document.createElement("span");
        textSpan.className = "history-query-text";
        textSpan.textContent = query;
        textSpan.title = query;
        
        const iconSpan = document.createElement("span");
        iconSpan.textContent = "→";
        iconSpan.className = "history-query-arrow";
        
        item.appendChild(textSpan);
        item.appendChild(iconSpan);
        
        item.addEventListener("click", () => {
            const cleanQuery = query.trim().toLowerCase();
            const targetBubble = chatBox.querySelector(`[data-query-text="${cleanQuery}"]`);
            if (targetBubble) {
                targetBubble.scrollIntoView({ behavior: "smooth", block: "center" });
                targetBubble.classList.add("bg-[#00A0E9]/30");
                setTimeout(() => {
                    targetBubble.classList.remove("bg-[#00A0E9]/30");
                }, 1500);
            } else {
                if (chatInput) {
                    chatInput.value = query;
                    chatInput.focus();
                }
            }
        });
        
        historyQueriesList.appendChild(item);
    });
}

if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener("click", () => {
        pastQueries = [];
        savePastQueries();
        renderPastQueries();
    });
}

// --- Clipboard Copy Helper ---
function copyToClipboard(text, btnElement) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = btnElement.innerHTML;
        btnElement.innerHTML = "✓ Tersalin!";
        setTimeout(() => {
            btnElement.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        console.error("Gagal menyalin teks: ", err);
    });
}

// --- Markdown Table TSV Clipboard Copy Helper ---
window.copyTableText = function(btn) {
    const container = btn.closest(".relative");
    const table = container.querySelector("table");
    if (!table) return;
    
    let text = "";
    const rows = table.querySelectorAll("tr");
    rows.forEach((row) => {
        const cells = row.querySelectorAll("th, td");
        const cellTexts = [];
        cells.forEach(cell => {
            cellTexts.push(cell.textContent.trim());
        });
        text += cellTexts.join("\t") + "\n";
    });
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = "✓ Tersalin!";
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        console.error("Gagal menyalin tabel: ", err);
    });
};

// --- Database Schema Modal Events ---
function initSchemaModal() {
    const schemaModalBtn = document.getElementById("schema-modal-btn");
    const schemaModal = document.getElementById("schema-modal");
    const schemaModalBackdrop = document.getElementById("schema-modal-backdrop");
    const schemaModalClose = document.getElementById("schema-modal-close");

    if (schemaModalBtn && schemaModal) {
        schemaModalBtn.addEventListener("click", () => {
            schemaModal.classList.remove("hidden");
        });
    }

    const hideSchemaModal = () => {
        if (schemaModal) schemaModal.classList.add("hidden");
    };

    if (schemaModalClose) schemaModalClose.addEventListener("click", hideSchemaModal);
    if (schemaModalBackdrop) schemaModalBackdrop.addEventListener("click", hideSchemaModal);
}

// --- Suggestion Chips Click Binder ---
function initSuggestionChips() {
    renderSuggestionChips();
}

// --- Download Chart as PNG Helper ---
window.downloadChart = function(canvasId, filename) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    try {
        const isLight = document.body.classList.contains("light");
        const bgColor = isLight ? "#ffffff" : "#0f172a"; // Match themes background
        
        const tempCanvas = document.createElement("canvas");
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        const ctx = tempCanvas.getContext("2d");
        
        // Fill canvas background
        ctx.fillStyle = bgColor;
        ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
        
        // Draw chart canvas onto it
        ctx.drawImage(canvas, 0, 0);
        
        const url = tempCanvas.toDataURL("image/png");
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        link.style.visibility = "hidden";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (e) {
        console.error("Gagal menyimpan grafik:", e);
        // Fallback: direct download (transparent background)
        const url = canvas.toDataURL("image/png");
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
};

// --- Translation Logic ---
function updateLanguage() {
    const langData = translations[currentLang];
    if (!langData) return;
    
    // Update elements with data-i18n
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (langData[key]) {
            el.textContent = langData[key];
        }
    });
    
    // Update placeholders with data-i18n-placeholder
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        const key = el.getAttribute("data-i18n-placeholder");
        if (langData[key]) {
            el.setAttribute("placeholder", langData[key]);
        }
    });
    
    // Update lang button text
    const langBtnText = currentLang === "id" ? "English" : "Bahasa";
    document.querySelectorAll("#lang-toggle-btn, #lang-toggle-btn-mobile").forEach(btn => {
        btn.textContent = langBtnText;
    });
    
    // Re-render suggestion chips
    renderSuggestionChips();
    
    // Re-apply theme text translations
    const isLight = document.body.classList.contains("light");
    applyTheme(isLight ? "light" : "dark");
    
    // If the welcome message is the only bubble, translate it too
    const chatBubbleAiList = chatBox.querySelectorAll(".chat-bubble-ai");
    if (chatBubbleAiList.length === 1 && chatHistory.length === 0) {
        chatBubbleAiList[0].textContent = langData.chat_welcome;
    }
    
    // Update active database tables list select loading label if needed
    if (dbSelect && dbSelect.value === "") {
        const opt = dbSelect.querySelector("option");
        if (opt) opt.textContent = langData.option_loading;
    }
}

// Bind language toggles
const langToggleBtns = document.querySelectorAll("#lang-toggle-btn, #lang-toggle-btn-mobile");
langToggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        currentLang = currentLang === "id" ? "en" : "id";
        localStorage.setItem("pln_lang", currentLang);
        updateLanguage();
        
        // Re-calculate KPIs and table info texts
        if (currentTableData.length > 0) {
            renderTable(dbSelect.value, currentTableData);
            calculateKPIs(dbSelect.value, currentTableData);
            renderCharts(dbSelect.value, currentTableData);
        }
    });
});


