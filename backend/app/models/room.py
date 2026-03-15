from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class Salle(Base):
    __tablename__ = "salles"

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    nom = Column(String(100), nullable=False)
    capacite = Column(Integer, default=30)
    type = Column(String(50), default="classique")  # classique, labo, info, sport
    created_at = Column(DateTime, server_default=func.now())

    ecole = relationship("Ecole", back_populates="salles")
    lecons = relationship("Lecon", back_populates="salle")
