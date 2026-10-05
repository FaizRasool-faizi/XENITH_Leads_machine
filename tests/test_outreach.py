"""Unit tests for outreach draft generator and reviewer workflows."""
import pytest
from database.connection import init_db
from database.models import Business, BusinessWebsite, WebsiteAnalysis, OutreachDraft, SuppressionRecord
from outreach.generator import generate_outreach_draft, update_draft_status


def test_generate_evidence_backed_draft(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    biz = Business(
        name="Peak Performance Chiropractic",
        category="Chiropractor",
        city="Calgary",
        country="Canada"
    )
    session.add(biz)
    session.flush()

    session.add(BusinessWebsite(
        business_id=biz.id,
        raw_url="https://peakchiro.ca",
        normalized_domain="peakchiro.ca"
    ))
    session.add(WebsiteAnalysis(
        business_id=biz.id,
        finding_category="BOOKING_AUTOMATION",
        short_explanation="Clinic requires patients to call or send plain email; no online self-scheduling widget detected.",
        evidence_url="https://peakchiro.ca",
        recommended_service="AI Workflow & Process Automation"
    ))
    session.commit()

    # Generate draft
    draft, msg = generate_outreach_draft(session, biz.id)
    assert draft is not None
    assert "Peak Performance Chiropractic" in draft.subject_line
    assert "https://peakchiro.ca" in draft.message_body
    assert "no online self-scheduling widget" in draft.message_body
    assert draft.status == "DRAFT"

    # Review and approve draft
    updated = update_draft_status(
        session, draft.id, status="APPROVED", reviewer_name="Faiz", updated_body=draft.message_body + "\nPS: Excited to connect!"
    )
    assert updated is True
    assert draft.status == "APPROVED"
    assert "Excited to connect!" in draft.message_body

    session.close()


def test_draft_blocked_on_suppression(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    biz = Business(name="Do Not Contact Co", normalized_name="do not contact")
    session.add(biz)
    session.commit()

    # Suppress business
    session.add(SuppressionRecord(record_type="COMPANY_NAME", value="do not contact", reason="OPT_OUT"))
    session.commit()

    # Attempt to draft
    draft, msg = generate_outreach_draft(session, biz.id)
    assert draft is None
    assert "BLOCKED BY SUPPRESSION" in msg

    session.close()
