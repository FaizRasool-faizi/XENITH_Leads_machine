"""Authorized commercial directory & registry connector."""
from typing import Optional
from connectors.base import BaseConnector, DiscoveredLead
from core.logging import get_logger

logger = get_logger("directory_connector")


class DirectoryConnector(BaseConnector):
    """
    Extensible connector for public commercial directories and registries.
    Enforces explicit verification of terms before enabling automated requests.
    """

    def __init__(
        self,
        name: str,
        source_url: str,
        terms_reviewed: bool = False,
        collection_permitted: bool = False,
        license_type: str = "Authorized Public Registry",
        attribution_required: bool = True,
        attribution_text: Optional[str] = None
    ):
        super().__init__(name=name, source_url=source_url)
        self.terms_reviewed = terms_reviewed
        self.collection_permitted = collection_permitted
        self.license_type = license_type
        self.attribution_required = attribution_required
        self.attribution_text = attribution_text or f"Data sourced from {name}."

    def verify_terms(self) -> tuple[bool, str]:
        if not self.terms_reviewed:
            return False, f"Terms for '{self.name}' have not yet been verified. Automated collection disabled."
        if not self.collection_permitted:
            return False, f"Source '{self.name}' does not permit automated collection. Please use lawful manual CSV import."
        return True, f"Verified: Automated collection permitted under {self.license_type}."

    def search(self, **kwargs) -> list[DiscoveredLead]:
        is_allowed, reason = self.verify_terms()
        if not is_allowed:
            logger.warning(f"Blocked discovery on '{self.name}': {reason}")
            raise PermissionError(reason)
            
        # Extensible implementation for authorized endpoints
        logger.info(f"Directory '{self.name}' queried with authorized criteria: {kwargs}")
        return []
