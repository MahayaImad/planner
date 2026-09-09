from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class Classe(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    nom = Column(String(100), nullable=False)      # "4ème A"
    niveau = Column(String(50), nullable=False)    # "primaire", "moyen", "secondaire"
    effectif = Column(Integer, default=30)
    # Salle de classe attitrée : les élèves ne se déplacent que pour le
    # laboratoire, l'informatique ou le sport.
    salle_attitree_id = Column(Integer, ForeignKey("salles.id"), nullable=True)
    max_heures_par_jour = Column(Integer, default=6, server_default="6")
    created_at = Column(DateTime, server_default=func.now())

    ecole = relationship("Ecole", back_populates="classes")
    salle_attitree = relationship("Salle", foreign_keys=[salle_attitree_id])
    lecons = relationship("Lecon", back_populates="classe")
