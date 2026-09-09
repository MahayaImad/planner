"""Configuration de l'application via variables d'environnement."""

import secrets
import warnings
from typing import List

from pydantic_settings import BaseSettings

# Valeur historiquement présente dans le dépôt : elle ne doit jamais
# servir en production, la connaître suffirait à forger des jetons.
CLE_PAR_DEFAUT = "changez-moi-en-production-avec-une-cle-secrete-longue"


class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = "postgresql://planner:planner@db:5432/planner"

    # JWT — aucune valeur par défaut : voir valider() ci-dessous.
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

    # Origines autorisées à appeler l'API, séparées par des virgules.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Générations simultanées, et threads accordés à chaque résolution.
    GENERATIONS_SIMULTANEES: int = 2
    SOLVEUR_THREADS: int = 8
    LIMITE_SECONDES_MAX: int = 900

    # App
    APP_TITLE: str = "Plateforme Emploi du Temps Scolaire"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

    # ── Dérivés ───────────────────────────────────────────────────
    @property
    def origines_cors(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    def valider(self) -> None:
        """
        Contrôle les réglages sensibles au démarrage.

        En production une clé absente ou laissée à la valeur du dépôt
        est une faille : mieux vaut refuser de démarrer que servir des
        jetons forgeables. En développement, une clé éphémère est
        générée — les sessions ne survivront pas à un redémarrage.
        """
        if not self.SECRET_KEY or self.SECRET_KEY == CLE_PAR_DEFAUT:
            if not self.DEBUG:
                raise RuntimeError(
                    "SECRET_KEY absente ou laissée à la valeur par défaut. "
                    "Définissez-la dans l'environnement, par exemple :\n"
                    "  SECRET_KEY=$(python3 -c \"import secrets;"
                    "print(secrets.token_urlsafe(48))\")"
                )
            self.SECRET_KEY = secrets.token_urlsafe(48)
            warnings.warn(
                "SECRET_KEY générée pour cette session de développement : "
                "les jetons émis seront invalidés au redémarrage.",
                stacklevel=2,
            )

        if not self.DEBUG and "*" in self.origines_cors:
            raise RuntimeError(
                "CORS_ORIGINS ne peut pas valoir « * » en production : "
                "l'API accepte les requêtes authentifiées."
            )


settings = Settings()
settings.valider()
