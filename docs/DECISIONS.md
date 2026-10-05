# XENITH Lead Generator — Architectural & Design Decisions (ADR)

## ADR-001: Local-First Python Architecture with SQLite
- **Context:** The application must run reliably on a local Windows 11 workstation without requiring continuous cloud servers, VPS fees, or hosted automation orchestrators (e.g., hosted n8n).
- **Decision:** Use Python 3.14 with an embedded SQLite database managed via SQLAlchemy.
- **Consequences:** Zero infrastructure operational costs; full data privacy; local backups; fast zero-latency queries.

## ADR-002: Streamlit for Interactive Dashboard UI
- **Context:** The product requires a multi-view dashboard for non-technical users featuring metrics, discovery maps/filters, evidence inspection, scoring adjustment, and outreach drafting.
- **Decision:** Build a Streamlit application with custom XENITH brand styling, dark/light mode responsiveness, and distinct navigation tabs.
- **Consequences:** Fast iterative UI development, reactive state management, seamless integration with Python data processing pipelines.

## ADR-003: Conservative & Ethical Crawling Policy
- **Context:** Automated prospecting easily risks abuse, server overload, terms violations, or security breaches (such as Server-Side Request Forgery - SSRF).
- **Decision:**
  1. Strict SSRF filter blocking private/loopback/link-local IPv4 & IPv6 addresses.
  2. Mandatory robots.txt verification; default to conservative skip if uncertain.
  3. Strict rate limiting (1 request per second per target domain).
  4. Content-length capped at 2 MB; timeout strictly enforced at 10 seconds.
  5. Never harvest residential addresses or personal unlisted numbers.
- **Consequences:** Safe, responsible, legally defensive data collection.

## ADR-004: Factual & Evidence-Grounded Opportunity Scoring
- **Context:** Generic lead scoring frequently relies on hallucinated assumptions (e.g. "needs automation because revenue is down").
- **Decision:** Every single point in the scoring model is mapped to a tangible, timestamped `EvidenceRecord` (e.g., HTTP response code, lack of mobile viewport meta tag, presence of a plain email vs interactive booking system).
- **Consequences:** High-trust, verifiable intelligence that salespeople can stand behind during outreach.

## ADR-005: Suppression List Precedence
- **Context:** Leads that opt out or businesses placed on a Do-Not-Contact (DNC) list must never be re-introduced by subsequent imports or discovery passes.
- **Decision:** The `suppression_records` table acts as a global pre-filter across normalized domain, email, phone, and company name. Subsequent imports matching a suppressed entity are flagged and quarantined.
- **Consequences:** Reliable compliance with international privacy rules (CAN-SPAM, CASL, Australian Spam Act, UAE regulations).

## ADR-006: Optional Local AI (Ollama) with Hard Fallback
- **Context:** High-quality outreach drafts and summaries can benefit from LLMs, but paid API keys should never be mandatory, and user privacy must be protected.
- **Decision:** Implement an adapter for local Ollama models (e.g. Llama 3, Mistral, Qwen) using a standardized local HTTP client, with a deterministic rule-based template engine as the default fallback.
- **Consequences:** The application is 100% operational offline without any AI model installed.
