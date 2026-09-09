"""
Application et contrôle des migrations de schéma.

Le schéma était jusqu'ici créé au démarrage par
``Base.metadata.create_all``. Cette méthode crée les tables manquantes
mais ne modifie jamais l'existant : dès qu'un établissement a des
données réelles, toute évolution du schéma devient impossible sans
intervention manuelle. Alembic versionne ces évolutions.
"""

import logging
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from .config import settings
from .database import engine

logger = logging.getLogger(__name__)

RACINE = Path(__file__).resolve().parent.parent
FICHIER_CONFIG = RACINE / "alembic.ini"


def configuration() -> Config:
    config = Config(str(FICHIER_CONFIG))
    config.set_main_option("script_location", str(RACINE / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))
    return config


def revision_cible() -> Optional[str]:
    """Dernière révision présente dans le dépôt."""
    return ScriptDirectory.from_config(configuration()).get_current_head()


def revision_appliquee() -> Optional[str]:
    """Révision inscrite dans la base, ou None si Alembic n'y est pas encore."""
    with engine.connect() as connexion:
        return MigrationContext.configure(connexion).get_current_revision()


def appliquer() -> None:
    """
    Amène la base à la dernière révision.

    Attention en production : lancer plusieurs processus qui migrent en
    même temps peut les faire entrer en conflit. La migration doit être
    jouée UNE fois avant de démarrer les serveurs — c'est ce que fait la
    commande de démarrage du conteneur.
    """
    command.upgrade(configuration(), "head")


def estamper(revision: str = "head") -> None:
    """
    Déclare la base à jour sans exécuter les migrations.

    Sert aux bases créées avant Alembic par ``create_all`` : leurs tables
    existent déjà, rejouer la révision initiale échouerait.
    """
    command.stamp(configuration(), revision)


def verifier() -> None:
    """
    Contrôle que la base est à jour au démarrage.

    Sans ce contrôle, un schéma en retard se manifeste par des erreurs
    SQL obscures au premier appel d'API. Ici, le message dit quoi faire.
    """
    cible, appliquee = revision_cible(), revision_appliquee()
    if appliquee == cible:
        return

    if appliquee is None:
        detail = (
            "La base ne porte aucune version de schéma.\n"
            "  • Base vide          : alembic upgrade head\n"
            "  • Base déjà en place, créée avant Alembic :\n"
            "        alembic stamp 0001 && alembic upgrade head"
        )
    else:
        detail = (f"La base est en révision {appliquee}, le code attend {cible}.\n"
                  f"  Appliquez les migrations : alembic upgrade head")

    if settings.DEBUG:
        logger.warning("Schéma en retard — migration automatique.\n%s", detail)
        appliquer()
        return

    raise RuntimeError(f"Schéma de base non à jour.\n{detail}")
