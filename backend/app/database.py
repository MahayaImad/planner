"""Connexion SQLAlchemy + session factory."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dépendance FastAPI : fournit une session DB et la ferme après la requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
