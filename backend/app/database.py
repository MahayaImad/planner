"""Connexion SQLAlchemy + session factory."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

# Les tâches de génération s'exécutent dans des threads séparés :
# SQLite refuse par défaut qu'une connexion change de thread.
_options = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    _options["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **_options)

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
