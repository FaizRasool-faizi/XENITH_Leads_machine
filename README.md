# XENITH Solutions — B2B Lead Generator & Intelligence Platform

An end-to-end, free B2B Lead Generation and Opportunity Analysis platform built specifically for **XENITH Solutions**. 

The platform offers two production-grade user experiences:
1. **Modern React / Next.js SaaS Web Application** (`frontend/`): Built with Next.js 16, React 19, TailwindCSS, glassmorphic UI, micro-animations, and full Vercel 1-click cloud readiness.
2. **Python & Streamlit Power Desktop Platform** (`ui/app.py`): Full 14-view workspace with local SQLite persistence, live OSM ingestion, and comprehensive audit logs.

---

## 🌟 Key Features

- **100% Free & Open-Source Core:** No mandatory paid APIs, SaaS subscriptions, cloud servers, or hosted n8n required.
- **Genuine Business Discovery:**
  - **OpenStreetMap (Overpass API):** Discovers verified businesses across clinics, law firms, IT consultancies, contractors, trades, and commercial offices with ODbL attribution.
  - **Lawful File Importer:** Imports CSV/Excel datasets with intelligent column mapping, validation, and rejected-row auditing.
  - **Extensible Directory Framework:** Pre-configured connectors with terms verification safeguards.
- **Conservative & SSRF-Protected Crawler:**
  - Prohibits internal IP access (RFC 1918, loopback, link-local, cloud metadata).
  - Honors `robots.txt` with conservative fallback.
  - Enforces rate limits (1 req/sec per domain), 10s timeouts, and 2 MB max payload limits.
- **Observable Opportunity Analysis:**
  - Website modernization signals (missing mobile viewport, missing title/meta description, SSL status, HTTP error status).
  - Customer support gaps (absence of AI chatbot / live support widgets).
  - Booking & intake bottlenecks (missing online scheduling tools in service businesses).
  - AI voice agent candidate identification (high-volume phone reliance).
- **Explainable Multi-Dimensional Scoring (0–100):**
  - Business Legitimacy (0–20 pts)
  - Relevance to XENITH Services (0–20 pts)
  - Observable Tech Opportunity (0–25 pts)
  - Contact Channel Availability (0–15 pts)
  - Evidence Quality & Recency (0–20 pts)
  - Full point breakdown and manual score overrides with audit logging.
- **Compliance & Do-Not-Contact (DNC):**
  - Global suppression list across normalized domain, email, phone, and company name.
  - Suppressed entities survive deduplication and subsequent imports.
  - Right-to-be-forgotten permanent purge workflow.
  - Regional guidance for US (CAN-SPAM/TCPA), Canada (CASL), Australia (Spam Act), and UAE/Gulf markets.
- **Personalized Outreach Drafts:**
  - Tailored copy for Website Redesign, AI Chatbots, Workflow Automation, and AI Voice Bots.
  - Explicit citations of verified observations (no hallucinated problems or fabricated relationships).
  - Reviewer workflow: Approve, Reject, or Edit drafts prior to export.
- **Export & Reporting:**
  - One-click export to CSV and formatted Microsoft Excel (.xlsx) with complete provenance.
- **Optional Local AI (Ollama):**
  - Connects to local Ollama models (e.g. `llama3`) for message refinement while operating with 100% fidelity offline via rule-based templates.

---

## 📋 Prerequisites

- **Operating System:** Windows 10 / Windows 11 (64-bit).
- **Python:** Python 3.11 or newer (Python 3.14 recommended).
- **RAM:** Minimum 4 GB.
- **Disk Space:** ~500 MB (excluding optional local LLMs).

---

## 🚀 Quick Setup & Installation (Windows CMD)

### 1. Clone or Open Workspace
Open Windows Command Prompt (`cmd.exe`) and navigate to the project directory:
```cmd
cd /d D:\Faiz\XENITH\Lead_Genrator
```

### 2. Create Virtual Environment
```cmd
py -m venv .venv
```

### 3. Activate Virtual Environment
```cmd
call .venv\Scripts\activate.bat
```

### 4. Install Dependencies
```cmd
python -m pip install -r requirements.txt
```

### 5. Initialize SQLite Database
```cmd
python -c "from database.connection import init_db; init_db()"
```

---

## 🖥️ How to Launch the Application

### Option A: One-Click Windows Batch Launcher
Double-click `run.bat` in the project root folder, or run:
```cmd
run.bat
```

### Option B: Manual Command Line
```cmd
.\.venv\Scripts\python.exe -m streamlit run ui\app.py
```
The dashboard will open automatically in your default desktop browser at **http://localhost:8501**.

---

## 📖 Operational User Guide

### 1. Discover Leads via OpenStreetMap
1. In the sidebar, select **2. Lead Discovery (OSM)**.
2. Enter the target **City** (e.g. `Austin`, `Denver`, `Sydney`, `Dubai`, `Toronto`) and select the **Country**.
3. Choose the business verticals (e.g., *Healthcare & Medical*, *Legal & Financial*, *Trades & Contractors*).
4. Click **Run Discovery Query**. Genuine registered business nodes will be ingested and deduplicated automatically.

### 2. Import External Business Data (CSV / Excel)
1. In the sidebar, select **3. File Importer (CSV/Excel)**.
2. Upload a `.csv` or `.xlsx` file.
3. The system maps headers automatically (e.g., `Company Name`, `Website`, `Category`, `Phone`, `Email`).
4. Click **Validate & Ingest File**. Duplicate records will be merged with historic evidence, and any suppressed records will be quarantined.

### 3. Inspect Websites & Discover Opportunities
1. Navigate to **6. Website Opportunity Analysis**.
2. Select an individual business or use the **Batch Analyze** tab.
3. Click **Run Safe Website Inspection**. The crawler tests the live site, extracts public contact channels, and logs observable gaps.

### 4. Review Lead Scores & Calibrate Weights
1. Navigate to **7. Lead Scoring & Weights**.
2. Customize the weights based on current sales focus (e.g. increase Opportunity weight for tech gaps).
3. Click **Recalculate Scores for All Businesses**.
4. Check **8. Lead Detail & Evidence** for an individual breakdown of why any company scored high or low.

### 5. Generate & Approve Outreach Drafts
1. Go to **9. Outreach Draft Generator**.
2. Select the target business and preferred service pitch (Website, Chatbot, Automation, Voice Bot).
3. Click **Generate Factual Outreach Draft**.
4. Edit the message text if desired, then click **Approve Draft**.

### 6. Export Verified Leads
1. Navigate to **13. Export & Reporting**.
2. Filter by priority tier (*HIGH_PRIORITY*, *POTENTIAL_PROSPECT*, or *All*).
3. Click **Download CSV** or **Download Excel (.xlsx)**.

---

## 🧪 Running Automated Tests

Execute the comprehensive Pytest suite (38 tests covering all 14 required business scenarios):
```cmd
.\.venv\Scripts\python.exe -m pytest -v
```

---

## 🛡️ Security & SSRF Protection Architecture

The crawler strictly blocks all requests to private and reserved network addresses:
- `127.0.0.0/8` (Loopback / Localhost)
- `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (Private RFC 1918)
- `169.254.0.0/16` (Link-Local / Cloud Instance Metadata)
- `::1` (IPv6 Loopback)
- `fc00::/7` (IPv6 Unique Local)

---

## 📂 Project Structure

```
Lead_Genrator/
├── core/                        # Configuration, SSRF security, logging, AI client
├── database/                    # SQLAlchemy models, SQLite connection, deduplication, repo
├── connectors/                  # OSM Overpass, CSV/Excel importer, Directory connectors
├── analyzer/                    # Safe crawler, robots checker, contact & opportunity analyzers
├── scoring/                     # 5-dimensional scoring model & weight profiles
├── outreach/                    # Personalized factual templates & draft generator
├── compliance/                  # Global DNC suppression, GDPR purge, market policies
├── ui/                          # Streamlit application, branded styling, export service
├── tests/                       # 38 passing unit and integration tests
├── data/                        # Local SQLite database (xenith_leads.db)
├── docs/                        # Complete technical specifications & architectural ADRs
├── requirements.txt             # Frozen dependency list
├── run.bat                      # Windows one-click launcher
└── README.md                    # This document
```

---

## 📄 License & Attribution
- OpenStreetMap data is licensed under the **Open Database License (ODbL)**: *© OpenStreetMap contributors*.
- Application architecture and software developed for **XENITH Solutions**.
