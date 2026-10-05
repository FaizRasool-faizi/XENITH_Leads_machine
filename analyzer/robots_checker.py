"""Compliant robots.txt parser and domain policy cache."""
import time
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import requests
from core.config import settings
from core.security import validate_url_for_crawling
from core.logging import get_logger

logger = get_logger("robots_checker")


class RobotsChecker:
    """Manages cached robots.txt files with conservative fallback."""

    def __init__(self):
        self._cache: dict[str, tuple[float, RobotFileParser, bool]] = {}  # domain -> (timestamp, parser, is_allowed_default)

    def _fetch_robots_txt(self, base_url: str) -> tuple[RobotFileParser, bool]:
        """Fetch and parse robots.txt for a given base URL."""
        parsed = urlparse(base_url)
        domain = parsed.netloc.lower()
        now = time.time()

        # Cache check (1 hour TTL)
        if domain in self._cache:
            ts, parser, allow_default = self._cache[domain]
            if now - ts < 3600:
                return parser, allow_default

        robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
        parser = RobotFileParser()
        parser.set_url(robots_url)

        # Validate SSRF
        is_safe, reason = validate_url_for_crawling(robots_url)
        if not is_safe:
            logger.warning(f"robots.txt URL failed security check: {reason}")
            self._cache[domain] = (now, parser, False)
            return parser, False

        try:
            resp = requests.get(
                robots_url,
                headers={"User-Agent": settings.DEFAULT_USER_AGENT},
                timeout=settings.REQUEST_TIMEOUT_SECONDS
            )
            if resp.status_code == 200:
                parser.parse(resp.text.splitlines())
                self._cache[domain] = (now, parser, True)
                return parser, True
            elif resp.status_code in (404, 410):
                # Standard web convention: 404 means no robots restrictions
                self._cache[domain] = (now, parser, True)
                return parser, True
            elif resp.status_code in (401, 403):
                # Access denied to robots.txt: conservative stance, do not crawl
                logger.info(f"Access denied ({resp.status_code}) to robots.txt on {domain}. Respecting prohibition.")
                self._cache[domain] = (now, parser, False)
                return parser, False
            else:
                self._cache[domain] = (now, parser, True)
                return parser, True
        except Exception as e:
            # Conservative policy on error: disallow if uncertain
            logger.warning(f"Could not retrieve robots.txt from {domain}: {e}. Conservative fallback active.")
            self._cache[domain] = (now, parser, False)
            return parser, False

    def is_allowed(self, target_url: str, user_agent: str = None) -> bool:
        """Check if target_url can be crawled under robots.txt."""
        ua = user_agent or settings.DEFAULT_USER_AGENT
        parser, default_allow = self._fetch_robots_txt(target_url)
        if not default_allow:
            return False
        try:
            return parser.can_fetch(ua, target_url)
        except Exception:
            return default_allow
