"""Unit and mock tests for crawler, contact extractor, and opportunity analyzer."""
import pytest
from bs4 import BeautifulSoup
from analyzer.crawler import CrawlResult
from analyzer.contact_extractor import extract_business_contacts
from analyzer.opportunity_analyzer import analyze_opportunities


SAMPLE_LEGACY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Short</title>
    <!-- Notice missing viewport and missing meta description -->
</head>
<body>
    <h1>Welcome to Bob's Plumbing & Heating</h1>
    <p>We provide full emergency plumbing and HVAC repair services.</p>
    <div class="contact-box">
        <p>Call us today for a quote: <a href="tel:+13035550199">(303) 555-0199</a></p>
        <p>Email our office: <a href="mailto:service@bobsplumbing.com">service@bobsplumbing.com</a></p>
        <p><a href="/contact-us">Send an inquiry via form</a></p>
        <p><a href="https://linkedin.com/company/bobs-plumbing">Follow our LinkedIn</a></p>
    </div>
</body>
</html>
"""

SAMPLE_MODERN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Dental Care - Premier Family Dentistry in Austin</title>
    <meta name="description" content="State of the art dental care with 24/7 online booking and patient support.">
    <script src="https://widget.intercom.io/widget/12345"></script>
</head>
<body>
    <h1>Modern Dental Care</h1>
    <p>Schedule your visit today: <a href="https://calendly.com/moderndental/consult">Book Online</a></p>
    <a href="mailto:office@moderndental.com">office@moderndental.com</a>
</body>
</html>
"""


def test_extract_business_contacts():
    soup = BeautifulSoup(SAMPLE_LEGACY_HTML, "html.parser")
    contacts = extract_business_contacts(soup, "https://bobsplumbing.com")

    types = {c.channel_type: c.value for c in contacts}
    assert "EMAIL" in types
    assert types["EMAIL"] == "service@bobsplumbing.com"
    assert "PHONE" in types
    assert "303" in types["PHONE"]
    assert "CONTACT_FORM" in types
    assert "https://bobsplumbing.com/contact-us" in types["CONTACT_FORM"]
    assert "LINKEDIN" in types
    assert "bobs-plumbing" in types["LINKEDIN"]


def test_legacy_site_opportunity_analysis():
    crawl_res = CrawlResult("http://bobsplumbing.com")
    crawl_res.is_reachable = True
    crawl_res.final_url = "http://bobsplumbing.com"
    crawl_res.has_ssl = False
    crawl_res.html_content = SAMPLE_LEGACY_HTML
    crawl_res.page_title = "Short"
    crawl_res.meta_description = ""
    crawl_res.soup = BeautifulSoup(SAMPLE_LEGACY_HTML, "html.parser")

    findings = analyze_opportunities(
        crawl_result=crawl_res,
        business_name="Bob's Plumbing",
        business_category="Plumber & HVAC"
    )

    categories = [f.finding_category for f in findings]
    # Should catch: SSL missing, Viewport missing, Title too short, Meta description missing, No chatbot, No booking
    assert "WEBSITE_DEVELOPMENT" in categories
    assert "AI_CHATBOT" in categories
    assert "BOOKING_AUTOMATION" in categories
    assert "AI_CALLING_AGENT" in categories

    explanations = " ".join([f.short_explanation for f in findings])
    assert "SSL" in explanations
    assert "viewport" in explanations
    assert "booking" in explanations


def test_modern_site_opportunity_analysis():
    crawl_res = CrawlResult("https://moderndental.com")
    crawl_res.is_reachable = True
    crawl_res.final_url = "https://moderndental.com"
    crawl_res.has_ssl = True
    crawl_res.html_content = SAMPLE_MODERN_HTML
    crawl_res.page_title = "Modern Dental Care - Premier Family Dentistry in Austin"
    crawl_res.meta_description = "State of the art dental care with 24/7 online booking and patient support."
    crawl_res.soup = BeautifulSoup(SAMPLE_MODERN_HTML, "html.parser")

    findings = analyze_opportunities(
        crawl_result=crawl_res,
        business_name="Modern Dental Care",
        business_category="Dentist"
    )

    categories = [f.finding_category for f in findings]
    # Modern site has viewport, good title, description, SSL, Intercom chatbot, and Calendly booking
    assert "WEBSITE_DEVELOPMENT" not in categories
    assert "AI_CHATBOT" not in categories
    assert "BOOKING_AUTOMATION" not in categories


def test_unreachable_site_opportunity_analysis():
    crawl_res = CrawlResult("https://offlinebiz.com")
    crawl_res.is_reachable = False
    crawl_res.http_status = 502
    crawl_res.error_message = "HTTP 502 Bad Gateway"

    findings = analyze_opportunities(
        crawl_result=crawl_res,
        business_name="Offline Biz",
        business_category="Consulting"
    )

    assert len(findings) == 1
    assert findings[0].finding_category == "WEBSITE_DEVELOPMENT"
    assert "502" in findings[0].short_explanation
