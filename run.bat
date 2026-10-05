@echo off
TITLE XENITH Solutions - B2B Lead Generator
cd /d "%~dp0"

echo ===================================================
echo     XENITH Solutions - B2B Lead Generator
echo ===================================================
echo.

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found. Setting up .venv...
    py -m venv .venv
    IF ERRORLEVEL 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed.
        pause
        exit /b 1
    )
    echo [INFO] Installing required dependencies...
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo [INFO] Starting XENITH Lead Generator Dashboard...
echo [INFO] Dashboard will open in your default browser at http://localhost:8501
echo.
.\.venv\Scripts\python.exe -m streamlit run ui\app.py

pause
