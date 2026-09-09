"""
Révision 0003 — service hebdomadaire des enseignants et salle attitrée.

Le solveur exploitait déjà ces notions, mais le schéma ne savait pas les
stocker : elles ne pouvaient donc pas transiter par l'API.

  professeurs.max_heures_par_semaine  plafond de service (colonne
                                      Max_Weekly_Hours des fiches
                                      enseignants) ; NULL = pas de plafond
  professeurs.max_heures_par_jour     plafond quotidien
  professeurs.assure_permanences      l'enseignant peut-il combler ses
                                      heures creuses par de l'accueil
  classes.salle_attitree_id           salle de la division : les élèves
                                      ne se déplacent que pour le
                                      laboratoire, l'informatique ou le sport
  classes.max_heures_par_jour         amplitude quotidienne de la division
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Nommer la contrainte : une clé étrangère anonyme ne peut pas être
# supprimée lors du retour arrière sur PostgreSQL.
FK_SALLE_ATTITREE = "fk_classes_salle_attitree_id_salles"


def upgrade() -> None:
    with op.batch_alter_table("classes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("salle_attitree_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("max_heures_par_jour", sa.Integer(),
                      server_default="6", nullable=True))
        batch_op.create_foreign_key(
            FK_SALLE_ATTITREE, "salles", ["salle_attitree_id"], ["id"])

    with op.batch_alter_table("professeurs", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("max_heures_par_jour", sa.Integer(),
                      server_default="6", nullable=True))
        batch_op.add_column(
            sa.Column("max_heures_par_semaine", sa.Integer(), nullable=True))
        # NOT NULL sans valeur par défaut échouerait sur une table déjà
        # peuplée : les lignes existantes n'auraient rien à y mettre.
        batch_op.add_column(
            sa.Column("assure_permanences", sa.Boolean(),
                      server_default=sa.true(), nullable=False))


def downgrade() -> None:
    with op.batch_alter_table("professeurs", schema=None) as batch_op:
        batch_op.drop_column("assure_permanences")
        batch_op.drop_column("max_heures_par_semaine")
        batch_op.drop_column("max_heures_par_jour")

    with op.batch_alter_table("classes", schema=None) as batch_op:
        batch_op.drop_constraint(FK_SALLE_ATTITREE, type_="foreignkey")
        batch_op.drop_column("max_heures_par_jour")
        batch_op.drop_column("salle_attitree_id")
