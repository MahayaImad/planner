"""Configuration de l'application via variables d'environnement."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = "postgresql://planner:planner@db:5432/planner"

    # JWT
    SECRET_KEY: str = "changez-moi-en-production-avec-une-cle-secrete-longue"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # App
    APP_TITLE: str = "Plateforme Emploi du Temps Scolaire"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
