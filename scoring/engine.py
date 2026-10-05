"""Multi-dimensional lead qualification and scoring engine."""
import json
from datetime import datetime, timezone
from typing import Optional
from database.models import Business, BusinessWebsite, ContactChannel, WebsiteAnalysis, LeadScore
from scoring.weights import ScoringProfile, DEFAULT_SCORING_PROFILE
from core.logging import get_logger

logger = get_logger("scoring")

HIGH_RELEVANCE_KEYWORDS = [
    "dental", "dentist", "doctor", "clinic", "health", "law", "lawyer", "attorney",
    "legal", "cpa", "accounting", "tax", "consulting", "hvac", "plumbing", "plumber",
    "electrician", "roofing", "contractor", "real estate", "realtor", "agency", "marketing",
    "auto repair", "hospitality", "hotel", "resort"
]


class ScoreResult:
    def __init__(
        self,
        total_score: int,
        priority_label: str,
        score_legitimacy: int,
        score_relevance: int,
        score_opportunity: int,
        score_contact: int,
        score_evidence: int,
        breakdown_details: list[str]
    ):
        self.total_score = total_score
        self.priority_label = priority_label
        self.score_legitimacy = score_legitimacy
        self.score_relevance = score_relevance
        self.score_opportunity = score_opportunity
        self.score_contact = score_contact
        self.score_evidence = score_evidence
        self.breakdown_details = breakdown_details


def calculate_lead_score(
    business: Business,
    profile: ScoringProfile = DEFAULT_SCORING_PROFILE
) -> ScoreResult:
    """Calculate deterministic lead score (0-100) with full evidence breakdown."""
    breakdown: list[str] = []

    # 1. Legitimacy (max 20)
    score_leg = 0
    if business.name and len(business.name.strip()) > 2:
        score_leg += 5
        breakdown.append("+5: Valid registered business name")
    if business.category:
        score_leg += 5
        breakdown.append(f"+5: Identified category '{business.category}'")
    if business.city and business.country:
        score_leg += 3
        breakdown.append(f"+3: Valid location ({business.city}, {business.country})")
    if business.website and business.website.is_reachable:
        score_leg += 7
        breakdown.append("+7: Verified operational website (HTTP reachable)")
    elif business.website and business.website.http_status:
        score_leg += 2
        breakdown.append(f"+2: Website exists with HTTP status {business.website.http_status}")
    score_leg = min(score_leg, profile.max_legitimacy)

    # 2. Relevance to XENITH Services (max 20)
    score_rel = 0
    cat_lower = (business.category or "").lower()
    if any(kw in cat_lower for kw in HIGH_RELEVANCE_KEYWORDS):
        score_rel += 20
        breakdown.append("+20: High-fit vertical for XENITH AI/web/automation services")
    elif business.category:
        score_rel += 10
        breakdown.append("+10: Commercial business category")
    else:
        score_rel += 5
        breakdown.append("+5: Unclassified business prospect")
    score_rel = min(score_rel, profile.max_relevance)

    # 3. Observable Technology Opportunity (max 25)
    score_opp = 0
    num_opportunities = len(business.analyses) if business.analyses else 0
    if num_opportunities > 0:
        opp_types = {a.finding_category for a in business.analyses}
        if "WEBSITE_DEVELOPMENT" in opp_types:
            score_opp += 10
            breakdown.append("+10: Observable website modernization gap (mobile/SSL/error)")
        if "AI_CHATBOT" in opp_types:
            score_opp += 8
            breakdown.append("+8: Observable customer support / chatbot gap")
        if "BOOKING_AUTOMATION" in opp_types:
            score_opp += 10
            breakdown.append("+10: Observable manual booking/intake bottleneck")
        if "AI_CALLING_AGENT" in opp_types:
            score_opp += 7
            breakdown.append("+7: Phone-first candidate for AI voice agent")
    elif not business.website:
        score_opp += 15
        breakdown.append("+15: No website detected (candidate for new web build)")
    score_opp = min(score_opp, profile.max_opportunity)

    # 4. Business Contact Availability (max 15)
    score_con = 0
    contacts = business.contacts or []
    has_email = any(c.channel_type == "EMAIL" for c in contacts)
    has_phone = any(c.channel_type == "PHONE" for c in contacts)
    has_form = any(c.channel_type == "CONTACT_FORM" for c in contacts)

    if has_email:
        score_con += 8
        breakdown.append("+8: Official public business email available")
    if has_phone:
        score_con += 5
        breakdown.append("+5: Official business phone available")
    if has_form:
        score_con += 2
        breakdown.append("+2: Verified contact form URL available")
    score_con = min(score_con, profile.max_contact)

    # 5. Evidence Quality & Recency (max 20)
    score_evi = 0
    if business.website and business.website.last_crawled_at:
        score_evi += 12
        breakdown.append("+12: Direct website inspection completed")
    elif business.source:
        score_evi += 8
        breakdown.append(f"+8: Authorized source data ({business.source.name})")

    if num_opportunities >= 2:
        score_evi += 8
        breakdown.append("+8: Multiple corroborated technology signals")
    elif num_opportunities == 1:
        score_evi += 4
        breakdown.append("+4: Verified single technology signal")
    score_evi = min(score_evi, profile.max_evidence)

    total = score_leg + score_rel + score_opp + score_con + score_evi
    total = max(0, min(100, total))

    # Priority tiering
    if total >= profile.high_priority_min:
        priority = "HIGH_PRIORITY"
    elif total >= profile.potential_prospect_min:
        priority = "POTENTIAL_PROSPECT"
    else:
        priority = "NEEDS_RESEARCH"

    return ScoreResult(
        total_score=total,
        priority_label=priority,
        score_legitimacy=score_leg,
        score_relevance=score_rel,
        score_opportunity=score_opp,
        score_contact=score_con,
        score_evidence=score_evi,
        breakdown_details=breakdown
    )


def apply_lead_score_to_business(
    session,
    business_id: int,
    profile: ScoringProfile = DEFAULT_SCORING_PROFILE,
    override_score: Optional[int] = None,
    override_reason: Optional[str] = None
) -> LeadScore:
    """Calculate and persist or update the score record for a given business."""
    biz = session.query(Business).filter(Business.id == business_id).first()
    if not biz:
        raise ValueError(f"Business with ID {business_id} not found.")

    score_res = calculate_lead_score(biz, profile)

    lead_score = session.query(LeadScore).filter(LeadScore.business_id == business_id).first()
    if not lead_score:
        lead_score = LeadScore(business_id=business_id)
        session.add(lead_score)

    if override_score is not None:
        lead_score.total_score = max(0, min(100, override_score))
        lead_score.is_overridden = True
        lead_score.override_reason = override_reason or "Manual reviewer adjustment"
        if lead_score.total_score >= profile.high_priority_min:
            lead_score.priority_label = "HIGH_PRIORITY"
        elif lead_score.total_score >= profile.potential_prospect_min:
            lead_score.priority_label = "POTENTIAL_PROSPECT"
        else:
            lead_score.priority_label = "NEEDS_RESEARCH"
    else:
        lead_score.total_score = score_res.total_score
        lead_score.priority_label = score_res.priority_label
        lead_score.is_overridden = False
        lead_score.override_reason = None

    lead_score.score_legitimacy = score_res.score_legitimacy
    lead_score.score_relevance = score_res.score_relevance
    lead_score.score_opportunity = score_res.score_opportunity
    lead_score.score_contact = score_res.score_contact
    lead_score.score_evidence = score_res.score_evidence
    lead_score.score_breakdown = json.dumps(score_res.breakdown_details)
    lead_score.updated_at = datetime.now(timezone.utc)

    # Set business verification status to VERIFIED only if legitimate
    if score_res.score_legitimacy >= 15:
        biz.verification_status = "VERIFIED"

    session.commit()
    return lead_score
