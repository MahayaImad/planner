from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class CoursRequisInput(BaseModel):
    """Un cours à planifier : quelle classe, quelle matière, quel prof, combien d'heures."""
    classe_id: int
    matiere_id: int
    professeur_id: int
    heures_par_semaine: int
    # Nombre de séances de 2 h accolées à réserver dans ce volume.
    nb_seances_doubles: int = 0
    # Plafond d'heures de cette matière dans une même journée.
    max_heures_par_jour: int = 2
    # Fouj : deux cours partageant cet identifiant sont donnés en même
    # temps à deux demi-groupes de la classe (TD arabe / TD maths…).
    couplage_id: Optional[str] = None
    groupe: str = ""


class GrilleInput(BaseModel):
    """Grille horaire de l'établissement."""
    jours: List[str] = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"]
    horaires: List[Tuple[str, str]] = [
        ("08:00", "08:55"), ("09:00", "09:55"), ("10:05", "11:00"),
        ("11:05", "12:00"), ("13:00", "13:55"), ("14:00", "14:55"),
        ("15:05", "16:00"),
    ]
    shifts: List[Tuple[str, List[int]]] = [
        ("matin", [0, 1, 2, 3]), ("apres-midi", [4, 5, 6]),
    ]
    # Fermetures officielles : (index du jour, [index de séances]).
    fermetures: List[Tuple[int, List[int]]] = []


class FenetreInput(BaseModel):
    """Matière interdite sur une plage (journée d'inspection)."""
    matiere_id: int
    index_jour: int
    seances_bloquees: List[int]
    libelle: str = ""


class PonderationsInput(BaseModel):
    """Poids des contraintes souples, arbitrés par l'établissement."""
    trous_professeurs: int = 6
    trous_doubles_professeurs: int = 25
    heure_isolee_professeur: int = 12
    jours_presence_professeurs: int = 3
    recompense_permanence: int = 4
    # Coût d'occupation par séance, indexée à partir de 0 : la séance
    # « slot_N » de l'établissement porte l'index N-1.
    penalites_seance: Dict[int, int] = {0: 20, 3: 8, 4: 10, 5: 30, 6: 150}
    equite_derniere_seance: int = 25
    seance_soumise_a_equite: int = 6
    equilibrage_charge_classes: int = 4
    demi_journees_travaillees_classes: int = 0
    matieres_lourdes_apres_midi: int = 0


class GenererRequest(BaseModel):
    """Corps de la requête POST /emplois-du-temps/{id}/generer."""
    cours_requis: List[CoursRequisInput]
    grille: GrilleInput = GrilleInput()
    fenetres_pedagogiques: List[FenetreInput] = []
    ponderations: PonderationsInput = PonderationsInput()
    presence_minimale: Dict[str, int] = {}
    type_salle_ordinaire: str = "classique"
    limite_secondes: int = 120


class DiagnosticResponse(BaseModel):
    """Compte rendu du contrôle des données, avant toute résolution."""
    erreurs: List[str] = []
    avertissements: List[str] = []
    realisable: bool = True


class LeconRead(BaseModel):
    id: int
    classe_id: int
    matiere_id: int
    professeur_id: int
    salle_id: int
    jour: str
    heure_debut: str
    heure_fin: str

    # Noms pour l'affichage (peuplés via jointure)
    classe_nom: Optional[str] = None
    matiere_nom: Optional[str] = None
    professeur_nom: Optional[str] = None
    salle_nom: Optional[str] = None

    model_config = {"from_attributes": True}


class EmploiDuTempsCreate(BaseModel):
    nom: str
    annee_scolaire: str = "2024-2025"
    notes: Optional[str] = None


class EmploiDuTempsRead(BaseModel):
    id: int
    ecole_id: int
    nom: str
    annee_scolaire: str
    statut: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    nb_lecons: Optional[int] = 0

    model_config = {"from_attributes": True}


class TacheRead(BaseModel):
    """État d'une génération lancée en arrière-plan."""
    id: int
    emploi_du_temps_id: int
    statut: str                       # en_attente | en_cours | terminee | echouee | annulee
    message: Optional[str] = None
    cout_courant: Optional[int] = None
    nb_solutions: int = 0
    lecons_planifiees: int = 0
    resultat: Optional[dict] = None
    erreurs: List[str] = []
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    terminee: bool = False
