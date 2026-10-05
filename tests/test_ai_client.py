"""Unit tests for optional local AI client and graceful offline fallback."""
from core.ai_client import LocalAIClient


def test_ai_client_offline_graceful_fallback():
    # Point client to a guaranteed non-existent local port
    client = LocalAIClient(base_url="http://127.0.0.1:59999", default_model="llama3")
    
    # 1. is_available should return False with empty models without throwing exception
    available, models = client.is_available()
    assert available is False
    assert models == []

    # 2. generate_completion should return None cleanly
    resp = client.generate_completion("Test prompt")
    assert resp is None

    # 3. enhance_outreach should return original draft untouched
    base_text = "Hello Company, here is your outreach draft. Opt-out: Reply unsubscribe."
    result = client.enhance_outreach(
        company_name="Acme Corp",
        category="Trade",
        service="Web Development",
        observations=["Missing viewport tag"],
        base_draft=base_text
    )
    assert result == base_text
