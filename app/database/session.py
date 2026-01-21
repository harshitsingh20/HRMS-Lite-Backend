from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Database setup
database_url = settings.get_database_url()
engine = create_engine(
    database_url,
    echo=False,
    pool_size=1,
    max_overflow=0,
    connect_args={"connect_timeout": 10, "keepalives": 1, "keepalives_idle": 30}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
