from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Table, func, text,
)
from sqlalchemy.orm import relationship
from ..database import Base

# Table d'association professeur ↔ matière
professeur_matiere = Table(
    "professeur_matiere",
    Base.metadata,
    Column("professeur_id", Integer, ForeignKey("professeurs.id"), primary_key=True),
    Column("matiere_id", Integer, ForeignKey("matieres.id"), primary_key=True),
)


class Professeur(Base):
    __tablename__ = "professeurs"

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    telephone = Column(String(20))
    email = Column(String(200))
    max_heures_consecutives = Column(Integer, default=4)
    max_heures_par_jour = Column(Integer, default=6, server_default="6")
    # Service hebdomadaire maximum (NULL = pas de plafond).
    max_heures_par_semaine = Column(Integer, nullable=True)
    # L'enseignant peut-il assurer une permanence dans ses heures creuses ?
    assure_permanences = Column(Boolean, default=True,
                                server_default=text("true"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    ecole = relationship("Ecole", back_populates="professeurs")
    matieres = relationship("Matiere", secondary=professeur_matiere, back_populates="professeurs")
    disponibilites = relationship("DisponibiliteProfesseur", back_populates="professeur", cascade="all, delete-orphan")
    lecons = relationship("Lecon", back_populates="professeur")

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
