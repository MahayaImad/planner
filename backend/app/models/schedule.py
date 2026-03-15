from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from ..database import Base


class EmploiDuTemps(Base):
    """Un emploi du temps généré pour une école (snapshot hebdomadaire)."""
    __tablename__ = "emplois_du_temps"

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    nom = Column(String(200), nullable=False)          # "Semaine type - 2024/2025"
    annee_scolaire = Column(String(20), nullable=False) # "2024-2025"
    statut = Column(String(20), default="brouillon")   # brouillon, publié, archivé
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    ecole = relationship("Ecole", back_populates="emplois_du_temps")
    lecons = relationship("Lecon", back_populates="emploi_du_temps", cascade="all, delete-orphan")


class Lecon(Base):
    """Une leçon placée dans l'emploi du temps."""
    __tablename__ = "lecons"

    id = Column(Integer, primary_key=True, index=True)
    emploi_du_temps_id = Column(Integer, ForeignKey("emplois_du_temps.id"), nullable=False)
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    professeur_id = Column(Integer, ForeignKey("professeurs.id"), nullable=False)
    salle_id = Column(Integer, ForeignKey("salles.id"), nullable=False)

    # Créneau horaire
    jour = Column(String(20), nullable=False)         # "Lundi"
    heure_debut = Column(String(10), nullable=False)  # "08:00"
    heure_fin = Column(String(10), nullable=False)    # "09:00"

    emploi_du_temps = relationship("EmploiDuTemps", back_populates="lecons")
    classe = relationship("Classe", back_populates="lecons")
    matiere = relationship("Matiere", back_populates="lecons")
    professeur = relationship("Professeur", back_populates="lecons")
    salle = relationship("Salle", back_populates="lecons")
