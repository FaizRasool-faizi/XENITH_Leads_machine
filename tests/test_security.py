"""Unit tests for security, SSRF validation, and domain normalization."""
import pytest
from core.security import (
    normalize_domain,
    is_ip_blocked,
    validate_url_for_crawling,
    sanitize_url
)


def test_normalize_domain():
    assert normalize_domain("https://www.example.com/path?arg=1") == "example.com"
    assert normalize_domain("http://sub.domain.co.uk:8080/index.html") == "sub.domain.co.uk"
    assert normalize_domain("www.xenithsolutions.ai") == "xenithsolutions.ai"
    assert normalize_domain("my-biz.com/") == "my-biz.com"
    assert normalize_domain("") == ""


def test_ssrf_blocked_ips():
    # Loopback
    assert is_ip_blocked("127.0.0.1") is True
    assert is_ip_blocked("127.255.255.255") is True
    assert is_ip_blocked("::1") is True
    
    # Private RFC 1918
    assert is_ip_blocked("10.0.0.1") is True
    assert is_ip_blocked("192.168.1.1") is True
    assert is_ip_blocked("172.16.0.5") is True
    
    # Cloud metadata link-local
    assert is_ip_blocked("169.254.169.254") is True
    
    # Public IPs should NOT be blocked
    assert is_ip_blocked("8.8.8.8") is False
    assert is_ip_blocked("1.1.1.1") is False


def test_validate_url_for_crawling():
    # Reject bad protocols
    is_safe, reason = validate_url_for_crawling("ftp://example.com")
    assert is_safe is False
    assert "scheme" in reason.lower()
    
    is_safe, reason = validate_url_for_crawling("file:///C:/Windows/system.ini")
    assert is_safe is False

    # Reject localhost / direct private IPs
    is_safe, reason = validate_url_for_crawling("http://127.0.0.1/admin")
    assert is_safe is False
    assert "SSRF" in reason

    is_safe, reason = validate_url_for_crawling("http://192.168.1.1:8080/")
    assert is_safe is False
    assert "SSRF" in reason

    is_safe, reason = validate_url_for_crawling("http://169.254.169.254/latest/meta-data/")
    assert is_safe is False
    assert "SSRF" in reason

    # Localhost hostname resolution
    is_safe, reason = validate_url_for_crawling("http://localhost:3000")
    assert is_safe is False

    # Valid public URL
    is_safe, reason = validate_url_for_crawling("https://example.com")
    assert is_safe is True
    assert reason == ""


def test_sanitize_url():
    assert sanitize_url("example.com") == "https://example.com"
    assert sanitize_url("http://example.com/test#section") == "http://example.com/test"
