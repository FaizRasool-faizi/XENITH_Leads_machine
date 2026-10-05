"""Application configuration settings."""
import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class ScoringWeights(BaseModel):
    legitimacy: int = Field(default=20, ge=0, le=100)
    relevance: int = Field(default=20, ge=0, le=100)
    opportunity: int = Field(default=25, ge=0, le=100)
    contact_availability: int = Field(default=15, ge=0, le=100)
    evidence_quality: int = Field(default=20, ge=0, le=100)


class Settings(BaseModel):
    APP_NAME: str = "XENITH Lead Generator"
    APP_VERSION: str = "1.0.0"
    COMPANY_NAME: str = "XENITH Solutions"
    DATABASE_PATH: Path = DATA_DIR / "xenith_leads.db"
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH.as_posix()}"
    
    # Crawler and HTTP settings
    REQUEST_TIMEOUT_SECONDS: int = 10
    MAX_RESPONSE_BYTES: int = 2 * 1024 * 1024  # 2 MB limit
    RATE_LIMIT_SECONDS: float = 1.0
    DEFAULT_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (XENITH-Lead-Prospector/1.0; +https://xenithsolutions.ai)"
    )
    
    # Target markets supported
    TARGET_MARKETS: list[str] = [
        "United States",
        "Canada",
        "Australia",
        "United Arab Emirates",
        "Saudi Arabia",
        "Qatar"
    ]
    
    # Core XENITH Services for matching
    OFFERED_SERVICES: list[str] = [
        "Website Design & Development",
        "Custom Web Applications & Software",
        "AI Chatbots & Customer Support Agents",
        "AI Workflow & Process Automation",
        "AI Calling Agents & Voice Bots",
        "CRM & Systems Integration",
        "Generative AI Solutions & Consulting"
    ]
    
    # Default scoring weights
    SCORING_WEIGHTS: ScoringWeights = ScoringWeights()
    SCORE_HIGH_PRIORITY_THRESHOLD: int = 80
    SCORE_POTENTIAL_THRESHOLD: int = 60
    
    # Optional local AI settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:latest"
    OLLAMA_ENABLED: bool = False


settings = Settings()
