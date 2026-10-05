"""Entity deduplication and normalization engine."""
import re
from typing import Optional
from sqlalchemy.orm import Session
from database.models import Business, BusinessWebsite, ContactChannel
from core.security import normalize_domain

# Common corporate legal suffixes to strip for normalized matching
CORP_SUFFIXES = [
    r"\bllc\b", r"\binc\b", r"\bincorporated\b", r"\bcorp\b", r"\bcorporation\b",
    r"\bltd\b", r"\blimited\b", r"\bpty\b", r"\bpty ltd\b", r"\bco\b", r"\bcompany\b",
    r"\bfze\b", r"\bfzco\b", r"\bllp\b", r"\bgmbh\b", r"\bplc\b"
]
CORP_PATTERN = re.compile("|".join(CORP_SUFFIXES), flags=re.IGNORECASE)


def normalize_business_name(raw_name: str) -> str:
    """Normalize company name by stripping legal forms, punctuation, and extra whitespace."""
    if not raw_name:
        return ""
    name = raw_name.lower().strip()
    # Remove characters other than alphanumeric and spaces
    name = re.sub(r"[^\w\s]", " ", name)
    # Strip corporate suffixes
    name = CORP_PATTERN.sub(" ", name)
    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name).strip()
    return name


def normalize_phone_number(raw_phone: str) -> str:
    """Extract numeric digits from phone number for matching."""
    if not raw_phone:
        return ""
    digits = re.sub(r"\D", "", raw_phone)
    # Standardize 10/11 digit US/International numbers
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits


def find_duplicate_business(
    session: Session,
    name: str,
    website_url: Optional[str] = None,
    city: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
) -> tuple[Optional[Business], str]:
    """
    Search for an existing duplicate business using a tiered multi-factor strategy:
    1. Exact normalized domain match (highest confidence).
    2. Normalized business name + City match.
    3. Normalized phone match.
    4. Verified business email match.
    
    Returns (matched_business_or_none, match_reason).
    """
    # 1. Domain match
    if website_url:
        domain = normalize_domain(website_url)
        if domain:
            existing_web = (
                session.query(BusinessWebsite)
                .filter(BusinessWebsite.normalized_domain == domain)
                .first()
            )
            if existing_web and existing_web.business:
                return existing_web.business, f"Domain match: {domain}"

    # 2. Normalized business name + City match
    norm_name = normalize_business_name(name)
    if norm_name:
        query = session.query(Business).filter(Business.normalized_name == norm_name)
        if city:
            city_clean = city.strip().lower()
            query = query.filter(Business.city.ilike(city_clean))
        existing_biz = query.first()
        if existing_biz:
            return existing_biz, f"Name + City match: {norm_name} ({city or 'any'})"

    # 3. Phone match
    if phone:
        norm_phone = normalize_phone_number(phone)
        if len(norm_phone) >= 7:
            existing_contact = (
                session.query(ContactChannel)
                .filter(ContactChannel.channel_type == "PHONE")
                .all()
            )
            for c in existing_contact:
                if normalize_phone_number(c.value) == norm_phone:
                    return c.business, f"Phone match: {phone}"

    # 4. Email match
    if email and "@" in email:
        clean_email = email.strip().lower()
        existing_contact = (
            session.query(ContactChannel)
            .filter(ContactChannel.channel_type == "EMAIL")
            .filter(ContactChannel.value.ilike(clean_email))
            .first()
        )
        if existing_contact:
            return existing_contact.business, f"Email match: {clean_email}"

    return None, ""
