# XENITH Lead Generator — Compliance & Data Governance Guide

## 1. Compliance Philosophy
XENITH Solutions is committed to ethical, transparent, and legally defensible B2B prospecting. The system does not harvest private individual data, residential addresses, or personal phone numbers. It indexes observable corporate and commercial characteristics to identify genuine technological opportunities.

---

## 2. Global Suppression & Do-Not-Contact (DNC)

### 2.1 Enforcement Mechanism
- The `suppression_records` table acts as a global blocker.
- Matching occurs across:
  - Normalized Domain (e.g. `badsite.com` matches `http://www.badsite.com/contact`)
  - Normalized Email (`clean.user@domain.com`)
  - Normalized Phone Digits (`5550199`)
  - Normalized Company Name (`acme corporation` matches `Acme Corp LLC`)
- Suppressed entities are:
  - Rejected immediately during CSV/Excel import.
  - Excluded from OpenStreetMap ingestion.
  - Blocked from outreach draft generation.
  - Excluded from export lists.
  - Preservation guarantee: Suppression records survive all deduplication and re-import passes.

### 2.2 Right to be Forgotten (GDPR / CCPA / Privacy Act)
- Any prospect requesting data removal can be permanently purged via the UI ("Suppression & DNC Controls" -> "Right to be Forgotten").
- Purging permanently deletes the business, website, contact channels, analysis findings, and outreach drafts.

---

## 3. Jurisdictional Regulations & Best Practices

### 3.1 United States
- **Governing Law:** CAN-SPAM Act (15 U.S.C. 7701 et seq.) & TCPA (47 U.S.C. 227).
- **Requirements:**
  1. No misleading header information or deceptive subject lines.
  2. Clear identification of message as an advertisement or consultative inquiry.
  3. Valid physical postal address of XENITH Solutions.
  4. Working opt-out mechanism honored within 10 business days.
  5. Telemarketing / AI voice calling strictly prohibited without prior express consent.

### 3.2 Canada
- **Governing Law:** Canada's Anti-Spam Legislation (CASL).
- **Requirements:**
  1. Conspicuously published business emails qualify for implied consent ONLY if the outreach message is directly relevant to the recipient's business role AND no statement on the website indicates they do not wish to receive unsolicited electronic messages.
  2. Full sender identification and functional unsubscribe mechanism required.

### 3.3 Australia
- **Governing Law:** Spam Act 2003 (Cth) & Do Not Call Register Act 2006.
- **Requirements:**
  1. Inferred consent exists for conspicuously published business addresses relevant to business capacity without a "no spam" notice.
  2. Accurate sender identity and 30-day working unsubscribe link.

### 3.4 United Arab Emirates & Gulf Markets
- **Governing Law:** TDRA Unsolicited Electronic Communications Framework & Cabinet Resolution No. 56 of 2024.
- **Requirements:**
  1. Telemarketing cold calls strictly restricted to licensed entities during 9:00 AM – 6:00 PM.
  2. Prior business relationship or explicit consent required for commercial messages.
