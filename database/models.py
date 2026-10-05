"""SQLAlchemy ORM models for XENITH Lead Generator."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    source_url = Column(String(500), nullable=True)
    terms_reviewed = Column(Boolean, default=False)
    collection_permitted = Column(Boolean, default=False)
    license_type = Column(String(100), default="Unknown")
    attribution_required = Column(Boolean, default=False)
    attribution_text = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    businesses = relationship("Business", back_populates="source")


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    category = Column(String(150), nullable=True)
    normalized_category = Column(String(150), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    verification_status = Column(String(50), default="UNVERIFIED")  # UNVERIFIED, VERIFIED, INVALID
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    source = relationship("Source", back_populates="businesses")
    website = relationship("BusinessWebsite", back_populates="business", uselist=False, cascade="all, delete-orphan")
    contacts = relationship("ContactChannel", back_populates="business", cascade="all, delete-orphan")
    analyses = relationship("WebsiteAnalysis", back_populates="business", cascade="all, delete-orphan")
    score = relationship("LeadScore", back_populates="business", uselist=False, cascade="all, delete-orphan")
    outreach_drafts = relationship("OutreachDraft", back_populates="business", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name and not self.normalized_name:
            import re
            cleaned = re.sub(r"[^\w\s]", " ", self.name.lower().strip())
            self.normalized_name = re.sub(r"\s+", " ", cleaned).strip()


class BusinessWebsite(Base):
    __tablename__ = "business_websites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, unique=True)
    raw_url = Column(String(500), nullable=False)
    normalized_domain = Column(String(255), nullable=False, index=True)
    http_status = Column(Integer, nullable=True)
    is_reachable = Column(Boolean, default=False)
    final_url = Column(String(500), nullable=True)
    page_title = Column(String(500), nullable=True)
    meta_description = Column(Text, nullable=True)
    has_ssl = Column(Boolean, default=False)
    subpages_found = Column(Text, nullable=True)  # JSON or comma-separated detected paths
    last_crawled_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    business = relationship("Business", back_populates="website")


class ContactChannel(Base):
    __tablename__ = "contact_channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_type = Column(String(50), nullable=False)  # EMAIL, PHONE, CONTACT_FORM, LINKEDIN
    value = Column(String(255), nullable=False, index=True)
    is_public_business_channel = Column(Boolean, default=True)
    source_url = Column(String(500), nullable=True)
    verified = Column(Boolean, default=False)
    last_verified_at = Column(DateTime, nullable=True)

    business = relationship("Business", back_populates="contacts")


class WebsiteAnalysis(Base):
    __tablename__ = "website_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    finding_category = Column(String(100), nullable=False)  # WEBSITE_MODERNIZATION, AI_CHATBOT, BOOKING_AUTOMATION, etc.
    short_explanation = Column(Text, nullable=False)
    evidence_url = Column(String(500), nullable=True)
    confidence = Column(String(20), default="MEDIUM")  # HIGH, MEDIUM, LOW
    verification_status = Column(String(50), default="OBSERVED")  # OBSERVED, INFERRED, RESOLVED
    recommended_service = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    business = relationship("Business", back_populates="analyses")


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_score = Column(Integer, nullable=False, default=0, index=True)
    priority_label = Column(String(50), default="NEEDS_RESEARCH")  # HIGH_PRIORITY, POTENTIAL_PROSPECT, NEEDS_RESEARCH
    score_legitimacy = Column(Integer, default=0)
    score_relevance = Column(Integer, default=0)
    score_opportunity = Column(Integer, default=0)
    score_contact = Column(Integer, default=0)
    score_evidence = Column(Integer, default=0)
    score_breakdown = Column(Text, nullable=True)
    is_overridden = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    business = relationship("Business", back_populates="score")


class OutreachDraft(Base):
    __tablename__ = "outreach_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    service_focus = Column(String(150), nullable=False)
    subject_line = Column(String(255), nullable=False)
    message_body = Column(Text, nullable=False)
    evidence_citations = Column(Text, nullable=True)  # JSON formatted citations
    status = Column(String(50), default="DRAFT")  # DRAFT, APPROVED, REJECTED, EXPORTED
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    business = relationship("Business", back_populates="outreach_drafts")


class SuppressionRecord(Base):
    """Global suppression and Do-Not-Contact registry."""
    __tablename__ = "suppression_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_type = Column(String(50), nullable=False)  # DOMAIN, EMAIL, PHONE, COMPANY_NAME
    value = Column(String(255), nullable=False, unique=True, index=True)
    reason = Column(String(100), default="OPT_OUT")  # OPT_OUT, REQUESTED_REMOVAL, COMPLIANCE_HOLD
    added_at = Column(DateTime, default=utcnow)
    notes = Column(Text, nullable=True)


class ImportJob(Base):
    """Tracks batch imports with audit stats."""
    __tablename__ = "import_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_identifier = Column(String(255), nullable=False)
    total_rows = Column(Integer, default=0)
    imported_count = Column(Integer, default=0)
    duplicates_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class AuditEvent(Base):
    """Audit log of key actions, overrides, and exports."""
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utcnow)
