"""Extracts public business contact channels from verified HTML."""
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# Regex patterns for business contacts
EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
)
PHONE_REGEX = re.compile(
    r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"
)

# Common non-business or image extensions falsely matched as emails
EXCLUDED_EMAIL_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js", ".woff", ".woff2"
)


class ExtractedContact:
    def __init__(self, channel_type: str, value: str, source_url: str):
        self.channel_type = channel_type  # EMAIL, PHONE, CONTACT_FORM, LINKEDIN
        self.value = value.strip()
        self.source_url = source_url


def extract_business_contacts(soup: BeautifulSoup, source_url: str) -> list[ExtractedContact]:
    """Extract public official business contact details from page DOM."""
    if not soup:
        return []

    contacts: list[ExtractedContact] = []
    seen = set()

    # 1. Look for mailto: links (highest fidelity)
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("mailto:"):
            raw_email = href[7:].split("?")[0].strip().lower()
            if raw_email and "@" in raw_email and not raw_email.endswith(EXCLUDED_EMAIL_EXTENSIONS):
                key = ("EMAIL", raw_email)
                if key not in seen:
                    contacts.append(ExtractedContact("EMAIL", raw_email, source_url))
                    seen.add(key)

        # 2. Look for tel: links
        elif href.lower().startswith("tel:"):
            raw_phone = href[4:].split("?")[0].strip()
            digits = re.sub(r"\D", "", raw_phone)
            if len(digits) >= 7:
                key = ("PHONE", raw_phone)
                if key not in seen:
                    contacts.append(ExtractedContact("PHONE", raw_phone, source_url))
                    seen.add(key)

        # 3. Look for dedicated Contact Forms
        elif any(kw in href.lower() for kw in ["/contact", "/contact-us", "/get-in-touch", "/inquiry", "/reach-us"]):
            full_contact_page = urljoin(source_url, href)
            key = ("CONTACT_FORM", full_contact_page)
            if key not in seen:
                contacts.append(ExtractedContact("CONTACT_FORM", full_contact_page, source_url))
                seen.add(key)

        # 4. Official Social Links (LinkedIn business pages)
        elif "linkedin.com/company" in href.lower():
            clean_li = href.split("?")[0].strip()
            key = ("LINKEDIN", clean_li)
            if key not in seen:
                contacts.append(ExtractedContact("LINKEDIN", clean_li, source_url))
                seen.add(key)

    # 5. Extract text emails from page content
    text_content = soup.get_text()
    for match in EMAIL_REGEX.finditer(text_content):
        found_email = match.group(0).lower().strip()
        if not found_email.endswith(EXCLUDED_EMAIL_EXTENSIONS):
            # Exclude obvious mock or template emails
            if not any(dummy in found_email for dummy in ["example.com", "yoursite.com", "domain.com", "email@"]):
                key = ("EMAIL", found_email)
                if key not in seen:
                    contacts.append(ExtractedContact("EMAIL", found_email, source_url))
                    seen.add(key)

    # 6. Extract text phones from header/footer or strong tags
    # Focus on header, footer, or contact containers to avoid extracting random numbers
    contact_containers = soup.find_all(["header", "footer", "nav", "div"], class_=re.compile(r"contact|footer|header|phone", re.I))
    for container in contact_containers:
        for match in PHONE_REGEX.finditer(container.get_text()):
            phone_candidate = match.group(0).strip()
            digits = re.sub(r"\D", "", phone_candidate)
            if 10 <= len(digits) <= 12:
                key = ("PHONE", phone_candidate)
                if key not in seen:
                    contacts.append(ExtractedContact("PHONE", phone_candidate, source_url))
                    seen.add(key)

    return contacts
