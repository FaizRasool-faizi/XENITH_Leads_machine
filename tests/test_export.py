"""Unit tests for Excel and CSV export service."""
import pytest
import pandas as pd
from database.connection import init_db
from database.models import Business, BusinessWebsite, ContactChannel, LeadScore, WebsiteAnalysis
from ui.export_service import export_leads_to_dataframe, export_leads_to_excel, export_leads_to_csv


def test_export_leads_to_dataframe_and_excel(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    biz = Business(
        name="Global Maritime Logistics",
        category="Logistics & Freight",
        city="Dubai",
        country="United Arab Emirates"
    )
    session.add(biz)
    session.flush()

    session.add(BusinessWebsite(
        business_id=biz.id,
        raw_url="https://globalmaritime.ae",
        normalized_domain="globalmaritime.ae",
        is_reachable=True,
        http_status=200,
        page_title="Global Maritime Logistics LLC"
    ))
    session.add(ContactChannel(
        business_id=biz.id,
        channel_type="EMAIL",
        value="operations@globalmaritime.ae"
    ))
    session.add(LeadScore(
        business_id=biz.id,
        total_score=85,
        priority_label="HIGH_PRIORITY"
    ))
    session.add(WebsiteAnalysis(
        business_id=biz.id,
        finding_category="AI_CHATBOT",
        short_explanation="Absence of 24/7 client booking/status chatbot",
        recommended_service="AI Chatbots & Customer Support Agents"
    ))
    session.commit()

    # 1. Export DataFrame
    df = export_leads_to_dataframe(session)
    assert len(df) == 1
    assert df.iloc[0]["Business Name"] == "Global Maritime Logistics"
    assert df.iloc[0]["Country"] == "United Arab Emirates"
    assert df.iloc[0]["Lead Score (0-100)"] == 85
    assert "operations@globalmaritime.ae" in df.iloc[0]["Emails"]

    # 2. Export CSV
    csv_bytes = export_leads_to_csv(df)
    assert len(csv_bytes) > 0
    assert b"Global Maritime Logistics" in csv_bytes

    # 3. Export Excel (.xlsx)
    excel_bytes = export_leads_to_excel(df)
    assert len(excel_bytes) > 0
    # Valid ZIP header for modern xlsx (PK\x03\x04)
    assert excel_bytes[:4] == b"PK\x03\x04"

    session.close()
