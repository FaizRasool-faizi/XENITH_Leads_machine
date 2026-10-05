"""Jurisdictional marketing compliance guidelines and warning generator."""

JURISDICTION_POLICIES = {
    "United States": {
        "regulations": ["CAN-SPAM Act (15 U.S.C. 7701)", "TCPA (47 U.S.C. 227)"],
        "email_rules": [
            "Do not use false or misleading header information.",
            "Do not use deceptive subject lines.",
            "Identify the message as an advertisement.",
            "Include a valid physical postal address of XENITH Solutions.",
            "Provide a clear, conspicuous opt-out/unsubscribe mechanism and honor it within 10 days."
        ],
        "calling_rules": [
            "Prohibits automated marketing calls without prior express written consent.",
            "Do not call numbers on the National Do Not Call Registry."
        ],
        "risk_level": "Moderate (Requires strict opt-out handling and truthful subject lines)"
    },
    "Canada": {
        "regulations": ["CASL (Canada's Anti-Spam Legislation)"],
        "email_rules": [
            "Strict opt-in regime: Sending Commercial Electronic Messages (CEM) requires express or existing implied consent.",
            "Conspicuously published business emails qualify for implied consent ONLY if relevant to the recipient's business role AND not accompanied by a statement refusing unsolicited messages.",
            "Clear sender identification and working unsubscribe link mandatory."
        ],
        "calling_rules": [
            "CRTC National Do Not Call List rules apply.",
            "Automated calling requires prior consent."
        ],
        "risk_level": "Strict (Verify published role relevance before sending CEM)"
    },
    "Australia": {
        "regulations": ["Spam Act 2003 (Cth)"],
        "email_rules": [
            "Consent required (express or inferred). Inferred consent exists for conspicuously published business addresses relevant to business capacity without a 'no spam' notice.",
            "Accurate sender identity details must be present.",
            "Functional unsubscribe facility required (must remain active for at least 30 days)."
        ],
        "calling_rules": [
            "Do Not Call Register Act 2006 applies to telemarketing."
        ],
        "risk_level": "Strict (Respect 'no unsolicited messages' notices on websites)"
    },
    "United Arab Emirates": {
        "regulations": ["TDRA Unsolicited Electronic Communications Framework", "Cabinet Resolution No. 56 of 2024"],
        "email_rules": [
            "Prior commercial relationship or consent required.",
            "Sender company identity and registration license details must be identifiable.",
            "Opt-out option required in all correspondence."
        ],
        "calling_rules": [
            "Telemarketing cold calls are heavily regulated by TDRA and require licensed operation and strict calling hours (9 AM - 6 PM)."
        ],
        "risk_level": "Strict (Commercial licensing and consent mandatory)"
    }
}


def get_market_policy(country_name: str) -> dict:
    """Retrieve compliance requirements for a specific target market."""
    if not country_name:
        return JURISDICTION_POLICIES["United States"]
    
    country_clean = country_name.strip().lower()
    for market, policy in JURISDICTION_POLICIES.items():
        if market.lower() in country_clean or country_clean in market.lower():
            return policy

    # Gulf region check
    if any(gulf in country_clean for gulf in ["gulf", "dubai", "abu dhabi", "saudi", "qatar", "kuwait", "bahrain"]):
        return JURISDICTION_POLICIES["United Arab Emirates"]

    return JURISDICTION_POLICIES["United States"]
