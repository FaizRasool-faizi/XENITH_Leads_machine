"""Observable website opportunity analysis engine for XENITH Solutions."""
import re
from typing import Optional
from bs4 import BeautifulSoup
from analyzer.crawler import CrawlResult

# Known live chat and support widget script indicators
CHATBOT_SIGNALS = [
    "intercom", "drift", "crisp.chat", "tidio", "zendesk", "livechat",
    "freshchat", "hubspot-messages", "tawk.to", "smartsupp", "chaport",
    "chatra", "zoho.salesiq", "botpress", "voiceflow"
]

# Known online booking and scheduling platforms
BOOKING_SIGNALS = [
    "calendly", "acuityscheduling", "fresha", "booksy", "jane.app",
    "appointlet", "youcanbook.me", "setmore", "square.site/appointments",
    "opentable", "resy", "vagaro", "mindbodyonline", "hubspot.com/meetings"
]


class OpportunityFinding:
    """Represents a factual, verifiable observation indicating a service opportunity."""

    def __init__(
        self,
        finding_category: str,
        short_explanation: str,
        evidence_url: str,
        recommended_service: str,
        confidence: str = "HIGH",
        verification_status: str = "OBSERVED"
    ):
        self.finding_category = finding_category
        self.short_explanation = short_explanation
        self.evidence_url = evidence_url
        self.recommended_service = recommended_service
        self.confidence = confidence
        self.verification_status = verification_status


def analyze_opportunities(
    crawl_result: CrawlResult,
    business_name: str,
    business_category: Optional[str] = None
) -> list[OpportunityFinding]:
    """
    Perform observable opportunity checks based strictly on verifiable facts.
    Never hallucinates issues; each finding corresponds to observable DOM or HTTP characteristics.
    """
    findings: list[OpportunityFinding] = []
    target_url = crawl_result.target_url
    cat = (business_category or "").lower()

    # 1. Check for Missing Website or HTTP Failure
    if not crawl_result.is_reachable:
        if crawl_result.http_status in (404, 500, 502, 503):
            findings.append(
                OpportunityFinding(
                    finding_category="WEBSITE_DEVELOPMENT",
                    short_explanation=f"Website returns server error ({crawl_result.http_status}), preventing customer access.",
                    evidence_url=target_url,
                    recommended_service="Website Design & Development",
                    confidence="HIGH"
                )
            )
        elif crawl_result.error_message:
            findings.append(
                OpportunityFinding(
                    finding_category="WEBSITE_DEVELOPMENT",
                    short_explanation=f"Website is unreachable or offline: {crawl_result.error_message}",
                    evidence_url=target_url,
                    recommended_service="Website Design & Development",
                    confidence="HIGH"
                )
            )
        return findings

    soup = crawl_result.soup
    if not soup:
        return findings

    html_lower = crawl_result.html_content.lower()

    # 2. Check for SSL / HTTPS Security
    if not crawl_result.has_ssl or crawl_result.final_url.startswith("http://"):
        findings.append(
            OpportunityFinding(
                finding_category="WEBSITE_DEVELOPMENT",
                short_explanation="Website operates on unencrypted HTTP without SSL certification, risking browser warnings.",
                evidence_url=crawl_result.final_url,
                recommended_service="Website Design & Development",
                confidence="HIGH"
            )
        )

    # 3. Check for Mobile Responsiveness (Viewport Meta Tag)
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if not viewport:
        findings.append(
            OpportunityFinding(
                finding_category="WEBSITE_DEVELOPMENT",
                short_explanation="Missing viewport meta tag, indicating legacy non-mobile-responsive layout on mobile devices.",
                evidence_url=crawl_result.final_url,
                recommended_service="Website Design & Development",
                confidence="HIGH"
            )
        )

    # 4. Check for SEO Metadata (Title & Meta Description)
    if not crawl_result.page_title or len(crawl_result.page_title) < 10:
        findings.append(
            OpportunityFinding(
                finding_category="WEBSITE_DEVELOPMENT",
                short_explanation="Homepage lacks a descriptive title tag (<10 characters), impairing search visibility.",
                evidence_url=crawl_result.final_url,
                recommended_service="Website Design & Development",
                confidence="MEDIUM"
            )
        )

    if not crawl_result.meta_description:
        findings.append(
            OpportunityFinding(
                finding_category="WEBSITE_DEVELOPMENT",
                short_explanation="Homepage lacks an SEO meta description tag, leading to unformatted search snippets.",
                evidence_url=crawl_result.final_url,
                recommended_service="Website Design & Development",
                confidence="MEDIUM"
            )
        )

    # 5. Check for AI Chatbot / Live Support Widget
    has_chat = any(signal in html_lower for signal in CHATBOT_SIGNALS)
    has_faq = any(kw in html_lower for kw in ["frequently asked", "faq", "q&a", "help center", "knowledge base"])
    
    if not has_chat:
        findings.append(
            OpportunityFinding(
                finding_category="AI_CHATBOT",
                short_explanation="No interactive customer chat or AI assistant detected on site; inquiries rely solely on static forms or phone.",
                evidence_url=crawl_result.final_url,
                recommended_service="AI Chatbots & Customer Support Agents",
                confidence="HIGH"
            )
        )

    # 6. Check for Online Booking & Workflow Automation
    has_booking = any(signal in html_lower for signal in BOOKING_SIGNALS)
    service_oriented = any(kw in cat for kw in ["clinic", "dental", "doctor", "lawyer", "legal", "plumber", "hvac", "electrician", "consult", "salon", "repair"])
    
    if not has_booking and service_oriented:
        findings.append(
            OpportunityFinding(
                finding_category="BOOKING_AUTOMATION",
                short_explanation=f"Service business ({business_category or 'services'}) has no direct online booking/scheduling tool; relies on manual contact.",
                evidence_url=crawl_result.final_url,
                recommended_service="AI Workflow & Process Automation",
                confidence="HIGH"
            )
        )

    # 7. Check for AI Calling Agent Candidates
    has_phone_cta = any(kw in html_lower for kw in ["call us today", "call for appointment", "call now", "call for quote", "speak to an expert"])
    if has_phone_cta and not has_booking:
        findings.append(
            OpportunityFinding(
                finding_category="AI_CALLING_AGENT",
                short_explanation="Business advertises heavy phone-first inquiry routing ('call now/for quote') without 24/7 automated scheduling.",
                evidence_url=crawl_result.final_url,
                recommended_service="AI Calling Agents & Voice Bots",
                confidence="MEDIUM"
            )
        )

    return findings
