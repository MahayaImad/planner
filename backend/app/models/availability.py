from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class DisponibiliteProfesseur(Base):
    """
    Indisponibilité d'un professeur sur un créneau donné.
    On stocke les créneaux où le prof N'EST PAS disponible.
    jour : "Lundi", "Mardi", etc.
    heure_debut : "08:00"
    """
    __tablename__ = "disponibilites_professeurs"
    __table_args__ = (
        UniqueConstraint("professeur_id", "jour", "heure_debut", name="uq_dispo"),
    )

    id = Column(Integer, primary_key=True, index=True)
    professeur_id = Column(Integer, ForeignKey("professeurs.id"), nullable=False)
    jour = Column(String(20), nullable=False)
    heure_debut = Column(String(10), nullable=False)  # "08:00"
    disponible = Column(Integer, default=0)  # 0 = indisponible, 1 = disponible

    professeur = relationship("Professeur", back_populates="disponibilites")
