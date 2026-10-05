# XENITH Lead Generator — Project Implementation Plan

## 1. Project Overview & Business Mission
**Business Name:** XENITH Solutions  
**Purpose:** Build a reliable, locally runnable, free, end-to-end B2B prospecting, verification, opportunity analysis, scoring, outreach drafting, and compliance system tailored for XENITH Solutions.  
**Target Markets:** United States, Canada, Australia, UAE and other Gulf markets.  
**Core Offerings:**
1. Website design and development
2. Custom web applications & business software
3. AI chatbots and customer-support agents
4. AI workflow & business-process automation
5. AI calling agents
6. CRM integrations
7. Generative AI solutions & consulting

---

## 2. Core Constraints & Guiding Principles
- **100% Free & Open-Source Core:** No mandatory paid API keys or cloud dependencies (no hosted n8n, no VPS, no SaaS monthly subscriptions required).
- **Windows 11 Native & Local:** Python 3.14 venv with SQLite persistence, running locally via desktop browser.
- **Evidence-Backed & Factual:** Strict provenance for every observation. No invented facts, no hallucinated defects, no fake sample data stored as real prospects.
- **Conservative Crawling & SSRF Protection:** Private IP blocking (127.0.0.1, 10.x, 192.168.x, 169.254.x), robots.txt checking, timeouts, rate-limiting, and max payload limits.
- **DNC & Suppression by Design:** Global suppression lists prevent contacting opted-out or restricted entities; suppression survives deduplication.
- **Human-in-the-Loop:** Outreach drafts are prepared with evidence references for human review. No auto-dialing, unsolicited auto-mailing, or unreviewed outbound calls.

---

## 3. Phased Implementation Roadmap

### Phase 0: Workspace Inspection & Setup
- **Tasks:**
  - Verify Python version (Python 3.14.5 64-bit on Windows 11).
  - Create workspace virtual environment (`.venv`).
  - Install dependencies (`pydantic`, `sqlalchemy`, `requests`, `beautifulsoup4`, `pandas`, `openpyxl`, `pytest`, `streamlit`, `fastapi`, `uvicorn`).
  - Establish `docs/` architecture, decisions, plan, testing strategy, and progress log.
- **Dependencies:** None.
- **Acceptance Criteria:** Environment created, packages installed, documentation written.

### Phase 1: Application Architecture & Foundation Modules
- **Tasks:**
  - Design modular directory layout: `core/`, `database/`, `connectors/`, `analyzer/`, `scoring/`, `outreach/`, `compliance/`, `ui/`, `tests/`.
  - Implement core configuration (`core/config.py`), logging (`core/logging.py`), and error handling (`core/errors.py`).
  - Setup SSRF protection and safe networking utilities (`core/security.py`).
- **Dependencies:** Phase 0.
- **Acceptance Criteria:** Modular package layout with passing baseline imports and config validation.

### Phase 2: Database Schema & Deduplication Engine (Phase 7 unified foundation)
- **Tasks:**
  - Implement normalized SQLite models using SQLAlchemy: `Business`, `BusinessWebsite`, `Source`, `EvidenceRecord`, `WebsiteAnalysis`, `LeadScore`, `ContactChannel`, `OutreachDraft`, `SuppressionRecord`, `ImportJob`, `AuditEvent`.
  - Build robust deduplication engine (domain normalization, company name fuzzy/exact match, registry/identifier match).
  - Implement audit logging and transactional safety.
- **Dependencies:** Phase 1.
- **Acceptance Criteria:** Schema migrations/initialization, CRUD operations, deduplication tests passing without data loss.

### Phase 3: Data Connectors & Import Engine
- **Tasks:**
  - CSV/Excel generic importer with column mapping, data validation, and rejected-row reporting.
  - OpenStreetMap (Overpass API / local extract) connector with configurable categories (offices, craft, trade, services, retail, dining) and regional bounding box/city filtering.
  - Extensible Directory Connector framework with legal terms verification flag and attribution tracking.
- **Dependencies:** Phase 2.
- **Acceptance Criteria:** Successfully parses CSV/Excel and OSM datasets, detects duplicates, logs source attribution, respects rate limits.

### Phase 4: Business Verification & Conservative Crawler
- **Tasks:**
  - Domain normalization and URL validation.
  - Safe HTTP crawler with SSRF prevention, DNS resolution check, robots.txt compliance, timeout (10s), max size (2MB).
  - Extract metadata: HTTP status, title, meta description, likely subpages (contact, about, services, booking).
  - Extract publicly listed official business contact channels (email, phone, contact forms, social links) without harvesting personal addresses.
- **Dependencies:** Phase 2, Phase 3.
- **Acceptance Criteria:** Accurately classifies live, broken, redirected, or blocked websites with complete audit timestamps.

### Phase 5: Observable Website Opportunity Analysis Engine
- **Tasks:**
  - Website Modernization / Redesign Opportunities: Missing mobile viewport, slow/broken pages, missing title/description, outdated copyright/tech hints.
  - AI Chatbot & Customer Support Opportunities: Absence of self-service widget/FAQ, manual inquiry bottlenecks.
  - Online Booking & Workflow Automation Opportunities: Contact form instead of direct scheduling, manual quote requests for service businesses.
  - AI Voice/Calling Agent Candidate Opportunities: High-friction phone inquiry requirements, after-hours booking absence.
  - Evidence recording: Every finding must include `category`, `evidence_url`, `explanation`, `confidence`, and `verification_status`.
- **Dependencies:** Phase 4.
- **Acceptance Criteria:** Accurately produces evidence records on mock pages and real sites without fabricating defects.

### Phase 6: Lead Scoring & Qualification System
- **Tasks:**
  - Multi-dimensional scoring formula (0–100 total):
    1. Business Legitimacy (0–20 pts)
    2. Relevance to XENITH Services (0–20 pts)
    3. Observable Technology Opportunity (0–25 pts)
    4. Business Contact Channel Availability (0–15 pts)
    5. Evidence Quality & Recency (0–20 pts)
  - Configurable weights via UI/config.
  - Score breakdown explanation and manual review/override capabilities with audit log.
- **Dependencies:** Phase 5.
- **Acceptance Criteria:** Deterministic scoring with full breakdown; unverified records capped; tests covering edge cases.

### Phase 7: Compliance, Governance & Suppression Controls
- **Tasks:**
  - Global Suppression List (domain, email, phone, business name) with reason and timestamp.
  - Do-Not-Contact enforcement during discovery, import, scoring, and outreach export.
  - Jurisdictional compliance guide and warning banners (CAN-SPAM / TCPA for US, CASL for Canada, Spam Act 2003 for Australia, UAE TDRA regulations).
  - Data retention, export, and record deletion (right to be forgotten) workflows.
- **Dependencies:** Phase 2, Phase 6.
- **Acceptance Criteria:** Blocked entities never appear in outreach queue; suppression survives subsequent imports.

### Phase 8: Outreach Draft Generator
- **Tasks:**
  - Multi-service personalized templates: Website Redesign, Custom App, AI Chatbot, Workflow Automation, AI Calling Agent, CRM Integration.
  - Template engine combining business name, category, specific verified observation, value proposition, and professional CTA.
  - Human review interface with edit, approve, reject, and export actions.
- **Dependencies:** Phase 6, Phase 7.
- **Acceptance Criteria:** High-converting, non-spammy, truthful drafts generated with clear evidence references.

### Phase 9: Optional Local AI Integration (Ollama / Local LLM)
- **Tasks:**
  - Local LLM connector (`core/ai_client.py`) supporting Ollama (e.g., Llama 3, Mistral, Qwen) or local OpenAI-compatible endpoint.
  - Graceful fallback: complete system operational when AI is offline or uninstalled.
  - Prompt templates for summarizing evidence, refining outreach copy, and explaining scores.
- **Dependencies:** Phase 8.
- **Acceptance Criteria:** Works seamlessly with or without local AI; no crashes when Ollama is inactive.

### Phase 10: Professional Streamlit User Interface
- **Tasks:**
  - Branded XENITH Solutions UI (modern dark/light aesthetic, responsive tabs, clean typography).
  - 13 comprehensive views:
    1. Overview Dashboard (KPIs, opportunity pipeline, country/category distribution)
    2. Lead Discovery & OSM Search
    3. CSV/Excel File Importer
    4. Lead Database & Advanced Filter
    5. Website Opportunity Analyzer
    6. Lead Scoring & Weight Configurator
    7. Lead Detail & Evidence Inspector
    8. Outreach Drafts & Editor
    9. Campaign & Outreach Status Tracker
    10. Do-Not-Contact & Suppression Manager
    11. Data Source Permissions & Governance
    12. Export & Reporting (CSV/Excel)
    13. System Settings & Diagnostics
- **Dependencies:** Phases 1–9.
- **Acceptance Criteria:** Intuitive, responsive dashboard reflecting live database data with 0 hardcoded metrics.

### Phase 11: Testing, Security & Verification
- **Tasks:**
  - Comprehensive Pytest suite: unit tests, mock website crawler tests, SSRF prevention tests, scoring tests, suppression tests, export tests.
  - Security audit: safe URL parsing, loopback prohibition, input sanitization.
- **Dependencies:** Phases 1–10.
- **Acceptance Criteria:** 100% passing test suite across all modules.

### Phase 12: Documentation, Packaging & Delivery
- **Tasks:**
  - `README.md`, `requirements.txt`, `.env.example`, `.gitignore`.
  - Windows launcher `run.bat` and CLI runner.
  - Comprehensive documentation in `docs/`.
  - Final operational verification.
- **Dependencies:** Phase 11.
- **Acceptance Criteria:** Clean, ready-to-run installation verified on Windows 11.
