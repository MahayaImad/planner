from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CoursRequisInput(BaseModel):
    """Un cours à planifier : quelle classe, quelle matière, quel prof, combien d'heures."""
    classe_id: int
    matiere_id: int
    professeur_id: int
    heures_par_semaine: int


class GenererRequest(BaseModel):
    """Corps de la requête POST /schedules/{id}/generer."""
    cours_requis: List[CoursRequisInput]
    limite_secondes: int = 120


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
