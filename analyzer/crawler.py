"""Conservative, SSRF-safe, rate-limited web crawler."""
import time
import socket
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from core.config import settings
from core.security import validate_url_for_crawling, normalize_domain, sanitize_url
from core.logging import get_logger
from analyzer.robots_checker import RobotsChecker

logger = get_logger("crawler")


class CrawlResult:
    """Encapsulates the crawl outcome and extracted document properties."""

    def __init__(self, target_url: str):
        self.target_url = target_url
        self.is_reachable = False
        self.http_status: int = 0
        self.final_url: str = target_url
        self.page_title: str = ""
        self.meta_description: str = ""
        self.has_ssl: bool = target_url.startswith("https://")
        self.subpages_found: list[str] = []
        self.html_content: str = ""
        self.response_time_ms: float = 0.0
        self.error_message: str = ""
        self.soup: BeautifulSoup = None


class SafeCrawler:
    """Safe, ethical HTTP crawler enforcing rate limits and security boundaries."""

    def __init__(self, robots_checker: RobotsChecker = None):
        self.robots_checker = robots_checker or RobotsChecker()
        self._last_domain_request: dict[str, float] = {}

    def _enforce_rate_limit(self, domain: str):
        """Ensure minimum delay between consecutive calls to the same domain."""
        now = time.time()
        if domain in self._last_domain_request:
            elapsed = now - self._last_domain_request[domain]
            if elapsed < settings.RATE_LIMIT_SECONDS:
                sleep_needed = settings.RATE_LIMIT_SECONDS - elapsed
                time.sleep(sleep_needed)
        self._last_domain_request[domain] = time.time()

    def crawl_page(self, raw_url: str, check_robots: bool = True) -> CrawlResult:
        """Fetch and analyze a single website entry point safely."""
        clean_url = sanitize_url(raw_url)
        result = CrawlResult(clean_url)

        if not clean_url:
            result.error_message = "Invalid or empty URL."
            return result

        domain = normalize_domain(clean_url)

        # 1. SSRF and Protocol check
        is_safe, sec_reason = validate_url_for_crawling(clean_url)
        if not is_safe:
            result.error_message = f"Security check rejected URL: {sec_reason}"
            logger.warning(f"Blocked crawl on {clean_url}: {sec_reason}")
            return result

        # 2. robots.txt check
        if check_robots:
            if not self.robots_checker.is_allowed(clean_url):
                result.error_message = "Crawling prohibited by website robots.txt or access policy."
                logger.info(f"Skipping {clean_url} due to robots.txt prohibition.")
                return result

        # 3. Rate limiting
        self._enforce_rate_limit(domain)

        headers = {
            "User-Agent": settings.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # 4. Execute streaming request to guard against oversized payloads
        start_time = time.time()
        try:
            with requests.get(
                clean_url,
                headers=headers,
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
                stream=True,
                allow_redirects=True
            ) as resp:
                result.response_time_ms = round((time.time() - start_time) * 1000, 2)
                result.http_status = resp.status_code
                result.final_url = str(resp.url)
                result.has_ssl = result.final_url.startswith("https://")

                # Verify final redirect target against SSRF
                if result.final_url != clean_url:
                    is_final_safe, final_reason = validate_url_for_crawling(result.final_url)
                    if not is_final_safe:
                        result.error_message = f"Redirect target rejected by SSRF protection: {final_reason}"
                        return result

                if resp.status_code != 200:
                    result.error_message = f"HTTP {resp.status_code}"
                    result.is_reachable = False
                    return result

                # Check Content-Type header
                content_type = resp.headers.get("Content-Type", "").lower()
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    result.error_message = f"Unsupported content type '{content_type}'. Non-HTML content skipped."
                    return result

                # Read body chunked up to MAX_RESPONSE_BYTES
                chunks = []
                bytes_read = 0
                for chunk in resp.iter_content(chunk_size=8192):
                    bytes_read += len(chunk)
                    if bytes_read > settings.MAX_RESPONSE_BYTES:
                        result.error_message = f"Response exceeded {settings.MAX_RESPONSE_BYTES} bytes limit."
                        return result
                    chunks.append(chunk)

                result.html_content = b"".join(chunks).decode("utf-8", errors="replace")
                result.is_reachable = True

        except requests.Timeout:
            result.error_message = f"Connection timed out after {settings.REQUEST_TIMEOUT_SECONDS}s."
            return result
        except requests.RequestException as e:
            result.error_message = f"Network request failed: {str(e)}"
            return result
        except Exception as e:
            result.error_message = f"Crawl error: {str(e)}"
            return result

        # 5. Parse HTML with BeautifulSoup
        try:
            soup = BeautifulSoup(result.html_content, "html.parser")
            result.soup = soup

            # Title
            if soup.title and soup.title.string:
                result.page_title = soup.title.string.strip()

            # Meta description
            desc_tag = (
                soup.find("meta", attrs={"name": "description"})
                or soup.find("meta", attrs={"property": "og:description"})
            )
            if desc_tag and desc_tag.get("content"):
                result.meta_description = desc_tag["content"].strip()

            # Subpages / link discovery
            detected_paths = set()
            subpage_keywords = ["contact", "about", "services", "book", "schedule", "pricing", "team", "faq"]
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].lower()
                for kw in subpage_keywords:
                    if kw in href:
                        full_sub = urljoin(result.final_url, a_tag["href"])
                        if normalize_domain(full_sub) == domain:
                            detected_paths.add(full_sub)

            result.subpages_found = list(detected_paths)[:10]

        except Exception as e:
            logger.warning(f"Error parsing HTML for {clean_url}: {e}")

        return result
