"""
Révision 0001 — schéma initial.

Reprend le schéma tel qu'il était créé jusqu'ici par
``Base.metadata.create_all`` : établissements, comptes, ressources
pédagogiques, emplois du temps et leçons.

BASES DÉJÀ EN SERVICE
Une base créée avant l'introduction d'Alembic contient déjà ces tables
mais aucune table de version : rejouer cette révision échouerait. Il
faut l'estamper une fois, sans rien exécuter, puis appliquer la suite :

    alembic stamp 0001
    alembic upgrade head

Sur une base vide, ``alembic upgrade head`` suffit.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('ecoles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=200), nullable=False),
    sa.Column('adresse', sa.String(length=500), nullable=True),
    sa.Column('telephone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=200), nullable=False),
    sa.Column('ville', sa.String(length=100), nullable=True),
    sa.Column('wilaya', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ecoles_email'), 'ecoles', ['email'], unique=True)
    op.create_index(op.f('ix_ecoles_id'), 'ecoles', ['id'], unique=False)

    op.create_table('classes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=100), nullable=False),
    sa.Column('niveau', sa.String(length=50), nullable=False),
    sa.Column('effectif', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_classes_id'), 'classes', ['id'], unique=False)

    op.create_table('emplois_du_temps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=200), nullable=False),
    sa.Column('annee_scolaire', sa.String(length=20), nullable=False),
    sa.Column('statut', sa.String(length=20), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emplois_du_temps_id'), 'emplois_du_temps', ['id'], unique=False)

    op.create_table('matieres',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=200), nullable=False),
    sa.Column('coefficient', sa.Float(), nullable=True),
    sa.Column('type_salle_requis', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_matieres_id'), 'matieres', ['id'], unique=False)

    op.create_table('professeurs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=100), nullable=False),
    sa.Column('prenom', sa.String(length=100), nullable=False),
    sa.Column('telephone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=200), nullable=True),
    sa.Column('max_heures_consecutives', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_professeurs_id'), 'professeurs', ['id'], unique=False)

    op.create_table('salles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=100), nullable=False),
    sa.Column('capacite', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_salles_id'), 'salles', ['id'], unique=False)

    op.create_table('utilisateurs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecole_id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(length=100), nullable=False),
    sa.Column('prenom', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=200), nullable=False),
    sa.Column('mot_de_passe_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=True),
    sa.Column('actif', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['ecole_id'], ['ecoles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utilisateurs_email'), 'utilisateurs', ['email'], unique=True)
    op.create_index(op.f('ix_utilisateurs_id'), 'utilisateurs', ['id'], unique=False)

    op.create_table('disponibilites_professeurs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('professeur_id', sa.Integer(), nullable=False),
    sa.Column('jour', sa.String(length=20), nullable=False),
    sa.Column('heure_debut', sa.String(length=10), nullable=False),
    sa.Column('disponible', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['professeur_id'], ['professeurs.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('professeur_id', 'jour', 'heure_debut', name='uq_dispo')
    )
    op.create_index(op.f('ix_disponibilites_professeurs_id'), 'disponibilites_professeurs', ['id'], unique=False)

    op.create_table('lecons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('emploi_du_temps_id', sa.Integer(), nullable=False),
    sa.Column('classe_id', sa.Integer(), nullable=False),
    sa.Column('matiere_id', sa.Integer(), nullable=False),
    sa.Column('professeur_id', sa.Integer(), nullable=False),
    sa.Column('salle_id', sa.Integer(), nullable=False),
    sa.Column('jour', sa.String(length=20), nullable=False),
    sa.Column('heure_debut', sa.String(length=10), nullable=False),
    sa.Column('heure_fin', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['classe_id'], ['classes.id'], ),
    sa.ForeignKeyConstraint(['emploi_du_temps_id'], ['emplois_du_temps.id'], ),
    sa.ForeignKeyConstraint(['matiere_id'], ['matieres.id'], ),
    sa.ForeignKeyConstraint(['professeur_id'], ['professeurs.id'], ),
    sa.ForeignKeyConstraint(['salle_id'], ['salles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lecons_id'), 'lecons', ['id'], unique=False)

    op.create_table('professeur_matiere',
    sa.Column('professeur_id', sa.Integer(), nullable=False),
    sa.Column('matiere_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['matiere_id'], ['matieres.id'], ),
    sa.ForeignKeyConstraint(['professeur_id'], ['professeurs.id'], ),
    sa.PrimaryKeyConstraint('professeur_id', 'matiere_id')
    )

def downgrade() -> None:
    op.drop_table('professeur_matiere')
    op.drop_index(op.f('ix_lecons_id'), table_name='lecons')

    op.drop_table('lecons')
    op.drop_index(op.f('ix_disponibilites_professeurs_id'), table_name='disponibilites_professeurs')

    op.drop_table('disponibilites_professeurs')
    op.drop_index(op.f('ix_utilisateurs_id'), table_name='utilisateurs')
    op.drop_index(op.f('ix_utilisateurs_email'), table_name='utilisateurs')

    op.drop_table('utilisateurs')
    op.drop_index(op.f('ix_salles_id'), table_name='salles')

    op.drop_table('salles')
    op.drop_index(op.f('ix_professeurs_id'), table_name='professeurs')

    op.drop_table('professeurs')
    op.drop_index(op.f('ix_matieres_id'), table_name='matieres')

    op.drop_table('matieres')
    op.drop_index(op.f('ix_emplois_du_temps_id'), table_name='emplois_du_temps')

    op.drop_table('emplois_du_temps')
    op.drop_index(op.f('ix_classes_id'), table_name='classes')

    op.drop_table('classes')
    op.drop_index(op.f('ix_ecoles_id'), table_name='ecoles')
    op.drop_index(op.f('ix_ecoles_email'), table_name='ecoles')

    op.drop_table('ecoles')
