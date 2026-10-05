"""Comprehensive end-to-end tests for all 14 required business scenarios."""
import pytest
from unittest.mock import patch, MagicMock
import requests
from database.connection import init_db
from database.models import Business, BusinessWebsite, ContactChannel, SuppressionRecord
from database.repository import upsert_business, is_suppressed
from analyzer.crawler import SafeCrawler, CrawlResult
from analyzer.robots_checker import RobotsChecker
from analyzer.opportunity_analyzer import analyze_opportunities
from connectors.file_importer import import_leads_from_file
from core.security import validate_url_for_crawling
from core.ai_client import LocalAIClient
import io


# Scenario 1: A valid business website
def test_scenario_01_valid_business_website():
    crawler = SafeCrawler()
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://legitbusiness.com"
        mock_resp.headers = {"Content-Type": "text/html"}
        mock_resp.iter_content.return_value = [b"<html><head><title>Legit Business</title></head><body><h1>Welcome</h1></body></html>"]
        mock_resp.__enter__.return_value = mock_resp
        mock_get.return_value = mock_resp

        res = crawler.crawl_page("https://legitbusiness.com", check_robots=False)
        assert res.is_reachable is True
        assert res.http_status == 200
        assert res.page_title == "Legit Business"


# Scenario 2: A missing website
def test_scenario_02_missing_website(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    biz, is_new, msg = upsert_business(
        session, name="No Website Co", website_url=None, city="Miami", country="United States"
    )
    assert biz.website is None
    assert is_new is True
    session.close()


# Scenario 3: A broken website (e.g. 500 / 502)
def test_scenario_03_broken_website():
    res = CrawlResult("https://brokensite.com")
    res.is_reachable = False
    res.http_status = 502
    findings = analyze_opportunities(res, "Broken Site")
    assert any(f.finding_category == "WEBSITE_DEVELOPMENT" for f in findings)
    assert any("502" in f.short_explanation for f in findings)


# Scenario 4: A website that times out
def test_scenario_04_website_timeout():
    crawler = SafeCrawler()
    with patch("analyzer.crawler.validate_url_for_crawling", return_value=(True, "")):
        with patch("requests.get", side_effect=requests.Timeout("Connection timed out")):
            res = crawler.crawl_page("https://slowsite.com", check_robots=False)
            assert res.is_reachable is False
            assert "timed out" in res.error_message.lower()


# Scenario 5: An inaccessible robots.txt file (e.g. 403 / 500 conservative fallback)
def test_scenario_05_inaccessible_robots():
    checker = RobotsChecker()
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_get.return_value = mock_resp

        # 403 on robots.txt triggers conservative refusal to crawl
        allowed = checker.is_allowed("https://forbidden-robots.com/page")
        assert allowed is False


# Scenario 6: A disallowed page under robots.txt
def test_scenario_06_disallowed_page_robots():
    checker = RobotsChecker()
    robots_content = "User-agent: *\nDisallow: /private/\nAllow: /public/"
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = robots_content
        mock_get.return_value = mock_resp

        assert checker.is_allowed("https://mysite.com/public/about") is True
        assert checker.is_allowed("https://mysite.com/private/secret") is False


# Scenario 7: A duplicate business (by domain, phone, name+city)
def test_scenario_07_duplicate_business(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    b1, is_new1, _ = upsert_business(session, name="Unique Plumber LLC", website_url="http://plumb.com", city="Dallas")
    b2, is_new2, _ = upsert_business(session, name="Unique Plumber Inc", website_url="https://plumb.com/contact", city="Dallas")
    assert is_new1 is True
    assert is_new2 is False
    assert b1.id == b2.id
    session.close()


# Scenario 8: A business with conflicting information (enrich without silent overwrite)
def test_scenario_08_conflicting_info_preservation(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    b1, _, _ = upsert_business(session, name="Dental Care", website_url="http://dentalcare.com", phone="555-0001")
    # Second import arrives with newly discovered phone number
    b2, _, _ = upsert_business(session, name="Dental Care", website_url="http://dentalcare.com", phone="555-0002")
    
    contacts = session.query(ContactChannel).filter(ContactChannel.business_id == b1.id).all()
    phone_values = [c.value for c in contacts if c.channel_type == "PHONE"]
    assert "555-0001" in phone_values
    assert "555-0002" in phone_values
    session.close()


# Scenario 9: A business with no published contact channel
def test_scenario_09_no_published_contacts(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    biz, _, _ = upsert_business(session, name="Ghost Co", website_url="http://ghostco.com")
    assert len(biz.contacts) == 0
    session.close()


# Scenario 10: A suppressed contact
def test_scenario_10_suppressed_contact(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    session.add(SuppressionRecord(record_type="EMAIL", value="ceo@suppressed.com", reason="OPT_OUT"))
    session.commit()

    biz, is_new, msg = upsert_business(session, name="Suppressed Firm", email="ceo@suppressed.com")
    assert biz is None
    assert is_new is False
    assert "SUPPRESSED" in msg
    session.close()


# Scenario 11: An invalid CSV file (missing company name header or empty file)
def test_scenario_11_invalid_csv(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    bad_csv = io.BytesIO(b"UnknownCol1,UnknownCol2\nVal1,Val2\n")
    res = import_leads_from_file(bad_csv, "corrupt.csv", session)
    assert res["success"] is False
    assert "Missing required company name column" in res["error"]
    session.close()


# Scenario 12: A malicious URL or redirect to private network (SSRF protection)
def test_scenario_12_malicious_ssrf_url():
    # Loopback
    safe, msg = validate_url_for_crawling("http://127.0.0.1:8000/api")
    assert safe is False
    assert "SSRF" in msg

    # AWS metadata IP
    safe, msg = validate_url_for_crawling("http://169.254.169.254/latest/meta-data")
    assert safe is False

    # Private RFC 1918
    safe, msg = validate_url_for_crawling("http://10.0.0.1/admin")
    assert safe is False


# Scenario 13: An unavailable optional AI model
def test_scenario_13_unavailable_ai_model():
    client = LocalAIClient(base_url="http://127.0.0.1:54321")
    is_up, _ = client.is_available()
    assert is_up is False
    # Generates None cleanly without crashing
    assert client.generate_completion("Test") is None


# Scenario 14: A failed database operation / transaction rollback
def test_scenario_14_failed_database_rollback(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    # Attempt inserting an invalid model missing required non-null field
    try:
        from database.models import Business
        bad_biz = Business(name=None)
        session.add(bad_biz)
        session.commit()
    except Exception:
        session.rollback()

    # Session remains healthy and usable after rollback
    good_biz = Business(name="Healthy Business Inc", normalized_name="healthy business")
    session.add(good_biz)
    session.commit()
    assert good_biz.id is not None
    session.close()
