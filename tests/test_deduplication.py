"""Unit tests for entity deduplication and database repository."""
import pytest
from database.models import Base, Business, BusinessWebsite, ContactChannel, SuppressionRecord
from database.deduplication import normalize_business_name, normalize_phone_number
from database.repository import upsert_business, is_suppressed
from database.connection import init_db

def test_normalize_business_name():
    assert normalize_business_name("Acme Dental LLC") == "acme dental"
    assert normalize_business_name("Apex Solutions Inc.") == "apex solutions"
    assert normalize_business_name("Skyline Logistics Pty Ltd") == "skyline logistics"
    assert normalize_business_name("Dubai Trade FZE") == "dubai trade"
    assert normalize_business_name("   Multi - Space   Corp   ") == "multi space"


def test_normalize_phone_number():
    assert normalize_phone_number("+1 (555) 234-5678") == "5552345678"
    assert normalize_phone_number("1-800-555-0199") == "8005550199"
    assert normalize_phone_number("0412 345 678") == "0412345678"


def test_deduplication_and_upsert(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    # 1. Ingest initial business
    biz1, is_new1, msg1 = upsert_business(
        session=session,
        name="Global Tech Consulting LLC",
        website_url="https://www.globaltech.com",
        city="Austin",
        state="TX",
        country="United States",
        phone="555-0100",
        email="contact@globaltech.com"
    )
    session.commit()
    assert is_new1 is True
    assert biz1.id is not None
    assert biz1.website.normalized_domain == "globaltech.com"

    # 2. Ingest duplicate by domain with slightly different protocol/path
    biz2, is_new2, msg2 = upsert_business(
        session=session,
        name="Global Tech LLC",
        website_url="http://globaltech.com/about",
        city="Austin",
        country="United States"
    )
    session.commit()
    assert is_new2 is False
    assert biz2.id == biz1.id
    assert "Domain match" in msg2

    # 3. Ingest duplicate by normalized name and city without website
    biz3, is_new3, msg3 = upsert_business(
        session=session,
        name="GLOBAL TECH CONSULTING INC.",
        city="Austin",
        country="United States"
    )
    session.commit()
    assert is_new3 is False
    assert biz3.id == biz1.id

    # 4. Ingest completely distinct business
    biz4, is_new4, msg4 = upsert_business(
        session=session,
        name="Metro Plumbing Services",
        website_url="https://metroplumbing.com.au",
        city="Sydney",
        country="Australia"
    )
    session.commit()
    assert is_new4 is True
    assert biz4.id != biz1.id

    session.close()


def test_suppression_quarantine(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    # Add domain to suppression
    sup = SuppressionRecord(
        record_type="DOMAIN",
        value="badspamdomain.com",
        reason="OPT_OUT",
        notes="Requested do-not-contact"
    )
    session.add(sup)
    session.commit()

    # Attempt to upsert suppressed lead
    biz, is_new, msg = upsert_business(
        session=session,
        name="Spammy Company",
        website_url="https://www.badspamdomain.com/home",
        city="New York"
    )
    assert biz is None
    assert is_new is False
    assert "SUPPRESSED" in msg

    session.close()
