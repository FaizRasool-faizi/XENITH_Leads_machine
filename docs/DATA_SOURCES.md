# XENITH Lead Generator — Data Sources & Attribution

## 1. Supported Discovery Sources

### 1.1 OpenStreetMap (Overpass API)
- **Official URL:** `https://www.openstreetmap.org`
- **Access Protocol:** Overpass QL via public endpoints (`https://overpass-api.de/api/interpreter`, `https://lz4.overpass-api.de/api/interpreter`).
- **License:** Open Database License (ODbL) 1.0.
- **Permitted Use:** Commercial use permitted with proper attribution.
- **Mandatory Attribution Statement:**  
  *© OpenStreetMap contributors. Data available under the Open Database License (ODbL).*
- **Fields Extracted:** Registered business name, category tag (amenity, office, craft, healthcare, shop), city, state, country, public website URL, public telephone number, public email.
- **Constraints & Etiquette:**
  - Rate limiting enforced (minimum 1 second delay between consecutive requests).
  - Conservative timeout set to 30 seconds.
  - Queries restricted to specific municipal boundaries or bounding boxes.

### 1.2 Manual CSV & Excel Importer
- **Format:** Standard RFC 4180 CSV, Microsoft Excel (.xlsx, .xls).
- **Access Method:** Local file upload via Streamlit UI.
- **Intended Use:** Ingestion of verified, lawfully acquired business lead datasets (e.g., chamber of commerce directories, trade show exhibitor lists, public registry exports).
- **Validation Pipeline:**
  - Header detection across common variants (`Company`, `Organization`, `Firm`, `Website`, `Phone`, `Email`, etc.).
  - Rejection of invalid records (missing name).
  - Pre-import suppression screening against global DNC registry.
  - Multi-factor entity deduplication.

### 1.3 Extensible Commercial Directory Connector
- **Format:** Pluggable connector class (`connectors/directory_connector.py`).
- **Policy:** Explicit verification required (`terms_reviewed=True`, `collection_permitted=True`) before automated queries can be scheduled.
- **Manual Alternative:** When automated collection terms are ambiguous, data should be downloaded manually and ingested via the lawful CSV importer.

---

## 2. Crawled Business Websites
- **Target Pages:** Public root homepage, `/contact`, `/about`, `/services`, `/booking`.
- **Policy:**
  - Strict SSRF protection (loopback, RFC 1918 private subnets, cloud metadata IPs rejected).
  - Robots.txt parser checks permissions before HTTP request.
  - Max response size capped at 2 MB.
  - Respects HTTP 403 / 401 with conservative skip.
