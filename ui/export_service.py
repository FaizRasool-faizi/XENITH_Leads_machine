"""Export service for CSV and formatted Excel reports."""
from datetime import datetime
import io
import pandas as pd
from sqlalchemy.orm import Session
from database.models import Business, BusinessWebsite, ContactChannel, LeadScore, OutreachDraft


def export_leads_to_dataframe(session: Session, priority_filter: str = None) -> pd.DataFrame:
    """Generate a clean tabular representation of businesses for export."""
    query = session.query(Business)
    if priority_filter:
        query = query.join(Business.score).filter(LeadScore.priority_label == priority_filter)

    businesses = query.all()
    rows = []
    for b in businesses:
        web = b.website.raw_url if b.website else ""
        domain = b.website.normalized_domain if b.website else ""
        status = b.website.http_status if b.website else ""
        title = b.website.page_title if b.website else ""

        emails = [c.value for c in b.contacts if c.channel_type == "EMAIL"]
        phones = [c.value for c in b.contacts if c.channel_type == "PHONE"]
        forms = [c.value for c in b.contacts if c.channel_type == "CONTACT_FORM"]

        total_score = b.score.total_score if b.score else 0
        priority = b.score.priority_label if b.score else "NEEDS_RESEARCH"

        opps = [a.finding_category for a in b.analyses]
        rec_services = [a.recommended_service for a in b.analyses if a.recommended_service]

        rows.append({
            "Business ID": b.id,
            "Business Name": b.name,
            "Category": b.category or "",
            "City": b.city or "",
            "State": b.state or "",
            "Country": b.country or "",
            "Verification Status": b.verification_status,
            "Website URL": web,
            "Normalized Domain": domain,
            "HTTP Status": status,
            "Page Title": title,
            "Emails": "; ".join(emails),
            "Phones": "; ".join(phones),
            "Contact Forms": "; ".join(forms),
            "Lead Score (0-100)": total_score,
            "Priority Label": priority,
            "Observable Opportunities": "; ".join(set(opps)),
            "Recommended XENITH Services": "; ".join(set(rec_services)),
            "Source": b.source.name if b.source else "Manual"
        })

    return pd.DataFrame(rows)


def export_leads_to_excel(df: pd.DataFrame) -> bytes:
    """Generate styled Excel workbook bytes with openpyxl."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="XENITH Prospects")
    return output.getvalue()


def export_leads_to_csv(df: pd.DataFrame) -> bytes:
    """Generate CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")
