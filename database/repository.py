"""Data Access Repository for XENITH Lead Generator."""
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_
from database.models import (
    Business, BusinessWebsite, ContactChannel, WebsiteAnalysis,
    LeadScore, OutreachDraft, SuppressionRecord, ImportJob, AuditEvent, Source
)
from database.deduplication import (
    normalize_business_name, find_duplicate_business
)
from core.security import normalize_domain, sanitize_url
from core.logging import get_logger

logger = get_logger("repository")


def add_audit_event(session: Session, action: str, entity_type: str = None, entity_id: int = None, details: str = None):
    """Log an audit event."""
    event = AuditEvent(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    session.add(event)


def is_suppressed(
    session: Session,
    domain: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    company_name: Optional[str] = None
) -> tuple[bool, str]:
    """
    Check if any field matches the global suppression list.
    Returns (is_suppressed, reason).
    """
    records = session.query(SuppressionRecord).all()
    if not records:
        return False, ""

    if domain:
        norm_dom = normalize_domain(domain)
        for r in records:
            if r.record_type == "DOMAIN" and normalize_domain(r.value) == norm_dom:
                return True, f"Domain '{domain}' suppressed: {r.reason}"

    if email:
        clean_email = email.strip().lower()
        for r in records:
            if r.record_type == "EMAIL" and r.value.strip().lower() == clean_email:
                return True, f"Email '{email}' suppressed: {r.reason}"

    if phone:
        digits = "".join(filter(str.isdigit, phone))
        for r in records:
            if r.record_type == "PHONE" and "".join(filter(str.isdigit, r.value)) == digits:
                return True, f"Phone '{phone}' suppressed: {r.reason}"

    if company_name:
        norm_name = normalize_business_name(company_name)
        for r in records:
            if r.record_type == "COMPANY_NAME" and normalize_business_name(r.value) == norm_name:
                return True, f"Company '{company_name}' suppressed: {r.reason}"

    return False, ""


def upsert_business(
    session: Session,
    name: str,
    website_url: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    source_name: str = "Manual CSV/Excel Import",
    notes: Optional[str] = None
) -> tuple[Business, bool, str]:
    """
    Safely ingest or update a business with multi-factor deduplication and suppression checks.
    Returns (business_obj, is_new, message).
    """
    # 1. Suppression check
    suppressed, sup_reason = is_suppressed(
        session, domain=website_url, email=email, phone=phone, company_name=name
    )
    if suppressed:
        return None, False, f"SUPPRESSED: {sup_reason}"

    # 2. Check for duplicate
    existing_biz, match_reason = find_duplicate_business(
        session=session,
        name=name,
        website_url=website_url,
        city=city,
        phone=phone,
        email=email
    )

    norm_name = normalize_business_name(name)
    norm_cat = category.strip().lower() if category else None

    # Get source ID
    source = session.query(Source).filter_by(name=source_name).first()
    source_id = source.id if source else None

    if existing_biz:
        # Update missing fields gracefully
        if not existing_biz.category and category:
            existing_biz.category = category
            existing_biz.normalized_category = norm_cat
        if not existing_biz.city and city:
            existing_biz.city = city
        if not existing_biz.state and state:
            existing_biz.state = state
        if not existing_biz.country and country:
            existing_biz.country = country
        
        # Add website if missing
        if website_url and not existing_biz.website:
            norm_dom = normalize_domain(website_url)
            web = BusinessWebsite(
                business_id=existing_biz.id,
                raw_url=website_url,
                normalized_domain=norm_dom
            )
            session.add(web)

        # Add phone contact if missing
        if phone:
            has_phone = any(c.channel_type == "PHONE" and c.value == phone for c in existing_biz.contacts)
            if not has_phone:
                c_phone = ContactChannel(
                    business_id=existing_biz.id,
                    channel_type="PHONE",
                    value=phone,
                    is_public_business_channel=True
                )
                session.add(c_phone)

        # Add email contact if missing
        if email:
            has_email = any(c.channel_type == "EMAIL" and c.value.lower() == email.lower() for c in existing_biz.contacts)
            if not has_email:
                c_email = ContactChannel(
                    business_id=existing_biz.id,
                    channel_type="EMAIL",
                    value=email.strip().lower(),
                    is_public_business_channel=True
                )
                session.add(c_email)

        add_audit_event(session, "UPDATE_DEDUP", "Business", existing_biz.id, f"Merged update via {match_reason}")
        return existing_biz, False, f"Duplicate detected ({match_reason}) - record enriched."

    # Create new business
    biz = Business(
        name=name.strip(),
        normalized_name=norm_name,
        category=category.strip() if category else None,
        normalized_category=norm_cat,
        city=city.strip() if city else None,
        state=state.strip() if state else None,
        country=country.strip() if country else None,
        source_id=source_id,
        verification_status="UNVERIFIED",
        notes=notes
    )
    session.add(biz)
    session.flush()  # Generate biz.id

    # Create website record if provided
    if website_url:
        norm_dom = normalize_domain(website_url)
        clean_url = sanitize_url(website_url)
        web = BusinessWebsite(
            business_id=biz.id,
            raw_url=clean_url,
            normalized_domain=norm_dom
        )
        session.add(web)

    # Add contacts
    if phone:
        c_phone = ContactChannel(
            business_id=biz.id,
            channel_type="PHONE",
            value=phone.strip(),
            is_public_business_channel=True
        )
        session.add(c_phone)

    if email:
        c_email = ContactChannel(
            business_id=biz.id,
            channel_type="EMAIL",
            value=email.strip().lower(),
            is_public_business_channel=True
        )
        session.add(c_email)

    add_audit_event(session, "CREATE_BUSINESS", "Business", biz.id, f"Created new business {biz.name}")
    return biz, True, "New business record created successfully."


def get_all_businesses(
    session: Session,
    search_query: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 200,
    offset: int = 0
) -> list[Business]:
    """Retrieve businesses with filters and eager loaded relationships."""
    query = (
        session.query(Business)
        .options(
            joinedload(Business.website),
            joinedload(Business.score),
            joinedload(Business.contacts),
            joinedload(Business.analyses)
        )
    )

    if search_query:
        sq = f"%{search_query.strip()}%"
        query = query.filter(
            or_(
                Business.name.ilike(sq),
                Business.city.ilike(sq),
                Business.category.ilike(sq)
            )
        )

    if country:
        query = query.filter(Business.country.ilike(country.strip()))

    if category:
        query = query.filter(Business.category.ilike(f"%{category.strip()}%"))

    if priority:
        query = query.join(Business.score).filter(LeadScore.priority_label == priority)

    return query.order_by(desc(Business.id)).offset(offset).limit(limit).all()


def get_business_by_id(session: Session, business_id: int) -> Optional[Business]:
    """Retrieve single business with all related records."""
    return (
        session.query(Business)
        .options(
            joinedload(Business.website),
            joinedload(Business.score),
            joinedload(Business.contacts),
            joinedload(Business.analyses),
            joinedload(Business.outreach_drafts),
            joinedload(Business.source)
        )
        .filter(Business.id == business_id)
        .first()
    )


def get_database_metrics(session: Session) -> dict[str, Any]:
    """Retrieve actual metrics from database."""
    total_businesses = session.query(func.count(Business.id)).scalar() or 0
    verified_businesses = session.query(func.count(Business.id)).filter(Business.verification_status == "VERIFIED").scalar() or 0
    
    # Businesses with websites
    with_website = session.query(func.count(BusinessWebsite.id)).scalar() or 0
    reachable_websites = session.query(func.count(BusinessWebsite.id)).filter(BusinessWebsite.is_reachable == True).scalar() or 0
    
    # Qualified prospects
    high_priority = session.query(func.count(LeadScore.id)).filter(LeadScore.priority_label == "HIGH_PRIORITY").scalar() or 0
    potential_prospects = session.query(func.count(LeadScore.id)).filter(LeadScore.priority_label == "POTENTIAL_PROSPECT").scalar() or 0
    
    # Contact channels
    with_contacts = session.query(func.count(func.distinct(ContactChannel.business_id))).scalar() or 0
    
    # Website opportunities identified
    total_analyses = session.query(func.count(WebsiteAnalysis.id)).scalar() or 0
    
    # Outreach drafts
    total_drafts = session.query(func.count(OutreachDraft.id)).scalar() or 0
    approved_drafts = session.query(func.count(OutreachDraft.id)).filter(OutreachDraft.status == "APPROVED").scalar() or 0
    
    # Suppression count
    suppressed_count = session.query(func.count(SuppressionRecord.id)).scalar() or 0

    return {
        "total_businesses": total_businesses,
        "verified_businesses": verified_businesses,
        "with_website": with_website,
        "reachable_websites": reachable_websites,
        "high_priority_leads": high_priority,
        "potential_leads": potential_prospects,
        "with_contacts": with_contacts,
        "total_opportunities": total_analyses,
        "total_drafts": total_drafts,
        "approved_drafts": approved_drafts,
        "suppressed_records": suppressed_count
    }
