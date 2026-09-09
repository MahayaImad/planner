from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from ..database import Base


class LigneProgramme(Base):
    """
    Une ligne du programme annuel : telle classe suit tant d'heures de
    telle matière avec tel enseignant.

    Le programme ne change qu'à la rentrée, mais il fallait le ressaisir
    à chaque génération — près de quatre cents lignes pour un collège de
    vingt divisions. Il est désormais enregistré.

    Les clés étrangères sont en suppression en cascade : retirer une
    classe, une matière ou un enseignant retire les lignes qui en
    dépendent, faute de quoi la base porterait des références mortes.
    """
    __tablename__ = "programme"

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False, index=True)
    classe_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"),
                       nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id", ondelete="CASCADE"),
                        nullable=False)
    professeur_id = Column(Integer, ForeignKey("professeurs.id", ondelete="CASCADE"),
                           nullable=False)

    heures_par_semaine = Column(Integer, nullable=False)
    # Blocs de deux heures accolées à réserver dans le volume.
    nb_seances_doubles = Column(Integer, nullable=False, default=0,
                                server_default="0")
    # Plafond d'heures de cette ligne dans une même journée.
    max_heures_par_jour = Column(Integer, nullable=False, default=2,
                                 server_default="2")

    # Fouj : deux lignes partageant cet identifiant sont enseignées en
    # même temps à deux demi-groupes de la classe.
    couplage_id = Column(String(60), nullable=True, index=True)
    groupe = Column(String(10), nullable=False, default="", server_default="")

    created_at = Column(DateTime, server_default=func.now())

    classe = relationship("Classe")
    matiere = relationship("Matiere")
    professeur = relationship("Professeur")
