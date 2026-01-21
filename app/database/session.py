import logging
import time
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from app.config import settings

logger = logging.getLogger(__name__)

# Database setup
database_url = settings.get_database_url()
_db_target = make_url(database_url)
engine = create_engine(
    database_url,
    echo=False,
    pool_size=1,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=900,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 30,
        "keepalives": 1,
        "keepalives_idle": 30,
    },
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_db_ready(max_attempts: int = 10, delay_seconds: int = 6) -> None:
    """Try connecting a few times before giving up."""
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            logger.warning(
                "Database connection attempt %s/%s to %s:%s failed: %s",
                attempt,
                max_attempts,
                _db_target.host,
                _db_target.port,
                exc,
            )
            if attempt == max_attempts:
                logger.error(
                    "Unable to reach database at %s:%s after %s attempts. "
                    "Verify network egress, IP allowlist/VPC settings, and credentials.",
                    _db_target.host,
                    _db_target.port,
                    max_attempts,
                )
                raise
            time.sleep(delay_seconds * attempt)


def init_db():
    """Initialize database tables"""
    _ensure_db_ready()
    Base.metadata.create_all(bind=engine)
