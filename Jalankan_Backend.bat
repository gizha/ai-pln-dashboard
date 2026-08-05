@echo off
title Backend AI PLN Dashboard
echo ==================================================
echo         MENJALANKAN BACKEND AI PLN
echo ==================================================
echo.
echo Script ini akan mengaktifkan virtual environment (.venv)
echo dan menjalankan server FastAPI (backend) di port 8000.
echo.
echo Menghubungkan ke database online (Railway)...
echo.

:: Masuk ke folder root project
cd /d "%~dp0"

:: Cek apakah folder .venv ada
if not exist .venv (
    echo [ERROR] Virtual Environment .venv tidak ditemukan di folder root!
    echo Pastikan virtual environment sudah dibuat.
    pause
    exit /b
)

:: Jalankan uvicorn secara langsung menggunakan python dari virtual environment
cd separated_app\backend
..\..\.venv\Scripts\python.exe -m uvicorn main:app --reload

pause



