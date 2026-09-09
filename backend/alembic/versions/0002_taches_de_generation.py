"""
Révision 0002 — suivi des générations d'emplois du temps.

Une résolution dure de quelques secondes à plusieurs minutes : elle est
menée en arrière-plan, et son avancement doit survivre à la requête qui
l'a déclenchée. Cette table porte l'état de chaque génération, la
requête d'origine — ce qui rend une génération reproductible — et son
compte rendu.

La suppression d'un emploi du temps emporte ses tâches (ON DELETE
CASCADE) : un historique orphelin n'aurait aucun sens.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('taches_generation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('emploi_du_temps_id', sa.Integer(), nullable=False),
    sa.Column('statut', sa.String(length=20), nullable=False),
    sa.Column('message', sa.String(length=500), nullable=True),
    sa.Column('requete', sa.Text(), nullable=False),
    sa.Column('resultat', sa.Text(), nullable=True),
    sa.Column('erreurs', sa.Text(), nullable=True),
    sa.Column('cout_courant', sa.Integer(), nullable=True),
    sa.Column('nb_solutions', sa.Integer(), nullable=True),
    sa.Column('lecons_planifiees', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('finished_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.ForeignKeyConstraint(['emploi_du_temps_id'], ['emplois_du_temps.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_taches_generation_id'), 'taches_generation', ['id'], unique=False)
    op.create_index(op.f('ix_taches_generation_statut'), 'taches_generation', ['statut'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_taches_generation_statut'), table_name='taches_generation')
    op.drop_index(op.f('ix_taches_generation_id'), table_name='taches_generation')

    op.drop_table('taches_generation')
