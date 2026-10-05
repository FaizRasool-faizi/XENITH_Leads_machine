# XENITH Lead Generator — Testing Strategy

## 1. Testing Philosophy
The application requires high reliability across diverse inputs, network conditions, and data formats. Automated tests must execute locally and deterministically **without performing live, uncontrolled internet crawling during test suites**.

## 2. Test Pyramid & Scope

### 2.1 Unit Tests
- **Security & SSRF (`tests/test_security.py`):**
  - Verification of IPv4/IPv6 private ranges (e.g. `127.0.0.1`, `10.0.0.1`, `192.168.1.1`, `169.254.169.254`, `::1`).
  - Safe redirect validation.
  - Domain normalization rules.
- **Deduplication Engine (`tests/test_deduplication.py`):**
  - Exact match vs normalized domain vs fuzzy business name matching.
  - Conflict resolution and evidence preservation.
- **Lead Scoring Engine (`tests/test_scoring.py`):**
  - Boundary scores (0, 50, 100).
  - Missing field penalties.
  - Evidence degradation rules.
  - Weight configuration adjustments.
- **Suppression & DNC Engine (`tests/test_suppression.py`):**
  - Matching across normalized domain, phone, email, and business name.
  - Quarantine of incoming imports matching suppressed records.
- **Outreach Draft Generation (`tests/test_outreach.py`):**
  - Service-specific template rendering (web redesign, chatbot, calling agent, etc.).
  - Substitution of factual observations without hallucinations.

### 2.2 Integration Tests
- **Mock Web Crawler (`tests/test_crawler.py`):**
  - Using mocked HTTP responses and local test HTML fixtures.
  - Handling of HTTP 200, 301/302 redirects, 404, 500, and timeout conditions.
  - Extraction of page titles, meta descriptions, and business contact links.
  - Robots.txt parser and policy enforcement.
- **Observable Opportunity Analyzer (`tests/test_analyzer.py`):**
  - Identification of missing viewport tag (mobile responsiveness signal).
  - Detection of contact forms lacking modern booking mechanisms.
  - Evaluation of FAQ presence for AI chatbot opportunity scoring.
- **Data Ingestion & Importers (`tests/test_importer.py`):**
  - CSV and Excel parsing with valid and corrupted structures.
  - OpenStreetMap Overpass JSON parser with missing attributes.

### 2.3 Acceptance Criteria
- All tests must pass cleanly under `pytest`.
- Zero live outbound network requests required during test execution.
- Clear error messages and full audit logs on edge-case failures.
