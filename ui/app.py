"""Main Streamlit Dashboard for XENITH Solutions B2B Lead Generator."""
import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from datetime import datetime

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.config import settings, ScoringWeights
from core.logging import get_logger
from core.ai_client import LocalAIClient
from database.connection import init_db, get_db_session
from database.models import (
    Business, BusinessWebsite, ContactChannel, WebsiteAnalysis,
    LeadScore, OutreachDraft, SuppressionRecord, Source, ImportJob, AuditEvent
)
from database.repository import (
    get_all_businesses, get_business_by_id, get_database_metrics,
    upsert_business, is_suppressed
)
from connectors.osm_connector import OSMConnector, OSM_CATEGORY_TAGS
from connectors.file_importer import import_leads_from_file
from analyzer.crawler import SafeCrawler
from analyzer.contact_extractor import extract_business_contacts
from analyzer.opportunity_analyzer import analyze_opportunities
from scoring.engine import calculate_lead_score, apply_lead_score_to_business
from scoring.weights import ScoringProfile
from outreach.generator import generate_outreach_draft, update_draft_status
from compliance.suppression import add_suppression_entry, delete_business_data
from compliance.policies import get_market_policy, JURISDICTION_POLICIES
from ui.styles import CUSTOM_CSS, render_xenith_header
from ui.export_service import export_leads_to_dataframe, export_leads_to_excel, export_leads_to_csv

logger = get_logger("ui")

# Page config
st.set_page_config(
    page_title="XENITH Solutions — B2B Lead Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize database schema if not present
init_db()


def main():
    # Render branded header
    st.markdown(render_xenith_header(), unsafe_allow_html=True)

    # Sidebar Navigation
    st.sidebar.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
    st.sidebar.title("Navigation")
    
    sections = [
        "1. Overview Dashboard",
        "2. Lead Discovery (OSM)",
        "3. File Importer (CSV/Excel)",
        "4. Search Configuration",
        "5. Lead Database & Search",
        "6. Website Opportunity Analysis",
        "7. Lead Scoring & Weights",
        "8. Lead Detail & Evidence",
        "9. Outreach Draft Generator",
        "10. Campaign Tracking",
        "11. Suppression & DNC Controls",
        "12. Data Sources & Governance",
        "13. Export & Reporting",
        "14. Settings & Diagnostics"
    ]
    
    choice = st.sidebar.radio("Go to Section:", sections)

    with get_db_session() as session:
        # -------------------------------------------------------------
        # 1. OVERVIEW DASHBOARD
        # -------------------------------------------------------------
        if choice == "1. Overview Dashboard":
            st.subheader("📊 Executive Overview & Business Metrics")
            metrics = get_database_metrics(session)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Total Discovered</div>
                    <div class="metric-value">{metrics['total_businesses']}</div>
                    <span class="metric-badge badge-cyan">Genuine Records</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Verified Legitimacy</div>
                    <div class="metric-value">{metrics['verified_businesses']}</div>
                    <span class="metric-badge badge-green">Verified Entities</span>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">High Priority Leads</div>
                    <div class="metric-value">{metrics['high_priority_leads']}</div>
                    <span class="metric-badge badge-amber">Score 80-100</span>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Observable Tech Gaps</div>
                    <div class="metric-value">{metrics['total_opportunities']}</div>
                    <span class="metric-badge badge-purple">Service Signals</span>
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.metric("Websites Indexed", f"{metrics['with_website']}")
            with col6:
                st.metric("Contact Channels", f"{metrics['with_contacts']}")
            with col7:
                st.metric("Approved Outreach", f"{metrics['approved_drafts']} / {metrics['total_drafts']}")
            with col8:
                st.metric("Suppressed / DNC", f"{metrics['suppressed_records']}")

            st.divider()

            # Detailed Breakdown Charts
            c_left, c_right = st.columns(2)
            businesses = session.query(Business).all()
            
            with c_left:
                st.markdown("#### 🌍 Distribution by Target Country")
                if businesses:
                    countries = [b.country or "Unspecified" for b in businesses]
                    df_country = pd.DataFrame(countries, columns=["Country"]).value_counts().reset_index()
                    df_country.columns = ["Country", "Count"]
                    st.dataframe(df_country, use_container_width=True, hide_index=True)
                else:
                    st.info("No business records in database yet. Use 'Lead Discovery' or 'File Importer' to begin.")

            with c_right:
                st.markdown("#### 💼 Top Business Categories")
                if businesses:
                    categories = [b.category or "Commercial" for b in businesses]
                    df_cat = pd.DataFrame(categories, columns=["Category"]).value_counts().head(10).reset_index()
                    df_cat.columns = ["Category", "Count"]
                    st.dataframe(df_cat, use_container_width=True, hide_index=True)
                else:
                    st.info("Categories will populate automatically as businesses are indexed.")

            st.divider()
            st.markdown("#### 💰 Research Cost & Efficiency")
            st.success(
                "⚡ **Cost Tracking:** $0.00 Spent | 100% Free & Open Stack (OpenStreetMap, SQLite, Python, BeautifulSoup, Local Inference)."
            )

        # -------------------------------------------------------------
        # 2. LEAD DISCOVERY (OSM)
        # -------------------------------------------------------------
        elif choice == "2. Lead Discovery (OSM)":
            st.subheader("🗺️ OpenStreetMap Commercial Discovery")
            st.markdown(
                "Discover genuine registered commercial businesses using OpenStreetMap Overpass API under ODbL terms."
            )

            col_city, col_country, col_limit = st.columns([2, 2, 1])
            with col_city:
                search_city = st.text_input("City / Municipality", value="Austin")
            with col_country:
                search_country = st.selectbox(
                    "Target Market Country",
                    options=["United States", "Canada", "Australia", "United Arab Emirates", "Saudi Arabia", "Qatar"]
                )
            with col_limit:
                search_limit = st.number_input("Max Results", min_value=5, max_value=200, value=25)

            selected_categories = st.multiselect(
                "Select Business Verticals to Search",
                options=list(OSM_CATEGORY_TAGS.keys()),
                default=["Healthcare & Medical", "Legal & Financial Services", "Consulting & IT Companies"]
            )

            if st.button("🚀 Run Discovery Query", type="primary"):
                with st.spinner(f"Querying OpenStreetMap for commercial entities in {search_city}, {search_country}..."):
                    connector = OSMConnector()
                    leads = connector.search(
                        city=search_city,
                        country=search_country,
                        categories=selected_categories,
                        limit=search_limit
                    )
                    
                    if not leads:
                        st.warning(f"No results returned for {search_city}. Check city spelling or select broader categories.")
                    else:
                        st.success(f"Discovered {len(leads)} genuine businesses. Ingesting with deduplication and suppression checks...")
                        ingested = 0
                        duplicates = 0
                        suppressed_count = 0

                        for lead in leads:
                            biz, is_new, msg = upsert_business(
                                session=session,
                                name=lead.name,
                                website_url=lead.website_url,
                                category=lead.category,
                                city=lead.city,
                                state=lead.state,
                                country=lead.country,
                                phone=lead.phone,
                                email=lead.email,
                                source_name="OpenStreetMap"
                            )
                            if not biz and "SUPPRESSED" in msg:
                                suppressed_count += 1
                            elif is_new:
                                ingested += 1
                            else:
                                duplicates += 1

                        session.commit()
                        st.success(
                            f"✅ Ingestion Complete: {ingested} New Leads Added, {duplicates} Duplicates Enriched, {suppressed_count} Suppressed."
                        )

        # -------------------------------------------------------------
        # 3. FILE IMPORTER (CSV/EXCEL)
        # -------------------------------------------------------------
        elif choice == "3. File Importer (CSV/Excel)":
            st.subheader("📁 Lawful Business Data File Importer")
            st.markdown(
                "Upload a CSV or Excel (`.xlsx`) file containing business records collected through lawful, authorized means. "
                "The engine automatically matches headers (Name, Website, Category, City, Phone, Email), validates inputs, "
                "prevents duplicates, and flags suppressed entities."
            )

            uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])
            source_label = st.text_input("Source Attribution Name", value="Manual CSV/Excel Import")

            if uploaded_file and st.button("📥 Validate & Ingest File", type="primary"):
                with st.spinner("Processing file..."):
                    result = import_leads_from_file(
                        file_or_path=uploaded_file,
                        filename=uploaded_file.name,
                        session=session,
                        source_name=source_label
                    )

                    if result["success"]:
                        st.success(
                            f"✅ Processed {result['total_rows']} rows: "
                            f"{result['imported_count']} new businesses ingested, "
                            f"{result['duplicates_count']} duplicates merged, "
                            f"{result['rejected_count']} rejected."
                        )
                        if result["rejected_rows"]:
                            st.warning("Rejected Rows Audit (First 50):")
                            st.dataframe(pd.DataFrame(result["rejected_rows"]))
                    else:
                        st.error(f"Import Failed: {result.get('error')}")

        # -------------------------------------------------------------
        # 4. SEARCH CONFIGURATION
        # -------------------------------------------------------------
        elif choice == "4. Search Configuration":
            st.subheader("⚙️ Discovery & Crawling Parameters")
            st.markdown("Configure global parameters for conservative discovery and network crawling.")

            c1, c2 = st.columns(2)
            with c1:
                st.write("**Crawler Safety Constraints**")
                st.write(f"• Request Timeout: `{settings.REQUEST_TIMEOUT_SECONDS}s`")
                st.write(f"• Max Response Size: `{settings.MAX_RESPONSE_BYTES // (1024*1024)} MB`")
                st.write(f"• Domain Rate Delay: `{settings.RATE_LIMIT_SECONDS}s`")
                st.write(f"• SSRF Protection: `Active (RFC 1918 / Loopback / Link-Local prohibited)`")
                st.write(f"• robots.txt Adherence: `Strict (Conservative Default)`")

            with c2:
                st.write("**Supported Target Markets**")
                for market in settings.TARGET_MARKETS:
                    st.write(f"✓ {market}")

        # -------------------------------------------------------------
        # 5. LEAD DATABASE & SEARCH
        # -------------------------------------------------------------
        elif choice == "5. Lead Database & Search":
            st.subheader("🗄️ Lead Database Explorer")
            
            c_search, c_ctry, c_prio = st.columns([3, 2, 2])
            with c_search:
                q = st.text_input("🔍 Search Company, City, or Category", placeholder="e.g. Dental, Plumbing, Austin")
            with c_ctry:
                ctry = st.selectbox("Filter Country", ["All"] + settings.TARGET_MARKETS)
            with c_prio:
                prio = st.selectbox("Priority Tier", ["All", "HIGH_PRIORITY", "POTENTIAL_PROSPECT", "NEEDS_RESEARCH"])

            leads = get_all_businesses(
                session,
                search_query=q if q else None,
                country=None if ctry == "All" else ctry,
                priority=None if prio == "All" else prio,
                limit=100
            )

            st.write(f"Showing **{len(leads)}** records (max 100 per view):")

            if leads:
                table_data = []
                for b in leads:
                    score_val = b.score.total_score if b.score else 0
                    prio_val = b.score.priority_label if b.score else "NEEDS_RESEARCH"
                    has_web = "Yes" if b.website else "No"
                    opp_count = len(b.analyses) if b.analyses else 0
                    contact_count = len(b.contacts) if b.contacts else 0
                    
                    table_data.append({
                        "ID": b.id,
                        "Company Name": b.name,
                        "Category": b.category or "—",
                        "City": b.city or "—",
                        "Country": b.country or "—",
                        "Website": b.website.raw_url if b.website else "—",
                        "Score": score_val,
                        "Priority": prio_val,
                        "Opportunities": opp_count,
                        "Contacts": contact_count,
                        "Status": b.verification_status
                    })
                st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
            else:
                st.info("No matching business records found.")

        # -------------------------------------------------------------
        # 6. WEBSITE OPPORTUNITY ANALYSIS
        # -------------------------------------------------------------
        elif choice == "6. Website Opportunity Analysis":
            st.subheader("🔬 Website Opportunity Analysis Engine")
            st.markdown(
                "Safely crawl and analyze client websites for verifiable gaps: missing mobile viewport, lack of modern booking tools, "
                "absence of AI customer chat, SSL issues, and phone-first inquiry bottlenecks."
            )

            tab_single, tab_batch = st.tabs(["Analyze Single Lead", "Batch Analyze Uninspected Leads"])

            with tab_single:
                biz_list = session.query(Business).filter(Business.website != None).limit(50).all()
                if not biz_list:
                    st.warning("No businesses with websites found. Ingest leads with websites first.")
                else:
                    biz_choice = st.selectbox(
                        "Select Lead to Inspect:",
                        options=biz_list,
                        format_func=lambda b: f"ID {b.id}: {b.name} ({b.website.raw_url if b.website else 'No URL'})"
                    )

                    if st.button("🔍 Run Safe Website Inspection", type="primary"):
                        with st.spinner(f"Crawling {biz_choice.website.raw_url} safely..."):
                            crawler = SafeCrawler()
                            crawl_res = crawler.crawl_page(biz_choice.website.raw_url)

                            # Update website record
                            biz_choice.website.http_status = crawl_res.http_status
                            biz_choice.website.is_reachable = crawl_res.is_reachable
                            biz_choice.website.final_url = crawl_res.final_url
                            biz_choice.website.has_ssl = crawl_res.has_ssl
                            biz_choice.website.page_title = crawl_res.page_title
                            biz_choice.website.meta_description = crawl_res.meta_description
                            biz_choice.website.last_crawled_at = datetime.utcnow()
                            biz_choice.website.error_message = crawl_res.error_message
                            if crawl_res.subpages_found:
                                biz_choice.website.subpages_found = ", ".join(crawl_res.subpages_found)

                            # Extract contact channels
                            if crawl_res.soup:
                                extracted_contacts = extract_business_contacts(crawl_res.soup, crawl_res.final_url)
                                for ec in extracted_contacts:
                                    has_c = any(c.channel_type == ec.channel_type and c.value == ec.value for c in biz_choice.contacts)
                                    if not has_c:
                                        biz_choice.contacts.append(
                                            ContactChannel(
                                                business_id=biz_choice.id,
                                                channel_type=ec.channel_type,
                                                value=ec.value,
                                                source_url=ec.source_url,
                                                verified=True,
                                                last_verified_at=datetime.utcnow()
                                            )
                                        )

                            # Analyze opportunities
                            findings = analyze_opportunities(crawl_res, biz_choice.name, biz_choice.category)
                            # Remove old analyses
                            session.query(WebsiteAnalysis).filter(WebsiteAnalysis.business_id == biz_choice.id).delete()
                            for f in findings:
                                session.add(
                                    WebsiteAnalysis(
                                        business_id=biz_choice.id,
                                        finding_category=f.finding_category,
                                        short_explanation=f.short_explanation,
                                        evidence_url=f.evidence_url,
                                        confidence=f.confidence,
                                        recommended_service=f.recommended_service
                                    )
                                )

                            # Recalculate score
                            apply_lead_score_to_business(session, biz_choice.id)
                            session.commit()

                            st.success(f"Analysis Complete! Discovered {len(findings)} observable opportunities.")
                            
                            c_res1, c_res2 = st.columns(2)
                            with c_res1:
                                st.write("**Site Inspection Metadata:**")
                                st.write(f"• HTTP Status: `{crawl_res.http_status}`")
                                st.write(f"• SSL Encryption: `{'Yes' if crawl_res.has_ssl else 'No'}`")
                                st.write(f"• Title Tag: `{crawl_res.page_title or 'Missing'}`")
                                st.write(f"• Meta Description: `{crawl_res.meta_description or 'Missing'}`")
                                st.write(f"• Subpages Found: `{len(crawl_res.subpages_found)}`")

                            with c_res2:
                                st.write("**Observable Opportunity Signals:**")
                                for f in findings:
                                    st.markdown(
                                        f"<div class='evidence-pill'><b>[{f.finding_category}]</b> {f.short_explanation}<br>"
                                        f"<i>Recommended: {f.recommended_service}</i></div>",
                                        unsafe_allow_html=True
                                    )

            with tab_batch:
                uninspected = session.query(Business).filter(Business.website != None).all()
                uninspected_to_run = [b for b in uninspected if not b.website.last_crawled_at]
                st.write(f"Found **{len(uninspected_to_run)}** leads with websites awaiting initial inspection.")
                
                batch_limit = st.slider("Batch Size", min_value=1, max_value=20, value=5)
                if st.button("⚡ Start Batch Inspection", type="primary"):
                    progress = st.progress(0)
                    crawler = SafeCrawler()
                    for idx, b in enumerate(uninspected_to_run[:batch_limit]):
                        st.write(f"Analyzing [{idx+1}/{batch_limit}]: {b.name} ({b.website.raw_url})...")
                        res = crawler.crawl_page(b.website.raw_url)
                        b.website.http_status = res.http_status
                        b.website.is_reachable = res.is_reachable
                        b.website.final_url = res.final_url
                        b.website.has_ssl = res.has_ssl
                        b.website.page_title = res.page_title
                        b.website.meta_description = res.meta_description
                        b.website.last_crawled_at = datetime.utcnow()
                        b.website.error_message = res.error_message

                        findings = analyze_opportunities(res, b.name, b.category)
                        session.query(WebsiteAnalysis).filter(WebsiteAnalysis.business_id == b.id).delete()
                        for f in findings:
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
                        apply_lead_score_to_business(session, b.id)
                        progress.progress((idx + 1) / batch_limit)

                    session.commit()
                    st.success("Batch inspection complete!")

        # -------------------------------------------------------------
        # 7. LEAD SCORING & WEIGHTS
        # -------------------------------------------------------------
        elif choice == "7. Lead Scoring & Weights":
            st.subheader("⚖️ Lead Scoring & Weight Calibration")
            st.markdown(
                "Adjust the multi-dimensional scoring weights. Total score is computed from 0–100 across 5 factual dimensions."
            )

            col_w1, col_w2 = st.columns(2)
            with col_w1:
                w_leg = st.slider("Business Legitimacy Max Score", 0, 40, 20)
                w_rel = st.slider("Relevance to XENITH Services Max Score", 0, 40, 20)
                w_opp = st.slider("Observable Tech Opportunity Max Score", 0, 40, 25)
            with col_w2:
                w_con = st.slider("Business Contact Availability Max Score", 0, 30, 15)
                w_evi = st.slider("Evidence Quality & Recency Max Score", 0, 30, 20)
                th_high = st.slider("High Priority Minimum Threshold", 50, 95, 80)

            profile = ScoringProfile(
                max_legitimacy=w_leg,
                max_relevance=w_rel,
                max_opportunity=w_opp,
                max_contact=w_con,
                max_evidence=w_evi,
                high_priority_min=th_high
            )

            if st.button("🔄 Recalculate Scores for All Businesses in Database", type="primary"):
                with st.spinner("Recalculating scores..."):
                    all_b = session.query(Business).all()
                    for b in all_b:
                        apply_lead_score_to_business(session, b.id, profile)
                    session.commit()
                    st.success(f"Successfully updated lead scores across all {len(all_b)} businesses.")

        # -------------------------------------------------------------
        # 8. LEAD DETAIL & EVIDENCE
        # -------------------------------------------------------------
        elif choice == "8. Lead Detail & Evidence":
            st.subheader("🔍 Deep Evidence & Audit Inspector")
            all_b = session.query(Business).all()
            if not all_b:
                st.info("No business records in database.")
            else:
                sel_b = st.selectbox(
                    "Choose Business to Inspect:",
                    options=all_b,
                    format_func=lambda b: f"#{b.id} — {b.name} ({b.city or 'No City'}, {b.country or 'No Country'})"
                )

                b_full = get_business_by_id(session, sel_b.id)
                
                c_info, c_score = st.columns([2, 1])
                with c_info:
                    st.markdown(f"### {b_full.name}")
                    st.write(f"**Category:** {b_full.category or 'Uncategorized'}")
                    st.write(f"**Location:** {b_full.city or '—'}, {b_full.state or '—'}, {b_full.country or '—'}")
                    st.write(f"**Verification Status:** `{b_full.verification_status}`")
                    st.write(f"**Source Provenance:** {b_full.source.name if b_full.source else 'Manual Import'}")
                    if b_full.website:
                        st.write(f"**Website:** [{b_full.website.raw_url}]({b_full.website.raw_url}) (HTTP {b_full.website.http_status or 'N/A'})")
                        st.write(f"**Page Title:** {b_full.website.page_title or '—'}")
                        st.write(f"**Description:** {b_full.website.meta_description or '—'}")

                with c_score:
                    if b_full.score:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Lead Score</div>
                            <div class="metric-value">{b_full.score.total_score} / 100</div>
                            <span class="metric-badge badge-amber">{b_full.score.priority_label}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write(f"• Legitimacy: `{b_full.score.score_legitimacy}`")
                        st.write(f"• Relevance: `{b_full.score.score_relevance}`")
                        st.write(f"• Opportunity: `{b_full.score.score_opportunity}`")
                        st.write(f"• Contacts: `{b_full.score.score_contact}`")
                        st.write(f"• Evidence: `{b_full.score.score_evidence}`")
                    else:
                        st.info("Lead has not been scored yet.")

                st.divider()

                # Contact Channels
                st.markdown("#### 📞 Verified Official Contact Channels")
                if b_full.contacts:
                    c_rows = [{"Type": c.channel_type, "Value": c.value, "Verified": "Yes" if c.verified else "Unverified", "Source URL": c.source_url or "—"} for c in b_full.contacts]
                    st.dataframe(pd.DataFrame(c_rows), use_container_width=True, hide_index=True)
                else:
                    st.warning("No public business contact channels discovered yet.")

                # Observable Opportunities
                st.markdown("#### 💡 Observable Tech Opportunities")
                if b_full.analyses:
                    for a in b_full.analyses:
                        st.markdown(
                            f"<div class='evidence-pill'><b>[{a.finding_category}]</b> {a.short_explanation} "
                            f"(Evidence: <a href='{a.evidence_url}' target='_blank'>{a.evidence_url}</a>) — "
                            f"<b>Recommended Service:</b> {a.recommended_service}</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No opportunity analysis run on this lead yet.")

                # Score Override Form
                with st.expander("🛠️ Manual Score Override (Human Reviewer)"):
                    new_score = st.number_input("Override Score (0-100)", min_value=0, max_value=100, value=b_full.score.total_score if b_full.score else 50)
                    override_reason = st.text_input("Override Reason", placeholder="e.g. Verified high budget, referral")
                    if st.button("Apply Score Override"):
                        apply_lead_score_to_business(session, b_full.id, override_score=new_score, override_reason=override_reason)
                        st.success(f"Score updated to {new_score} with audit log entry.")

        # -------------------------------------------------------------
        # 9. OUTREACH DRAFT GENERATOR
        # -------------------------------------------------------------
        elif choice == "9. Outreach Draft Generator":
            st.subheader("✉️ Evidence-Grounded Outreach Draft Generator")
            st.markdown(
                "Generate consultative, highly personalized B2B outreach messages referencing observable facts. "
                "Drafts require human review and approval before any outbound engagement."
            )

            all_b = session.query(Business).all()
            if not all_b:
                st.info("No businesses in database.")
            else:
                sel_b = st.selectbox(
                    "Select Prospect for Outreach:",
                    options=all_b,
                    format_func=lambda b: f"#{b.id} — {b.name} (Score: {b.score.total_score if b.score else 'N/A'})"
                )

                pref_service = st.selectbox(
                    "Service Focus to Pitch:",
                    options=settings.OFFERED_SERVICES
                )

                if st.button("📝 Generate Factual Outreach Draft", type="primary"):
                    draft, msg = generate_outreach_draft(session, sel_b.id, preferred_service=pref_service)
                    if draft:
                        st.success("Draft created successfully!")
                    else:
                        st.error(f"Draft Generation Blocked: {msg}")

                # Display existing drafts for this business
                drafts = session.query(OutreachDraft).filter(OutreachDraft.business_id == sel_b.id).all()
                if drafts:
                    st.markdown("#### Existing Outreach Drafts:")
                    for d in drafts:
                        with st.expander(f"Draft #{d.id} — Focus: {d.service_focus} (Status: {d.status})"):
                            st.write(f"**Subject:** {d.subject_line}")
                            edited_body = st.text_area("Message Body (Editable)", value=d.message_body, height=220, key=f"draft_{d.id}")
                            
                            c_app, c_rej, c_save = st.columns([1, 1, 2])
                            with c_app:
                                if st.button("✅ Approve Draft", key=f"app_{d.id}"):
                                    update_draft_status(session, d.id, "APPROVED", updated_body=edited_body)
                                    st.success("Draft Approved!")
                                    st.rerun()
                            with c_rej:
                                if st.button("❌ Reject Draft", key=f"rej_{d.id}"):
                                    update_draft_status(session, d.id, "REJECTED")
                                    st.warning("Draft Rejected.")
                                    st.rerun()
                            with c_save:
                                if st.button("💾 Save Edits", key=f"save_{d.id}"):
                                    update_draft_status(session, d.id, d.status, updated_body=edited_body)
                                    st.success("Draft updated.")

        # -------------------------------------------------------------
        # 10. CAMPAIGN TRACKING
        # -------------------------------------------------------------
        elif choice == "10. Campaign Tracking":
            st.subheader("📈 Outreach Campaign & Review Pipeline")
            drafts = session.query(OutreachDraft).all()

            if not drafts:
                st.info("No outreach drafts generated yet. Head to 'Outreach Draft Generator' to prepare drafts.")
            else:
                d_list = []
                for d in drafts:
                    d_list.append({
                        "Draft ID": d.id,
                        "Company": d.business.name if d.business else "Unknown",
                        "Service": d.service_focus,
                        "Status": d.status,
                        "Subject Line": d.subject_line,
                        "Reviewed By": d.reviewed_by or "Pending Review",
                        "Created At": d.created_at.strftime("%Y-%m-%d %H:%M") if d.created_at else "—"
                    })
                st.dataframe(pd.DataFrame(d_list), use_container_width=True, hide_index=True)

        # -------------------------------------------------------------
        # 11. SUPPRESSION & DNC CONTROLS
        # -------------------------------------------------------------
        elif choice == "11. Suppression & DNC Controls":
            st.subheader("🛡️ Global Suppression & Do-Not-Contact Registry")
            st.markdown(
                "Strict compliance protection. Any domain, email, phone, or company name on this list is permanently blocked "
                "from being re-imported, qualified, or drafted for outreach."
            )

            col_add1, col_add2, col_add3 = st.columns([2, 3, 2])
            with col_add1:
                sup_type = st.selectbox("Record Type", ["DOMAIN", "EMAIL", "PHONE", "COMPANY_NAME"])
            with col_add2:
                sup_val = st.text_input("Value to Suppress", placeholder="e.g. badsite.com or 555-0100")
            with col_add3:
                sup_reason = st.selectbox("Reason", ["OPT_OUT", "REQUESTED_REMOVAL", "LEGAL_RESTRICTION", "COMPLIANCE_HOLD"])

            if st.button("🚫 Add to Suppression List", type="primary"):
                if sup_val:
                    success, msg = add_suppression_entry(session, sup_type, sup_val, reason=sup_reason)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter a value.")

            st.divider()

            records = session.query(SuppressionRecord).all()
            st.markdown(f"#### Active Suppressed Entities ({len(records)} entries)")
            if records:
                s_list = [{"Type": r.record_type, "Value": r.value, "Reason": r.reason, "Added At": r.added_at.strftime("%Y-%m-%d") if r.added_at else "—"} for r in records]
                st.dataframe(pd.DataFrame(s_list), use_container_width=True, hide_index=True)
            else:
                st.info("Suppression registry is currently empty.")

            st.divider()
            with st.expander("⚠️ Right to be Forgotten (Purge Business Record)"):
                st.markdown("Permanently delete a business and all linked contact/website data upon request.")
                all_b = session.query(Business).all()
                if all_b:
                    b_del = st.selectbox(
                        "Select Business to Permanently Purge:",
                        options=all_b,
                        format_func=lambda b: f"#{b.id} — {b.name}"
                    )
                    if st.button("🗑️ Permanently Delete Record", type="secondary"):
                        delete_business_data(session, b_del.id, reason="User right to be forgotten request")
                        st.success(f"Purged {b_del.name} from database.")
                        st.rerun()

        # -------------------------------------------------------------
        # 12. DATA SOURCES & GOVERNANCE
        # -------------------------------------------------------------
        elif choice == "12. Data Sources & Governance":
            st.subheader("📜 Data Sources, Terms & Governance")
            sources = session.query(Source).all()
            for src in sources:
                with st.expander(f"Source: {src.name} ({'Authorized' if src.collection_permitted else 'Review Pending'})"):
                    st.write(f"**URL:** {src.source_url or 'N/A'}")
                    st.write(f"**License Type:** `{src.license_type}`")
                    st.write(f"**Terms Reviewed:** {'Yes' if src.terms_reviewed else 'No'}")
                    st.write(f"**Automated Collection Permitted:** {'Yes' if src.collection_permitted else 'No'}")
                    st.write(f"**Attribution Statement:** {src.attribution_text or 'None'}")
                    st.write(f"**Usage Notes:** {src.notes or 'None'}")

            st.divider()
            st.markdown("#### 🌐 Jurisdictional Privacy & Cold Outreach Rules")
            sel_mkt = st.selectbox("Select Target Country for Compliance Review:", list(JURISDICTION_POLICIES.keys()))
            pol = get_market_policy(sel_mkt)
            st.info(f"**Regulations:** {', '.join(pol['regulations'])} | **Risk Profile:** {pol['risk_level']}")
            st.write("**Commercial Electronic Messaging Rules:**")
            for r in pol["email_rules"]:
                st.write(f"• {r}")
            st.write("**Calling & Voice Bot Rules:**")
            for cr in pol["calling_rules"]:
                st.write(f"• {cr}")

        # -------------------------------------------------------------
        # 13. EXPORT & REPORTING
        # -------------------------------------------------------------
        elif choice == "13. Export & Reporting":
            st.subheader("📊 Export & Prospect Reporting")
            st.markdown(
                "Export verified leads with observable opportunities, contact channels, and score breakdowns to CSV or Excel."
            )

            prio_filter = st.selectbox("Filter by Priority Tier:", ["All", "HIGH_PRIORITY", "POTENTIAL_PROSPECT", "NEEDS_RESEARCH"])
            df_export = export_leads_to_dataframe(session, priority_filter=None if prio_filter == "All" else prio_filter)

            st.write(f"Ready to export **{len(df_export)}** prospect records.")
            st.dataframe(df_export.head(10), use_container_width=True, hide_index=True)

            c_csv, c_excel = st.columns(2)
            with c_csv:
                csv_bytes = export_leads_to_csv(df_export)
                st.download_button(
                    label="📥 Download CSV File",
                    data=csv_bytes,
                    file_name=f"xenith_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            with c_excel:
                excel_bytes = export_leads_to_excel(df_export)
                st.download_button(
                    label="📊 Download Excel (.xlsx) Workbook",
                    data=excel_bytes,
                    file_name=f"xenith_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # -------------------------------------------------------------
        # 14. SETTINGS & DIAGNOSTICS
        # -------------------------------------------------------------
        elif choice == "14. Settings & Diagnostics":
            st.subheader("🔧 System Diagnostics & Runtime Environment")
            
            c_env1, c_env2 = st.columns(2)
            with c_env1:
                st.markdown("#### 💻 Runtime Status")
                st.write(f"• Operating System: `{sys.platform}` (Windows 11)")
                st.write(f"• Python Version: `{sys.version.split()[0]}`")
                st.write(f"• Database Path: `{settings.DATABASE_PATH}`")
                st.write(f"• Database Size: `{os.path.getsize(settings.DATABASE_PATH) / 1024:.2f} KB`")

            with c_env2:
                st.markdown("#### 🤖 Local AI Inference (Ollama)")
                ai = LocalAIClient()
                is_ai_up, models = ai.is_available()
                if is_ai_up:
                    st.success(f"Ollama Server Online at {ai.base_url}")
                    st.write(f"Available Models: `{', '.join(models) if models else 'None'}`")
                else:
                    st.warning(f"Ollama Server Offline at {ai.base_url}")
                    st.caption("Application is operating in 100% deterministic rule-based mode. To enable local AI, install and launch Ollama.")

            st.divider()
            st.markdown("#### 📋 Recent Audit Trail Events")
            recent_audits = session.query(AuditEvent).order_by(AuditEvent.id.desc()).limit(15).all()
            if recent_audits:
                a_data = [{"ID": a.id, "Action": a.action, "Entity": f"{a.entity_type} #{a.entity_id or ''}", "Details": a.details or "—", "Timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S") if a.timestamp else "—"} for a in recent_audits]
                st.dataframe(pd.DataFrame(a_data), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
