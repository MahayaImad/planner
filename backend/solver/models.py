"""
Modèles de données pour le générateur d'emplois du temps.
Ces dataclasses représentent les entités du domaine métier.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class Creneau:
    """Un créneau horaire dans la semaine (ex: Lundi 8h-9h)."""
    id: int
    jour: str        # "Lundi", "Mardi", etc.
    heure_debut: str  # "08:00"
    heure_fin: str    # "09:00"

    def __repr__(self):
        return f"{self.jour} {self.heure_debut}-{self.heure_fin}"


@dataclass
class Salle:
    """Une salle physique dans l'établissement."""
    id: int
    nom: str
    capacite: int
    type: str = "classique"  # "classique", "labo", "sport", "info"


@dataclass
class Matiere:
    """Une matière enseignée (ex: Mathématiques)."""
    id: int
    nom: str
    coefficient: float = 1.0


@dataclass
class Professeur:
    """Un professeur avec ses matières et disponibilités."""
    id: int
    nom: str
    prenom: str
    matieres_ids: List[int] = field(default_factory=list)
    # IDs des créneaux où le prof est disponible (vide = disponible tout le temps)
    creneaux_disponibles: Set[int] = field(default_factory=set)
    # Nombre max d'heures consécutives
    max_heures_consecutives: int = 3

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


@dataclass
class Classe:
    """Un groupe d'élèves (ex: 3ème année section A)."""
    id: int
    nom: str          # "1ère A", "2ème B", "3ème C"
    niveau: str       # "primaire", "moyen", "secondaire"
    effectif: int = 30


@dataclass
class CoursRequis:
    """
    Exigence : la classe X doit avoir N heures/semaine de matière Y
    avec le professeur Z (optionnel).
    """
    id: int
    classe_id: int
    matiere_id: int
    professeur_id: int
    heures_par_semaine: int  # nombre de créneaux à placer
    # Type de salle requis (None = n'importe quelle salle classique)
    type_salle_requis: Optional[str] = None


@dataclass
class LeconPlanifiee:
    """Résultat : une leçon placée dans l'emploi du temps."""
    cours_requis_id: int
    classe_id: int
    matiere_id: int
    professeur_id: int
    salle_id: int
    creneau_id: int
