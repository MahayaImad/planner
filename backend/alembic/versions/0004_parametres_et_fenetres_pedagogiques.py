"""
Révision 0004 — réglages de planification et fenêtres pédagogiques.

Grille horaire, poids des contraintes souples et présence minimale
étaient transmis à chaque génération. Ils ne changent qu'une ou deux
fois par an : les stocker permet de les régler une fois depuis
l'interface, et sert de valeur par défaut aux requêtes qui ne les
précisent pas.

Les fenêtres pédagogiques (journées d'inspection) suivent le même
raisonnement, et disparaissent avec la matière qu'elles concernent.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('parametres_etablissement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('grille', sa.JSON(), nullable=False),
    sa.Column('ponderations', sa.JSON(), nullable=False),
    sa.Column('presence_minimale', sa.JSON(), nullable=False),
    sa.Column('type_salle_ordinaire', sa.String(length=50), server_default='classique', nullable=False),
    sa.Column('limite_secondes', sa.Integer(), server_default='120', nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parametres_etablissement_ecole_id'), 'parametres_etablissement', ['ecole_id'], unique=True)
    op.create_index(op.f('ix_parametres_etablissement_id'), 'parametres_etablissement', ['id'], unique=False)

    op.create_table('fenetres_pedagogiques',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('matiere_id', sa.Integer(), nullable=False),
    sa.Column('index_jour', sa.Integer(), nullable=False),
    sa.Column('seances_bloquees', sa.String(length=100), nullable=False),
    sa.Column('libelle', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.ForeignKeyConstraint(['matiere_id'], ['matieres.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('matiere_id', 'index_jour', name='uq_fenetre_matiere_jour')
    )
    op.create_index(op.f('ix_fenetres_pedagogiques_ecole_id'), 'fenetres_pedagogiques', ['ecole_id'], unique=False)
    op.create_index(op.f('ix_fenetres_pedagogiques_id'), 'fenetres_pedagogiques', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_fenetres_pedagogiques_id'), table_name='fenetres_pedagogiques')
    op.drop_index(op.f('ix_fenetres_pedagogiques_ecole_id'), table_name='fenetres_pedagogiques')

    op.drop_table('fenetres_pedagogiques')
    op.drop_index(op.f('ix_parametres_etablissement_id'), table_name='parametres_etablissement')
    op.drop_index(op.f('ix_parametres_etablissement_ecole_id'), table_name='parametres_etablissement')

    op.drop_table('parametres_etablissement')
