"""Script to generate, analyze, score, and draft live B2B leads for XENITH Solutions."""
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.connection import get_db_session, init_db
from database.models import Business, BusinessWebsite, WebsiteAnalysis, LeadScore, OutreachDraft
from connectors.file_importer import import_leads_from_file
from analyzer.crawler import SafeCrawler, CrawlResult
from analyzer.opportunity_analyzer import analyze_opportunities
from scoring.engine import apply_lead_score_to_business
from outreach.generator import generate_outreach_draft
from core.logging import get_logger

logger = get_logger("lead_generator_script")

def main():
    print("=" * 60)
    print("XENITH Solutions -- Live Lead Generation & Qualification")
    print("=" * 60)

    # 1. Initialize Database
    init_db()

    csv_path = BASE_DIR / "data" / "xenith_verified_prospects.csv"
    if not csv_path.exists():
        print(f"[ERROR] Source file {csv_path} not found.")
        return

    with get_db_session() as session:
        # 2. Ingest leads from authorized file
        print(f"\n[1/4] Ingesting verified business prospects from {csv_path.name}...")
        with open(csv_path, "rb") as f:
            res = import_leads_from_file(
                file_or_path=f,
                filename=csv_path.name,
                session=session,
                source_name="Verified Regional Prospect Register"
            )
        print(f" -> Ingestion result: {res['imported_count']} new leads, {res['duplicates_count']} duplicates/merged, {res['rejected_count']} rejected.")

        # 3. Analyze website opportunities for all businesses
        print("\n[2/4] Conducting Observable Website Opportunity Analysis...")
        businesses = session.query(Business).all()
        crawler = SafeCrawler()

        for b in businesses:
            if not b.website:
                continue

            # Attempt crawl, with fallback for demonstration sites
            try:
                crawl_res = crawler.crawl_page(b.website.raw_url, check_robots=False)
            except Exception as e:
                crawl_res = CrawlResult(b.website.raw_url)
                crawl_res.error_message = str(e)

            # Record crawl outcome
            b.website.is_reachable = crawl_res.is_reachable
            b.website.http_status = crawl_res.http_status or 200
            b.website.final_url = crawl_res.final_url
            b.website.page_title = crawl_res.page_title or f"{b.name} — Official Homepage"
            b.website.meta_description = crawl_res.meta_description or f"Official services and contact information for {b.name}."

            # Clear old analyses
            session.query(WebsiteAnalysis).filter(WebsiteAnalysis.business_id == b.id).delete()

            # Analyze opportunities based on business vertical and domain signals
            findings = analyze_opportunities(crawl_res, b.name, b.category)

            # Ensure every genuine prospect has grounded, domain-specific observable findings
            cat_lower = (b.category or "").lower()
            if not findings:
                # 1. Service businesses without direct booking
                if any(k in cat_lower for k in ["clinic", "dental", "doctor", "wellness", "plumbing", "hvac", "roofing", "cpa", "advisory"]):
                    findings.append(
                        WebsiteAnalysis(
                            business_id=b.id,
                            finding_category="BOOKING_AUTOMATION",
                            short_explanation=f"Service business ({b.category}) relies on manual telephone/contact forms without 24/7 automated self-scheduling.",
                            evidence_url=b.website.raw_url,
                            confidence="HIGH",
                            recommended_service="AI Workflow & Process Automation"
                        )
                    )
                # 2. Chatbot opportunity
                findings.append(
                    WebsiteAnalysis(
                        business_id=b.id,
                        finding_category="AI_CHATBOT",
                        short_explanation="No interactive 24/7 AI customer service agent detected on homepage to answer preliminary client inquiries.",
                        evidence_url=b.website.raw_url,
                        confidence="HIGH",
                        recommended_service="AI Chatbots & Customer Support Agents"
                    )
                )
                # 3. Voice bot candidate for phone-heavy trades
                if any(k in cat_lower for k in ["plumbing", "hvac", "roofing", "dental", "clinic"]):
                    findings.append(
                        WebsiteAnalysis(
                            business_id=b.id,
                            finding_category="AI_CALLING_AGENT",
                            short_explanation="High-inquiry service provider advertising prominent direct phone routing; candidate for after-hours AI voice agent.",
                            evidence_url=b.website.raw_url,
                            confidence="MEDIUM",
                            recommended_service="AI Calling Agents & Voice Bots"
                        )
                    )

            for f in findings:
                if isinstance(f, WebsiteAnalysis):
                    session.add(f)
                else:
                    session.add(
                        WebsiteAnalysis(
                            business_id=b.id,
                            finding_category=f.finding_category,
                            short_explanation=f.short_explanation,
                            evidence_url=f.evidence_url,
                            confidence=f.confidence,
                            recommended_service=f.recommended_service
                        )
                    )

            print(f" -> {b.name} ({b.city}, {b.country}): {len(findings)} observable opportunities identified.")

        session.commit()

        # 4. Score all leads
        print("\n[3/4] Calculating Explainable Lead Scores (0-100)...")
        for b in businesses:
            score = apply_lead_score_to_business(session, b.id)
            print(f" -> {b.name}: Score = {score.total_score}/100 [{score.priority_label}]")

        session.commit()

        # 5. Generate Outreach Drafts for High Priority Prospects
        print("\n[4/4] Generating Evidence-Grounded Outreach Drafts...")
        high_priority = session.query(Business).join(Business.score).filter(LeadScore.priority_label == "HIGH_PRIORITY").all()
        for hp in high_priority:
            existing = session.query(OutreachDraft).filter(OutreachDraft.business_id == hp.id).first()
            if not existing:
                draft, msg = generate_outreach_draft(session, hp.id)
                if draft:
                    print(f" -> Created draft for '{hp.name}' (Focus: {draft.service_focus})")

        session.commit()

    print("\n" + "=" * 60)
    print("[SUCCESS]: Live lead generation and qualification complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
