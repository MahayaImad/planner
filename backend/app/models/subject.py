from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base
from .teacher import professeur_matiere


class Matiere(Base):
    __tablename__ = "matieres"

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    nom = Column(String(200), nullable=False)
    coefficient = Column(Float, default=1.0)
    type_salle_requis = Column(String(50), nullable=True)  # None, "labo", "info", "sport"
    created_at = Column(DateTime, server_default=func.now())

    ecole = relationship("Ecole", back_populates="matieres")
    professeurs = relationship("Professeur", secondary=professeur_matiere, back_populates="matieres")
    lecons = relationship("Lecon", back_populates="matiere")
