"""Security utilities, SSRF prevention, and safe URL validation."""
import ipaddress
import socket
from urllib.parse import urlparse, urlunparse
from core.errors import SecurityError
from core.logging import get_logger

logger = get_logger("security")

# Disallowed IP networks for SSRF protection
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network
    ipaddress.ip_network("10.0.0.0/8"),         # Private-Use (RFC 1918)
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback
    ipaddress.ip_network("169.254.0.0/16"),     # Link-Local (AWS/GCP metadata!)
    ipaddress.ip_network("172.16.0.0/12"),      # Private-Use (RFC 1918)
    ipaddress.ip_network("192.168.0.0/16"),     # Private-Use (RFC 1918)
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved for future use
    ipaddress.ip_network("::/128"),             # Unspecified
    ipaddress.ip_network("::1/128"),            # Loopback
    ipaddress.ip_network("fc00::/7"),           # Unique Local Address (IPv6)
    ipaddress.ip_network("fe80::/10"),          # Link-Local Unicast (IPv6)
]


def normalize_domain(url_or_domain: str) -> str:
    """Extract and normalize domain from a URL or raw domain string."""
    if not url_or_domain:
        return ""
    
    val = url_or_domain.strip().lower()
    if not val.startswith(("http://", "https://")):
        val = f"http://{val}"
    
    try:
        parsed = urlparse(val)
        host = parsed.netloc or parsed.path
        # Strip port if present
        host = host.split(":")[0].strip()
        # Strip common trailing dots
        host = host.rstrip(".")
        # Strip leading www. for uniform deduplication
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def is_ip_blocked(ip_str: str) -> bool:
    """Check if an IP string belongs to any blocked / private networks."""
    try:
        ip = ipaddress.ip_address(ip_str)
        for net in BLOCKED_NETWORKS:
            if ip in net:
                return True
        return False
    except ValueError:
        return True


def validate_url_for_crawling(url: str) -> tuple[bool, str]:
    """
    Validate that a URL is safe to crawl (HTTP/HTTPS only, no SSRF, no internal IP).
    Returns (is_safe, error_reason).
    """
    if not url or not isinstance(url, str):
        return False, "Empty or non-string URL."
    
    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Malformed URL syntax: {str(e)}"
    
    if parsed.scheme not in ("http", "https"):
        return False, f"Unsupported URL scheme '{parsed.scheme}'. Only http and https permitted."
    
    hostname = parsed.hostname
    if not hostname:
        return False, "URL does not contain a valid hostname."
    
    # Check for direct IP access attempts
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if is_ip_blocked(str(ip_obj)):
            return False, f"SSRF Protection: Direct access to private/reserved IP {hostname} is prohibited."
    except ValueError:
        # Hostname is a domain, resolve via DNS
        try:
            resolved_ips = socket.getaddrinfo(hostname, None)
            for item in resolved_ips:
                sockaddr = item[4]
                ip_addr = sockaddr[0]
                if is_ip_blocked(ip_addr):
                    return False, f"SSRF Protection: Hostname '{hostname}' resolves to private/reserved IP {ip_addr}."
        except socket.gaierror:
            return False, f"DNS resolution failed for hostname '{hostname}'."
        except Exception as e:
            return False, f"Resolution error: {str(e)}"
            
    return True, ""


def sanitize_url(raw_url: str) -> str:
    """Clean and standardize a web URL."""
    if not raw_url:
        return ""
    val = raw_url.strip()
    if not val.startswith(("http://", "https://")):
        val = f"https://{val}"
    
    try:
        parsed = urlparse(val)
        # Rebuild clean URL without fragments
        clean = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            parsed.query,
            ""  # No fragment
        ))
        return clean
    except Exception:
        return val
