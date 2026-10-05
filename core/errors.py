"""Custom domain exception classes."""


class XenithBaseError(Exception):
    """Base error for all XENITH application exceptions."""
    pass


class SecurityError(XenithBaseError):
    """Raised when an operation violates security constraints (e.g. SSRF)."""
    pass


class CrawlerBlockedError(XenithBaseError):
    """Raised when crawling is disbarred by robots.txt or rate limits."""
    pass


class ValidationError(XenithBaseError):
    """Raised when imported data fails validation or integrity constraints."""
    pass


class DatabaseError(XenithBaseError):
    """Raised when a database transaction or operation fails."""
    pass


class SuppressionError(XenithBaseError):
    """Raised when an action is attempted on a suppressed / DNC entity."""
    pass


class ConnectorError(XenithBaseError):
    """Raised when an external discovery connector fails."""
    pass
