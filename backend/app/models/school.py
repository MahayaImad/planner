from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class Ecole(Base):
    __tablename__ = "ecoles"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False)
    adresse = Column(String(500))
    telephone = Column(String(20))
    email = Column(String(200), unique=True, index=True, nullable=False)
    ville = Column(String(100))
    wilaya = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())

    # Relations
    utilisateurs = relationship("Utilisateur", back_populates="ecole", cascade="all, delete-orphan")
    professeurs = relationship("Professeur", back_populates="ecole", cascade="all, delete-orphan")
    matieres = relationship("Matiere", back_populates="ecole", cascade="all, delete-orphan")
    salles = relationship("Salle", back_populates="ecole", cascade="all, delete-orphan")
    classes = relationship("Classe", back_populates="ecole", cascade="all, delete-orphan")
    emplois_du_temps = relationship("EmploiDuTemps", back_populates="ecole", cascade="all, delete-orphan")
