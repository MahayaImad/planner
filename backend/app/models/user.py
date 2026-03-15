from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")  # admin, secretaire
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    ecole = relationship("Ecole", back_populates="utilisateurs")
