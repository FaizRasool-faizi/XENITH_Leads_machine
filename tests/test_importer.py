"""Unit and integration tests for CSV/Excel file importer and discovery connectors."""
import io
import pytest
import pandas as pd
from connectors.file_importer import detect_column_mapping, import_leads_from_file
from connectors.osm_connector import OSMConnector
from database.connection import init_db
from database.models import Business, BusinessWebsite, ImportJob, SuppressionRecord


def test_detect_column_mapping():
    cols1 = ["Company Name", "Web", "Industry", "Town", "State", "Phone Number", "Email"]
    mapping1 = detect_column_mapping(cols1)
    assert mapping1["name"] == "Company Name"
    assert mapping1["website_url"] == "Web"
    assert mapping1["category"] == "Industry"
    assert mapping1["city"] == "Town"
    assert mapping1["phone"] == "Phone Number"
    assert mapping1["email"] == "Email"

    cols2 = ["business", "site", "contact_phone"]
    mapping2 = detect_column_mapping(cols2)
    assert mapping2["name"] == "business"
    assert mapping2["website_url"] == "site"
    assert mapping2["phone"] == "contact_phone"


def test_import_leads_from_csv(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    # Pre-seed one suppression record
    session.add(SuppressionRecord(record_type="DOMAIN", value="dnc-lead.com", reason="OPT_OUT"))
    session.commit()

    # Create in-memory CSV
    csv_data = """Company,Website,Category,City,State,Country,Phone,Email
Alpha Architecture,https://alphaarch.com,Architecture,Denver,CO,United States,303-555-0111,info@alphaarch.com
Beta Dental Clinic,https://betadental.com,Dental,Denver,CO,United States,303-555-0222,smile@betadental.com
Alpha Architecture LLC,https://alphaarch.com/contact,Architecture,Denver,CO,United States,303-555-0111,info@alphaarch.com
,https://noname.com,Trade,Denver,CO,United States,303-555-0333,bad@noname.com
Blocked Corp,https://dnc-lead.com,Consulting,Denver,CO,United States,303-555-0444,optout@dnc-lead.com
"""
    csv_bytes = io.BytesIO(csv_data.encode("utf-8"))

    result = import_leads_from_file(
        file_or_path=csv_bytes,
        filename="test_leads.csv",
        session=session
    )

    assert result["success"] is True
    assert result["total_rows"] == 5
    assert result["imported_count"] == 2  # Alpha Architecture & Beta Dental
    assert result["duplicates_count"] == 1  # Alpha Architecture LLC merged into Alpha Architecture
    assert result["rejected_count"] == 2  # Missing name (1) + Suppressed domain (1)

    # Verify database state
    businesses = session.query(Business).all()
    assert len(businesses) == 2
    names = [b.name for b in businesses]
    assert "Alpha Architecture" in names
    assert "Beta Dental Clinic" in names

    # Verify import job record
    job = session.query(ImportJob).first()
    assert job is not None
    assert job.source_identifier == "test_leads.csv"
    assert job.imported_count == 2
    assert job.duplicates_count == 1

    session.close()


def test_osm_query_builder():
    connector = OSMConnector()
    query = connector.build_query(
        city="Austin",
        country="United States",
        categories=["Healthcare & Medical", "Legal & Financial Services"],
        limit=25
    )
    assert 'area["name"="Austin"]' in query
    assert '["amenity"="clinic"]' in query
    assert '["office"="lawyer"]' in query
    assert "out body 25;" in query
