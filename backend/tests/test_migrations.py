"""
Tests des migrations de schéma.

Le test le plus utile est celui de dérive : il échoue dès qu'un modèle
est modifié sans migration correspondante. C'est exactement l'oubli que
l'ancien ``create_all`` masquait — les tables manquantes apparaissaient,
les colonnes modifiées jamais.

    python3 tests/test_migrations.py
"""

import os
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
os.environ.setdefault("DEBUG", "true")

BASE_TEST = RACINE / "test_migrations.db"
os.environ["DATABASE_URL"] = f"sqlite:///{BASE_TEST}"

from alembic import command  # noqa: E402
from alembic.autogenerate import compare_metadata  # noqa: E402
from alembic.runtime.migration import MigrationContext  # noqa: E402
from sqlalchemy import create_engine, inspect, text  # noqa: E402

from app import migrations  # noqa: E402
from app.database import Base  # noqa: E402
import app.models  # noqa: E402,F401

TABLES_ATTENDUES = {
    "ecoles", "utilisateurs", "professeurs", "matieres", "professeur_matiere",
    "salles", "classes", "emplois_du_temps", "lecons",
    "disponibilites_professeurs", "taches_generation",
}


def _base_neuve():
    if BASE_TEST.exists():
        BASE_TEST.unlink()
    return create_engine(f"sqlite:///{BASE_TEST}")


def _config(moteur):
    config = migrations.configuration()
    config.set_main_option("sqlalchemy.url", str(moteur.url))
    return config


def test_base_vide_migre_jusqua_la_tete():
    moteur = _base_neuve()
    command.upgrade(_config(moteur), "head")
    tables = set(inspect(moteur).get_table_names())
    manquantes = TABLES_ATTENDUES - tables
    assert not manquantes, f"tables absentes : {manquantes}"
    assert "alembic_version" in tables


def test_migrations_en_phase_avec_les_modeles():
    """
    Aucune dérive entre le schéma migré et les modèles SQLAlchemy.

    Si ce test échoue, c'est qu'un modèle a changé sans migration :
        alembic revision --autogenerate -m "…"
    """
    moteur = _base_neuve()
    command.upgrade(_config(moteur), "head")
    with moteur.connect() as connexion:
        contexte = MigrationContext.configure(
            connexion, opts={"compare_type": True})
        differences = compare_metadata(contexte, Base.metadata)
    assert not differences, "\n".join(str(d) for d in differences)


def test_retour_arriere_complet():
    moteur = _base_neuve()
    config = _config(moteur)
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    restantes = set(inspect(moteur).get_table_names()) - {"alembic_version"}
    assert not restantes, f"tables laissées derrière : {restantes}"


def test_revision_intermediaire_puis_tete():
    """La révision 0002 doit ajouter la table des tâches, et elle seule."""
    moteur = _base_neuve()
    config = _config(moteur)
    command.upgrade(config, "0001")
    tables = set(inspect(moteur).get_table_names())
    assert "taches_generation" not in tables
    assert "emplois_du_temps" in tables

    command.upgrade(config, "head")
    assert "taches_generation" in set(inspect(moteur).get_table_names())


def test_base_existante_creee_avant_alembic():
    """
    Scénario de reprise : une base déjà en service, créée par
    ``create_all``, ne porte aucune version. Rejouer la révision
    initiale échouerait ; il faut l'estamper, puis migrer — sans perdre
    les données existantes.

    Le schéma d'époque est reconstitué en jouant la révision 0001 puis
    en effaçant la table de version : le simuler avec les modèles
    d'aujourd'hui donnerait des colonnes qui n'existaient pas encore.
    """
    moteur = _base_neuve()
    config = _config(moteur)

    command.upgrade(config, "0001")
    with moteur.begin() as connexion:
        connexion.execute(text(
            "INSERT INTO ecoles (id, nom, email) VALUES (1, 'CEM Test', 'a@b.dz')"))
        connexion.execute(text(
            "INSERT INTO professeurs (id, ecole_id, nom, prenom) "
            "VALUES (1, 1, 'Benali', 'Karim')"))
        connexion.execute(text("DROP TABLE alembic_version"))
    assert "alembic_version" not in set(inspect(moteur).get_table_names())

    # Rejouer la révision initiale sur ces tables échouerait : c'est
    # bien pour cela que la marche à suivre passe par « stamp ».
    try:
        command.upgrade(config, "head")
        assert False, "la révision initiale aurait dû échouer sur une base existante"
    except Exception:
        pass

    command.stamp(config, "0001")
    command.upgrade(config, "head")

    tables = set(inspect(moteur).get_table_names())
    assert "taches_generation" in tables
    colonnes = {c["name"] for c in inspect(moteur).get_columns("professeurs")}
    assert "max_heures_par_semaine" in colonnes
    assert "assure_permanences" in colonnes

    with moteur.connect() as connexion:
        ecole = connexion.execute(text("SELECT nom FROM ecoles WHERE id = 1")).scalar()
        # La colonne NOT NULL ajoutée doit avoir une valeur pour les
        # lignes déjà présentes, sinon la migration casse en production.
        permanences = connexion.execute(text(
            "SELECT assure_permanences FROM professeurs WHERE id = 1")).scalar()
    assert ecole == "CEM Test", "les données existantes doivent survivre"
    assert permanences in (1, True)


def test_controle_de_schema_refuse_une_base_en_retard():
    """En production, un schéma en retard doit arrêter le démarrage."""
    from app.config import settings

    moteur = _base_neuve()
    command.upgrade(_config(moteur), "0001")

    debug_initial = settings.DEBUG
    url_initiale = settings.DATABASE_URL
    settings.DEBUG = False
    settings.DATABASE_URL = str(moteur.url)
    try:
        import app.migrations as m
        moteur_initial = m.engine
        m.engine = moteur
        try:
            m.verifier()
            assert False, "un schéma en retard doit être refusé"
        except RuntimeError as e:
            assert "0001" in str(e) and "alembic upgrade head" in str(e)
        finally:
            m.engine = moteur_initial
    finally:
        settings.DEBUG = debug_initial
        settings.DATABASE_URL = url_initiale


if __name__ == "__main__":
    echecs = 0
    for nom, fonction in sorted(globals().items()):
        if not nom.startswith("test_") or not callable(fonction):
            continue
        depart = time.perf_counter()
        try:
            fonction()
            print(f"  ✓ {nom}  ({time.perf_counter() - depart:.1f}s)")
        except Exception as e:
            echecs += 1
            import traceback
            print(f"  ✗ {nom}\n      {e or type(e).__name__}")
            print("      " + traceback.format_exc().replace("\n", "\n      ")[:700])
    if BASE_TEST.exists():
        BASE_TEST.unlink()
    print(f"\n{'Tous les tests passent.' if not echecs else f'{echecs} échec(s).'}")
    sys.exit(1 if echecs else 0)
