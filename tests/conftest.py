"""Global test fixtures and configuration."""
import pytest
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def temp_db():
    """Provides a temporary SQLite database engine for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    yield engine, Session
    engine.dispose()
    try:
        Path(db_path).unlink(missing_ok=True)
    except PermissionError:
        pass
