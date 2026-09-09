"""
Révision 0005 — programme annuel.

Le programme — quelle classe suit quelle matière, avec quel enseignant
et combien d'heures — était transmis à chaque génération. Pour un
collège de vingt divisions, cela représentait près de quatre cents
lignes à ressaisir. Il est désormais enregistré.

Les clés étrangères sont en suppression en cascade : retirer une classe,
une matière ou un enseignant retire les lignes de programme qui en
dépendent, plutôt que de laisser des références mortes.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0005'
down_revision: Union[str, Sequence[str], None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('programme',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('classe_id', sa.Integer(), nullable=False),
    sa.Column('matiere_id', sa.Integer(), nullable=False),
    sa.Column('professeur_id', sa.Integer(), nullable=False),
    sa.Column('heures_par_semaine', sa.Integer(), nullable=False),
    sa.Column('nb_seances_doubles', sa.Integer(), server_default='0', nullable=False),
    sa.Column('max_heures_par_jour', sa.Integer(), server_default='2', nullable=False),
    sa.Column('couplage_id', sa.String(length=60), nullable=True),
    sa.Column('groupe', sa.String(length=10), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['classe_id'], ['classes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.ForeignKeyConstraint(['matiere_id'], ['matieres.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['professeur_id'], ['professeurs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_programme_couplage_id'), 'programme', ['couplage_id'], unique=False)
    op.create_index(op.f('ix_programme_ecole_id'), 'programme', ['ecole_id'], unique=False)
    op.create_index(op.f('ix_programme_id'), 'programme', ['id'], unique=False)



def downgrade() -> None:
    op.drop_index(op.f('ix_programme_id'), table_name='programme')
    op.drop_index(op.f('ix_programme_ecole_id'), table_name='programme')
    op.drop_index(op.f('ix_programme_couplage_id'), table_name='programme')

    op.drop_table('programme')
