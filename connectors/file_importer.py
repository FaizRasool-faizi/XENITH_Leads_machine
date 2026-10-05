"""File import connector for CSV and Excel business lead datasets."""
from pathlib import Path
from typing import Optional, BinaryIO, Union
import pandas as pd
from sqlalchemy.orm import Session
from connectors.base import DiscoveredLead
from database.models import ImportJob
from database.repository import upsert_business
from core.logging import get_logger

logger = get_logger("file_importer")

# Flexible column alias mappings
COLUMN_ALIASES = {
    "name": ["business_name", "company_name", "company", "name", "business", "organization", "firm", "title"],
    "website_url": ["website", "url", "web", "site", "domain", "homepage", "website_url"],
    "category": ["category", "industry", "business_type", "type", "niche", "sector"],
    "city": ["city", "town", "locality", "municipality"],
    "state": ["state", "province", "region"],
    "country": ["country", "nation"],
    "phone": ["phone", "telephone", "tel", "mobile", "phone_number", "contact_phone"],
    "email": ["email", "e_mail", "mail", "contact_email", "email_address"]
}


def detect_column_mapping(columns: list[str]) -> dict[str, str]:
    """Map user file header columns to standardized field names."""
    mapping = {}
    lower_cols = {col.lower().strip().replace(" ", "_"): col for col in columns}
    
    for standard_field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower_cols:
                mapping[standard_field] = lower_cols[alias]
                break
    return mapping


def import_leads_from_file(
    file_or_path: Union[str, Path, BinaryIO],
    filename: str,
    session: Session,
    source_name: str = "Manual CSV/Excel Import"
) -> dict:
    """
    Parse CSV or Excel file, validate each row, deduplicate and import to SQLite database.
    Returns audit summary with counts and rejected rows.
    """
    # 1. Read file into Pandas DataFrame
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file_or_path)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_or_path)
        else:
            return {
                "success": False,
                "error": f"Unsupported file format: {filename}. Please upload .csv or .xlsx",
                "total_rows": 0,
                "imported_count": 0,
                "duplicates_count": 0,
                "rejected_count": 0,
                "rejected_rows": []
            }
    except Exception as e:
        logger.error(f"Failed to read file {filename}: {e}")
        return {
            "success": False,
            "error": f"Could not parse file: {str(e)}",
            "total_rows": 0,
            "imported_count": 0,
            "duplicates_count": 0,
            "rejected_count": 0,
            "rejected_rows": []
        }

    total_rows = len(df)
    if total_rows == 0:
        return {
            "success": False,
            "error": "The uploaded file is empty.",
            "total_rows": 0,
            "imported_count": 0,
            "duplicates_count": 0,
            "rejected_count": 0,
            "rejected_rows": []
        }

    # 2. Detect column mapping
    mapping = detect_column_mapping(list(df.columns))
    if "name" not in mapping:
        return {
            "success": False,
            "error": f"Missing required company name column. Available columns: {list(df.columns)}. Expected one of {COLUMN_ALIASES['name']}",
            "total_rows": total_rows,
            "imported_count": 0,
            "duplicates_count": 0,
            "rejected_count": total_rows,
            "rejected_rows": []
        }

    name_col = mapping["name"]
    web_col = mapping.get("website_url")
    cat_col = mapping.get("category")
    city_col = mapping.get("city")
    state_col = mapping.get("state")
    country_col = mapping.get("country")
    phone_col = mapping.get("phone")
    email_col = mapping.get("email")

    imported_count = 0
    duplicates_count = 0
    rejected_count = 0
    rejected_rows = []

    # 3. Process each row
    for idx, row in df.iterrows():
        raw_name = row.get(name_col)
        if pd.isna(raw_name) or not str(raw_name).strip():
            rejected_count += 1
            rejected_rows.append({"row": int(idx) + 1, "reason": "Missing business name"})
            continue

        name = str(raw_name).strip()
        web = str(row.get(web_col)).strip() if web_col and not pd.isna(row.get(web_col)) else None
        cat = str(row.get(cat_col)).strip() if cat_col and not pd.isna(row.get(cat_col)) else None
        city = str(row.get(city_col)).strip() if city_col and not pd.isna(row.get(city_col)) else None
        state = str(row.get(state_col)).strip() if state_col and not pd.isna(row.get(state_col)) else None
        country = str(row.get(country_col)).strip() if country_col and not pd.isna(row.get(country_col)) else None
        phone = str(row.get(phone_col)).strip() if phone_col and not pd.isna(row.get(phone_col)) else None
        email = str(row.get(email_col)).strip() if email_col and not pd.isna(row.get(email_col)) else None

        # Clean string "nan" or "None"
        if web in ("nan", "None", ""): web = None
        if cat in ("nan", "None", ""): cat = None
        if city in ("nan", "None", ""): city = None
        if state in ("nan", "None", ""): state = None
        if country in ("nan", "None", ""): country = None
        if phone in ("nan", "None", ""): phone = None
        if email in ("nan", "None", ""): email = None

        biz, is_new, msg = upsert_business(
            session=session,
            name=name,
            website_url=web,
            category=cat,
            city=city,
            state=state,
            country=country,
            phone=phone,
            email=email,
            source_name=source_name
        )

        if not biz and "SUPPRESSED" in msg:
            rejected_count += 1
            rejected_rows.append({"row": int(idx) + 1, "name": name, "reason": msg})
        elif is_new:
            imported_count += 1
        else:
            duplicates_count += 1

    session.commit()

    # Record job
    job = ImportJob(
        source_identifier=filename,
        total_rows=total_rows,
        imported_count=imported_count,
        duplicates_count=duplicates_count,
        rejected_count=rejected_count,
        error_summary=f"Processed {total_rows} rows: {imported_count} new, {duplicates_count} duplicates/merged, {rejected_count} rejected."
    )
    session.add(job)
    session.commit()

    return {
        "success": True,
        "filename": filename,
        "total_rows": total_rows,
        "imported_count": imported_count,
        "duplicates_count": duplicates_count,
        "rejected_count": rejected_count,
        "rejected_rows": rejected_rows[:50]  # First 50 rejected rows
    }
