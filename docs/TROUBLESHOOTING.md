# XENITH Lead Generator — Troubleshooting Guide

## 1. Common Installation & Startup Issues

### 1.1 Python Not Found / Virtual Environment Issues
- **Symptom:** `py` or `python` not recognized in Windows CMD.
- **Resolution:**
  1. Confirm Python 3.11+ is installed.
  2. Use the Windows Python launcher: `py -3 -m venv .venv`.
  3. Ensure execution policy allows script running or launch via:
     ```cmd
     .\.venv\Scripts\python.exe -m streamlit run ui\app.py
     ```

### 1.2 SQLite Permission Error on Teardown (WinError 32)
- **Symptom:** `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`.
- **Cause:** Windows locks open file handles on SQLite database files until the engine is explicitly disposed.
- **Resolution:** Always call `engine.dispose()` before attempting to delete or move `.db` files on Windows.

### 1.3 OpenStreetMap (Overpass API) Rate Limit / Timeout
- **Symptom:** "Overpass query returned no results" or HTTP 429/504.
- **Cause:** Public Overpass endpoints experience periodic queue throttling.
- **Resolution:**
  1. The connector automatically cycles through 3 fallback mirrors (`overpass-api.de`, `lz4.overpass-api.de`, `maps.mail.ru`).
  2. Reduce the `Max Results` slider (e.g. from 100 to 25).
  3. Wait 10 seconds before initiating subsequent queries.

---

## 2. Crawler & Network Errors

### 2.1 "Security check rejected URL: SSRF Protection"
- **Cause:** The target website hostname resolved to an internal IP (e.g., `127.0.0.1`, `192.168.x.x`, `10.x.x.x`, or AWS metadata `169.254.169.254`).
- **Explanation:** This is an intentional security safeguard preventing the crawler from querying internal network infrastructure or private cloud endpoints.

### 2.2 "Crawling prohibited by website robots.txt"
- **Cause:** The target site's `robots.txt` explicitly disallows automated User-Agents or returned an access denial code (HTTP 401/403).
- **Resolution:** The crawler defaults to conservative skip to respect website terms. If manual verification is permitted, inspect the site directly in your web browser.

---

## 3. Local AI (Ollama) Integration

### 3.1 Ollama Status Shows "Offline"
- **Cause:** Ollama service is not running locally on port 11434.
- **Resolution:**
  1. Download and start Ollama from `https://ollama.com`.
  2. Pull your preferred model:
     ```cmd
     ollama pull llama3
     ```
  3. The lead generator automatically detects the online model.
  4. Note: AI is entirely optional. All lead discovery, scoring, opportunity analysis, and outreach generation functions operate with 100% fidelity without Ollama.

---

## 4. Database Backup & Restore

### 4.1 Backup
Simply copy the SQLite file while the app is idle:
```cmd
copy data\xenith_leads.db data\xenith_leads_backup.db
```

### 4.2 Restore
Replace `data\xenith_leads.db` with your backup copy and restart the application.
