"""Unit tests for lead scoring and qualification engine."""
import pytest
from database.connection import init_db
from database.models import Business, BusinessWebsite, ContactChannel, WebsiteAnalysis
from scoring.engine import calculate_lead_score, apply_lead_score_to_business
from scoring.weights import ScoringProfile


def test_scoring_high_priority_lead(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    # Create a high quality candidate: Dental clinic with legacy site, missing booking, and phone/email contacts
    biz = Business(
        name="Austin Family Dental",
        normalized_name="austin family dental",
        category="Dentist & Dental Clinic",
        city="Austin",
        state="TX",
        country="United States"
    )
    session.add(biz)
    session.flush()

    web = BusinessWebsite(
        business_id=biz.id,
        raw_url="http://austinfamilydental.com",
        normalized_domain="austinfamilydental.com",
        is_reachable=True,
        http_status=200
    )
    session.add(web)

    # Add contacts
    session.add(ContactChannel(business_id=biz.id, channel_type="EMAIL", value="info@austinfamilydental.com"))
    session.add(ContactChannel(business_id=biz.id, channel_type="PHONE", value="512-555-0199"))

    # Add opportunities
    session.add(WebsiteAnalysis(
        business_id=biz.id,
        finding_category="BOOKING_AUTOMATION",
        short_explanation="Dental clinic lacks online booking.",
        evidence_url="http://austinfamilydental.com"
    ))
    session.add(WebsiteAnalysis(
        business_id=biz.id,
        finding_category="AI_CHATBOT",
        short_explanation="No after-hours chat assistant.",
        evidence_url="http://austinfamilydental.com"
    ))
    session.commit()

    score = calculate_lead_score(biz)
    assert score.total_score >= 70
    assert score.score_legitimacy >= 15
    assert score.score_relevance == 20
    assert score.score_contact >= 13

    # Apply score via service
    lead_score = apply_lead_score_to_business(session, biz.id)
    assert lead_score.total_score == score.total_score
    assert biz.verification_status == "VERIFIED"

    session.close()


def test_scoring_manual_override(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    biz = Business(name="Generic Trading", normalized_name="generic trading")
    session.add(biz)
    session.commit()

    # Calculate default
    score = calculate_lead_score(biz)
    assert score.total_score < 50
    assert score.priority_label == "NEEDS_RESEARCH"

    # Override manually
    lead_score = apply_lead_score_to_business(
        session,
        business_id=biz.id,
        override_score=95,
        override_reason="Strategic partner referral"
    )
    assert lead_score.total_score == 95
    assert lead_score.is_overridden is True
    assert lead_score.priority_label == "HIGH_PRIORITY"
    assert "referral" in lead_score.override_reason

    session.close()
