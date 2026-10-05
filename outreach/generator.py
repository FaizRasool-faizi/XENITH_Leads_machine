"""Generates evidence-backed personalized outreach drafts for human review."""
import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from database.models import Business, OutreachDraft
from database.repository import is_suppressed, add_audit_event
from outreach.templates import OUTREACH_TEMPLATES
from core.logging import get_logger

logger = get_logger("outreach_generator")


def generate_outreach_draft(
    session: Session,
    business_id: int,
    preferred_service: Optional[str] = None
) -> tuple[Optional[OutreachDraft], str]:
    """
    Generate an evidence-grounded outreach draft for a business.
    Returns (draft_or_none, message).
    """
    biz = session.query(Business).filter(Business.id == business_id).first()
    if not biz:
        return None, f"Business ID {business_id} not found."

    # 1. Mandatory Suppression check
    suppressed, sup_reason = is_suppressed(
        session,
        domain=biz.website.normalized_domain if biz.website else None,
        company_name=biz.name
    )
    if suppressed:
        return None, f"BLOCKED BY SUPPRESSION: {sup_reason}"

    # 2. Select service focus based on verified observations
    analyses = biz.analyses or []
    target_service = preferred_service

    if not target_service:
        # Prioritize based on observable evidence
        cat_map = {
            "WEBSITE_DEVELOPMENT": "Website Design & Development",
            "AI_CHATBOT": "AI Chatbots & Customer Support Agents",
            "BOOKING_AUTOMATION": "AI Workflow & Process Automation",
            "AI_CALLING_AGENT": "AI Calling Agents & Voice Bots"
        }
        for a in analyses:
            if a.finding_category in cat_map:
                target_service = cat_map[a.finding_category]
                break

    if not target_service or target_service not in OUTREACH_TEMPLATES:
        target_service = "Website Design & Development"

    template = OUTREACH_TEMPLATES[target_service]

    # 3. Build specific observation
    matching_findings = [a for a in analyses if a.recommended_service == target_service]
    if matching_findings:
        specific_obs = matching_findings[0].short_explanation
        evidence_url = matching_findings[0].evidence_url or (biz.website.raw_url if biz.website else "your website")
    elif analyses:
        specific_obs = analyses[0].short_explanation
        evidence_url = analyses[0].evidence_url or (biz.website.raw_url if biz.website else "your website")
    elif not biz.website:
        specific_obs = "your business currently does not have a dedicated website indexed for customers"
        evidence_url = "public directories"
    else:
        specific_obs = "your website could benefit from updated mobile performance and interactive customer engagement"
        evidence_url = biz.website.raw_url

    # Location & category phrases
    loc_parts = [p for p in [biz.city, biz.country] if p]
    location_phrase = ", ".join(loc_parts) if loc_parts else "your local market"
    category_phrase = biz.category or "professional services"

    # Fill template
    subject = template["subject"].format(
        company_name=biz.name,
        category_phrase=category_phrase,
        location_phrase=location_phrase,
        evidence_url=evidence_url,
        specific_observation=specific_obs
    )

    body = template["body"].format(
        company_name=biz.name,
        category_phrase=category_phrase,
        location_phrase=location_phrase,
        evidence_url=evidence_url,
        specific_observation=specific_obs
    )

    citations = [
        {
            "finding_category": a.finding_category,
            "explanation": a.short_explanation,
            "evidence_url": a.evidence_url,
            "confidence": a.confidence
        }
        for a in analyses
    ]

    # 4. Save draft in database
    draft = OutreachDraft(
        business_id=biz.id,
        service_focus=target_service,
        subject_line=subject,
        message_body=body,
        evidence_citations=json.dumps(citations),
        status="DRAFT",
        created_at=datetime.now(timezone.utc)
    )
    session.add(draft)
    add_audit_event(session, "GENERATE_DRAFT", "OutreachDraft", None, f"Generated draft for {biz.name} ({target_service})")
    session.commit()

    return draft, "Outreach draft generated successfully."


def update_draft_status(
    session: Session,
    draft_id: int,
    status: str,
    reviewer_name: str = "Admin",
    updated_body: Optional[str] = None
) -> bool:
    """Approve, reject, or edit an outreach draft."""
    draft = session.query(OutreachDraft).filter(OutreachDraft.id == draft_id).first()
    if not draft:
        return False

    draft.status = status
    draft.reviewed_by = reviewer_name
    draft.reviewed_at = datetime.now(timezone.utc)
    if updated_body:
        draft.message_body = updated_body

    add_audit_event(session, "REVIEW_DRAFT", "OutreachDraft", draft_id, f"Draft marked {status} by {reviewer_name}")
    session.commit()
    return True
