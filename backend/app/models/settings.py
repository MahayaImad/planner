from sqlalchemy import (
    JSON, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func,
)
from sqlalchemy.orm import relationship

from ..database import Base

# Grille par défaut : semaine algérienne, 4 séances le matin, 3 l'après-midi.
GRILLE_DEFAUT = {
    "jours": ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"],
    "horaires": [
        ["08:00", "08:55"], ["09:00", "09:55"], ["10:05", "11:00"],
        ["11:05", "12:00"], ["13:00", "13:55"], ["14:00", "14:55"],
        ["15:05", "16:00"],
    ],
    "shifts": [["matin", [0, 1, 2, 3]], ["apres-midi", [4, 5, 6]]],
    "fermetures": [],
}

PONDERATIONS_DEFAUT = {
    "trous_professeurs": 6,
    "trous_doubles_professeurs": 25,
    "journee_hachee_professeur": 80,
    "heure_isolee_professeur": 12,
    "jours_presence_professeurs": 3,
    "penalites_heures_par_jour": {"5": 15, "6": 45},
    "recompense_permanence": 4,
    "penalites_seance": {"0": 20, "3": 8, "4": 10, "5": 30, "6": 150},
    "equite_derniere_seance": 25,
    "seance_soumise_a_equite": 6,
    "equilibrage_charge_classes": 4,
    "demi_journees_travaillees_classes": 0,
    "matieres_lourdes_apres_midi": 0,
    "blocs_hors_politique": 25,
    "matieres_repetees_par_jour": 12,
}


class ParametresEtablissement(Base):
    """
    Réglages de planification propres à un établissement.

    Grille horaire, poids des contraintes souples et présence minimale
    ne changent qu'une ou deux fois par an : les redemander à chaque
    génération n'aurait aucun sens. Ils sont donc stockés ici et servent
    de valeurs par défaut quand la requête ne les précise pas.
    """
    __tablename__ = "parametres_etablissement"

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False,
                      unique=True, index=True)

    grille = Column(JSON, nullable=False, default=lambda: dict(GRILLE_DEFAUT))
    ponderations = Column(JSON, nullable=False,
                          default=lambda: dict(PONDERATIONS_DEFAUT))
    # Heures minimales de présence d'une classe par demi-journée.
    presence_minimale = Column(JSON, nullable=False, default=dict)
    # Nom du type de salle ordinaire dans le parc de l'établissement.
    type_salle_ordinaire = Column(String(50), nullable=False,
                                  default="classique", server_default="classique")
    limite_secondes = Column(Integer, nullable=False, default=120,
                             server_default="120")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    ecole = relationship("Ecole")


class FenetrePedagogique(Base):
    """
    Plage où une matière est interdite dans tout l'établissement.

    Sert aux journées d'inspection et aux réunions de coordination :
    « aucun cours d'arabe le lundi matin » libère d'un coup tous les
    professeurs d'arabe.
    """
    __tablename__ = "fenetres_pedagogiques"
    __table_args__ = (
        UniqueConstraint("matiere_id", "index_jour", name="uq_fenetre_matiere_jour"),
    )

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False, index=True)
    matiere_id = Column(Integer, ForeignKey("matieres.id", ondelete="CASCADE"),
                        nullable=False)
    # Index du jour dans la grille (0 = premier jour travaillé).
    index_jour = Column(Integer, nullable=False)
    # Numéros OFFICIELS des séances bloquées, séparés par « ; » — même
    # écriture que dans les fichiers de l'établissement : "0;1;2;3".
    seances_bloquees = Column(String(100), nullable=False)
    libelle = Column(String(200))

    matiere = relationship("Matiere", back_populates="fenetres")

    @property
    def seances(self):
        return sorted(int(x) for x in self.seances_bloquees.split(";") if x.strip())
