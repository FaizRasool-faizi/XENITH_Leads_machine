"""Base interface for all data discovery connectors."""
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, Field


class DiscoveredLead(BaseModel):
    """Normalized prospect record discovered by a connector."""
    name: str = Field(..., min_length=1)
    website_url: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    source_name: str
    source_reference_id: Optional[str] = None
    raw_data: Optional[dict] = None


class BaseConnector(ABC):
    """Abstract connector base class."""
    
    def __init__(self, name: str, source_url: str):
        self.name = name
        self.source_url = source_url

    @abstractmethod
    def verify_terms(self) -> tuple[bool, str]:
        """Verify whether automated collection is permitted under source terms."""
        pass

    @abstractmethod
    def search(self, **kwargs) -> list[DiscoveredLead]:
        """Execute discovery search and return normalized leads."""
        pass
