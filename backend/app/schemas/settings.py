from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class GrilleInput(BaseModel):
    """Grille horaire de l'établissement."""
    jours: List[str] = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"]
    # Horaire de chaque séance de la journée, dans l'ordre.
    horaires: List[Tuple[str, str]] = [
        ("08:00", "08:55"), ("09:00", "09:55"), ("10:05", "11:00"),
        ("11:05", "12:00"), ("13:00", "13:55"), ("14:00", "14:55"),
        ("15:05", "16:00"),
    ]
    # Demi-journées : (nom, index des séances qui la composent).
    shifts: List[Tuple[str, List[int]]] = [
        ("matin", [0, 1, 2, 3]), ("apres-midi", [4, 5, 6]),
    ]
    # Fermetures officielles : (index du jour, index des séances fermées).
    # Le mardi après-midi fermé s'écrit (2, [4, 5, 6]).
    fermetures: List[Tuple[int, List[int]]] = []


class PonderationsInput(BaseModel):
    """
    Poids des contraintes souples. Zéro désactive un critère ; plus le
    poids est élevé, plus le solveur cherche à éviter la situation.
    """
    trous_professeurs: int = 6
    trous_doubles_professeurs: int = 25
    # Heures creuses supplémentaires dans une même journée.
    journee_hachee_professeur: int = 80
    heure_isolee_professeur: int = 12
    jours_presence_professeurs: int = 3
    # Atteindre N heures de cours dans la journée coûte ce poids,
    # en plus de ceux des seuils inférieurs.
    penalites_heures_par_jour: Dict[int, int] = {5: 15, 6: 45}
    recompense_permanence: int = 4
    # Coût d'occupation par séance, indexée à partir de 0 : la séance
    # « slot N » de l'établissement porte l'index N-1.
    penalites_seance: Dict[int, int] = {0: 20, 3: 8, 4: 10, 5: 30, 6: 150}
    equite_derniere_seance: int = 25
    seance_soumise_a_equite: int = 6
    equilibrage_charge_classes: int = 4
    demi_journees_travaillees_classes: int = 0
    matieres_lourdes_apres_midi: int = 0
    # Heures d'une matière groupées au-delà de ce que la politique de
    # blocs du programme autorise, et empilement de plusieurs matières
    # doublées dans la même journée.
    blocs_hors_politique: int = 60
    matieres_repetees_par_jour: int = 12


class ParametresRead(BaseModel):
    grille: GrilleInput
    ponderations: PonderationsInput
    presence_minimale: Dict[str, int] = {}
    type_salle_ordinaire: str = "classique"
    limite_secondes: int = 120


class ParametresUpdate(BaseModel):
    grille: Optional[GrilleInput] = None
    ponderations: Optional[PonderationsInput] = None
    presence_minimale: Optional[Dict[str, int]] = None
    type_salle_ordinaire: Optional[str] = None
    limite_secondes: Optional[int] = Field(default=None, ge=5, le=3600)


class FenetreCreate(BaseModel):
    """Matière interdite un jour donné, sur les séances indiquées."""
    matiere_id: int
    index_jour: int = Field(ge=0, le=6)
    seances_bloquees: List[int]
    libelle: Optional[str] = None


class FenetreRead(BaseModel):
    id: int
    matiere_id: int
    matiere_nom: Optional[str] = None
    index_jour: int
    seances_bloquees: List[int]
    libelle: Optional[str] = None
