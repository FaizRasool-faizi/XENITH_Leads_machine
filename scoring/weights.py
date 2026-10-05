"""Scoring weight configuration profiles."""
from pydantic import BaseModel, Field


class ScoringProfile(BaseModel):
    max_legitimacy: int = Field(default=20, ge=0, le=100)
    max_relevance: int = Field(default=20, ge=0, le=100)
    max_opportunity: int = Field(default=25, ge=0, le=100)
    max_contact: int = Field(default=15, ge=0, le=100)
    max_evidence: int = Field(default=20, ge=0, le=100)

    # Thresholds
    high_priority_min: int = Field(default=80, ge=0, le=100)
    potential_prospect_min: int = Field(default=60, ge=0, le=100)


DEFAULT_SCORING_PROFILE = ScoringProfile()
