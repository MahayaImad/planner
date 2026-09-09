"""
Environnement Alembic.

L'URL de la base vient de la configuration de l'application, jamais
d'alembic.ini : un identifiant de production ne doit pas être versionné.
"""

from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

# Rendre le paquet « app » importable quand Alembic est lancé depuis
# n'importe quel répertoire.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings          # noqa: E402
from app.database import Base            # noqa: E402
import app.models                        # noqa: E402,F401  (enregistre les tables)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

target_metadata = Base.metadata


def _options_communes() -> dict:
    return {
        "target_metadata": target_metadata,
        "compare_type": True,
        "compare_server_default": True,
        # SQLite ne sait pas modifier une colonne en place : Alembic
        # recrée la table. Sans cela, toute migration ALTER échouerait
        # sur les bases de développement et de test.
        "render_as_batch": settings.DATABASE_URL.startswith("sqlite"),
    }


def run_migrations_offline() -> None:
    """Génère le SQL sans se connecter (alembic upgrade --sql)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **_options_communes(),
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, **_options_communes())
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
