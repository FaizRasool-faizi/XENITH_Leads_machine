"""OpenStreetMap (Overpass API) business discovery connector."""
import time
import requests
from typing import Optional
from connectors.base import BaseConnector, DiscoveredLead
from core.config import settings
from core.logging import get_logger

logger = get_logger("osm_connector")

# Standard business category queries mapped to OpenStreetMap tags
OSM_CATEGORY_TAGS = {
    "Healthcare & Medical": [
        '["amenity"="clinic"]',
        '["amenity"="dentist"]',
        '["amenity"="doctors"]',
        '["healthcare"="clinic"]'
    ],
    "Legal & Financial Services": [
        '["office"="lawyer"]',
        '["office"="accountant"]',
        '["office"="financial"]',
        '["office"="insurance"]'
    ],
    "Consulting & IT Companies": [
        '["office"="it"]',
        '["office"="company"]',
        '["office"="consulting"]'
    ],
    "Trades & Contractors (HVAC, Plumbing, Electrical)": [
        '["craft"="plumber"]',
        '["craft"="electrician"]',
        '["craft"="hvac"]',
        '["craft"="builder"]',
        '["craft"="roofer"]'
    ],
    "Hospitality & Dining": [
        '["amenity"="restaurant"]',
        '["amenity"="cafe"]'
    ],
    "Automotive & Repair": [
        '["shop"="car_repair"]',
        '["shop"="car"]'
    ],
    "Real Estate": [
        '["office"="estate_agent"]'
    ]
}

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]


class OSMConnector(BaseConnector):
    """OpenStreetMap discovery client with Overpass query generator."""

    def __init__(self):
        super().__init__(
            name="OpenStreetMap",
            source_url="https://www.openstreetmap.org"
        )
        self.attribution = "© OpenStreetMap contributors. Data available under the Open Database License (ODbL)."

    def verify_terms(self) -> tuple[bool, str]:
        return (
            True,
            "OSM data is freely usable for commercial/business prospecting under the Open Database License (ODbL) with attribution."
        )

    def build_query(
        self,
        city: str,
        country: Optional[str] = None,
        categories: Optional[list[str]] = None,
        limit: int = 50
    ) -> str:
        """Construct an Overpass QL query string."""
        selected_cats = categories or list(OSM_CATEGORY_TAGS.keys())
        tag_filters = []
        for cat in selected_cats:
            if cat in OSM_CATEGORY_TAGS:
                tag_filters.extend(OSM_CATEGORY_TAGS[cat])

        # If none matched, default to general offices & clinics
        if not tag_filters:
            tag_filters = ['["office"="company"]', '["office"="lawyer"]', '["amenity"="clinic"]']

        filter_block = ""
        for tag in tag_filters:
            filter_block += f'  node{tag}(area.searchArea)["name"];\n'
            filter_block += f'  way{tag}(area.searchArea)["name"];\n'

        # Geocode area query
        area_search = f'area["name"="{city}"]'
        if country:
            area_search += f'["ISO3166-1"="{country}"]' if len(country) == 2 else f'["is_in:country"="{country}"]'

        query = f"""
[out:json][timeout:30];
{area_search}->.searchArea;
(
{filter_block}
);
out body {limit};
>;
out skel qt;
"""
        return query

    def search_by_city(
        self,
        city: str,
        country: Optional[str] = None,
        categories: Optional[list[str]] = None,
        limit: int = 50
    ) -> list[DiscoveredLead]:
        """Fetch real business nodes from Overpass API."""
        query = self.build_query(city=city, country=country, categories=categories, limit=limit)
        headers = {"User-Agent": settings.DEFAULT_USER_AGENT}

        data = None
        last_error = ""

        # Try endpoints with graceful fallback
        for endpoint in OVERPASS_ENDPOINTS:
            try:
                resp = requests.post(endpoint, data={"data": query}, headers=headers, timeout=35)
                if resp.status_code == 200:
                    data = resp.json()
                    break
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
            except Exception as e:
                last_error = str(e)
                continue

        if not data or "elements" not in data:
            logger.warning(f"Overpass query returned no results or failed: {last_error}")
            return []

        leads: list[DiscoveredLead] = []
        for el in data["elements"]:
            tags = el.get("tags")
            if not tags or "name" not in tags:
                continue

            name = tags["name"].strip()
            # Extract contact and website
            website = (
                tags.get("contact:website")
                or tags.get("website")
                or tags.get("url")
            )
            phone = (
                tags.get("contact:phone")
                or tags.get("phone")
            )
            email = (
                tags.get("contact:email")
                or tags.get("email")
            )

            # Determine best category label
            category = (
                tags.get("office")
                or tags.get("craft")
                or tags.get("amenity")
                or tags.get("healthcare")
                or tags.get("shop")
                or "Commercial Business"
            )
            category_title = category.replace("_", " ").title()

            node_city = tags.get("addr:city") or city
            node_state = tags.get("addr:state")
            node_country = tags.get("addr:country") or country

            leads.append(
                DiscoveredLead(
                    name=name,
                    website_url=website,
                    category=category_title,
                    city=node_city,
                    state=node_state,
                    country=node_country,
                    phone=phone,
                    email=email,
                    source_name=self.name,
                    source_reference_id=f"osm_{el.get('type')}_{el.get('id')}",
                    raw_data=tags
                )
            )

        logger.info(f"Discovered {len(leads)} genuine businesses in {city} via OpenStreetMap.")
        return leads

    def search(self, **kwargs) -> list[DiscoveredLead]:
        city = kwargs.get("city", "Austin")
        country = kwargs.get("country")
        categories = kwargs.get("categories")
        limit = kwargs.get("limit", 50)
        return self.search_by_city(city=city, country=country, categories=categories, limit=limit)
