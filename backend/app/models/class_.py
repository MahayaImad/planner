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
    created_at = Column(DateTime, server_default=func.now())

    ecole = relationship("Ecole", back_populates="classes")
    lecons = relationship("Lecon", back_populates="classe")
