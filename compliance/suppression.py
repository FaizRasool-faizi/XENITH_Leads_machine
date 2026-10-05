"""Suppression list management and right-to-be-forgotten deletion workflows."""
from typing import Optional
from sqlalchemy.orm import Session
from database.models import SuppressionRecord, Business, AuditEvent
from database.repository import is_suppressed, add_audit_event
from core.security import normalize_domain
from core.logging import get_logger

logger = get_logger("compliance")


def add_suppression_entry(
    session: Session,
    record_type: str,
    value: str,
    reason: str = "OPT_OUT",
    notes: Optional[str] = None
) -> tuple[bool, str]:
    """
    Add a domain, email, phone, or company name to the global Do-Not-Contact registry.
    """
    clean_val = value.strip()
    if record_type == "DOMAIN":
        clean_val = normalize_domain(clean_val)
    elif record_type == "EMAIL":
        clean_val = clean_val.lower()
    elif record_type == "PHONE":
        clean_val = "".join(filter(str.isdigit, clean_val))

    if not clean_val:
        return False, "Cannot suppress empty value."

    existing = (
        session.query(SuppressionRecord)
        .filter(SuppressionRecord.record_type == record_type)
        .filter(SuppressionRecord.value == clean_val)
        .first()
    )
    if existing:
        return False, f"Entry '{clean_val}' is already present in suppression list ({existing.reason})."

    record = SuppressionRecord(
        record_type=record_type,
        value=clean_val,
        reason=reason,
        notes=notes
    )
    session.add(record)
    add_audit_event(session, "ADD_SUPPRESSION", "SuppressionRecord", None, f"Suppressed {record_type}: {clean_val}")
    session.commit()
    logger.info(f"Added {record_type} '{clean_val}' to suppression list.")
    return True, f"Successfully suppressed {record_type}: {clean_val}"


def delete_business_data(session: Session, business_id: int, reason: str = "Right to be forgotten") -> bool:
    """
    Permanently purge a business and all linked contact/website data.
    """
    biz = session.query(Business).filter(Business.id == business_id).first()
    if not biz:
        return False

    name = biz.name
    session.delete(biz)
    add_audit_event(session, "PURGE_BUSINESS", "Business", business_id, f"Purged business '{name}': {reason}")
    session.commit()
    logger.info(f"Permanently purged business ID {business_id} ('{name}').")
    return True
