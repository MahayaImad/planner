from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClasseCreate(BaseModel):
    nom: str
    niveau: str  # primaire, moyen, secondaire
    effectif: int = 30
    salle_attitree_id: Optional[int] = None
    max_heures_par_jour: int = 6


class ClasseUpdate(BaseModel):
    nom: Optional[str] = None
    niveau: Optional[str] = None
    effectif: Optional[int] = None
    salle_attitree_id: Optional[int] = None
    max_heures_par_jour: Optional[int] = None


class ClasseRead(BaseModel):
    id: int
    ecole_id: int
    nom: str
    niveau: str
    effectif: int
    salle_attitree_id: Optional[int]
    max_heures_par_jour: int
    created_at: datetime

    model_config = {"from_attributes": True}
