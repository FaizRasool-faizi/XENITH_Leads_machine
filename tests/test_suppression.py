"""Unit tests for compliance policies and suppression list management."""
import pytest
from database.connection import init_db
from database.models import Business, SuppressionRecord
from compliance.suppression import add_suppression_entry, delete_business_data
from compliance.policies import get_market_policy
from database.repository import is_suppressed


def test_add_suppression_entry(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    # Add domain suppression
    success, msg = add_suppression_entry(
        session, "DOMAIN", "https://www.donotcallme.com/about", reason="OPT_OUT"
    )
    assert success is True
    assert "donotcallme.com" in msg

    # Re-adding should fail gracefully
    success2, msg2 = add_suppression_entry(
        session, "DOMAIN", "donotcallme.com", reason="OPT_OUT"
    )
    assert success2 is False
    assert "already present" in msg2

    # Verify is_suppressed catches it
    suppressed, reason = is_suppressed(session, domain="https://donotcallme.com")
    assert suppressed is True

    session.close()


def test_delete_business_data_purge(temp_db):
    engine, Session = temp_db
    init_db(engine)
    session = Session()

    biz = Business(name="Delete Me Inc", normalized_name="delete me")
    session.add(biz)
    session.commit()
    biz_id = biz.id

    assert session.query(Business).filter(Business.id == biz_id).first() is not None

    # Execute purge
    deleted = delete_business_data(session, biz_id, reason="User GDPR deletion request")
    assert deleted is True
    assert session.query(Business).filter(Business.id == biz_id).first() is None

    session.close()


def test_market_policies():
    us_pol = get_market_policy("United States")
    assert "CAN-SPAM" in us_pol["regulations"][0]

    can_pol = get_market_policy("Canada")
    assert "CASL" in can_pol["regulations"][0]

    uae_pol = get_market_policy("Dubai, UAE")
    assert "TDRA" in uae_pol["regulations"][0]
