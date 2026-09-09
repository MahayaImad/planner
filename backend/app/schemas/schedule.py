from pydantic import BaseModel

from .settings import GrilleInput, PonderationsInput
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


class FenetreInput(BaseModel):
    """Matière interdite sur une plage (journée d'inspection)."""
    matiere_id: int
    index_jour: int
    seances_bloquees: List[int]
    libelle: str = ""


class GenererRequest(BaseModel):
    """
    Corps de la requête POST /emplois-du-temps/{id}/generer.

    Tout ce qui n'est pas fourni est repris des réglages enregistrés de
    l'établissement : le client n'a normalement à envoyer que la liste
    des cours.
    """
    cours_requis: List[CoursRequisInput]
    grille: Optional[GrilleInput] = None
    fenetres_pedagogiques: Optional[List[FenetreInput]] = None
    ponderations: Optional[PonderationsInput] = None
    presence_minimale: Optional[Dict[str, int]] = None
    type_salle_ordinaire: Optional[str] = None
    limite_secondes: Optional[int] = None


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
