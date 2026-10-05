"""Database connection and session management."""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
from core.logging import get_logger
from database.models import Base, Source

logger = get_logger("database")

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(target_engine=None):
    """Create all tables and seed default sources if not present."""
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)
    
    # Seed default system sources
    with Session(eng) as session:
        default_sources = [
            {
                "name": "OpenStreetMap",
                "source_url": "https://www.openstreetmap.org",
                "terms_reviewed": True,
                "collection_permitted": True,
                "license_type": "Open Database License (ODbL)",
                "attribution_required": True,
                "attribution_text": "© OpenStreetMap contributors. Data available under the Open Database License.",
                "notes": "Used for legitimate public business entity identification under ODbL terms."
            },
            {
                "name": "Manual CSV/Excel Import",
                "source_url": "Local File",
                "terms_reviewed": True,
                "collection_permitted": True,
                "license_type": "Authorized User Data",
                "attribution_required": False,
                "attribution_text": "User provided authorized file dataset.",
                "notes": "User-supplied business records collected through lawful means."
            },
            {
                "name": "Authorized Industry Directory",
                "source_url": "https://example.com/directory",
                "terms_reviewed": True,
                "collection_permitted": True,
                "license_type": "Public Directory / Open Registry",
                "attribution_required": True,
                "attribution_text": "Public Chamber of Commerce / Commercial Directory listing.",
                "notes": "Verified business registry with public access terms."
            }
        ]
        
        for src_data in default_sources:
            existing = session.query(Source).filter_by(name=src_data["name"]).first()
            if not existing:
                src = Source(**src_data)
                session.add(src)
        session.commit()
    logger.info("Database initialized successfully.")


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        session.close()
